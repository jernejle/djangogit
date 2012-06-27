import random
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from djangogit import func
from django.template.defaultfilters import escape
from git import *
import pdb

@dajaxice_register
def getobjects(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    sha = escape(sha)
    if not obj:
        return
    
    dajax = Dajax()
    trees = func.getAllObjects(obj.get('repoObj'),"tree",sha)
    blobs = func.getAllObjects(obj.get('repoObj'),"blob",sha)
    icon = "<i class='icon-folder-close'></i>"
    tablerow = ["<tr><td id='%s' class='tree'>%s %s</td></tr>" % (obj["sha"],icon,obj["name"]) for obj in trees]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    icon = "<i class='icon-file'></i>"
    tablerow = ["<tr><td id='%s' class='blob'>%s %s</td></tr>" % (obj["sha"],icon,obj["name"]) for obj in blobs]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    dajax.add_data("", "setEvents")
    return dajax.json()

@dajaxice_register
def getBlob(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    try:
        blob = func.showBlob(obj.get('repoObj'),sha).replace("\n","<br />")
    except:
        blob = None
        
    if not blob:
        return
    
    dajax = Dajax()
    dajax.add_data(blob, "writeBlob")
    return dajax.json()

@dajaxice_register
def getCommitDiff(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    try:
        commit = obj.get('repoObj').commit(sha)
        difflist = obj.get('repoObj').git.execute(["git","diff-tree","-p",sha])
    except:
        commit = None
    
    if not commit or not difflist:
        return
    
    dajax = Dajax()
    dajax.add_data(''.join(difflist), "writeDiff")
    return dajax.json()

@dajaxice_register
def addtodifflist(request,userid,slug,sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    #sha exists ?
    reponame = "%s%s" %(userid,slug)
    reposession = request.session.get(reponame, None)
    shalist = []
    
    if not reposession:
        shalist.append(sha)
        request.session[reponame] = shalist
    else:
        shalist = reposession
        if sha not in shalist:
            shalist.append(sha)
        request.session[reponame] = shalist
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def clearlist(request,userid,slug):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    reponame = "%s%s" %(userid,slug)
    if request.session.get(reponame,None):
        request.session[reponame] = None
        
    dajax = Dajax()
    return dajax.json()