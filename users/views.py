from datetime import datetime, timedelta
from django.contrib import messages
from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .forms import UserRegistrationForm, UserLoginForm, ProfileForm
from .models import Profile
# Create your views here.


class Register(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'authform.html', {
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
        return render(request, 'authform.html', {
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
                return redirect('authenticate')
        return redirect('index_1')


def Logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта!')
    return redirect('index_1')


class Profiles(View):
    def get(self, request):
        profiles = Profile.objects.all()
        context = {
            'title': 'Профили',
            'profiles': profiles
        }
        return render(request, 'users/profiles.html', context)

    @staticmethod
    def detailed(request, id_user):
        id_user = int(id_user)
        profile = get_object_or_404(Profile, id_user=id_user)
        form = ProfileForm({
            'vip': profile.vip,
            'activation_till': profile.activation_till
        })
        context = {
            'title': 'Редактировать профиль',
            'form': form
        }
        return render(request, 'users/profile_detailed.html', context)


class DetailedProfile(View):
    def get(self, request, id_user):
        id_user = int(id_user)
        profile = get_object_or_404(Profile, id_user=id_user)
        form = ProfileForm({
            'vip': profile.vip,
            'activation_till': profile.activation_till
        })
        context = {
            'title': 'Редактировать профиль',
            'form': form
        }
        return render(request, 'users/profile_detailed.html', context)

    def post(self, request, id_user):
        id_user = int(id_user)
        profile = get_object_or_404(Profile, id_user=id_user)
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile.vip = form.cleaned_data.get('vip')
            if form.cleaned_data.get('vip'):
                profile.activation_till = form.cleaned_data.get(
                    'activation_till'
                )
            else:
                profile.activation_till = 0
            profile.save()
        return redirect('profiles')


class Activate(View):
    def get(self, request):
        return redirect('profiles')

    def post(self, request):
        data = request.POST
        print(dict(data))
        profile = get_object_or_404(Profile, id_user=data.get('id_user'))

        if 'action' in data and 'amount' in data:
            if data.get('action') == 'append':
                if profile.activation_till > datetime.timestamp(datetime.now()):
                    profile.activation_till += 2592000 * \
                        int(data.get('amount'))
                else:
                    profile.activation_date = datetime.timestamp(
                        datetime.now())
                    profile.activation_till = datetime.timestamp(
                        datetime.now() + timedelta(int(data.get('amount'))))
                profile.vip = True
                profile.need_vip = False
            elif data.get('action') == 'remove':
                profile.activation_till == 0
                profile.vip = False
                profile.need_vip = False
            else:
                messages.error('Error has occured')
                return redirect('profiles')
            profile.save()
        else:
            messages.error('Error has occured')
            return redirect('profiles')

        return redirect('profiles')
