from django.conf.urls.defaults import *

urlpatterns = patterns('tech.views',
    url(r'^$', 'index'),
    url(r'^posts.json$','posts'),
    url(r'^(?P<pk>\d+)/like$','like'),
    url(r'^(?P<pk>\d+)/dislike$','dislike'),
)
