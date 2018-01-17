<<<<<<< HEAD
from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms import Textarea, PasswordInput, TextInput


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'text_small', 'text_big', 'img_small', 'img_big', 'tags', 'category', 'url', 'comments_mode',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': "Input your comment and press ENTER", 'style': "width:87%;height:50px"}),
        }


class AuthForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password',)
        widgets = {
            'username': TextInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
            'password': PasswordInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
        }


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(label="Username", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
#     password = forms.CharField(label="Password", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
=======
from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms import Textarea, PasswordInput, TextInput


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'text_small', 'text_big', 'img_small', 'img_big', 'tags', 'category', 'url', 'comments_mode',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': "Input your comment and press ENTER", 'style': "width:87%;height:50px"}),
        }


class AuthForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password',)
        widgets = {
            'username': TextInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
            'password': PasswordInput(attrs={'cols': 20, 'rows': 2, 'style': "hello bro"}),
        }


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(label="Username", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
#     password = forms.CharField(label="Password", max_length=30,
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
>>>>>>> 64d5b50a23ee4bd33e7ebc3854e494618345a6e9
