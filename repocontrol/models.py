from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime

class Repository(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=False, blank=True)
    description = models.TextField()
    private = models.BooleanField(blank=True)
    created = models.DateTimeField(blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    team = models.ManyToManyField(User, related_name="repository_collabolators", blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.slug)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
    
        super(Repository, self).save(*args, **kwargs)
        
class CommitComment(models.Model):
    comment = models.TextField()
    date = models.DateTimeField(blank=True, null=True)
    sha = models.TextField(blank=True, null=True)
    repository = models.ForeignKey(Repository, blank=True, null=True)
    author = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return str(self.date)
