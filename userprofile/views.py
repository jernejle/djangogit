from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from userprofile.forms import UserForm


def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
    elif request.method == "GET":
        form = UserForm()
    return render_to_response('userprofile/register.html', {'form': form}, context_instance=RequestContext(request))
