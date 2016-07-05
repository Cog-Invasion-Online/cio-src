"""

  Filename: DatabaseManager.py
  Created by: DecodedLogic (04Nov15)
  Designed to successfully manage our accounts.

"""

from os import listdir
from os.path import isfile, join
import os, yaml

class Account:
    
    def __init__(self, username):
        self.username = username
        self.avatars = []
        
    def addAvatar(self, avatarFile):
        self.avatars.append(avatarFile)

def loadEntries():
    databasePath = "astron/databases/astrondb"
    files = os.listdir(databasePath)
    docs = []
    for file in files:
        filePath = "%s/%s" % (databasePath, file)
        stream = open(filePath, 'r+')
        dataMap = yaml.safe_load(stream)
        docs.append(yaml.dump(dataMap, stream))
        stream.close()
    accounts = []
    toons = []
    for doc in docs:
        print doc
        if doc.get("class") == "DistributedToon":
            toons.append(doc)
        else:
            accounts.append(doc)
    print "Accounts: %s \nToons: %s" % (str(len(accounts)), str(len(toons)))


print "Starting Database Manager by DecodedLogic. \nPlease wait..."

databasePath = os.path.join(os.path.dirname(__file__), "astron/databases/astrondb")
test()