from django.contrib import admin
from repocontrol.models import Repository,CommitComment
class RepositoryAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(CommitComment)