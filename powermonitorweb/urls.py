from django.conf.urls import patterns, url
from powermonitorweb import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^add_user/$', views.add_user, name='add_user'),
                       url(r'^setup_household/$', views.setup_household, name='setup_household'),
                       url(r'^post_to_socialmedia/$', views.post_to_socialmedia, name='post_to_socialmedia'),
                       url(r'^manage_reports/$', views.manage_reports, name='manage_reports'),
                       url(r'^manage_accounts/$', views.manage_accounts, name='manage_accounts'),
                       url(r'login/$', views.user_login, name='login'),
                       url(r'logout/$', views.user_logout, name='logout'),
                       url(r'change_password/$', views.change_password, name='change_password'),
                       )
