# Filename: DistributedTutorialAI.py
# Created by:  blach (16Oct15)

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog import SuitBank, Variant
import DistributedTutorialSuitAI

class DistributedTutorialAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedTutorialAI')
    notify.setInfo(True)

    def __init__(self, air, avatarId):
        DistributedObjectAI.__init__(self, air)
        self.avatarId = avatarId
        self.av = self.air.doId2do.get(self.avatarId)
        self.tutSuit = None

    def makeSuit(self, index):
        plan = SuitBank.Flunky
        level = 1
        variant = Variant.NORMAL
        suit = DistributedTutorialSuitAI.DistributedTutorialSuitAI(self.air, index, self, self.avatarId)
        suit.generateWithRequired(self.zoneId)
        suit.b_setLevel(level)
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        suit.b_setName(plan.getName())
        suit.b_setParent(CIGlobals.SPHidden)
        self.tutSuit = suit

    def finishedTutorial(self):
        self.notify.info('Deleting tutorial: avatar finished')
        self.av.b_setTutorialCompleted(1)
        self.requestDelete()

    def __monitorAvatar(self, task):
        if not self.avatarId in self.air.doId2do.keys():
            self.notify.info('Deleting tutorial: avatar logged out')
            self.requestDelete()
            return task.done
        return task.cont

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        base.taskMgr.add(self.__monitorAvatar, self.uniqueName('monitorAvatar'))

    def delete(self):
        base.taskMgr.remove(self.uniqueName('monitorAvatar'))
        self.avatarId = None
        self.av = None
        if self.tutSuit:
            self.tutSuit.disable()
            self.tutSuit.requestDelete()
            self.tutSuit = None
        DistributedObjectAI.delete(self)
