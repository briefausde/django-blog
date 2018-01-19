from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from ..models import Post
from ..forms import PostForm
from ..views import logs_add
# from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from random import randint
from re import sub


def refactor_url(text):
    return str.lower(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', text.replace("-", " ")).replace(" ", "-"))


def upd(request, form):
    logs_add(request)
    post = form.save(commit=False)
    post.author = request.user
    post.published_date = timezone.now()
    if len(post.url) > 1:
        if Post.objects.filter(url=refactor_url(post.url)).exclude(pk=post.pk).order_by('url'):  # where url=post.url and pk isn't post.pk
            post.url = refactor_url(post.url) + "-" + str(randint(1, 999999))
        else:
            post.url = refactor_url(post.url)
    else:
        post.url = refactor_url(post.name)
    post.save()
    return post.url


@login_required(login_url='/auth/login/')
def new(request):  # добавить функцию в модель поста
    logs_add(request)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            return redirect('post_detail', name=upd(request, form))
    else:
        form = PostForm()
    return render(request, 'engine/post_edit.html', {'form': form})


@login_required(login_url='/auth/login/')
def edit(request, pk):
    logs_add(request)
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('post_detail', pk=post.pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            return redirect('post_detail', name=upd(request, form))
    else:
        form = PostForm(instance=post)
    return render(request, 'engine/post_edit.html', {'form': form})


def detail(request, name):
    logs_add(request)
    post = get_object_or_404(Post, url=refactor_url(name))
    Post.objects.filter(pk=post.pk).update(views=(post.views + 1))
    from math import floor
    time = floor(len(post.text_big) * 0.075 / 60)
    return render(request, 'engine/post_detail.html', {'post': post, 'read_time': time, 'views': post.views})
