from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from userprofile.forms import UserForm, UserLogin, UpdateProfile, NewSSHKeyForm
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from djangogit import func
from userprofile.models import SSHKey
import datetime

def register(request):
    if request.user.is_authenticated():
        return redirect("/users/my")
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
                return redirect(profile)
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
        return render_to_response(template, {'form':form, 'user':user, 'activelink':request.path}, context_instance=RequestContext(request))
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
                        return render_to_response(template, {'form':form, 'mes':mes, 'activelink':request.path}, context_instance=RequestContext(request))
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
            return render_to_response(template, {'form':form, 'mes':mes, 'activelink':request.path}, context_instance=RequestContext(request))

@login_required
def addNewKey(request):
    template = "userprofile/addsshkey.html"
    if request.method == "GET":
        form = NewSSHKeyForm()
        return render_to_response(template, {'form':form, 'activelink':request.path}, context_instance=RequestContext(request))
    elif request.method == "POST":
        form = NewSSHKeyForm(request.POST)
        
        if form.is_valid():
            object = form.save(commit=False)
            object.user = request.user
            object.datetime = datetime.datetime.now()
            object.save()
            
            # add key to gitolite-admin repo if key is active
            if object.active: 
                func.cloneAdminRepo()
                func.addKey(request.user, object.key, object.keyid)
                keyfile = "keydir/%s/%s@%s.pub" %(request.user,request.user,object.keyid)
                func.gitAdd(keyfile)
                message = "SSH key %s@%s.pub added" %(request.user,object.keyid)
                func.commitChange(message)
                func.pushUpstream()
            return redirect(listkeys)
        else:
            return render_to_response(template, {'form':form, 'activelink':request.path}, context_instance=RequestContext(request))
        
@login_required
def listkeys(request):
    template = "userprofile/listsshkeys.html"
    keys = SSHKey.objects.filter(user=request.user)
    return render_to_response(template, {'keys':keys, 'activelink':request.path}, context_instance=RequestContext(request))

@login_required
def activatekey(request,keyid):
    key = get_object_or_404(SSHKey,pk=keyid)
    
    if key.active:
        return redirect(listkeys)
    func.addKey(request.user, key.key, key.keyid)
    keyfile = "keydir/%s/%s@%s.pub" %(request.user,request.user,key.keyid)
    func.gitAdd(keyfile)
    message = "SSH key %s@%s.pub added" %(request.user,key.keyid)
    func.commitChange(message)
    func.pushUpstream()
    key.active = True
    key.save()
    return redirect(listkeys)

def deletekey(request,keyid):
    key = get_object_or_404(SSHKey, pk=keyid)
    keyfile = keyfile = "keydir/%s/%s@%s.pub" %(request.user,request.user,key.keyid)
    func.deleteKeyFile(keyfile)
    message = "Deleted keyfile %s@%s.pub" %(request.user,key.keyid)
    func.commitChange(message)
    func.pushUpstream()
    key.delete()
    return redirect(listkeys)
    

def deactivatekey(request,keyid):
    key = get_object_or_404(SSHKey,pk=keyid)
    if not key.active:
        return redirect(listkeys)
    
    keyfile = keyfile = "keydir/%s/%s@%s.pub" %(request.user,request.user,key.keyid)
    func.deleteKeyFile(keyfile)
    message = "Deleted keyfile %s@%s.pub" %(request.user,key.keyid)
    func.commitChange(message)
    func.pushUpstream()
    key.active = False
    key.save()
    return redirect(listkeys)

def viewprofile(request, keyid):
    pass