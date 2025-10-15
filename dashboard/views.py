from typing import Any
from datetime import date
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from .forms import CustomLoginForm, UpdateForm, SignUpForm
from django.views.generic import ListView, TemplateView
from .models import CustomUser, Investments, Calls, Update
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
# Create your views here.

class BaseClass:
    def authenticate_session(self):
            if self.request.user.is_authenticated:
                return True
            else:
                #route to the sign in page
                return redirect('login')

# def dateChecker(user):
#     investments = Investments.objects.filter(investor=user)
#     if investments.call.projected_end_date < datetime.now():
#         return "active"
#     else:
#         return "inactive"
    
def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin-home')  
                elif user.is_verified:
                    login(request, user)
                    return redirect('user-home')  
                else:
                    messages.error(request, "Your account hasn't been verified, so you can't log in.")
            else:
                messages.error(request, "Invalid Credentials.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


class AdminHomePage(ListView, LoginRequiredMixin, BaseClass):
    model = Investments
    template_name = "index.html"
    login_url = "login"

    def get_queryset(self):
        self.authenticate_session()
        if self.request.user.is_authenticated:
            return Investments.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['number_users'] = CustomUser.objects.filter(is_superuser=False).count()
        context['total_money'] = Investments.objects.aggregate(Sum('price'))['price__sum']
        context['updates'] = Update.objects.all()
        return context

class UserHomePage(ListView, BaseClass):
    model = Investments
    template_name = "index_user.html"
    login_url = "login"

    def get_queryset(self):
        self.authenticate_session()
        if self.request.user.is_authenticated:
            return Investments.objects.filter(investor=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_money'] = Investments.objects.filter(investor=self.request.user).aggregate(Sum('price'))['price__sum']
        context['updates'] = Update.objects.all()
        context['username'] = self.request.user.username
        context['current_date'] = date.today()
        return context

class CallView(ListView):
    template_name = "calls.html"
    model = Calls

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Calls.objects.all()
        else:
            return redirect('login')


def update_details(request, id):
    if request.user.is_superuser:
        investments = Investments.objects.all()
        new_updates = Update.objects.all()
        update = get_object_or_404(Update, id=id)
        number_users = CustomUser.objects.filter(is_superuser=False).count()
        total_money = Investments.objects.aggregate(Sum('price'))['price__sum']
    else:
        update = get_object_or_404(Update, id=id)
        investments = Investments.objects.filter(investor=request.user)
        new_updates = Update.objects.all()
    
    context = {
        'update': update, 
        "object_list": investments, 
        "updates": new_updates,
        "number_users" : number_users,
        "total_money": total_money,
    }
    return render(request, 'update_details.html', context)


def manage_investors(request):
    investments = Investments.objects.all()

    if request.method == "POST":
        investment_id = request.POST.get("investment_id")
        investment = Investments.objects.get(id=investment_id)
        investment.is_verified = True
        investment.save()
        return redirect("admin-home") 

    return render(request, "investors.html", {"investments": investments})

def sign_up(request):
    investment_data = request.session.get('investment_data', None)  

    if investment_data is None:
        messages.error(request, "Please fill the investment form first.")
        return redirect('investment_form')

    name = investment_data.get('name', '')
    acre = int(investment_data.get('acre', 0))
    call_id = investment_data.get('call_id', '')

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            investment_call = get_object_or_404(Calls, id=call_id)  # Convert string to integer automatically
            user = form.save()
            user.is_verified = True
            price = investment_call.price_of_acre * acre
            user.save()
            investment = Investments(call=investment_call, investor=user, size=acre, price=price, rate=investment_call.rate)
            investment.save()

            login(request, user)
            # Clear session data
            del request.session['investment_data']
            return redirect('user-home')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})


def add_update(request):
    calls = Calls.objects.all()
    if request.method == "POST":
        form = UpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            call_id = request.POST.get("calls")
            
            try:
                call = Calls.objects.get(id=call_id)
                update.call = call  
                update.save()
                messages.success(request, "Update added successfully")
                return redirect('add_update')
            except Calls.DoesNotExist:
                messages.error(request, "Invalid call selected")
        else:
            messages.error(request, "Form is not valid")
    else:
        form = UpdateForm()

    return render(request, "add_update.html", {"form": form, "calls": calls})

def add_investment(request):
    calls = Calls.objects.all()
    investments = Investments.objects.filter(investor=request.user)
    new_updates = Update.objects.all()
    if request.method == "POST":
        acre = int(request.POST.get('acre'))
        call_id = request.POST.get('calls')
        investment_call = get_object_or_404(Calls, id=call_id)
        price = investment_call.price_of_acre * acre

        investment = Investments(call=investment_call, investor=request.user, size=acre, price=price, rate=investment_call.rate)
        investment.save()
        return redirect('user-home')
    return render(request, "add_investments.html", {'calls': calls, "object_list": investments, "updates": new_updates})


def investment_form(request):
    calls = Calls.objects.all()
    if request.method == "POST":
        acre = int(request.POST.get('acre'))
        call_id = request.POST.get('calls')
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        investment_call = get_object_or_404(Calls, id=call_id)
        price = investment_call.price_of_acre * acre

        investment = Investments(call=investment_call, investor=request.user, 
                                 size=acre, 
                                 price=price, 
                                 rate=investment_call.rate,
                                 full_name=full_name, email=email)
        investment.save()
    return render(request, 'fill_form.html', {'calls': calls})


def logout(request):
    request.session.flush()
    return redirect('login')