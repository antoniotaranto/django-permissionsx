from django.conf.urls import patterns, include, url

from example.demo.views import (
    home_view,
    profile_view,
    access_denied_view,
    log_in_view,
    log_out_view,
)


urlpatterns = patterns('',
    url(r'^$', home_view, name='home'),
    url(r'^profile/$', profile_view, name='profile'),
    url(r'^denied/$', access_denied_view, name='access_denied'),
    url(r'^log-in/$', log_in_view, name='log_in'),
    url(r'^log-out/$', log_out_view, name='log_out'),
)
