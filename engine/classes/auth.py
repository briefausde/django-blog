<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from ..forms import AuthForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse


def login(request):
    if not request.user.is_authenticated():
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = auth_authenticate(username=username, password=password)
            # from django.contrib.auth.validators import ASCIIUsernameValidator
            # username_validator = ASCIIUsernameValidator()
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    next_url = request.GET.get('next', '')
                    if next_url and (next_url is not "/auth/logout/"):
                        return redirect(next_url)
                    else:
                        return redirect('main')
                else:
                    return render(request, 'engine/auth/login.html', {'text': 1})
            else:
                return render(request, 'engine/auth/login.html', {'text': 2})
        else:
            form = AuthForm()
        return render(request, 'engine/auth/login.html', {'form': form})
    else:
        return redirect('main')


def register():
    print("register")
    return reverse('main')


@login_required(login_url='/auth/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'engine/auth/login.html', {'form': form})


@login_required(login_url='/auth/login/')
def logout(request):
    auth_logout(request)
    return render(request, 'engine/auth/logout.html')
=======
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from ..forms import AuthForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse


def login(request):
    if not request.user.is_authenticated():
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = auth_authenticate(username=username, password=password)
            # from django.contrib.auth.validators import ASCIIUsernameValidator
            # username_validator = ASCIIUsernameValidator()
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    next_url = request.GET.get('next', '')
                    if next_url and (next_url is not "/auth/logout/"):
                        return redirect(next_url)
                    else:
                        return redirect('main')
                else:
                    return render(request, 'engine/auth/login.html', {'text': 1})
            else:
                return render(request, 'engine/auth/login.html', {'text': 2})
        else:
            form = AuthForm()
        return render(request, 'engine/auth/login.html', {'form': form})
    else:
        return redirect('main')


def register():
    print("register")
    return reverse('main')


@login_required(login_url='/auth/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'engine/auth/login.html', {'form': form})


@login_required(login_url='/auth/login/')
def logout(request):
    auth_logout(request)
    return render(request, 'engine/auth/logout.html')
>>>>>>> 64d5b50a23ee4bd33e7ebc3854e494618345a6e9
