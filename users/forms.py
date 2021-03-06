from django import forms
from django.forms.widgets import PasswordInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password1', 'password2']


class UserLoginForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.Field(required=True, widget=PasswordInput, label='Пароль')


class ProfileForm(forms.ModelForm):
    class Meta:

        model = Profile
        fields = ('vip', 'activation_till')
