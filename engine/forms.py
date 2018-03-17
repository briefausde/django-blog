from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'text_small', 'text_big', 'img_small', 'img_big', 'tags', 'category', 'url', 'comments_mode',)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


# example of form style.
# from django.contrib.auth.models import User
# from django.forms import Textarea, PasswordInput, TextInput
# class AuthForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password',)
#         widgets = {
#             'username': TextInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
#             'password': PasswordInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
#         }
