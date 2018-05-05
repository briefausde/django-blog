from django.conf.urls import url, include
from . import views
from .models import EngineSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.views import *
from engine.utils import reload
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from rest_framework import routers


sitemaps = {
    "pages": EngineSitemap,
    "flatpages": FlatPageSitemap
}


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)


accounts_urlpatterns = [
    url(r'^login/$',
        LoginView.as_view(template_name="registration/_login.html"),
        name='login'),
    url(r'^logout/$',
        LogoutView.as_view(template_name="registration/_logged_out.html"),
        name='logout'),
    url(r'^password_change/$',
        PasswordChangeView.as_view(success_url=reverse_lazy('accounts:password_change_done'),
                                   template_name="registration/_password_change_form.html"),
        name='password_change'),
    url(r'^password_change/done/$',
        PasswordChangeDoneView.as_view(template_name="registration/_password_change_done.html"),
        name='password_change_done'),
    url(r'^password_reset/$',
        PasswordResetView.as_view(success_url=reverse_lazy('accounts:password_reset_done'),
                                  template_name="registration/_password_reset_form.html"),
        name='password_reset'),
    url(r'^password_reset/done/$',
        PasswordResetDoneView.as_view(template_name="registration/_password_reset_done.html"),
        name='password_reset_done'),
    url(r'^password_reset/complete/$',
        PasswordChangeDoneView.as_view(template_name="registration/_password_reset_complete.html"),
        name='password_reset_complete'),
    url(r'^password_reset/confirm/$',
        PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_complete'),
                                         template_name="registration/_password_reset_confirm.html"),
        name='password_reset_confirm'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_confirm'),
                                         template_name="registration/_password_reset_done.html"),
        name='password_reset_confirm'),
    url(r'^register/$',
        views.RegisterView.as_view(),
        name='register'),
    url(r'^register/done/$',
        TemplateView.as_view(template_name="registration/_register_done.html"),
        name='register_done'),
]


urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.PostsListView.as_view(), name='main'),
    url(r'^article/new/$', views.PostCreateView.as_view(), name='post_new'),
    url(r'^article/(?P<pk>[0-9]+)/edit/$', views.PostEditView.as_view(), name='post_edit'),
    url(r'^article/(?P<pk>[0-9]+)/delete/$', views.PostDeleteView.as_view(), name='post_delete'),
    url(r'^article/(?P<name>[-\w]+)$', views.PostDetailsView.as_view(), name='post_detail'),
    url(r'^category/(?P<category_name>[-\w]+)$', views.PostsListView.as_view(), name='get_from_category'),
    url(r'^category/(?P<category_name>[-\w]+)/(?P<pk>[0-9]+)$', views.PostsListView.as_view(),
        name='get_from_category_pages'),
    url(r'^search/$', views.SearchListView.as_view(), name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.SearchListView.as_view(), name='find_word_pages'),
    url(r'^user/(?P<username>[-\w]+)$', views.UserDetailsView.as_view(), name='user_detail'),
    url(r'^user/edit/$', views.UserEditView.as_view(), name='user_edit'),
    url(r'^user/email/edit/$', views.UserChangeEmailView.as_view(), name='user_change_email'),
    url(r'^logs/$', views.LogsView.as_view(), name='logs_view'),
    url(r'^logs/list/$', views.LogsListView.as_view(), name='logs_list'),
    url(r'^logs/(?P<pk>[0-9]+)/$', views.LogDetailsView.as_view(), name='logs_detail'),
    url(r'^feedback/$', views.FeedbackSendView.as_view(), name='feedback_send'),
    url(r'^feedback/list/$', views.FeedbackListView.as_view(), name='feedback_list'),
    url(r'^feedback/(?P<pk>[0-9]+)/$', views.FeedbackDetailsView.as_view(), name='feedback_detail'),
    url(r'^feedback/answered/$', views.FeedbackAnsweredView.as_view(), name='feedback_answered'),
    url(r'^notifications/list/$', views.NotificationsListView.as_view(), name='notifications_list'),
    url(r'^notifications/count/$', views.NotificationsCountView.as_view(), name='notifications_count'),
    url(r'^notifications/author/subscribe/$', views.SubscribeOnUserNotificationsView.as_view(),
        name='subscribe_on_author'),
    url(r'^notifications/author/unsubscribe/$', views.UnSubscribeFromUserNotificationsView.as_view(),
        name='unsubscribe_from_author'),
    url(r'^notifications/post/subscribe/$', views.SubscribeOnPostNotificationsView.as_view(),
        name='subscribe_on_post'),
    url(r'^notifications/post/unsubscribe/$', views.UnSubscribeFromPostNotificationsView.as_view(),
        name='unsubscribe_from_post'),
    url(r'^notifications/viewed/$', views.NotificationViewedView.as_view(), name='notification_viewed'),
    url(r'^notifications/delete/$', views.NotificationDeleteView.as_view(), name='notification_delete'),
    url(r'^reload/$', reload, name='reload'),
    url(r'^accounts/', include(accounts_urlpatterns, namespace='accounts')),
    url(r'^comments/(?P<post_id>[\d+]*)/$', views.CommentsListView.as_view(), name='comments'),
    url(r'^comments/(?P<post_id>[\d+]*)/add/$', views.CommentAddView.as_view(), name='add_comment'),
    url(r'^comments/remove/$', views.CommentDeleteView.as_view(), name='remove_comment'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'', include('django.contrib.flatpages.urls'))  # this include always must be in the end
]
