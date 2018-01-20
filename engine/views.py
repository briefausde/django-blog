from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
# from django.http import HttpResponse, Http404
from django.utils import timezone
# from django.utils.decorators import method_decorator
from .models import Post, Log, Category, Comment, StaticPage
from django.contrib.auth.models import User
from .classes import search
from django.views import generic

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
    search.delete_indexes()
    search.create_indexes()
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

    posts = search.find(word)
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


# from django.contrib.auth.decorators import user_passes_test
# @user_passes_test(lambda u: u.is_superuser)
# запретить доставать комменты с /comments/id get запросом, только лишь post
