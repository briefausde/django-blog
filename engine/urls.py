from django.conf.urls import url, include
from . import views
from .models import EngineSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.contrib.auth.views import *


categories_list = views.category_list
static_pages_list = views.static_pages_list


sitemaps = {
    "blog": EngineSitemap
}

# accounts_urlpatterns = [
#     url(r'^login/$', views.login, name='login'),
    # url(r'^login/$', (CreateView.as_view(model=User, get_success_url=views.login, form_class=AuthenticationForm,
    #                                      template_name="engine/auth/_login.html")), name='login'),
    # url(r'^register/$', (CreateView.as_view(model=User, get_success_url=views.register, form_class=UserCreationForm,
    #                                         template_name="engine/auth/register.html")), name='register'),
    # url(r'^logout/$', views.logout, name='logout'),
    # url(r'^change_password/$', views.change_password, name='change_password'),
# ]

accounts_urlpatterns = [
    # url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),
    url(r'^login/$', LoginView.as_view(template_name="registration/_login.html"), name='login'),
    url(r'^logout/$', LogoutView.as_view(template_name="registration/_logged_out.html"), name='logout'),
    url(r'^password_change/$', PasswordChangeView.as_view(template_name="registration/_password_change_form.html"), name='password_change'),
    url(r'^password_change/done/$', PasswordChangeDoneView.as_view(template_name="registration/_password_change_done.html"), name='password_change_done'),
    url(r'^password_reset/$', PasswordResetView.as_view(template_name="registration/_password_reset_form.html"), name='password_reset'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(template_name="registration/_password_reset_done.html"), name='password_reset_confirm'),
    url(r'^register/$', (CreateView.as_view(model=User, get_success_url=views.register, form_class=UserCreationForm,
                                                     template_name="engine/auth/register.html")), name='register'),
]

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.PostsListView.as_view(), name='main'),
    # url(r'^view/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.PostCreateView.as_view(), name='post_new'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.PostEditView.as_view(), name='post_edit'),
    url(r'^article/(?P<name>[-\w]+)$', views.PostDetailsView.as_view(), name='post_detail'),
    url(r'^(?P<category_name>%s)/$' % categories_list,
        views.PostsListView.as_view(),
        name='get_from_category'),
    url(r'^(?P<category_name>%s)/(?P<pk>[0-9]+)$' % categories_list,
        views.PostsListView.as_view(),
        name='get_from_category_pages'),
    url(r'^(?P<page_name>%s)$' % static_pages_list, views.StaticPageView.as_view(), name='load_static_page'),
    url(r'^search/$', views.find_word, name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.find_word, name='find_word_pages'),
    url(r'^user/(?P<username>[-\w]+)$', views.UserDetailsView.as_view(), name='user_profile'),
    url(r'^logs/$', views.LogsView.as_view(), name='logs_view'),
    url(r'^logs_list/$', views.LogsListView.as_view(), name='logs_list'),
    url(r'^logs/(?P<pk>[0-9]+)/$', views.LogDetailsView.as_view(), name='logs_detail'),
    url(r'^reload/$', views.reload, name='reload'),
    url(r'^accounts/', include(accounts_urlpatterns, namespace='accounts')),
    url(r'^accounts/password_reset/done/$', PasswordResetDoneView.as_view(template_name="registration/_password_reset_done.html"), name='password_reset_done'),
    url(r'^comments/(?P<post_id>[\d+]*)$', views.CommentsListView.as_view(), name='comments'),
    url(r'^add_comment/(?P<post_id>[\d+]*)$', views.add_comment, name='add_comment'),
    url(r'^remove_comment/$', views.remove_comment, name='remove_comment'),
]
