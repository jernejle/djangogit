from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^users/register/$', 'userprofile.views.register'),
    url(r'^users/login/$', 'userprofile.views.login'),
    url(r'^users/logout/$', 'userprofile.views.logout'),
    url(r'^users/my/$', 'userprofile.views.profile'),
    url(r'^users/my/addkey/$', 'userprofile.views.addNewKey'),
    url(r'^users/my/listkeys/$', 'userprofile.views.listkeys'),
    url(r'^users/my/listkeys/activatekey/(?P<keyid>\d)/$', 'userprofile.views.activatekey'),
    url(r'^users/my/listkeys/deletekey/(?P<keyid>\d)/$', 'userprofile.views.deletekey'),
    url(r'^users/my/listkeys/deactivatekey/(?P<keyid>\d)/$', 'userprofile.views.deactivatekey'),
    url(r'^new/$', 'repocontrol.views.addnewrepo'),
    # Examples:
    # url(r'^$', 'djangogit.views.home', name='home'),
    # url(r'^djangogit/', include('djangogit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
