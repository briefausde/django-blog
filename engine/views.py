from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from django.urls import reverse, reverse_lazy
from engine.utils import paginator
from django.views.decorators.http import require_POST
from .forms import PostForm, UserForm, RegisterForm
from .models import Post, Log, Category, Comment, Index


# Js в отдельный файл и убрать из html
# Убрать логи
# Python manage.py commands
# add_coment, remove_comment поменять на view
# Js (jQuery), databases, book, Django REST

# выключить debug.
# cache
# from django.views.decorators.cache import cache_page
# from django.core.cache import cache
# cache.clear()
# @cache_page(120, key_prefix="main")


class RegisterView(generic.CreateView):
    model = User
    form_class = RegisterForm
    template_name = "registration/_register.html"

    def get_success_url(self):
        return reverse_lazy("accounts:register_done")


class StaffRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class LogMixin(object):
    def dispatch(self, request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
        Log.objects.create(ip=ip,
                           author=request.user,
                           method=request.method,
                           path=request.path,
                           body=str(request.body).strip(),
                           cookies=str(request.COOKIES),
                           meta=str(request.META),
                           date=timezone.now()
                           )
        return super(LogMixin, self).dispatch(request, *args, **kwargs)


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
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class UserDetailsView(LogMixin, generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'engine/user.html'

    def get_object(self):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = User
    form_class = UserForm
    template_name = 'engine/form_edit.html'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user)

    def get_success_url(self):
        return reverse('user_detail', args=(self.object.username,))


@require_POST
@staff_member_required
def user_block_unblock(request, username):
    user = get_object_or_404(User, username=username)
    if not user.is_staff:
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()


class CommentsListView(generic.ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'engine/comments.html'

    def get_queryset(self):
        return self.model.objects.filter(post__pk=self.kwargs['post_id']).order_by('-pk')


@require_POST
@login_required(login_url='/accounts/login/')
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    text = request.POST.get('text', '').strip()
    if text != '':
        comment = Comment.objects.create(author=request.user, text=text, post=post, created_date=timezone.now())
        comment.save()
    return redirect('/')


@require_POST
@login_required(login_url='/accounts/login/')
def remove_comment(request):
    comment_id = int(request.POST.get("id"))
    user = request.user
    comment = get_object_or_404(Comment, pk=comment_id)
    if user == comment.author or user.is_staff:
        comment.delete()
    return redirect('/')


class PostCreateView(LoginRequiredMixin, LogMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'engine/form_edit.html'

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
        if (self.request.user != post.author) and not self.request.user.is_staff:
            return redirect('post_detail', name=post.url)
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PostEditView(AuthorOrStaffRequiredMixin, LogMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'engine/form_edit.html'

    def get_success_url(self):
        return reverse('post_detail', args=(self.object.url,))


class PostsListView(LogMixin, generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'engine/post_list.html'

    def get_context_data(self, **kwargs):
        context = super(PostsListView, self).get_context_data(**kwargs)
        category = self.kwargs.get('category_name', 'all')
        pk = self.kwargs.get('pk', 1)
        posts = []

        if category != "all":
            context['category'] = category
            if get_object_or_404(Category, name=category):
                posts = Post.objects.filter(category__name=category,
                                            created_date__lte=timezone.now()).order_by('category', '-created_date')
        else:
            if pk != 1:
                context['category'] = "all"
            posts = Post.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')

        context['posts'] = paginator(posts, pk, 15)
        return context


class PostDetailsView(LogMixin, generic.DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'engine/post_detail.html'

    def get_context_data(self, **kwargs):
        post = self.get_object()
        post.update_views()
        context = super(PostDetailsView, self).get_context_data()
        from math import floor
        time = floor(len(post.text_big) * 0.075 / 60)
        context['read_time'] = time
        context['user'] = self.request.user
        return context

    def get_object(self):
        return Post.objects.filter(url=Post.url_refactoring(Post, self.kwargs['name'])).first()


class SearchListView(LogMixin, generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = "engine/search.html"

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data()
        word = self.request.GET.get('q', '')
        context['search_text'] = word

        if (len(word) < 3) or (len(word) > 120):
            context['text'] = "Search query should be from 3 to 120 characters"
        else:
            posts = Index.find(Index, word)
            if posts:
                self.template_name = "engine/post_list.html"
                context['posts'] = paginator(posts, self.request.GET.get('pk', 1), 15)
                context['query'] = word
            else:
                context['text'] = "Nothing found"
        return context
