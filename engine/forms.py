from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'text_small', 'text_big', 'img_small', 'img_big', 'tags', 'category', 'url', 'comments_mode',)


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
