from django.conf.urls import patterns, url
from powermonitorweb import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^setup_household/$', views.setup_household, name='setup_household'),
                       url(r'^post_to_socialmedia/$', views.post_to_socialmedia, name='post_to_socialmedia'),
                       url(r'^manage_reports/$', views.manage_reports, name='manage_reports'),
                       url(r'^manage_alerts/$', views.manage_alerts, name='manage_alerts'),
                       url(r'^login/$', views.user_login, name='login'),
                       url(r'^logout/$', views.user_logout, name='logout'),
                       url(r'^change_password/$', views.change_password, name='change_password'),
                       url(r'^manage_users/$', views.manage_users, name='manage_users'),
                       url(r'^add_user/$', views.add_user, name='add_user'),
                       url(r'^reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           views.reset_password_confirm, name='reset_password_confirm'),
                       url(r'^reset_password/$', views.reset_password, name='reset_password'),
                       url(r'^reset_password_complete/$', views.reset_password_complete,
                           name='reset_password_complete'),
                       url(r'^profile/$', views.profile, name='profile'),
                       url(r'^graphs/$', views.graphs, name='graphs')
                       )
