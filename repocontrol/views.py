from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from repocontrol.forms import NewRepo
from djangogit.settings import TEMP_REPODIR, GITOLITE_CONF
from repocontrol.models import Repository
from django.contrib.auth.models import User
from djangogit import func
from git import *
from django.core.context_processors import csrf
from dajax.core.Dajax import Dajax
from dajaxice.decorators import dajaxice_register
from django.http import Http404
from django.utils.encoding import smart_str, smart_unicode
import datetime

@login_required
def addnewrepo(request):
    template = "repocontrol/addnew.html"
    if request.method == "GET":
        form = NewRepo()
        return render_to_response(template, {'form':form}, context_instance=RequestContext(request))
    elif request.method == "POST":
        form = NewRepo(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.user = request.user
            object.created = datetime.datetime.now()
            object.save()
            func.addRepo(request.user, object.slug, "RW+")
            message = "Repo %s/%s added" % (request.user, object.slug)
            file = "%s/conf/%s/%s.conf" % (TEMP_REPODIR, request.user, object.slug)
            includeline = "\ninclude \"%s/%s.conf\"" % (request.user, object.slug)
            func.appendToGitoliteConf(GITOLITE_CONF, includeline)
            func.gitAdd(file)
            func.gitAdd(GITOLITE_CONF)
            func.commitChange(message)
            func.pushUpstream()
            return HttpResponse("added")
        else:
            return render_to_response(template, {'form':form}, context_instance=RequestContext(request))
        
def viewrepo(request, userid, slug):
    template = "repocontrol/viewrepo.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    if obj.get('repoObj'):
        comm_date = datetime.datetime.fromtimestamp(obj.get('repoObj').head.commit.committed_date)
        latest_commit = obj.get('repoObj').head.commit
        return render_to_response(template, {'reponame':obj.get('reponame'), 'repodb':obj.get('repo'), 'latest_commit':latest_commit, 'date':comm_date, 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':''}, context_instance=RequestContext(request))
    # else statement
    
def viewfiles(request, userid, slug):
    template = "repocontrol/viewfiles.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    branches = func.getBranches("")
    branches.pop(0)
    return render_to_response(template, {'reponame':obj.get('reponame'), 'branches':branches, 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'files'}, context_instance=RequestContext(request))

def showcommits(request,userid,slug,branch="origin/master"):
    template = "repocontrol/viewcommits.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    if obj.get('repoObj'):
        branches = func.getBranches("repo")
        branches.pop(0)
        
        if not branch in branches:
            raise Http404
        
        commits = func.getCommits("", branch)
        comlist = []
        if commits:
            for commit in commits:
                newcom = {'author':smart_str(commit.author),'message':smart_str(commit.message),'date':datetime.datetime.fromtimestamp(commit.committed_date), 'sha':commit.hexsha}
                comlist.append(newcom)

        return render_to_response(template, {'reponame':obj.get('reponame'), 'commits':comlist, 'branches':branches, 'repodb':obj.get('repo'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'viewcommits'}, context_instance=RequestContext(request))
    return HttpResponse(branch)