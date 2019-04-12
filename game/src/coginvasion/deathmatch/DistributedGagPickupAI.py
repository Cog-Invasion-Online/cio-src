"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagPickupAI.py
@author Brian Lach
@date April 11, 2019

"""

from src.coginvasion.gags import GagGlobals
from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

import random

class DistributedGagPickupAI(DistributedEntityAI):

    RespawnMin = 10.0
    RespawnMax = 20.0

    Pickups = GagGlobals.tempAllowedGags

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.pickupState = 1
        self.gagId = self.__pickGagId()

    def __pickGagId(self):
        gagName = random.choice(self.Pickups)
        gagId = base.attackMgr.getAttackIDByName(gagName)
        return gagId

    def delete(self):
        taskMgr.remove(self.taskName("doRespawn"))
        self.pickupState = None
        self.gagId = None
        DistributedEntityAI.delete(self)

    def setPickupState(self, state):
        self.pickupState = state

    def b_setPickupState(self, state):
        self.sendUpdate('setPickupState', [state])
        self.setPickupState(state)

    def getPickupState(self):
        return self.pickupState

    def setGagId(self, gagId):
        self.gagId = gagId

    def b_setGagId(self, gagId):
        self.sendUpdate('setGagId', [gagId])
        self.setGagId(gagId)

    def getGagId(self):
        return self.gagId

    def onPickup(self):
        self.b_setPickupState(0)
        taskMgr.doMethodLater(random.uniform(self.RespawnMin, self.RespawnMax),
                              self.__doRespawnTask, self.taskName("doRespawn"))

    def __doRespawnTask(self, task):
        self.b_setGagId(self.__pickGagId())
        self.b_setPickupState(1)
        return task.done

    def requestPickup(self):
        if not self.pickupState:
            return

        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if avatar:
            currAttacks = avatar.getAttackIds()
            if not avatar.hasAttackId(self.gagId):
                # Add to arsenal
                avatar.b_setAttackIds(currAttacks + [self.gagId])
                avatar.b_setEquippedAttack(self.gagId)
            else:
                # Already have it, refill ammo
                attack = avatar.getAttack(self.gagId)
                if not attack.isAmmoFull():
                    attack.setAmmo(attack.getMaxAmmo())
                    attack.d_updateAttackAmmo()
            self.sendUpdateToAvatarId(avId, 'pickupAccepted', [])

            self.onPickup()
