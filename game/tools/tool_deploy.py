"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file tool_deploy.py
@author Brian Lach
@date March 18, 2017

"""

import paramiko
import hashlib
import os
import sys
import winsound

def playDone():
    winsound.PlaySound('tools/deploydone.wav', winsound.SND_FILENAME)

host = "50.87.26.220"
port = 22
transport = paramiko.Transport((host, port))

password = ":o?i|v-F3t?B"
username = "coginvas"
transport.connect(username = username, password = password)

sftp = paramiko.SFTPClient.from_transport(transport)

print 'Sucessfully opened sftp connection!'

servData = {}

print "Reading current server hash file..."

srvFile = sftp.file("public_html/download/coginvasion/file_info.txt", "r")

for line in srvFile.readlines():
    if not "//" in line and len(line) > 0 and not line.isspace():
        filename, sha = line.split(' ')
        sha = sha.replace('\n', '')
        if "-" in sha:
            sha = sha.replace('-', '')
        sha = sha.lower()
        servData[filename] = sha

bbin = raw_input("\nDo you need coginvasion.bin to be built?\n(Python code changes) [1/0] ")
if bbin in ["1"]:
    print "Building coginvasion.bin..."
    os.chdir("tools/nirai/")
    os.system("build_bin")
    os.chdir("../../")

bexe = raw_input("\nDo you need to build the exes?\n(C++ changes / Panda3D update) [1/0] ")
if bexe in ["1"]:
    print "Building the exes (OpenGL + DX9)"
    os.chdir("tools/nirai/")
    os.system("build_exe")
    os.chdir("../../")

print "Examining local game directory..."

class LocalFile:

    def __init__(self, fullfile):
        self.fullfile = fullfile
        splPath = fullfile.split('/')
        self.filename = splPath[len(splPath) - 1]

lclData = {}

filesToDeploy = []

files = open('tools/files.txt', 'r')
for fpath in files.readlines():
    fpath = fpath.replace('\n', '')
    splPath = fpath.split('/')
    lclFile = LocalFile(fpath)
    f = open(fpath, 'rb')
    sha = hashlib.sha1(f.read()).hexdigest()
    f.close()
    lclData[lclFile] = sha
    
    print "Local file: {0} Set hash to:".format(lclFile.filename)
    print sha

for lclFile, lclSha in lclData.items():
    srvSha = servData.get(lclFile.filename)

    if (srvSha != lclSha):
        print "\nI noticed that your {0} differs from the server's {0}".format(lclFile.filename)
        upd = raw_input("Do you want your {0} to be deployed? [1/0] ".format(lclFile.filename))
        if upd not in ["1"]:
            # They don't want this file to be deployed. Keep the same hash from before.
            lclData[lclFile] = srvSha
        else:
            if ".mf" in lclFile.filename:
                mfSHA = lclData[lclFile]
                comprFile = LocalFile(lclFile.fullfile[:-3] + ".tar.gz")
                filesToDeploy.append(comprFile)
            else:
                filesToDeploy.append(lclFile)

print

if not len(filesToDeploy):
    print "Everything matches with the server -- nothing to deploy!"
    print "Done!"
    sftp.close()
    playDone()
    sys.exit(0)

print "Writing and deploying hash file..."
hashfw = open('file_info.txt', 'w')
for lclFile, sha in lclData.items():
    if sha == None:
        print lclFile.filename
        print "^ THAT IS NONE"
        continue
    hashfw.write(lclFile.filename + " " + sha + "\n")
hashfw.flush()
hashfw.close()

hashfr = open('file_info.txt', 'r')
sftp.putfo(hashfr, "public_html/download/coginvasion/file_info.txt")
hashfr.close()
os.remove("file_info.txt")

print "Deploying {0} files...".format(len(filesToDeploy))

for lclFile in filesToDeploy:
    print "Deploying {0}...".format(lclFile.fullfile)
    f = open(lclFile.fullfile, 'rb')
    sftp.putfo(f, "public_html/download/coginvasion/" + lclFile.filename)
    f.close()

sftp.close()

print "Done!"
playDone()