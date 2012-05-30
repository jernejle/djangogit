from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


def register(request):
    return render_to_response('userprofile/register.html', {}, context_instance=RequestContext(request))