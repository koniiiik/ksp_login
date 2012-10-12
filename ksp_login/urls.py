from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ksp_login.views',
    url(r'^login/$', 'login', name='account_login'),
    url(r'^$', 'info', name='account_info'),
    url(r'^logout/$', 'logout', name='account_logout'),
    url(r'^register/$', 'register', name='account_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        'disconnect', name='account_disconnect'),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)
