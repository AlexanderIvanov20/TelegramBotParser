from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm
# Create your views here.


class Register(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'users/auth.html', {
            'title': 'Регистрация',
            'form': form,
            'action': 'register'
        })

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            form.save()
            user_registered = f'''
            Пользователь {username} успешно зарегистрирован!
            '''
            messages.success(request, user_registered)
            user = User.objects.get(username=username)
        else:
            return redirect('register')
        return redirect('authenticate')


class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'users/auth.html', {
            'title': 'Вход',
            'form': form,
            'action': 'login'
        })

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                messages.success(request, 'Вы успешно вошли в аккаунт!')
                login(request, user)
            else:
                messages.warning(request, 'Ошибка')
        return redirect('index')


def Logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта!')
    return redirect('index')
