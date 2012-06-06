from djangogit.settings import TEMP_REPODIR, GITOLITE_ADMIN_REPO, LOG_FILE
from git import *
import os
import subprocess
import shlex, subprocess
import sys
import datetime

def cloneAdminRepo():
    if not os.path.exists(TEMP_REPODIR):
        os.chdir(GITOLITE_ADMIN_REPO)
        command = "git clone %s %s" %(GITOLITE_ADMIN_REPO,TEMP_REPODIR)
        runAndLog(command)
        

def addKey(username,key,keyid):
    fulldir = TEMP_REPODIR + "/keydir/%s" % username
    if not os.path.isdir(fulldir):
        os.makedirs(fulldir)
    filestr = "%s/%s@%s.pub" %(fulldir,username,keyid)
    newkey = open(filestr,'w')
    newkey.write(key)
    newkey.close()
    
    
def runAndLog(command):
    out = subprocess.Popen(command,shell = True,stdout = subprocess.PIPE)
    stdout, stderr = out.communicate()
    returnCode = out.returncode

    if returnCode == 0:
        writeToLog(stdout)

    
def writeToLog(content):
    file = open(LOG_FILE, 'w')
    file.write(str(datetime.datetime.now()) + "\n")
    file.write(content)
    file.close()
    
def commitChange(message):
    repo = initRepo()
    commit = ["git","commit","-m",message]
    repo.git.execute(commit)
    
def gitAdd(file):
    repo = initRepo()
    addcommand = ["git","add",file]
    repo.git.execute(addcommand)
    
def initRepo():
    cloneAdminRepo()
    repo = Repo(TEMP_REPODIR)
    return repo
    
def pushUpstream():
    repo = initRepo()
    command = ["gitolite","push"]
    repo.git.execute(command)
    
def deleteKeyFile(key):
    repo = initRepo()
    command = ["git","rm","-f",key]
    repo.git.execute(command)
    
def addRepo(username,reponame,perm):
    repo = initRepo()
    dir = "%s/conf/%s" %(TEMP_REPODIR,username)
    
    if not os.path.isdir(dir):
        os.makedirs(dir)
    conf = "%s/%s.conf" %(dir,reponame)
    file = open(conf,'w')
    repowrite = "repo %s/%s \n" %(username,reponame) 
    permwrite = "    %s    =    %s" %(perm,username)
    file.write(repowrite)
    file.write(permwrite)
    file.close()

def appendToGitoliteConf(file,line):
    file = open(file,'a')
    file.write(line)
    file.close()