from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from repocontrol.forms import NewRepo
from djangogit.settings import TEMP_REPODIR, GITOLITE_CONF
import datetime
from djangogit import func

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
            message = "Repo %s/%s added" %(request.user,object.slug)
            file = "%s/conf/%s/%s.conf" %(TEMP_REPODIR,request.user,object.slug)
            includeline = "\ninclude \"%s/%s.conf\"" %(request.user,object.slug)
            func.appendToGitoliteConf(GITOLITE_CONF, includeline)
            func.gitAdd(file)
            func.gitAdd(GITOLITE_CONF)
            func.commitChange(message)
            return HttpResponse("added")
        else:
            return render_to_response(template, {'form':form}, context_instance=RequestContext(request))