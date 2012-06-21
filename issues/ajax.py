from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from djangogit import func
from django.template.defaultfilters import escape
from git import *
from issues.models import Issue
import datetime
import pdb

@dajaxice_register
def getObjectsByTag(request, userid, slug, tag):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return ""
    
    dajax = Dajax()
    issues = None
    try:
        if tag == "0":
            issues = Issue.objects.filter(repository=obj.get('repo'))
        elif tag == "closed":
            issues = Issue.objects.filter(repository=obj.get('repo'), open=False)
        elif tag == "open":
            issues = Issue.objects.filter(repository=obj.get('repo'), open=True)
        else:
            issues = Issue.objects.filter(repository=obj.get('repo'), label=int(tag))
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