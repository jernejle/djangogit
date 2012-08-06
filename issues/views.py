from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from djangogit import func
from issues.forms import NewIssue, NewComment, ChangeLabel, EditIssue, EditComment
from django.contrib.auth.decorators import login_required
from issues.models import Issue, IssueComment
from django.db.models import Q
from userprofile.models import Message
import pdb
import datetime

@login_required
def add(request, userid, slug):
    template = "issues/addnew.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    message = None
    team_members = obj.get('repo').team.all()
    
    if request.method == "GET":
        form = NewIssue()
        return render_to_response(template, {'repoadmin':obj.get('repo').user,'team':team_members,'activelink':'add', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'form':form}, context_instance=RequestContext(request))
    elif request.method == "POST":
        form = NewIssue(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.author = request.user
            issue.published = datetime.datetime.now()
            issue.open = True
            issue.repository = obj.get('repo')
            issue.save()
            message = "Your issue was added."
            team_members = obj.get('repo').team.all()
            
            mess = "User user#%s posted new issue in repo#%s" % (request.user, obj.get('reponame'))
            title = "New issue in %s" % (obj.get('reponame'))
            now = datetime.datetime.now()
            
            if request.user != obj.get('repo').user:
                Message.objects.create(title=title, content=mess, datetime=now, user=obj.get('repo').user, read=False)

            for member in team_members:
                if request.user != member:
                    Message.objects.create(title=title, content=mess, datetime=now, user=member, read=False)
            
        return render_to_response(template, {'message':message,'activelink':'add', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'form':form}, context_instance=RequestContext(request))
        
def all(request, userid, slug):
    template = "issues/all.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    return render_to_response(template, {'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'browse'}, context_instance=RequestContext(request))

def details(request, userid, slug, keyid):
    template = "issues/details.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    issue = get_object_or_404(Issue, pk=keyid)
    comments = IssueComment.objects.filter(issue=issue)
    form = NewComment()
    changelabel = ChangeLabel({'title':issue.title,'label':issue.label, 'deadline':issue.deadline})
    team = obj.get('repo').team.all()
    return render_to_response(template, {'team':team,'changelabel':changelabel,'form':form, 'issue':issue, 'comments':comments,'reponame':obj.get('reponame'), 'activelink':'browse', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))

@login_required
def postcomment(request,userid,slug,keyid):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        issue = get_object_or_404(Issue, pk=keyid)
        form = NewComment(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.date = datetime.datetime.now()
            issue.last_action = datetime.datetime.now()
            issue.save()
            comment.issue = issue
            comment.save()
            
            comments = IssueComment.objects.filter(issue=issue)
            users = []
            mess = "User user#%s posted new comment in repo#%s" % (request.user, obj.get('reponame'))
            title = "New comment on issue %s in %s" % (issue.title,obj.get('reponame'))
            now = datetime.datetime.now()
            for comment in comments:
                if comment.author == request.user:
                    continue
                
                if comment.author not in users:
                    users.append(comment.author)
                    Message.objects.create(title=title, content=mess, datetime=now, user=comment.author, read=False)
            
            if obj.get('repo').user not in users and obj.get('repo').user != request.user:
                Message.objects.create(title=title, content=mess, datetime=now, user=obj.get('repo').user, read=False)
            
            if issue.author not in users and issue.author != request.user:
                Message.objects.create(title=title, content=mess, datetime=now, user=issue.author, read=False)
            
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    else:
        return redirect("/")

def changestatus(request,userid,slug,keyid):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        issue = get_object_or_404(Issue, pk=keyid)
        team = obj.get('repo').team.all()
        if not issue.repository.user == request.user and not request.user in team:
            return redirect("/")
        
        if issue.open:
            issue.open = False
        else:
            issue.open = True
        
        issue.save()
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    else:
        return redirect("/")
    
def changelabel(request,userid,slug,keyid):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        issue = get_object_or_404(Issue,pk=keyid)
        team = obj.get('repo').team.all()
        
        if not issue.repository.user == request.user and request.user not in team:
            return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
        
        labelvalue = request.POST.get('label','')
        title = request.POST.get('title','')
        deadline = request.POST.get('deadline','')
        if labelvalue in dict(Issue.LABELS):
            issue.label = labelvalue
            if title:
                issue.title = title
            if deadline:
                issue.deadline = deadline
                
            issue.save()
        
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    
@login_required
def edit(request,userid,slug,keyid):
    template = "issues/editissue.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    issue = get_object_or_404(Issue,pk=keyid)
    team = obj.get('repo').team.all()
    
    if request.user == issue.author or request.user == issue.repository.user or request.user in team:
        if request.method == "GET":
            form = EditIssue({'content':issue.content})
            return render_to_response(template, {'form':form, 'issue':issue,'reponame':obj.get('reponame'), 'activelink':'browse', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))
        elif request.method == "POST":
            content = request.POST.get('content','')
            if content:
                issue.content = content
                issue.save()
            return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid)) 
    else:
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    
def deleteissue(request,userid,slug,keyid):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        issue = get_object_or_404(Issue,pk=keyid)
        team = obj.get('repo').team.all()
        
        if not issue.repository.user == request.user and request.user not in team:
            return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
        
        issue.delete()
        return redirect("/%s/%s/issues/" %(userid,slug))
    
def removecomment(request,userid,slug,keyid,commentid):
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    comment = get_object_or_404(IssueComment,pk=commentid)
    issue = get_object_or_404(Issue, pk=keyid)
    team = obj.get('repo').team.all()
        
    if not issue.repository.user == request.user and request.user not in team and not comment.author == request.user:
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    
    comment.delete()
    return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))

def editcomment(request,userid,slug,keyid,commentid):
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    comment = get_object_or_404(IssueComment,pk=commentid)
    issue = get_object_or_404(Issue, pk=keyid)
    team = obj.get('repo').team.all()
        
    if not issue.repository.user == request.user and request.user not in team and not comment.author == request.user:
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    
    if request.method == "GET":
        template = "issues/editcomment.html"
        form = EditComment({'comment':comment.comment})
        return render_to_response(template, {'form':form, 'issue':issue,'comment':comment,'reponame':obj.get('reponame'), 'activelink':'browse', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))
    elif request.method == "POST":
        new_comm = request.POST.get('comment','')
        if new_comm:
            comment.comment = new_comm
            comment.save()
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))

@login_required
def myissues(request,userid,slug):
    template = "issues/active.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    issues = Issue.objects.filter(author=request.user, repository=obj.get('repo')).order_by('-published')
    return render_to_response(template, {'issues':issues, 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'my'}, context_instance=RequestContext(request))
    