from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from djangogit import func
from django.template.defaultfilters import escape
from git import *
from issues.models import Issue
from django.db.models import Q
import datetime
import pdb

@dajaxice_register
def getObjectsByTag(request,userid,slug,tag):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return ""
    
    dajax = Dajax()
    issues = None
    try:
        if tag == "0":
            issues = Issue.objects.filter(repository=obj.get('repo')).order_by('-published')
        elif tag == "closed":
            issues = Issue.objects.filter(repository=obj.get('repo'), open=False).order_by('-published')
        elif tag == "open":
            issues = Issue.objects.filter(repository=obj.get('repo'), open=True).order_by('-published')
        elif tag == "active":
            now = datetime.datetime.now()
            yest = datetime.datetime.now() - datetime.timedelta(days=1)
            issues = Issue.objects.filter(Q(published__year=now.year,published__month=now.month,published__day=now.day, repository=obj.get('repo')) | Q(published__year=yest.year,published__month=yest.month,published__day=yest.day, repository=obj.get('repo'))).order_by('-published')
        else:
            issues = Issue.objects.filter(repository=obj.get('repo'), label=int(tag)).order_by('-published')
    except:
        return ""
        
    if not issues:
        return ""
    
    list = []
    if issues:
        for issue in issues:
            href = "%d/%s/issues/%s" % (obj.get('user_obj').id, slug, str(issue.id))
            list.append({'title':issue.title, 'author':issue.author.username, 'date':str(issue.published), 'href':href, 'open':issue.open, 'label':issue.get_label_display()})
    else:
        list = ""
        
    dajax.add_data(list, "postIssue")
    return dajax.json()
    