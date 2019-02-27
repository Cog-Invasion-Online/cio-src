"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDroppableCollectableJellybeanAI.py
@author Brian Lach
@date March 22, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeansAI import DistributedDroppableCollectableJellybeansAI

class DistributedDroppableCollectableJellybeanAI(DistributedDroppableCollectableJellybeansAI):
    notify = directNotify.newCategory("DistributedDroppableCollectableJellybeanAI")
    
    def __init__(self, air):
        DistributedDroppableCollectableJellybeansAI.__init__(self, air)
        self.collector = None
        
    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.collector:
            self.collector = avId
            self.sendUpdate('handlePickup', [avId])