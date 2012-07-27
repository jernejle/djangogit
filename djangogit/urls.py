from django.conf.urls import patterns, include, url
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover
from django.conf import settings
dajaxice_autodiscover()
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    url(r'^users/register/$', 'userprofile.views.register'),
    url(r'^users/login/$', 'userprofile.views.login'),
    url(r'^users/logout/$', 'userprofile.views.logout'),
    url(r'^users/my/$', 'userprofile.views.profile'),
    url(r'^users/viewprofile/(?P<keyid>\d+)/$', 'userprofile.views.viewprofile'),
    url(r'^users/my/addkey/$', 'userprofile.views.addNewKey'),
    url(r'^users/my/listkeys/$', 'userprofile.views.listkeys'),
    url(r'^users/my/listkeys/activatekey/(?P<keyid>\d+)/$', 'userprofile.views.activatekey'),
    url(r'^users/my/listkeys/deletekey/(?P<keyid>\d+)/$', 'userprofile.views.deletekey'),
    url(r'^users/my/listkeys/deactivatekey/(?P<keyid>\d+)/$', 'userprofile.views.deactivatekey'),
    url(r'^users/my/messages/$', 'userprofile.views.messages'),
    url(r'^users/viewprofile/(?P<username>\w+)/$', 'userprofile.views.redirect_to_profile'),
    url(r'^new/$', 'repocontrol.views.addnewrepo'),
    url(r'^search/$', 'repocontrol.views.searchrepos'),
    url(r'^search/redirect/$', 'repocontrol.views.redirectTo'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/$', 'repocontrol.views.viewrepo'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/files/(?P<branch>[a-zA-Z0-9\/\.\,_-]+)/$', 'repocontrol.views.viewfiles'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/files/$', 'repocontrol.views.viewfiles'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/commits/(?P<branch>[a-zA-Z0-9\/\.\,_-]+)/$', 'repocontrol.views.showcommits'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/commits/$', 'repocontrol.views.showcommits'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/commit/(?P<sha>[0-9a-f]{5,40})/$', 'repocontrol.views.commit'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/commit/(?P<sha>[0-9a-f]{5,40})/post/$', 'repocontrol.views.postcomment'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/difflist/$', 'repocontrol.views.difflist'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/diff/(?P<sha1>[0-9a-f]{5,40})/(?P<sha2>[0-9a-f]{5,40})/$', 'repocontrol.views.diff'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/team/$', 'repocontrol.views.team'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/delperm/$', 'repocontrol.views.deletepermission'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/getmembers/$', 'repocontrol.views.getmembers'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/add/$', 'issues.views.add'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/$', 'issues.views.all'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/(?P<keyid>\d+)/$', 'issues.views.details'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/(?P<keyid>\d+)/post/$', 'issues.views.postcomment'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/(?P<keyid>\d+)/status/$', 'issues.views.changestatus'),
    url(r'^(?P<userid>\d+)/(?P<slug>[a-zA-Z0-9_-]+)/issues/my/$', 'issues.views.myissues'),
    url(r'^(?P<username>\w+)/(?P<slug>[a-zA-Z0-9_-]+)/$', 'repocontrol.views.redirect_to_repo'),
    url(r'^$', 'repocontrol.views.index'),
    # Examples:
    # url(r'^$', 'djangogit.views.home', name='home'),
    # url(r'^djangogit/', include('djangogit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
