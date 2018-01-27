# from django.utils.decorators import method_decorator
# from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.template import TemplateDoesNotExist
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from .forms import AuthForm, PostForm
from .models import Post, Log, Category, Comment, StaticPage, Index
from re import sub


# запретить доставать комменты с /comments/id get запросом, только лишь post
# оптимизация базы
# выключить debug
# cache
# from django.views.decorators.cache import cache_page
# from django.core.cache import cache
# cache.clear()
# @cache_page(120, key_prefix="main")


# always restart server after appending new category
def declare_category_list():
    categories = ""
    for category in Category.objects.all():
        categories += category.name + "|"
    if not categories:
        Category.objects.create(name="all")
        Category.objects.create(name="news")
        return "all|news"
    return categories[0:-1]


category_list = declare_category_list()


# always restart server after appending new static_page
def declare_static_pages_list():
    pages = ""
    for page in StaticPage.objects.all():
        pages += page.url + "|"
    return pages[0:-1]


try:
    static_pages_list = declare_static_pages_list()
except:
    static_pages_list = "|"


def reload(request):
    logs_add(request)
    if not request.user.is_superuser:
        return redirect("main")
    delete_indexes()
    create_indexes()
    return redirect('main')


def logs_add(request, data=""):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
    Log.objects.create(ip=ip,
                       author=request.user,
                       method=request.method,
                       path=request.path,
                       body=str(request.body).strip(),
                       cookies=str(request.COOKIES),
                       meta=str(request.META),
                       data=str(data).strip(),
                       date=timezone.now()
                       )


def url_refactor(text):
    return str.lower(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', text.replace("-", " ")).replace(" ", "-"))


def split_str(string):
    return set(str.upper(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', string).replace("  ", " ")).split(" "))


def get_paginator_posts(posts, pk, count):
    pg = Paginator(posts, count)
    try:
        posts = pg.page(int(pk))
    except EmptyPage:
        posts = pg.page(pg.num_pages)
    return posts


class StaticPageView(generic.TemplateView):
    model = StaticPage
    template_name = ''

    def get_context_data(self, **kwargs):
        url = self.kwargs['page_name']
        logs_add(self.request, url)
        # добавить обработку ошибки если файла с шаблоном не существует
        self.template_name = 'engine/static/' + get_object_or_404(self.model, url=url).template_name
        return super(StaticPageView, self).get_context_data()


class StaffRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class LogsView(StaffRequiredMixin, generic.TemplateView):
    template_name = 'engine/logs_view.html'

    def get_context_data(self, **kwargs):
        context = super(LogsView, self).get_context_data()
        context['filter'] = self.request.GET.get('filter')
        context['path'] = self.request.GET.get('path')
        context['ip'] = self.request.GET.get('ip')
        context['author'] = self.request.GET.get('author')
        context['data'] = self.request.GET.get('data')
        return context


class LogsListView(StaffRequiredMixin, generic.ListView):
    model = Log
    context_object_name = 'logs'
    template_name = 'engine/logs_list.html'

    def get_queryset(self):
        filters = self.request.GET.get('filter')
        if filters == "path":
            return self.model.objects.filter(path=self.request.GET.get(filters)).order_by('-date')[0:500]
        if filters == "ip":
            return self.model.objects.filter(ip=self.request.GET.get(filters)).order_by('-date')[0:500]
        if filters == "author":
            return self.model.objects.filter(author=self.request.GET.get(filters)).order_by('-date')[0:500]
        if filters == "data":
            return self.model.objects.filter(data=self.request.GET.get(filters)).order_by('-date')[0:500]
        return self.model.objects.all().order_by('-date')[0:500]


class LogDetailsView(StaffRequiredMixin, generic.DetailView):
    model = Log
    context_object_name = 'log'
    template_name = 'engine/logs_detail.html'

    def get_object(self):
        logs_add(self.request)
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class UserDetailsView(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'engine/user.html'

    def get_object(self):
        logs_add(self.request)
        return get_object_or_404(self.model, username=self.kwargs['username'])


class CommentsListView(generic.ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'engine/comments.html'

    def get_queryset(self):
        return self.model.objects.filter(post__pk=self.kwargs['post_id']).order_by('-pk')


@login_required(login_url='/accounts/login/')
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


@login_required(login_url='/accounts/login/')
def remove_comment(request):
    if request.method == "POST":
        comment_id = str(request.body).split("=")[2][0:-1]
        logs_add(request, comment_id)
        user = request.user
        comment = get_object_or_404(Comment, pk=comment_id)
        if user == comment.author or user.is_staff:
            comment.delete()
    return redirect('/')


def register():
    return reverse("accounts:register_done")


class RegisterDoneView(generic.TemplateView):
    template_name = "registration/_register_done.html"

    def get_context_data(self, **kwargs):
        return super(RegisterDoneView, self).get_context_data()


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'engine/post_new_edit.html'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data()
        context.update(csrf(self.request))
        return context

    def form_valid(self, form):
        if self.request.user:
            form.instance.author = self.request.user
            return super(PostCreateView, self).form_valid(form)
        else:
            return redirect('main')


class AuthorOrStaffRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        # if (true) and (true(not true))
        if (self.request.user != post.author) and not self.request.user.is_superuser:
            return redirect('post_detail', name=post.url)
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PostEditView(AuthorOrStaffRequiredMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'engine/post_new_edit.html'

    def get_success_url(self):
        # return '/article/{}'.format(self.object.url)
        return reverse('post_detail', args=(self.object.url,))

    def get_context_data(self, **kwargs):
        logs_add(self.request)
        return super(PostEditView, self).get_context_data()


class PostsListView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'engine/post_list.html'

    def get_context_data(self, **kwargs):
        logs_add(self.request)
        context = super(PostsListView, self).get_context_data(**kwargs)
        category = self.kwargs.get('category_name', 'all')
        pk = self.kwargs.get('pk', 1)

        if (category in category_list) and (category != "all"):
            context['category'] = category
            posts = Post.objects.filter(category__name=category,
                                        created_date__lte=timezone.now()).order_by('category', '-created_date')
        else:
            if pk != 1:
                context['category'] = "all"
            posts = Post.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')

        context['posts'] = get_paginator_posts(posts, pk, 15)
        return context


class PostDetailsView(generic.DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'engine/post_detail.html'

    def get_context_data(self, **kwargs):
        logs_add(self.request)
        post = self.get_object()
        post.views += 1
        post.save()
        context = super(PostDetailsView, self).get_context_data()
        from math import floor
        time = floor(len(post.text_big) * 0.075 / 60)
        context['read_time'] = time
        context['user'] = self.request.user
        return context

    def get_object(self):
        return Post.objects.filter(url=url_refactor(self.kwargs['name'])).first()


def delete_indexes():
    Index.objects.all().delete()
    print("All indexes deleted")


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


class SearchListView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = "engine/search.html"

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data()
        word = self.request.GET.get('q', '')
        logs_add(self.request, data=word)
        context['search_text'] = word

        if (len(word) < 3) or (len(word) > 120):
            context['text'] = "Search query should be from 3 to 120 characters"
        else:
            posts = find(word)
            if posts:
                self.template_name = "engine/post_list.html"
                context['posts'] = get_paginator_posts(posts, self.request.GET.get('pk', 1), 15)
                context['query'] = word
            else:
                context['text'] = "Nothing find"

        return context
