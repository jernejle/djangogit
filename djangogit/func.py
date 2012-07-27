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
    pubview = "\n    R    =    @all"
    file.write(pubview)
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
    reponame = "%s/%s" % (user_obj.username, repo.slug)
    repoObj = getRepoObject(reponame)
    if not repoObj:
        return None
    obj = {'repoObj':repoObj, 'reponame':reponame, 'user_obj':user_obj, 'repo':repo}
    return obj

def objOr404(obj):
    if not obj:
        raise Http404

def getAllObjects(repo,type,branchorsha):
    repoobject = repo
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

def showBlob(repo,sha):
    repoobject = repo
    blob = repoobject.git.execute(["git","show",sha])
    return blob

def getBranches(repo):
    repoobject = repo
    branches = repoobject.git.execute(["git","branch","-a"]).strip("*").replace(" ", "").splitlines()
    return branches

def getCommits(repo,branch,per_page,skip):
    repoobject = repo
    commits = repoobject.iter_commits(branch,max_count=per_page, skip=skip)
    return commits

def getTeam(username,slug):
    repo = initRepo()
    if not repo:
        return None
    
    head_tree = repo.head.commit.tree
    conf_tree = head_tree.trees[0]
    
    stream = None
    permissions = []
    if conf_tree.name == "conf":
        for t in conf_tree.trees:
            if t.name == username:
                for blob in t.blobs:
                    if blob.name == "%s.conf" % (slug):
                        stream = blob.data_stream.read().splitlines()
    foundrepo = 0
    if stream:
        for line in stream:
            if re.search("repo .*/.*",line):
                foundrepo = 1
                continue
            elif foundrepo == 1:
                linesplit = line.split("=")
                try:
                    perm = getPermissions(linesplit[0].strip())
                    tmp = {'perm':perm, 'user':linesplit[1].strip()}
                    permissions.append(tmp)
                except:
                    pass
    return permissions

def getPermissions(type):
    perm = None
    if type == "R":
        perm = "Read only"
    elif type == "RW":
        perm = "Read and Write data"
    elif type == "RW+":
        perm = "Read, Write and Delete data"
    elif type == "-":
        perm = "Denied"
    
    return perm

def addTeamMember(reponame,user,perm):
    repo = initRepo()
    if not repo:
        return None
    
    dir = "%s/conf/%s.conf" % (TEMP_REPODIR, reponame)
    if os.path.exists(dir):
        permwrite = "\n    %s    =    %s" % (perm, user)
        file = open(dir,"a")
        file.write(permwrite)
        file.close()
        
def delTeamMember(reponame,user):
    repo = initRepo()
    if not repo:
        return False
    
    dir = "%s/conf/%s.conf" % (TEMP_REPODIR, reponame)
    if os.path.exists(dir):
        try:
            oldfile = os.rename(dir, "%s.old" % dir)
            old = open("%s.old" % dir, "r")
            newfile = open(dir, "w+")
            
            for line in old:
                if line.strip():
                    if re.search("repo .*/.*",line):
                        newfile.write(line)
                        continue
                    if re.search("RW+|RW|R|",line):
                        if user in line:
                            continue
                    newfile.write(line)
                else:
                    continue
            old.close()
            newfile.close()
            return True
        except:
            return False
    else:
        return False
    
def getDate(datetimeObj):
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    if datetimeObj.date() == today.date():
        return "Today at %s" %datetimeObj.strftime("%H:%M")
    elif datetimeObj.date() == yesterday.date():
        return "Yesterday at %s" %datetimeObj.strftime("%H:%M")
    else:
        return datetimeObj.strftime("%H:%M %B %d, %Y")