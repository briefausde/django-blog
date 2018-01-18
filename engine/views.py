from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.utils import timezone
from .models import Post, Log, Category, Comment, StaticPage
from django.contrib.auth.models import User
from .classes import search
from .forms import CommentForm

# оптимизация базы
# выключить debug
# cache

# from django.views.decorators.cache import cache_page
# from django.core.cache import cache
# cache.clear()
# @cache_page(120, key_prefix="main")

# for post in Post.objects.all():
#     if post.pk not in [57, 44, 69, 39, 63]:
#         post.delete()


category_list = ""
static_pages_list = ""
try:
    for i in Category.objects.all():
        category_list += i.name + "|"
    category_list = category_list[0:-1]

    for i in StaticPage.objects.all():
        static_pages_list += i.url + "|"
    static_pages_list = static_pages_list[0:-1]
except:
    print("Static_page_template_error: please add data in category or staticpage")


def reload(request):
    logs_add(request)
    if not request.user.is_superuser:
        return HttpResponse('You are not admin')
    search.delete_indexes()
    search.create_indexes()
    return redirect('main')


def get_logs(request):
    if not request.user.is_superuser:
        logs_add(request)
        return HttpResponse('You are not admin')
    logs = Log.objects.all().order_by('-date')[0:500]
    return render(request, 'engine/logs.html', {'logs': logs})


def logs_add(request, data=""):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    import datetime
    Log.objects.create(ip=ip, user=request.user, path=request.path, data=data, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # make for timezone django time


def get_posts(category):
    if (category == "all") or (category not in category_list):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    else:
        return Post.objects.filter(category=Category.objects.get(name=category), published_date__lte=timezone.now()).order_by('category', '-published_date')


def get_paginator_posts(posts, pk, count):
    pg = Paginator(posts, count)
    try:
        posts = pg.page(int(pk))
    except EmptyPage:
        posts = pg.page(pg.num_pages)
    return posts


def main(request):
    logs_add(request)
    return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(get_posts("all"), 1, 15)})


def category_page(request, category_name, pk=1):
    logs_add(request)
    return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(get_posts(category_name), pk, 15),
                                                     'category': category_name})


def load_static_page(request, page_name):
    logs_add(request)
    try:
        template = get_object_or_404(StaticPage, url=page_name).template_name
        return render(request, 'engine/static/' + template)
    except:
        return redirect('main')


def find_word(request, pk=1):
    word = request.GET.get('q', '')
    logs_add(request, data=word)
    if not word:
        return render(request, 'engine/search.html', {})

    if (len(word) < 3) or (len(word) > 120):
        return render(request, 'engine/search.html', {'search_text': word, 'text': 2})

    posts = search.find(word)
    if posts:
        return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(posts, pk, 15), 'query': word, 'search_text': word})
    else:
        return render(request, 'engine/search.html', {'search_text': word, 'text': 1})


def user_profile(request, username, pk=1):
    logs_add(request, username)
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, published_date__lte=timezone.now()).order_by('author', '-published_date')
    return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(posts, pk, 9), 'user_profile': user})


def get_comments(request, post_id):
    comments = Comment.objects.filter(post=Post.objects.get(pk=post_id)).order_by('-pk')
    return render(request, 'engine/comments.html', {'comments': comments})


def add_comment(request, post_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = User.objects.get(
                username=request.user) if request.user.is_authenticated else User.objects.get(username="Anonymous")
            comment.post = Post.objects.get(pk=post_id)
            comment.published_date = timezone.now()
            comment.save()
            return redirect('/')


def remove_comment(request):
    if request.method == "POST":
        print(request.body)
        comment_id = str(request.body).split("=")[2][0:-1]
        user = request.user
        comment = get_object_or_404(Comment, pk=comment_id)
        if user == comment.author or user.is_staff:
            comment.delete()
    return redirect('/')
