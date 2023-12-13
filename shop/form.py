from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms


class CustomUserForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-conntrol','placeholder':'Enter User Name'}))
    email=forms.CharField(widget=forms.TextInput(attrs={'class':'form-conntrol','placeholder':'Enter User Email Address'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-conntrol','placeholder':'Enter Your Password'}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-conntrol','placeholder':'Enter Confirm Password'}))
    class meta:
        model=User
        fields=['username','email','password1','password2']

class YourForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))



       