from django.conf.urls import url, include
from . import views
from .models import EngineSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.views import *
from engine.utils import reload
from django.contrib.flatpages.sitemaps import FlatPageSitemap


sitemaps = {
    "pages": EngineSitemap,
    "flatpages": FlatPageSitemap
}

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
    # url(r'^view/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.PostCreateView.as_view(), name='post_new'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.PostEditView.as_view(), name='post_edit'),
    url(r'^article/(?P<name>[-\w]+)$', views.PostDetailsView.as_view(), name='post_detail'),
    url(r'^category/(?P<category_name>[-\w]+)$', views.PostsListView.as_view(), name='get_from_category'),
    url(r'^category/(?P<category_name>[-\w]+)/(?P<pk>[0-9]+)$', views.PostsListView.as_view(), name='get_from_category_pages'),
    url(r'^search/$', views.SearchListView.as_view(), name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.SearchListView.as_view(), name='find_word_pages'),
    url(r'^user/(?P<username>[-\w]+)$', views.UserDetailsView.as_view(), name='user_profile'),
    url(r'^logs/$', views.LogsView.as_view(), name='logs_view'),
    url(r'^logs_list/$', views.LogsListView.as_view(), name='logs_list'),
    url(r'^logs/(?P<pk>[0-9]+)/$', views.LogDetailsView.as_view(), name='logs_detail'),
    url(r'^reload/$', reload, name='reload'),
    url(r'^accounts/', include(accounts_urlpatterns, namespace='accounts')),
    url(r'^comments/(?P<post_id>[\d+]*)$', views.CommentsListView.as_view(), name='comments'),
    url(r'^add_comment/(?P<post_id>[\d+]*)$', views.add_comment, name='add_comment'),
    url(r'^remove_comment/$', views.remove_comment, name='remove_comment'),
    url(r'^user_block_unblock/(?P<username>[-\w]+)$$', views.user_block_unblock, name='user_block_unblock'),
    url(r'', include('django.contrib.flatpages.urls')),
]
