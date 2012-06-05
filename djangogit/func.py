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
    repo = None
    try:
        repo = Repo(TEMP_REPODIR)
    except git.exc.NoSuchPathError:
        #log error
        pass
    finally:
        return repo
    
def pushUpstream():
    repo = initRepo()
    command = ["gitolite","push"]
    repo.git.execute(command)