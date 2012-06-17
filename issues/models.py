from django.db import models
from django.contrib.auth.models import User
from repocontrol.models import Repository

class Issue(models.Model):
    LABELS = (('1','Bug'), ('2','Enhancement'), ('3','Question'))
    title = models.CharField(max_length=30)
    content = models.TextField()
    published = models.DateTimeField(blank=True, null=True)
    open = models.BooleanField(blank=True)
    label = models.CharField(max_length=1, choices=LABELS)
    deadline = models.DateTimeField(blank=True)
    repository = models.ForeignKey(Repository, blank=True, null=True)
    author = models.ForeignKey(User, blank=True, null=True)
    
class IssueComment(models.Model):
    date = models.DateTimeField()
    comment = models.TextField()
    author = models.ForeignKey(User, blank=True, null=True)
    issue = models.ForeignKey(Issue, blank=True, null=True)