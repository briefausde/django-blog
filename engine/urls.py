<<<<<<< HEAD
from django.conf.urls import url, include
from . import views
from .classes import auth, posts
from .models import EngineSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView


categories_list = views.category_list
static_pages_list = views.static_pages_list


sitemaps = {
    "blog": EngineSitemap
}

auth_urlpatterns = [
    url(r'^login/$', auth.login, name='login'),
    url(r'^register/$', (CreateView.as_view(model=User, get_success_url=auth.register, form_class=UserCreationForm,
                                            template_name="engine/auth/register.html")), name='register'),
    url(r'^logout/$', auth.logout, name='logout'),
    url(r'^change_password/$', auth.change_password, name='change_password'),
    # from django.contrib.auth import views as auth_views
    # url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='engine/auth/login.html')),
]

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.main, name='main'),
    # url(r'^view/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', posts.new, name='post_new'),
    url(r'^edit/(?P<pk>[0-9]+)/$', posts.edit, name='post_edit'),
    url(r'^article/(?P<name>[-\w]+)$', posts.detail, name='post_detail'),
    url(r'^(?P<category_name>%s)/$' % categories_list,
        views.category_page,
        name='get_from_category'),
    url(r'^(?P<category_name>%s)/(?P<pk>[0-9]+)$' % categories_list,
        views.category_page,
        name='get_from_category_pages'),
    url(r'^(?P<page_name>%s)$' % static_pages_list, views.load_static_page, name='load_static_page'),
    url(r'^search/$', views.find_word, name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.find_word, name='find_word_pages'),
    url(r'^user/(?P<username>[-\w]+)$', views.user_profile, name='user_profile'),
    url(r'^user/(?P<username>[-\w]+)/(?P<pk>[0-9]+)$', views.user_profile, name='user_profile_pages'),
    url(r'^logs/$', views.get_logs, name='get_logs'),
    url(r'^reload/$', views.reload, name='reload'),
    url(r'^auth/', include(auth_urlpatterns, namespace='auth')),
    url(r'^comments/(?P<post_id>[\d+]*)$', views.get_comments, name='get_comments'),
    url(r'^add_comment/(?P<post_id>[\d+]*)$', views.add_comment, name='add_comment'),
    url(r'^remove_comment/$', views.remove_comment, name='remove_comment'),
]
=======
from django.conf.urls import url, include
from . import views
from .classes import auth, posts
from .models import EngineSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView


categories_list = views.category_list
static_pages_list = views.static_pages_list


sitemaps = {
    "blog": EngineSitemap
}

auth_urlpatterns = [
    url(r'^login/$', auth.login, name='login'),
    url(r'^register/$', (CreateView.as_view(model=User, get_success_url=auth.register, form_class=UserCreationForm,
                                            template_name="engine/auth/register.html")), name='register'),
    url(r'^logout/$', auth.logout, name='logout'),
    url(r'^change_password/$', auth.change_password, name='change_password'),
    # from django.contrib.auth import views as auth_views
    # url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='engine/auth/login.html')),
]

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.main, name='main'),
    # url(r'^view/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', posts.new, name='post_new'),
    url(r'^edit/(?P<pk>[0-9]+)/$', posts.edit, name='post_edit'),
    url(r'^article/(?P<name>[-\w]+)$', posts.detail, name='post_detail'),
    url(r'^(?P<category_name>%s)/$' % categories_list,
        views.category_page,
        name='get_from_category'),
    url(r'^(?P<category_name>%s)/(?P<pk>[0-9]+)$' % categories_list,
        views.category_page,
        name='get_from_category_pages'),
    url(r'^(?P<page_name>%s)$' % static_pages_list, views.load_static_page, name='load_static_page'),
    url(r'^search/$', views.find_word, name='find_word'),
    url(r'^search/(?P<pk>[0-9]+)/$', views.find_word, name='find_word_pages'),
    url(r'^user/(?P<username>[-\w]+)$', views.user_profile, name='user_profile'),
    url(r'^user/(?P<username>[-\w]+)/(?P<pk>[0-9]+)$', views.user_profile, name='user_profile_pages'),
    url(r'^logs/$', views.get_logs, name='get_logs'),
    url(r'^reload/$', views.reload, name='reload'),
    url(r'^auth/', include(auth_urlpatterns, namespace='auth')),
    url(r'^comments/(?P<post_id>[\d+]*)$', views.get_comments, name='get_comments'),
    url(r'^add_comment/(?P<post_id>[\d+]*)$', views.add_comment, name='add_comment'),
    url(r'^remove_comment/$', views.remove_comment, name='remove_comment'),
]
>>>>>>> 64d5b50a23ee4bd33e7ebc3854e494618345a6e9
