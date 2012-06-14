import random
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from djangogit import func
from django.template.defaultfilters import escape
from git import *

@dajaxice_register
def getobjects(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    sha = escape(sha)
    if not obj:
        return
    
    dajax = Dajax()
    trees = func.getAllObjects("tree",sha)
    blobs = func.getAllObjects("blob",sha)
    icon = "<i class='icon-folder-close'></i>"
    tablerow = ["<tr><td id='%s' class='tree'>%s %s</td><td>%s</td><td>%s</td></tr>" % (obj["sha"],icon,obj["name"], "size", "path") for obj in trees]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    icon = "<i class='icon-file'></i>"
    tablerow = ["<tr><td id='%s' class='blob'>%s %s</td><td>%s</td><td>%s</td></tr>" % (obj["sha"],icon,obj["name"], "size", "path") for obj in blobs]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    dajax.add_data("", "setEvents")
    return dajax.json()

@dajaxice_register
def getBlob(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    #obj = func.getRepoObjorNone(userid, slug)
    #if not obj:
    #    return
    
    #rep = Repo("/home/jernej/django")
    try:
        blob = func.showBlob(sha).replace("\n","<br />")
    except:
        blob = None
        
    if not blob:
        return
    
    dajax = Dajax()
    dajax.add_data(blob, "writeBlob")
    return dajax.json()