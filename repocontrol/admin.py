from django.contrib import admin
from repocontrol.models import Repository

class RepositoryAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Repository, RepositoryAdmin)