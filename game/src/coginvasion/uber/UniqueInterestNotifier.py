"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file UniqueInterestNotifier.py
@author Maverick Liberty
@date 30-09-17

"""

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class UniqueInterestNotifier(DistributedObjectGlobal):
    notify = directNotify.newCategory('UniqueInterestNotifier')
    
    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.interests = set()
        
    def acknowledgeInterestIn(self, doId):
        if not doId in self.interests:
            self.sendUpdate('acknowledgeInterestIn', [doId])

    def addChannelInterest(self, doChannelId, avId):
        if base.localAvatar.doId == avId:
            self.interests.add(doChannelId)
            
    def removeChannelInterest(self, doChannelId, avId):
        if base.localAvatar.doId == avId and doChannelId in self.interests:
            self.interests.remove(doChannelId)
            
    def message(self, doChannelId, msgId, msg):
        self.notify.info('Channel %d has sent message of ID %d: %s' % (doChannelId, msgId, msg))
