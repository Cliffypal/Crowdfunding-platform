from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Update
from .models import CustomUser


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password'
        })
    )

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ["subject", "body"]
    
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs.update({
            'class': 'update-subject',
            'placeholder': 'Enter your subject here',
        })
        self.fields['body'].widget.attrs.update({
            'class': 'blog-textarea',
            'placeholder': 'Enter your report here',
        })


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={
            'placeholder': 'Enter your email here',
        }
    ))
    class Meta:
        model = CustomUser
        fields = ["username", "email" ,"password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username here',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter password here',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password here',
        })