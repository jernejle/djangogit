from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from djangogit import func
from django.template.defaultfilters import escape
from git import *
from repocontrol.models import CommitComment, Repository
from issues.models import Issue, IssueComment
from django.contrib.auth.models import User
import pdb

@dajaxice_register
def getobjects(request, userid, slug, sha):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    sha = escape(sha)
    if not obj:
        return
    
    dajax = Dajax()
    trees = func.getAllObjects(obj.get('repoObj'), "tree", sha)
    blobs = func.getAllObjects(obj.get('repoObj'), "blob", sha)
    icon = "<i class='icon-folder-close'></i>"
    tablerow = ["<tr><td id='%s' class='tree'>%s %s</td></tr>" % (obj["sha"], icon, obj["name"]) for obj in trees]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    icon = "<i class='icon-file'></i>"
    tablerow = ["<tr><td id='%s' class='blob'>%s %s</td></tr>" % (obj["sha"], icon, obj["name"]) for obj in blobs]
    dajax.append("#filesbody", "innerHTML", ''.join(tablerow))
    dajax.add_data("", "setEvents")
    return dajax.json()

@dajaxice_register
def getBlob(request, userid, slug, sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    try:
        blob = func.showBlob(obj.get('repoObj'), sha).replace("\n", "<br />")
    except:
        blob = None
        
    if not blob:
        return
    
    dajax = Dajax()
    dajax.add_data(blob, "writeBlob")
    return dajax.json()

@dajaxice_register
def getCommitDiff(request, userid, slug, sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    try:
        commit = obj.get('repoObj').commit(sha)
        difflist = obj.get('repoObj').git.execute(["git", "diff-tree", "-p", sha])
    except:
        commit = None
    
    if not commit or not difflist:
        return
    
    dajax = Dajax()
    dajax.add_data(''.join(difflist), "writeDiff")
    return dajax.json()

@dajaxice_register
def addtodifflist(request, userid, slug, sha):
    userid = int(userid)
    slug = escape(slug)
    sha = escape(sha)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    #sha exists ?
    reponame = "%s%s" % (userid, slug)
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
def clearlist(request, userid, slug):
    userid = int(userid)
    slug = escape(slug)
    obj = func.getRepoObjorNone(userid, slug)
    if not obj:
        return
    
    reponame = "%s%s" % (userid, slug)
    if request.session.get(reponame, None):
        request.session[reponame] = None
        
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def myrepos_news(request):
    if request.user.is_authenticated():
        dajax = Dajax()
        
        commitscomments = CommitComment.objects.filter(repository__user=request.user).order_by('-date')[:5]
        myrepos_issues = Issue.objects.filter(repository__user=request.user).order_by('-published')[:5]
        myrepos_issues_comments = IssueComment.objects.filter(issue__repository__user=request.user).order_by('-date')[:5] 
        
        cc = [{'tab':'#tab2', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.repository.user.id, 'slug': comment.repository.slug, 'sha':comment.sha, 'repo_user':comment.repository.user.username, 'date': func.getDate(comment.date)} for comment in commitscomments]
        dajax.add_data(cc, "commitcomment")
        iss = [{'tab':'#tab2', 'label':issue.label, 'author_id':issue.author.id, 'author_username':issue.author.username, 'userid':issue.repository.user.id, 'slug':issue.repository.slug, 'id':issue.id, 'repo_user':issue.repository.user.username, 'date':func.getDate(issue.published)} for issue in myrepos_issues]
        dajax.add_data(iss, "issues")
        icom = [{'tab':'#tab2', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.issue.repository.user.id, 'slug':comment.issue.repository.slug, 'id':comment.issue.id, 'repo_user': comment.issue.repository.user.username, 'date':func.getDate(comment.date)} for comment in myrepos_issues_comments]
        dajax.add_data(icom, "issuescomments")
        
        return dajax.json()
    
@dajaxice_register
def teamrepos_news(request):
    if request.user.is_authenticated():
        dajax = Dajax()
        
        teamrepos = User.objects.get(username=request.user).repository_collabolators.order_by('-created')
        teamrepos_commits = CommitComment.objects.filter(repository__in=teamrepos).order_by('-date')[:5]
        teamrepos_issues = Issue.objects.filter(repository__in=teamrepos).order_by('-published')[:5]
        teamrepos_issues_comments = IssueComment.objects.filter(issue__repository__in=teamrepos).order_by('-date')[:5]
        
        cc = [{'tab':'#tab3', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.repository.user.id, 'slug': comment.repository.slug, 'sha':comment.sha, 'repo_user':comment.repository.user.username, 'date': func.getDate(comment.date)} for comment in teamrepos_commits]
        dajax.add_data(cc, "commitcomment")
        iss = [{'tab':'#tab3', 'label':issue.label, 'author_id':issue.author.id, 'author_username':issue.author.username, 'userid':issue.repository.user.id, 'slug':issue.repository.slug, 'id':issue.id, 'repo_user':issue.repository.user.username, 'date': func.getDate(issue.published)} for issue in teamrepos_issues]
        dajax.add_data(iss, "issues")
        icom = [{'tab':'#tab3', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.issue.repository.user.id, 'slug':comment.issue.repository.slug, 'id':comment.issue.id, 'repo_user': comment.issue.repository.user.username, 'date':func.getDate(comment.date)} for comment in teamrepos_issues_comments]
        dajax.add_data(icom, "issuescomments")
        
        return dajax.json()
    
@dajaxice_register
def index_news(request):
    dajax = Dajax()
    commitscomments = CommitComment.objects.filter(repository__private=False).order_by('-date')[:5]
    newrepos = Repository.objects.filter(private=False).order_by('-created')[:5]
    issues = Issue.objects.filter(repository__private=False).order_by('-published')[:5]
    issues_comments = IssueComment.objects.filter(issue__repository__private=False).order_by('-date')[:5]

    cc = [{'tab':'#tab1', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.repository.user.id, 'slug': comment.repository.slug, 'sha':comment.sha, 'repo_user':comment.repository.user.username, 'date': func.getDate(comment.date)} for comment in commitscomments]
    dajax.add_data(cc, "commitcomment")
    iss = [{'tab':'#tab1', 'label':issue.label, 'author_id':issue.author.id, 'author_username':issue.author.username, 'userid':issue.repository.user.id, 'slug':issue.repository.slug, 'id':issue.id, 'repo_user':issue.repository.user.username, 'date': func.getDate(issue.published)} for issue in issues]
    dajax.add_data(iss, "issues")
    icom = [{'tab':'#tab1', 'author_id':comment.author.id, 'author_username':comment.author.username, 'userid':comment.issue.repository.user.id, 'slug':comment.issue.repository.slug, 'id':comment.issue.id, 'repo_user': comment.issue.repository.user.username, 'date':func.getDate(comment.date)} for comment in issues_comments]
    dajax.add_data(icom, "issuescomments")
    newrep = [{'tab':'#tab1', 'author_id':repo.user.id, 'author_username':repo.user.username, 'slug':repo.slug, 'date':func.getDate(repo.created)} for repo in newrepos]
    dajax.add_data(newrep, "newrepos")
    
    return dajax.json()

