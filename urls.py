from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^tech/', include('tech.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
