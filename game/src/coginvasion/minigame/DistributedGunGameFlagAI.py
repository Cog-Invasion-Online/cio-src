# Filename: DistributedGunGameFlagAI.py
# Created by:  blach (21Nov15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

import GunGameGlobals as GGG

class DistributedGunGameFlagAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedGunGameFlagAI')

    FLAG_DROPPED_TIME = 30.0

    def __init__(self, air, mg, team):
        DistributedNodeAI.__init__(self, air)
        self.mg = mg
        self.team = team
        self.flagPickedUp = False

    def getTeam(self):
        return self.team

    def requestPickup(self):
        avId = self.air.getAvatarIdFromSender()
        base.taskMgr.remove(self.uniqueName('dropTimeUp'))
        self.flagPickedUp = True
        self.sendUpdate('pickupFlag', [avId])

    def dropFlag(self, x, y, z):
        self.flagPickedUp = False
        base.taskMgr.doMethodLater(self.FLAG_DROPPED_TIME, self.__dropTimeUp, self.uniqueName('dropTimeUp'))

    def __dropTimeUp(self, task):
        if not self.flagPickedUp:
            self.sendUpdate('flagReturned')
            self.sendUpdate('placeAtMainPoint')
        return task.done

    def requestDropOff(self):
        if self.flagPickedUp:
            avId = self.air.getAvatarIdFromSender()
            self.sendUpdate('dropOffFlag', [avId])
            self.sendUpdate('placeAtMainPoint')
            if self.team == GGG.Teams.RED:
                teamScored = GGG.Teams.BLUE
            elif self.team == GGG.Teams.BLUE:
                teamScored = GGG.Teams.RED
            self.mg.teamScored(teamScored)

    def delete(self):
        base.taskMgr.remove(self.uniqueName('dropTimeUp'))
        del self.mg
        del self.team
        del self.flagPickedUp
        DistributedNodeAI.delete(self)
