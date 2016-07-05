# Filename: DistributedDroppableCollectableBackpackAI.py
# Created by:  blach (22Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task

from DistributedDroppableCollectableObjectAI import DistributedDroppableCollectableObjectAI
from lib.coginvasion.gags.backpack.Backpack import Backpack
from lib.coginvasion.gags import GagGlobals

class DistributedDroppableCollectableBackpackAI(DistributedDroppableCollectableObjectAI):
    notify = directNotify.newCategory("DistributedDroppableCollectableBackpackAI")

    TimeActive = 90.0

    def __init__(self, air):
        try:
            self.DistributedDroppableCollectableBackpackAI_initialized
            return
        except:
            self.DistributedDroppableCollectableBackpackAI_initialized = 1
        DistributedDroppableCollectableObjectAI.__init__(self, air)
        self.bp = []
        self.bpAmmo = []

    def delete(self):
        self.stopTimer()
        self.bp = None
        self.bpAmmo = None
        DistributedDroppableCollectableObjectAI.delete(self)

    def startTimer(self):
        base.taskMgr.doMethodLater(self.TimeActive, self.__timeUp, self.uniqueName('DDCBAI.timeUp'))

    def __timeUp(self, task):
        self.requestDelete()
        return Task.done

    def stopTimer(self):
        base.taskMgr.remove(self.uniqueName('DDCBAI.timeUp'))

    def setBP(self, bp):
        self.bp = bp
        self.bpAmmo = []
        for i in range(4):
            name = GagGlobals.gagIds[self.bp[i]]
            self.bpAmmo.append(Backpack.amounts.get(name))

    def d_setBP(self, bp):
        self.sendUpdate('setBP', [bp])

    def b_setBP(self, bp):
        self.d_setBP(bp)
        self.setBP(bp)

    def getBP(self):
        return self.bp

    def getBPAmmo(self):
        return self.bpAmmo

    def collectedObject(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av:
            av.b_setBackpackAmmo(self.getBP(), self.getBPAmmo())
        DistributedDroppableCollectableObjectAI.collectedObject(self)
