# from django.utils.decorators import method_decorator
# from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from .forms import AuthForm, PostForm
from .models import Post, Log, Category, Comment, StaticPage, Index
from random import randint
from re import sub


# запретить доставать комменты с /comments/id get запросом, только лишь post
# оптимизация базы
# выключить debug
# cache
# from django.views.decorators.cache import cache_page
# from django.core.cache import cache
# cache.clear()
# @cache_page(120, key_prefix="main")


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
        return redirect("main")
    delete_indexes()
    create_indexes()
    return redirect('main')


def logs_add(request, data=""):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    import datetime
    Log.objects.create(ip=ip,
                       user=request.user,
                       method=request.method,
                       path=request.path,
                       body=str(request.body).strip(),
                       cookies=str(request.COOKIES),
                       meta=str(request.META),
                       data=str(data).strip(),
                       date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # make for timezone django time


# view_logs detailview
def view_logs(request, pk=0):
    logs_add(request)
    if request.user.is_staff:
        if pk == "0":
            return render(request, 'engine/logs_view.html')
        else:
            log = get_object_or_404(Log, pk=pk)
            return render(request, 'engine/logs_detail.html', {'log': log})
    return redirect("main")


class StaffRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class LogsListView(StaffRequiredMixin, generic.ListView):
    model = Log
    context_object_name = 'logs'
    template_name = 'engine/logs.html'

    def get_context_data(self, **kwargs):
        context = super(LogsListView, self).get_context_data(**kwargs)
        # context['some_data'] = 'This is just some data'
        return context

    def get_queryset(self):
        return Log.objects.all().order_by('-date')[0:500]


def get_paginator_posts(posts, pk, count):
    pg = Paginator(posts, count)
    try:
        posts = pg.page(int(pk))
    except EmptyPage:
        posts = pg.page(pg.num_pages)
    return posts


def get_posts(category_name):
    if (category_name == "all") or (category_name not in category_list):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    else:
        return Post.objects.filter(category__name=category_name,
                                   published_date__lte=timezone.now()).order_by('category', '-published_date')


class PostsListView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'engine/post_list.html'

    def get_context_data(self, **kwargs):
        logs_add(self.request)
        context = super(PostsListView, self).get_context_data(**kwargs)
        category = self.kwargs.get('category_name', 'all')
        pk = self.kwargs.get('pk', 1)
        if category != "all" or pk != 1:
            context['category'] = category
        return context

    def get_queryset(self):
        category = self.kwargs.get('category_name', 'all')
        pk = self.kwargs.get('pk', 1)
        return get_paginator_posts(get_posts(category), pk, 15)


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

    posts = find(word)
    if posts:
        return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(posts, pk, 15),
                                                         'query': word,
                                                         'search_text': word})
    else:
        return render(request, 'engine/search.html', {'search_text': word, 'text': 1})


def user_profile(request, username, pk=1):
    logs_add(request, username)
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, published_date__lte=timezone.now()).order_by('author', '-published_date')
    return render(request, 'engine/post_list.html', {'posts': get_paginator_posts(posts, pk, 9), 'user_profile': user})


class CommentsListView(generic.ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'engine/comments.html'

    def get_queryset(self):
        return Comment.objects.filter(post__pk=self.kwargs['post_id']).order_by('-pk')


@login_required(login_url='/auth/login/')
def add_comment(request, post_id):
    if request.POST:
        post = get_object_or_404(Post, pk=post_id)
        text = request.POST.get('text')
        text = text.strip()
        logs_add(request, text)
        if text != '':
            comment = Comment.objects.create(author=request.user, text=text, post=post, created_date=timezone.now())
            comment.save()
    return redirect('/')


@login_required(login_url='/auth/login/')
def remove_comment(request):
    if request.method == "POST":
        comment_id = str(request.body).split("=")[2][0:-1]
        logs_add(request, comment_id)
        user = request.user
        comment = get_object_or_404(Comment, pk=comment_id)
        if user == comment.author or user.is_staff:
            comment.delete()
    return redirect('/')


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


def refactor_url(text):
    return str.lower(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', text.replace("-", " ")).replace(" ", "-"))


def upd(request, form):
    logs_add(request)
    post = form.save(commit=False)
    post.author = request.user
    post.published_date = timezone.now()
    if len(post.url) > 1:
        # where url=post.url and pk isn't post.pk
        if Post.objects.filter(url=refactor_url(post.url)).exclude(pk=post.pk).order_by('url'):
            post.url = refactor_url(post.url) + "-" + str(randint(1, 999999))
        else:
            post.url = refactor_url(post.url)
    else:
        post.url = refactor_url(post.name)
    post.save()
    return post.url


@login_required(login_url='/auth/login/')
def post_new(request):  # добавить функцию в модель поста
    logs_add(request)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            return redirect('post_detail', name=upd(request, form))
    else:
        form = PostForm()
    return render(request, 'engine/post_edit.html', {'form': form})


@login_required(login_url='/auth/login/')
def post_edit(request, pk):
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


def post_detail(request, name):
    logs_add(request)
    post = get_object_or_404(Post, url=refactor_url(name))
    Post.objects.filter(pk=post.pk).update(views=(post.views + 1))
    from math import floor
    time = floor(len(post.text_big) * 0.075 / 60)
    return render(request, 'engine/post_detail.html', {'post': post, 'read_time': time, 'views': post.views})


def delete_indexes():
    Index.objects.all().delete()
    print("All indexes deleted")


def split_str(string):
    return set(str.upper(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', string).replace("  ", " ")).split(" "))


def test():
    posts = Post.objects.order_by('-pk')[0].pk
    print("test function: %s" % posts)


def create_indexes():
    last_pk = Post.objects.order_by('-pk')[0].pk
    indexes = {}
    for i in range(1, last_pk+1):
        try:
            post = get_object_or_404(Post, pk=i)
            words = split_str(post.text_big)
            for word in words:
                if len(word) > 1:
                    if not indexes.get(word):
                        indexes[word] = set()
                    indexes[word].add(post.pk)
        except:
            None
    for key in indexes:
        Index.objects.create(word=key, index=indexes[key])
        print("For {0} created index {1}".format(key, indexes[key]))


'''
def create_indexes():
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    indexes = {}
    for post in posts:
        words = split_str(post.text_big)
        for word in words:
            if len(word) > 1:
                if not indexes.get(word):
                    indexes[word] = set()
                indexes[word].add(post.pk)
    del posts
    for key in indexes:
        Index.objects.create(word=key, index=indexes[key])
        print("For {0} created index {1}".format(key, indexes[key]))
'''


def add_index(pk):
    post = get_object_or_404(Post, pk=pk)
    words = split_str(post.text_big)
    for word in words:
        if len(word) > 1:
            indexes = set()
            try:
                indexes = get_object_or_404(Index, word=word).getindex()
                indexes.add(pk)
                Index.objects.filter(word=word).update(index=indexes)
            except:
                indexes.add(pk)
                Index.objects.create(word=word, index=indexes)


def find(search_request):
    search_words = split_str(search_request)
    posts = []
    try:
        for key in search_words:
            posts.append(get_object_or_404(Index, word=key).getindex())
        rez = posts[0]
        for i in range(len(posts) - 1):
            rez = set(posts[i]) & set(posts[i + 1])
        posts = []
        for i in rez:
            posts.append(Post.objects.get(pk=i))
    except:
        None
    return posts
