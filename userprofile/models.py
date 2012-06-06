from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.

class SSHKey(models.Model):
    key = models.TextField()
    keyid = models.CharField(max_length=20)
    active = models.BooleanField(blank=True)
    datetime = models.DateTimeField(blank=True)
    user = models.ForeignKey(User,blank=True,null=True)
    
    def __unicode__(self):
        return "%s@%s" %(self.user.username,self.keyid)