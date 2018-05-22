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


accounts_urls = [
    url(
        r'^login/$',
        LoginView.as_view(template_name="registration/_login.html"),
        name='login'
    ),
    url(
        r'^logout/$',
        LogoutView.as_view(template_name="registration/_logged_out.html"),
        name='logout'
    ),
    url(
        r'^password_change/$',
        PasswordChangeView.as_view(
            success_url=reverse_lazy('accounts:password_change_done'),
            template_name="registration/_password_change_form.html"),
        name='password_change'
    ),
    url(
        r'^password_change/done/$',
        PasswordChangeDoneView.as_view(template_name="registration/_password_change_done.html"),
        name='password_change_done'
    ),
    url(
        r'^password_reset/$',
        PasswordResetView.as_view(
            success_url=reverse_lazy('accounts:password_reset_done'),
            template_name="registration/_password_reset_form.html"),
        name='password_reset'
    ),
    url(
        r'^password_reset/done/$',
        PasswordResetDoneView.as_view(template_name="registration/_password_reset_done.html"),
        name='password_reset_done'
    ),
    url(
        r'^password_reset/complete/$',
        PasswordChangeDoneView.as_view(template_name="registration/_password_reset_complete.html"),
        name='password_reset_complete'
    ),
    url(
        r'^password_reset/confirm/$',
        PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('accounts:password_reset_complete'),
            template_name="registration/_password_reset_confirm.html"),
        name='password_reset_confirm'
    ),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('accounts:password_reset_confirm'),
            template_name="registration/_password_reset_done.html"),
        name='password_reset_confirm'
    ),
    url(
        r'^register/$',
        views.RegisterView.as_view(),
        name='register'
    ),
    url(
        r'^register/done/$',
        TemplateView.as_view(template_name="registration/_register_done.html"),
        name='register_done'
    ),
]


notifications_urls = [
    url(r'^$', views.NotificationsListView.as_view(), name='notifications_list'),
    url(r'^count/$', views.NotificationsCountView.as_view(), name='notifications_count'),
    url(
        r'^author/subscribe/$',
        views.SubscribeOnUserNotificationsView.as_view(),
        name='subscribe_on_author'
    ),
    url(
        r'^author/unsubscribe/$',
        views.UnSubscribeFromUserNotificationsView.as_view(),
        name='unsubscribe_from_author'
    ),
    url(
        r'^post/subscribe/$',
        views.SubscribeOnPostNotificationsView.as_view(),
        name='subscribe_on_post'
    ),
    url(
        r'^post/unsubscribe/$',
        views.UnSubscribeFromPostNotificationsView.as_view(),
        name='unsubscribe_from_post'
    ),
    url(r'^viewed/$', views.NotificationViewedView.as_view(), name='notification_viewed'),
    url(r'^delete/$', views.NotificationDeleteView.as_view(), name='notification_delete'),
]


article_urls = [
    url(r'^new/$', views.PostCreateView.as_view(), name='post_new'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.PostEditView.as_view(), name='post_edit'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.PostDeleteView.as_view(), name='post_delete'),
    url(r'^(?P<name>[-\w]+)$', views.PostDetailsView.as_view(), name='post_detail'),
]


profile_urls = [
    url(r'^(?P<username>[-\w]+)$', views.UserDetailsView.as_view(), name='user_detail'),
    url(r'^edit/$', views.UserEditView.as_view(), name='user_edit'),
    url(r'^email/edit/$', views.UserChangeEmailView.as_view(), name='user_change_email'),
]


logs_urls = [
    url(r'^$', views.LogsView.as_view(), name='logs_view'),
    url(r'^list/$', views.LogsListView.as_view(), name='logs_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.LogDetailsView.as_view(), name='logs_detail'),
]


feedback_urls = [
    url(r'^$', views.FeedbackSendView.as_view(), name='feedback_send'),
    url(r'^list/$', views.FeedbackListView.as_view(), name='feedback_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.FeedbackDetailsView.as_view(), name='feedback_detail'),
    url(r'^answered/$', views.FeedbackAnsweredView.as_view(), name='feedback_answered'),
]


comments_urls = [
    url(r'^(?P<post_id>[\d+]*)/$', views.CommentsListView.as_view(), name='comments'),
    url(r'^(?P<post_id>[\d+]*)/add/$', views.CommentAddView.as_view(), name='add_comment'),
    url(r'^remove/$', views.CommentDeleteView.as_view(), name='remove_comment'),
]


urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.PostsListView.as_view(), name='main'),
    url(r'^article/', include(article_urls)),
    url(r'^user/', include(profile_urls)),
    url(r'^logs/', include(logs_urls)),
    url(r'^feedback/', include(feedback_urls)),
    url(r'^comments/', include(comments_urls)),
    url(r'^notifications/', include(notifications_urls)),
    url(r'^accounts/', include(accounts_urls, namespace='accounts')),
    url(r'^category/(?P<category_name>[-\w]+)$', views.PostsListView.as_view(), name='get_from_category'),
    url(
        r'^category/(?P<category_name>[-\w]+)/(?P<pk>[0-9]+)$',
        views.PostsListView.as_view(),
        name='get_from_category_pages'
    ),
    url(r'^search/$', views.SearchListView.as_view(), name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.SearchListView.as_view(), name='find_word_pages'),
    url(r'^reload/$', reload, name='reload'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'', include('django.contrib.flatpages.urls'))  # this include always must be in the end
]
