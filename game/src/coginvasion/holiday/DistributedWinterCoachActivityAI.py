"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedWinterCoachActivityAI.py
@author Maverick Liberty
@date November 14, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedWinterCoachActivityAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedWinterCoachActivityAI')
    
    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        
    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
        self.sendUpdate('greetAvatar', [avatar.getName()])
        
    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'exitAccepted', [])