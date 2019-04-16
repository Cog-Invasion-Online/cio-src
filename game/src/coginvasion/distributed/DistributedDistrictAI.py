"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDistrictAI.py
@author Brian Lach
@date December 14, 2014

"""

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify
import time

class DistributedDistrictAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedDistrictAI')
    
    def __init__(self, air):
        try:
            self.DistributedDistrictAI_initialized
            return
        except:
            self.DistributedDistrictAI_intialized = 1
        DistributedObjectAI.__init__(self, air)
        self.available = 0
        self.avatarIds = []
        self.population = 0
        self.popRecord = 0
        self.name = ""
        return

    def ping(self):
        sender = self.air.getMsgSender()
        # Ping!
        self.sendUpdateToChannel(sender, 'pingResp', [])

    def setDistrictName(self, name):
        self.name = name

    def d_setDistrictName(self, name):
        self.sendUpdate('setDistrictName', [name])

    def b_setDistrictName(self, name):
        self.d_setDistrictName(name)
        self.setDistrictName(name)

    def getDistrictName(self):
        return self.name

    def setPopRecord(self, record):
        self.popRecord = record

    def d_setPopRecord(self, record):
        self.sendUpdate('setPopRecord', [record])

    def b_setPopRecord(self, record):
        self.d_setPopRecord(record)
        self.setPopRecord(record)

    def getPopRecord(self):
        return self.popRecord

    def announceGenerate(self):
        taskMgr.add(self.monitorAvatars, "monitorAvatars")
        base.finalExitCallbacks.append(self.sendShutdown)
        DistributedObjectAI.announceGenerate(self)

    def sendShutdown(self):
        # Tell the district name manager we are shutting down to free up the name.
        self.air.districtNameMgr.d_shuttingDown(self.name)

    def setPopulation(self, amount):
        self.population = amount
        if amount > self.getPopRecord():
            self.notify.info("New Population Record: " + str(amount))
            self.b_setPopRecord(amount)

    def d_setPopulation(self, amount):
        self.sendUpdate('setPopulation', [amount])

    def b_setPopulation(self, amount):
        self.d_setPopulation(amount)
        self.setPopulation(amount)

    def getPopulation(self):
        return self.population

    def joining(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.info("[" + str(time.strftime("%m-%d-%Y %H:%M:%S")) + "] " + str(avId) + " is joining my district!")
        self.avatarIds.append(avId)
        self.b_setPopulation(self.getPopulation() + 1)

    def monitorAvatars(self, task):
        for avId in self.avatarIds:
            if not avId in self.air.doId2do.keys():
                self.notify.info("[" + str(time.strftime("%m-%d-%Y %H:%M:%S")) + "] " + str(avId) + " is leaving my district!")
                self.avatarIds.remove(avId)
                self.b_setPopulation(self.getPopulation() - 1)
        task.delayTime = 0.5
        return task.again

    def systemMessageCommand(self, accessLevel, message):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId, None)
        if av:
            if (accessLevel == av.getAccessLevel()):
                self.notify.info("Sending update 'systemMessage' with message: " + message)
                self.sendUpdate('systemMessage', [message])
        else:
            self.notify.info("Could not find the avatar that requested a system message...")

    def setAvailable(self, available):
        self.available = available

    def d_setAvailable(self, available):
        self.sendUpdate('setAvailable', [available])

    def b_setAvailable(self, available):
        self.d_setAvailable(available)
        self.setAvailable(available)

    def getAvailable(self):
        return self.available

    def delete(self):
        DistributedObjectAI.delete(self)
        del self.available
