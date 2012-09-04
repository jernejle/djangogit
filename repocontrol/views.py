from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from repocontrol.forms import NewRepo, NewComment, EditComment, FileForm
from djangogit.settings import TEMP_REPODIR, GITOLITE_CONF, TEMP_CLONE_DIR, UPLOAD_DIR
from repocontrol.models import Repository, CommitComment
from django.contrib.auth.models import User
from djangogit import func
from git import *
from django.core.context_processors import csrf
from dajax.core.Dajax import Dajax
from dajaxice.decorators import dajaxice_register
from django.http import Http404
from django.utils.encoding import smart_str, smart_unicode
from issues.models import Issue, IssueComment
from userprofile.models import Message
from django.core.servers.basehttp import FileWrapper
import datetime
import re
import pdb
import json
import os
import shutil

@login_required
def addnewrepo(request):
    template = "repocontrol/addnew.html"
    message = None
    if request.method == "GET":
        form = NewRepo()
        return render_to_response(template, {'activelink':'addnew', 'form':form}, context_instance=RequestContext(request))
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
            message = "Your repository was successfully created"
        return render_to_response(template, {'message':message, 'activelink':'addnew', 'form':form}, context_instance=RequestContext(request))
        
def viewrepo(request, userid, slug):
    template = "repocontrol/viewrepo.html"
    obj = func.getRepoObjorNone(userid, slug)
    userobj = User.objects.get(pk=userid)
    
    empty = False
    try:    
        repo = Repository.objects.get(user=userobj, slug=slug)
    except:
        repo = None
    
    comm_date = None
    latest_commit = None
    latest_commit_ref = None
    
    branches = func.getBranches(obj.get('repoObj'))
    if not branches:
        empty = True
    
    if not repo:
        raise Http404
    elif repo and obj:  
        try:
            comm_date = datetime.datetime.fromtimestamp(obj.get('repoObj').commit().committed_date)
            latest_commit = obj.get('repoObj').commit()
            latest_commit_ref = str(obj.get('repoObj').head.ref)
        except:
            pass
    else:
        empty = True
        
    if empty:
        return render_to_response(template, {'slug':slug, 'userobj':userobj.username, 'empty':True}, context_instance=RequestContext(request))
    
    latest_issues = Issue.objects.filter(repository=obj.get('repo')).order_by('-published')[:5]
    issues_latest_comments = Issue.objects.filter(repository=obj.get('repo'), last_action__isnull=False).order_by('-last_action')[:3]
    comments = []
    
    if issues_latest_comments:
        for li in issues_latest_comments:
            com = li.issuecomment_set.all().order_by('-date')[:2]
            comments.append(com)

    return render_to_response(template, {'latest_commit_ref':latest_commit_ref, 'issues_latest_comments':comments, 'latest_issues':latest_issues, 'reponame':obj.get('reponame'), 'repodb':obj.get('repo'), 'latest_commit':latest_commit, 'date':comm_date, 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':''}, context_instance=RequestContext(request))
    
def viewfiles(request, userid, slug, branch="master"):
    template = "repocontrol/viewfiles.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    branches = func.getBranches(obj.get('repoObj'))
    if branches and branch == "master":
        branch = branches[0] #teeeeest
    #if branches:
    #    branch = branches[0]
    
    if not branch in branches:
        raise Http404
    return render_to_response(template, {'chosenbranch':branch, 'reponame':obj.get('reponame'), 'branches':branches, 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'files'}, context_instance=RequestContext(request))

def showcommits(request, userid, slug, branch="master"):
    template = "repocontrol/viewcommits.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    branches = func.getBranches(obj.get('repoObj'))

    if branches and branch == "master":
        branch = branches[0] #teeeeest

    if not branch in branches:
        raise Http404
    
    page = request.GET.get("page", 1)
    
    try:
        page = int(page)
    except:
        page = 1
        
    show_per_page = 8 

    
    commits = list(func.getCommits(obj.get('repoObj'), branch, show_per_page, (page * show_per_page) - show_per_page))
    nextlist = list(func.getCommits(obj.get('repoObj'), branch, show_per_page, (page * show_per_page)))
    haspreviouslist = list(func.getCommits(obj.get('repoObj'), branch, show_per_page, (page * show_per_page) - 2 * show_per_page))
    
    hasnext = True
    hasprevious = True
    
    if len(nextlist) == 0:
        hasnext = False
    
    if page == 1 or len(haspreviouslist) == 0:
        hasprevious = False
    
    comlist = []
    if commits:
        for commit in commits:
            newcom = {'author':smart_str(commit.author), 'message':smart_str(commit.message), 'date':datetime.datetime.fromtimestamp(commit.committed_date), 'sha':commit.hexsha}
            comlist.append(newcom)

    return render_to_response(template, {'previouspage':page - 1, 'nextpage':page + 1, 'hasprevious':hasprevious, 'hasnext':hasnext, 'page':page, 'reponame':obj.get('reponame'), 'requestedbranch': branch, 'commits':comlist, 'branches':branches, 'repodb':obj.get('repo'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'viewcommits'}, context_instance=RequestContext(request))

def commit(request, userid, slug, sha):
    template = "repocontrol/viewcommit.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    form = NewComment()
    try:
        commit = obj.get('repoObj').commit(sha)
        difflist = obj.get('repoObj').git.execute(["git", "diff-tree", "-p", sha]).splitlines()
    except:
        commit = None
    
    if not commit:
        raise Http404
    
    try:
        comments = CommitComment.objects.filter(repository=obj.get('repo'), sha=sha)
    except:
        comments = None       
    
    difffiles = []
    seperate = []
    if difflist:
        del difflist[0]
        for line in difflist:
            if re.search("diff --git a/.* b/.*$", line):
                linespl = line.split(" ")
                line = linespl[2][2:]
                if seperate:
                    difffiles.append(seperate)
                seperate = []
            seperate.append(line + "\n")
            if line == difflist[-1]:
                difffiles.append(seperate)
    
    team = obj.get('repo').team.all()
    commitobj = {'author':smart_str(commit.author), 'date':datetime.datetime.fromtimestamp(commit.committed_date), 'message': smart_str(commit.message), 'tree':commit.tree, 'parents':commit.parents, 'sha':commit.hexsha}
    return render_to_response(template, {'team':team, 'form':form, 'comments':comments, 'diff':difffiles, 'commit':commitobj, 'reponame':obj.get('reponame'), 'activelink':'viewcommits', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))

def team(request, userid, slug):
    template = "repocontrol/team.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    team = func.getTeam(obj.get('user_obj').username, slug)
    repo = obj.get('repo')
    
    if request.method == "POST":
        if request.user != obj.get('repo').user:
            return HttpResponse("Only the owner can change user permissions")
        
        requser = request.POST.get('username', '')
        reqperm = request.POST.get('perm', '')
        permlist = {'r':'R', 'rw':'RW', 'rw+':'RW+'}
        perm = permlist.get(reqperm, '')
        
        if requser != "@all":
            newuser = get_object_or_404(User, username=requser)
        else:
            newuser = "@all"
        
        if perm and newuser:
            for u in team:
                if newuser != "@all" and newuser == u.get('user'):
                    return redirect("/%s/%s/team/" % (userid, slug))
                elif newuser == "@all" and newuser == u.get('user'):
                    return redirect("/%s/%s/team/" % (userid, slug))
            
            if newuser != "@all":
                repo.team.add(newuser)
                repo.save
                mess = "User user#%s added you as a team member in repo#%s You can now %s" % (request.user, obj.get('reponame'), func.getPermissions(perm))
                title = "Permission changes in %s" % (obj.get('reponame'))
                now = datetime.datetime.now()
                Message.objects.create(title=title, content=mess, datetime=now, user=newuser, read=False)
                func.addTeamMember(obj.get('reponame'), newuser.username, perm)
                file = "%s/conf/%s.conf" % (TEMP_REPODIR, obj.get('reponame'))
                func.gitAdd(file)
                func.commitChange("Added %s permission for user %s in %s" % (perm, newuser.username, obj.get('reponame')))
                func.pushUpstream()
            else:
                func.addTeamMember(obj.get('reponame'), "@all", perm)
                file = "%s/conf/%s.conf" % (TEMP_REPODIR, obj.get('reponame'))
                func.gitAdd(file)
                func.commitChange("Added %s permission for user %s in %s" % (perm, newuser, obj.get('reponame')))
                func.pushUpstream()
            
        return redirect("/%s/%s/team/" % (userid, slug))
        
    elif request.method == "GET":
        return render_to_response(template, {'owner':obj.get('repo').user, 'team':team, 'reponame':obj.get('reponame'), 'activelink':'team', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))
    
def getmembers(request, userid, slug):
    if request.is_ajax():
        obj = func.getRepoObjorNone(userid, slug)
        if not obj:
            return
        q = request.GET.get('term', '')
        users = User.objects.filter(username__icontains=q)
        results = []
        for user in users:
            user_json = {}
            user_json['id'] = user.id
            user_json['label'] = user.username
            user_json['value'] = user.username
            results.append(user_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def deletepermission(request, userid, slug):
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    
    if request.user != obj.get('repo').user:
        return HttpResponse("Only the owner can delete user permissions")
    
    requser = request.GET.get('user', '')
    if requser == "@all":
        a = func.delTeamMember(obj.get('reponame'), "@all")
        if a:
            func.gitAdd("%s/conf/%s.conf" % (TEMP_REPODIR, obj.get('reponame')))
            func.commitChange("Deleted permissions in %s for user %s" % (obj.get('reponame'), "@all"))
            func.pushUpstream()
        return redirect("/%s/%s/team/" % (userid, slug))
    
    user_obj = User.objects.get(username=requser)
    if not requser or not user_obj:
        return redirect("/%s/%s/team/" % (userid, slug))
    
    if user_obj.username == obj.get('repo').user.username:
        return HttpResponse("Can't delete owner!")
    
    a = func.delTeamMember(obj.get('reponame'), user_obj.username)
    if a:
        repo = obj.get('repo')
        repo.team.remove(user_obj)
        mess = "User user#%s deleted you as a team member in repo#%s" % (request.user, obj.get('reponame'))
        title = "Permission changes in %s" % (obj.get('reponame'))
        now = datetime.datetime.now()
        Message.objects.create(title=title, content=mess, datetime=now, user=user_obj, read=False)
        func.gitAdd("%s/conf/%s.conf" % (TEMP_REPODIR, obj.get('reponame')))
        func.commitChange("Deleted permissions in %s for user %s" % (obj.get('reponame'), user_obj.username))
        func.pushUpstream()
    return redirect("/%s/%s/team/" % (userid, slug))
    
@login_required
def postcomment(request, userid, slug, sha):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        form = NewComment(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.author = request.user
            object.date = datetime.datetime.now()
            object.sha = sha
            object.repository = obj.get('repo')
            object.save()
        return redirect("/%s/%s/commit/%s" % (userid, slug, sha))

def difflist(request, userid, slug):
    template = "repocontrol/difflist.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    sessname = "%s%s" % (userid, slug)
    reposess = request.session.get(sessname, None)

    commitobjects = []
    if reposess:
        for sha in reposess:
            try:
                commit = obj.get('repoObj').commit(sha)
                commitobj = {'author':smart_str(commit.author), 'date':datetime.datetime.fromtimestamp(commit.committed_date), 'message': smart_str(commit.message), 'tree':commit.tree, 'parents':commit.parents, 'sha':commit.hexsha}
            except:
                commitobj = None
            if commitobj:
                commitobjects.append(commitobj)
    
    return render_to_response(template, {'commits':commitobjects, 'reponame':obj.get('reponame'), 'activelink':'difflist', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))

def diff(request, userid, slug, sha1, sha2):
    template = "repocontrol/diff.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    
    try:
        commit1 = obj.get('repoObj').commit(sha1)
        commit2 = obj.get('repoObj').commit(sha2)
    except:
        commit1 = None
        commit2 = None
        
    if not commit1 or not commit2:
        return redirect("/%s/%s" % (userid, slug))
    
    try:
        diff = obj.get('repoObj').git.execute(["git", "diff", sha1, sha2]).splitlines()
    except:
        diff = None
    
    if not diff:
        return redirect("/%s/%s" % (userid, slug))
    
    difffiles = []
    seperate = []
    if diff:
        for line in diff:
            if re.search("diff --git a/.* b/.*$", line):
                linespl = line.split(" ")
                line = linespl[2][2:]
                if seperate:
                    difffiles.append(seperate)
                seperate = []
            seperate.append(line + "\n")
            if line == diff[-1]:
                difffiles.append(seperate)
    
    return render_to_response(template, {'diff':difffiles, 'sha1':sha1, 'sha2':sha2, 'activelink':'difflist', 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))
    
def index(request):
    template = "repocontrol/index.html"
    
    myrepos_new = None
    teamrepos = None
    
    if request.user.is_authenticated():
        myrepos_new = Repository.objects.filter(user=request.user).order_by('-created')
        teamrepos = User.objects.get(username=request.user).repository_collabolators.order_by('-created')
        
    return render_to_response(template, {'teamrepos':teamrepos, 'myrepos_new':myrepos_new}, context_instance=RequestContext(request))

def searchrepos(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        repos = Repository.objects.filter(name__icontains=q, private=False)
        results = []
        for repo in repos:
            repo_json = {}
            repo_json['id'] = repo.id
            repo_json['label'] = "%s/%s" % (repo.user.username, repo.slug)
            repo_json['value'] = "%s/%s" % (repo.user.username, repo.slug)
            results.append(repo_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def redirectTo(request):
    if request.method == "POST":
        q = request.POST.get('searchquery', None)
        if not q:
            raise Http404
        
        qsplit = q.split('/')
        repo = get_object_or_404(Repository, slug=qsplit[1], user__username=qsplit[0], private=False)
        
        return redirect("/%s/%s/" % (repo.user.id, repo.slug))
    else:
        raise Http404

def redirect_to_repo(request, username, slug):
    user = get_object_or_404(User, username=username)
    repo = get_object_or_404(Repository, user__id=user.id, slug=slug)
    return redirect("/%d/%s" % (user.id, repo.slug))

def editcomment(request, userid, slug, sha, commentid):
    template = "repocontrol/editcomment.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    comment = get_object_or_404(CommitComment, pk=commentid)
    
    team = obj.get('repo').team.all()
    if not comment.repository.user == request.user and not request.user in team and not comment.author == request.user:
        return redirect("/")
    
    if request.method == "GET":
        form = EditComment({'comment':comment.comment})
        return render_to_response(template, {'form':form, 'comment':comment, 'reponame':obj.get('reponame'), 'activelink':'viewcommits', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))
    elif request.method == "POST":
        new_comm = request.POST.get('comment', '')
        if new_comm:
            comment.comment = new_comm
            comment.save()
        return redirect("/%s/%s/commit/%s/" % (userid, slug, comment.sha))

def deletecomment(request, userid, slug, sha, commentid):
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    comment = get_object_or_404(CommitComment, pk=commentid)
    
    team = obj.get('repo').team.all()
    if not comment.repository.user == request.user and not request.user in team and not comment.author == request.user:
        return redirect("/")
    
    comment.delete()
    return redirect("/%s/%s/commit/%s/" % (userid, slug, comment.sha))

def graphs(request, userid, slug):
    template = "repocontrol/graphs.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
        
    return render_to_response(template, {'reponame':obj.get('reponame') , 'activelink':'graphs', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))

def commits_history(request, userid, slug):
    template = "repocontrol/graphs_commit_history.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    branches = func.getBranches(obj.get('repoObj'))
        
    return render_to_response(template, {'branches':branches,'reponame':obj.get('reponame') , 'activelink':'graphs', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))

def committers_history(request, userid, slug):
    template = "repocontrol/graphs_history_bycommiters.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    branches = func.getBranches(obj.get('repoObj'))
    
    return render_to_response(template, {'branches':branches,'reponame':obj.get('reponame') , 'activelink':'graphs', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))

def download(request,userid,slug):
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    func.cloneRepo(obj.get('reponame'))
    func.addToZip(TEMP_CLONE_DIR +"/"+obj.get('repo').slug + ".zip", TEMP_CLONE_DIR +"/"+obj.get('reponame')+"/", obj.get('reponame'))
    
    filename = TEMP_CLONE_DIR + "/" + obj.get('repo').slug + ".zip"                        
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

@login_required
def addfiles(request,userid,slug):
    template = "repocontrol/addfiles.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    user = User.objects.get(username=request.user)
    
    if not user.username == obj.get('user_obj').username:
        return redirect("/%s/%s" %(userid,slug))
    
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            updir = UPLOAD_DIR + obj.get('user_obj').username + "/" + slug
            if not os.path.exists(updir):
                    os.makedirs(updir)
            func.cloneLocalRepository(obj.get('reponame'), updir)
            temp_repo = Repo(updir)
            file_names = []
            for f in files:
                file_names.append(f.name)
                with open(updir + "/" + f.name, 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
            
            for name in file_names:
                temp_repo.git.execute(["git","add",name])

            com_author = user.username + " <" + user.email + ">"
            com_message = "Files " + ', '.join(file_names) + " added"
            au = "--author="+ "\""+ com_author +"\""
            try:
                temp_repo.git.execute(["git","commit","-m",com_message,au])
                command = ["/usr/share/gitolite/gl-admin-push"]
                temp_repo.git.execute(command)
            except:
                return HttpResponse("Cannot commit, push failed!")
            
            form = FileForm()
            message = "Your files has been successfully added"
        else:
            message = "Error!"
        return render_to_response(template, {'message': message,'form':form,'reponame':obj.get('reponame') , 'activelink':'addfiles', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))
    elif request.method == "GET":
        form = FileForm()
        return render_to_response(template, {'form':form,'reponame':obj.get('reponame') , 'activelink':'addfiles', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)}, context_instance=RequestContext(request))
    