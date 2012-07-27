from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from djangogit import func
from issues.forms import NewIssue, NewComment
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
    
    if request.method == "GET":
        form = NewIssue()
        return render_to_response(template, {'activelink':'add', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'form':form}, context_instance=RequestContext(request))
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
    return render_to_response(template, {'form':form, 'issue':issue, 'comments':comments,'reponame':obj.get('reponame'), 'activelink':'browse', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug)} , context_instance=RequestContext(request))

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
        if not issue.author == request.user and issue.repository.user != request.user:
            return redirect("/")
        
        if issue.open:
            issue.open = False
        else:
            issue.open = True
        
        issue.save()
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    else:
        return redirect("/")

@login_required
def myissues(request,userid,slug):
    template = "issues/active.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    issues = Issue.objects.filter(author=request.user, repository=obj.get('repo')).order_by('-published')
    return render_to_response(template, {'issues':issues, 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'my'}, context_instance=RequestContext(request))
    