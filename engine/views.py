from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.template.context_processors import csrf
from django.views import generic
from django.urls import reverse_lazy
from engine.utils import paginator
from .forms import *
from .models import *

from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from engine.serializers import *


# hide user email from api and from profile
# Js в отдельный файл и убрать из html
# Python manage.py commands
# Js (jQuery), databases, book, Django REST
# fix password_reset_confirm
# архив, модерация постов для всего сайта, загрузка картинок, убрать логи, добавить кеширование

# notifications: проверка на авторизованного юзера, проверка или это подписка на тебя, исправить ajaxunsub & ajaxsub
# поменять в сигналах post_save на pre_save


# Mixin views

class StaffRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class AuthorRequiredMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.author == self.request.user and not self.request.user.is_staff:
            return self.handle_no_permission()
        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)


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


# Feedback views

class FeedbackSendView(LogMixin, generic.CreateView):
    model = Feedback
    fields = ['email', 'subject', 'message']
    template_name = "engine/form_default.html"
    success_url = "/"


class FeedbackListView(StaffRequiredMixin, LogMixin, generic.ListView):
    model = Feedback
    context_object_name = 'feedback_list'
    template_name = "engine/feedback_list.html"

    def get_queryset(self):
        return self.model.objects.all().order_by('-date')[0:100]


class FeedbackDetailsView(StaffRequiredMixin, LogMixin, generic.DetailView):
    model = Feedback
    context_object_name = 'feedback'
    template_name = "engine/feedback_detail.html"


class FeedbackAnsweredView(StaffRequiredMixin, LogMixin, generic.UpdateView):
    model = Feedback
    fields = ['status']
    success_url = "/"
    template_name = "engine/base.html"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.POST.get('pk'))

    def post(self, *args, **kwargs):
        feedback = self.get_object()
        feedback.status = not feedback.status
        feedback.save()
        return self.get(self, *args, **kwargs)


# Users views

class UserDetailsView(LogMixin, generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'engine/user.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailsView, self).get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author__username=self.kwargs['username'])
        if self.request.user.subscriber.filter(author__username=self.kwargs['username']):
            context['subscribe'] = True
        return context

    def get_object(self):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = Profile
    fields = ['description', 'img']
    template_name = 'engine/form_default.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(user__username=self.request.user)

    def get_success_url(self):
        return reverse('user_detail', args=(self.object.user.username,))


class UserChangeEmailView(LoginRequiredMixin, LogMixin, generic.UpdateView):
    model = User
    fields = ['email']
    template_name = 'engine/form_default.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.request.user)

    def get_success_url(self):
        return reverse('user_detail', args=(self.object.username,))


# Notifications views

class SubscribeOnUserNotificationsView(LogMixin, LoginRequiredMixin, generic.View):

    def post(self, *args, **kwargs):
        if not self.request.user.subscriber.filter(author__username=self.request.POST.get('author')):
            AuthorsSubscriber.objects.create(
                author=get_object_or_404(User, username=self.request.POST.get('author')),
                subscriber=self.request.user
            )
        return HttpResponseRedirect('/')


class UnSubscribeOnUserNotificationsView(LogMixin, LoginRequiredMixin, generic.DeleteView):
    model = AuthorsSubscriber
    success_url = '/'

    def get_object(self, queryset=None):
        return get_object_or_404(AuthorsSubscriber,
                                 subscriber=self.request.user,
                                 author=get_object_or_404(User, username=self.request.POST.get('author'))
                                 )


class NotificationsListView(LogMixin, LoginRequiredMixin, generic.ListView):
    model = NewPostNotification
    context_object_name = 'notifications'
    template_name = 'engine/notifications.html'

    def get_queryset(self):
        return self.model.objects.filter(authors_subscriber__subscriber=self.request.user).order_by('-date')[0:50]


class NotificationsCountView(LogMixin, LoginRequiredMixin, generic.View):

    def post(self, *args, **kwargs):
        notifications = NewPostNotification.objects.filter(
            authors_subscriber__subscriber=self.request.user,
            status=False
        ).count()
        return HttpResponse(notifications)


class NotificationViewedView(StaffRequiredMixin, LogMixin, generic.UpdateView):
    model = NewPostNotification
    fields = ['status']
    success_url = "/"
    template_name = "engine/base.html"

    def get_object(self, queryset=None):
        owner = NewPostNotification.objects.get(pk=self.request.POST.get("pk")).authors_subscriber.subscriber.username
        if owner == self.request.user.username:
            return get_object_or_404(self.model, pk=self.request.POST.get('pk'))
        return HttpResponseForbidden()

    def post(self, *args, **kwargs):
        notification = self.get_object()
        notification.status = True
        notification.save()
        return self.get(self, *args, **kwargs)


class NotificationDeleteView(LogMixin, generic.DeleteView):
    model = NewPostNotification
    success_url = '/'

    def get_object(self, queryset=None):
        owner = NewPostNotification.objects.get(pk=self.request.POST.get("pk")).authors_subscriber.subscriber.username
        if owner == self.request.user.username:
            return get_object_or_404(NewPostNotification, pk=self.request.POST.get("pk"))
        return HttpResponseForbidden()


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


class CommentDeleteView(AuthorRequiredMixin, LogMixin, generic.DeleteView):
    model = Comment
    success_url = '/'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.request.POST.get("id"))


# Posts views

class PostCreateView(LoginRequiredMixin, LogMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'engine/form_default.html'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data()
        context.update(csrf(self.request))
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(PostCreateView, self).form_valid(form)


class PostEditView(AuthorRequiredMixin, LogMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'engine/form_default.html'

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['button_delete_show'] = True
        return context

    def get_success_url(self):
        return reverse('post_detail', args=(self.object.url,))


class PostDeleteView(AuthorRequiredMixin, LogMixin, generic.DeleteView):
    model = Post
    success_url = '/'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if self.request.POST.get("confirm_delete"):
            post.delete()
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            return HttpResponseRedirect(post.get_absolute_url())
        return self.get(self, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['pk'])


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
        time = floor(len(post.text_big) * 0.075 / 60) + 1  # move to models
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
    permission_classes = (IsOwnerOrIsStaffOrReadOnly, IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.all().order_by('-pk')
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-pk')
    serializer_class = CategorySerializer
