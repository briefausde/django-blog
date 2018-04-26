from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.views import generic
from django.urls import reverse_lazy
from engine.utils import paginator
from .forms import *
from .models import *

from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser
from engine.serializers import *


# hide user email from api and from profile
# Js в отдельный файл и убрать из html
# Убрать логи, добавить кеширование
# Python manage.py commands
# Js (jQuery), databases, book, Django REST


# Mixin view

class StaffRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


# Register view

class RegisterView(generic.CreateView):
    model = User
    form_class = RegisterForm
    template_name = "registration/_register.html"

    def get_success_url(self):
        return reverse_lazy("accounts:register_done")


# Logs views

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


# Users views

class UserDetailsView(LogMixin, generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'engine/user.html'

    def get_object(self):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = Profile
    fields = ['description', 'img']
    template_name = 'engine/form_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(user__username=self.request.user)

    def get_success_url(self):
        return reverse('user_detail', args=(self.object.user.username,))


class UserChangeEmailView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = User
    fields = ['email']
    template_name = 'engine/form_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.request.user)

    def get_success_url(self):
        return reverse('user_detail', args=(self.object.username,))


# Comments views

class CommentsListView(generic.ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'engine/comments.html'

    def get_queryset(self):
        return self.model.objects.filter(post__pk=self.kwargs['post_id']).order_by('-pk')


class CommentAddView(LoginRequiredMixin, LogMixin, generic.CreateView):
    model = Comment
    fields = ['text']
    template_name = "engine/comments.html"
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super(CommentAddView, self).form_valid(form)


class CommentDeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
    model = Comment
    success_url = '/'

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.request.POST.get("id"))
        if not comment.author == self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return comment


# Posts views

class PostCreateView(LoginRequiredMixin, LogMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'engine/form_edit.html'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data()
        context.update(csrf(self.request))
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(PostCreateView, self).form_valid(form)


class PostEditView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'engine/form_edit.html'

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['button_delete_show'] = True
        return context

    def get_object(self, queryset=None):
        post = super(PostEditView, self).get_object()
        if not post.author == self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return post

    def get_success_url(self):
        return reverse('post_detail', args=(self.object.url,))


class PostDeleteView(LoginRequiredMixin, LogMixin, generic.DeleteView):
    model = Post
    success_url = '/'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if self.request.POST.get("confirm_delete"):
            post.delete()
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            return self.get(self, *args, **kwargs)

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if not post.author == self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return post


# Main page

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
        time = floor(len(post.text_big) * 0.075 / 60) + 1
        context['read_time'] = time
        context['user'] = self.request.user
        return context

    def get_object(self):
        # post = Post.objects.filter(url=Post.url_refactoring(Post, self.kwargs['name'])).first()
        # if not post:
        #     raise Http404
        # return post
        return get_object_or_404(Post, url=Post.url_refactoring(Post, self.kwargs['name']))


# Search view

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


# API

class IsOwnerOrIsStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrIsStaffOrReadOnly,)
    queryset = Post.objects.all().order_by('-pk')
    serializer_class = PostSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-pk')
    serializer_class = CategorySerializer
