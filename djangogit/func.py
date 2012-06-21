from djangogit.settings import TEMP_REPODIR, GITOLITE_ADMIN_REPO, LOG_FILE, REPODIR
from git import *
from git import exc
from django.contrib.auth.models import User
from repocontrol.models import Repository
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

import os
import subprocess
import shlex, subprocess
import sys
import datetime
import re

def cloneAdminRepo():
    if not os.path.exists(TEMP_REPODIR):
        os.chdir(GITOLITE_ADMIN_REPO)
        command = "git clone %s %s" % (GITOLITE_ADMIN_REPO, TEMP_REPODIR)
        runAndLog(command)
        

def addKey(username, key, keyid):
    fulldir = TEMP_REPODIR + "/keydir/%s" % username
    if not os.path.isdir(fulldir):
        os.makedirs(fulldir)
    filestr = "%s/%s@%s.pub" % (fulldir, username, keyid)
    newkey = open(filestr, 'w')
    newkey.write(key)
    newkey.close()
    
    
def runAndLog(command):
    out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = out.communicate()
    returnCode = out.returncode

    if returnCode == 0:
        return stdout

    
def writeToLog(content):
    file = open(LOG_FILE, 'w')
    file.write(str(datetime.datetime.now()) + "\n")
    file.write(content)
    file.close()
    
def commitChange(message):
    repo = initRepo()
    commit = ["git", "commit", "-m", message]
    repo.git.execute(commit)
    
def gitAdd(file):
    repo = initRepo()
    addcommand = ["git", "add", file]
    repo.git.execute(addcommand)
    
def initRepo():
    cloneAdminRepo()
    repo = Repo(TEMP_REPODIR)
    return repo
    
def pushUpstream():
    repo = initRepo()
    command = ["/usr/share/gitolite/gl-admin-push"]
    repo.git.execute(command)
    
def deleteKeyFile(key):
    repo = initRepo()
    command = ["git", "rm", "-f", key]
    repo.git.execute(command)
    
def addRepo(username, reponame, perm):
    repo = initRepo()
    dir = "%s/conf/%s" % (TEMP_REPODIR, username)
    
    if not os.path.isdir(dir):
        os.makedirs(dir)
    conf = "%s/%s.conf" % (dir, reponame)
    file = open(conf, 'w')
    repowrite = "repo %s/%s \n" % (username, reponame) 
    permwrite = "    %s    =    %s" % (perm, username)
    file.write(repowrite)
    file.write(permwrite)
    file.close()

def appendToGitoliteConf(file, line):
    file = open(file, 'a')
    file.write(line)
    file.close()

#find and get actual repo object
def getRepoObject(reponame):
    path = "%s%s.git" % (REPODIR, reponame)
    try:
        repo = Repo(path)
    except exc.NoSuchPathError, exc.InvalidGitRepositoryError:
        repo = None
    return repo

#get user object, repo object from db and actual repo
def getRepoObjorNone(userid, slug):
    user_obj = None
    try:
        user_obj = User.objects.get(pk=userid)
    except ObjectDoesNotExist:
        return None
    repo = None
    try:    
        repo = Repository.objects.get(user=user_obj, slug=slug)
    except ObjectDoesNotExist:
        return None
    reponame = "%s/%s" % (user_obj, repo.slug)
    repoObj = getRepoObject(reponame)
    if not repoObj:
        return None
    obj = {'repoObj':repoObj, 'reponame':reponame, 'user_obj':user_obj, 'repo':repo}
    return obj

def objOr404(obj):
    if not obj:
        raise Http404

def getAllObjects(type,branchorsha):
    repoobject = Repo("/home/jernej/django")
    treestr = repoobject.git.execute(["git","ls-tree",branchorsha]).replace("\t"," ").splitlines()
    objects = []
    
    for line in treestr:
        linesplit = re.split("\s",line)
        obj = {"perm":linesplit[0],"type":linesplit[1],"sha":linesplit[2],"name":linesplit[3]}
        objects.append(obj)
    
    if type == "tree":
        typeobjects = [x for x in objects if x["type"] == "tree"]
    elif type =="blob":
        typeobjects = [x for x in objects if x["type"] == "blob"]
    return typeobjects

def showBlob(sha):
    repoobject = Repo("/home/jernej/django")
    blob = repoobject.git.execute(["git","show",sha])
    return blob

def getBranches(repo):
    repoobject = Repo("/home/jernej/django")
    branches = repoobject.git.execute(["git","branch","-r"]).replace(" ", "").splitlines()
    return branches

def getCommits(repo,branch):
    repoobject = Repo("/home/jernej/django")
    commits = repoobject.iter_commits(branch, max_count=20)
    return commits