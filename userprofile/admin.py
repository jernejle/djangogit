from django.contrib import admin
from userprofile.models import SSHKey

class SSHUser(admin.ModelAdmin):
    search_fields = ('keyid',)

admin.site.register(SSHKey, SSHUser)