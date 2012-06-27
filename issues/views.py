from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from djangogit import func
from issues.forms import NewIssue, NewComment
from django.contrib.auth.decorators import login_required
from issues.models import Issue, IssueComment
from django.db.models import Q
import pdb
import datetime

@login_required
def add(request, userid, slug):
    template = "issues/addnew.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    
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
            return HttpResponse("added")
        else:
            return render_to_response(template, {'activelink':'add', 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'form':form}, context_instance=RequestContext(request))
        
def all(request, userid, slug):
    template = "issues/all.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    issues = Issue.objects.filter(repository=obj.get('repo')).order_by('-published')
    return render_to_response(template, {'issues':issues, 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'browse'}, context_instance=RequestContext(request))

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
        return redirect("/%s/%s/issues/%s/" %(userid,slug,keyid))
    else:
        return redirect("/")
    
def active(request,userid,slug):
    template = "issues/active.html"
    obj = func.getRepoObjorNone(userid, slug)
    func.objOr404(obj)
    now = datetime.datetime.now()
    yest = datetime.datetime.now() - datetime.timedelta(days=1)
    issues = Issue.objects.filter(Q(published__year=now.year,published__month=now.month,published__day=now.day) | Q(published__year=yest.year,published__month=yest.month,published__day=yest.day))
    return render_to_response(template, {'issues':issues, 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'active'}, context_instance=RequestContext(request))

def changestatus(request,userid,slug,keyid):
    if request.method == "POST":
        obj = func.getRepoObjorNone(userid, slug)
        func.objOr404(obj)
        issue = get_object_or_404(Issue, pk=keyid)
        if not issue.author == request.user:
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
    issues = Issue.objects.filter(author=request.user)
    return render_to_response(template, {'issues':issues, 'reponame':obj.get('reponame'), 'href':"/%d/%s/" % (obj.get('user_obj').id, slug), 'activelink':'my'}, context_instance=RequestContext(request))
    