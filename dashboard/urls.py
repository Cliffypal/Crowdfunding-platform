from django.urls import path
from .views import (login_view, UserHomePage,CallView, 
                    logout, AdminHomePage, 
                    manage_investors, 
                    add_update, investment_form, sign_up, update_details, add_investment)


urlpatterns = [
    path('login/', login_view, name="login"),
    path('', UserHomePage.as_view(), name="user-home"),
    path('superuser', AdminHomePage.as_view(), name="admin-home"),
    path('calls/', CallView.as_view(), name="calls"),
    path('logout/', logout, name="logout"),
    path('investors/', manage_investors, name="investors"),
    path('investment_form/', investment_form, name="investment_form"),
    path('calls/add_update', add_update, name="add_update"),
    path('sign_up/', sign_up, name="sign_up"),
    path('add_investment/', add_investment, name="add_investment"),
    path('details/<int:id>/', update_details, name="update"),
]