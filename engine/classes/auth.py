from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from ..forms import AuthForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from ..views import logs_add


def login(request):
    if not request.user.is_authenticated():
        if request.method == "POST":
            username = request.POST['username']
            logs_add(request, '[trying login as] ' + username)
            password = request.POST['password']
            user = auth_authenticate(username=username, password=password)
            # from django.contrib.auth.validators import ASCIIUsernameValidator
            # username_validator = ASCIIUsernameValidator()
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    logs_add(request, '[successful login as] ' + username)
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
    logs_add(request)
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
    logs_add(request, '[logout]')
    auth_logout(request)
    return render(request, 'engine/auth/logout.html')
