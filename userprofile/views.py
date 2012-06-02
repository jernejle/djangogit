from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from userprofile.forms import UserForm, UserLogin, UpdateProfile
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(data.get('username'), data.get('email'), data.get('password'))
            user.save()
    elif request.method == "GET":
        form = UserForm()
    return render_to_response('userprofile/register.html', {'form': form}, context_instance=RequestContext(request))

def login(request):
    if request.user.is_authenticated():
        return redirect("/users/my")
    template = "userprofile/login.html"
    if request.method == "POST":
        form = UserLogin(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = auth.authenticate(username=data.get('username'), password=data.get('password'))
            if user and user.is_active:
                auth.login(request, user)
                return redirect("/")
            else:
                error = "Username or password incorrect"
                return render_to_response(template, {'form':form, 'error':error}, context_instance=RequestContext(request))
        else:
            return render_to_response(template, {'form':form}, context_instance=RequestContext(request))
    elif request.method == "GET":
        form = UserLogin()
        return render_to_response(template, {'form':form}, context_instance=RequestContext(request))
    
def logout(request):
    auth.logout(request)
    return login(request)

@login_required
def profile(request):
    template = "userprofile/profile.html"
    if request.method == "GET":
        user = User.objects.get(username=request.user.username)
        form = UpdateProfile()
        return render_to_response(template, {'form':form, 'user':user}, context_instance=RequestContext(request))
    elif request.method == "POST":
        form = UpdateProfile(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            if user and user.is_active:
                pass1 = form.cleaned_data.get('password')
                pass2 = form.cleaned_data.get('password2')
                if pass1:
                    if pass1 == pass2:
                        user.set_password(pass1)
                    else:
                        mes = "Passwords do not match"
                        return render_to_response(template, {'form':form,'mes':mes}, context_instance=RequestContext(request))
                data = form.cleaned_data
                if data.get('first_name'):
                    user.first_name = data.get('first_name')
                if data.get('last_name'):
                    user.last_name = data.get('last_name')
                if data.get('email'):
                    user.email = data.get('email')
                user.save()
                return redirect('/users/my/')
        else:
            mes = "Cannot update profile"
            return render_to_response(template, {'form':form, 'mes':mes}, context_instance=RequestContext(request))
