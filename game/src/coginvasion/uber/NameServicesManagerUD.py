"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file NameServicesManagerUD.py
@author Maverick Liberty
@date February 21, 2016

"""

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

from src.coginvasion.distributed.CogInvasionErrorCodes import EC_NON_EXISTENT_AV

import datetime
import json

NAME_PENDING = 0
NAME_ACCEPTED = 1
NAME_DECLINED = 2

class NameServicesManagerUD(DistributedObjectGlobalUD):

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.requestedNames = []
        self.dataPath = 'astron/nameRequests.json'

    def requestName(self, name, avId):
        accId = self.air.getAccountIdFromSender()

        def gotAccount(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return
            toons = fields['AVATAR_IDS']
            if not avId in toons:
                # Somebody is trying to request a name for a toon that doesn't belong to them.
                self.notify.warning("SECURITY: Account %s tried to request a name for a toon that doesn't belong to them.")
                self.air.eject(accId, EC_NON_EXISTENT_AV, "Tried to request name for toon that isn't on their account.")
                return

            now = datetime.datetime.now()
            date = "%s %s %s" % (now.month, now.day, now.year)
            self.requestedNames.append({'name' : name, 'avId' : avId, 'accId': accId, 'date' : date, 'status' : NAME_PENDING})
            self.saveData()

        self.air.csm.queryAccount(accId, callback = gotAccount)

    def requestNameData(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if True:
            names, avatarIds, accIds, dates, statuses = [], [], [], [], []
            for i in xrange((len(self.requestedNames))):
                nameRequest = self.requestedNames[i]
                names.append(nameRequest['name'])
                avatarIds.append(int(nameRequest['avId']))
                accIds.append(int(nameRequest['accId']))
                dates.append(nameRequest['date'])
                statuses.append(int(nameRequest['status']))
            self.sendUpdateToAvatarId(avId, 'nameDataRequest', [names, avatarIds, accIds, dates, statuses])
        else:
            avatar.ejectSelf('Attempted to access administrator only system.')

    def saveData(self):
        with open(self.dataPath, 'w') as dataFile:
            json.dump(self.requestedNames, dataFile, indent = 1)

    def loadData(self):
        with open(self.dataPath, 'r') as dataFile:
            self.requestedNames = list(json.load(dataFile))

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.loadData()
