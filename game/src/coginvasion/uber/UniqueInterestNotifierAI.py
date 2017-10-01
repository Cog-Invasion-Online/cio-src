"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file UniqueInterestNotifierAI.py
@author Maverick Liberty
@date 30-09-17

"""

from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

class UniqueInterestNotifierAI(DistributedObjectGlobalAI):
    
    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)
        self.msgChannels = {}
        
    def notifyListeners(self, doChannelId, msgId, msg):
        if doChannelId in self.msgChannels.keys():
            self.sendUpdate('sendMessageToListeners', [doChannelId, msgId, msg])
        
    def addChannelInterest(self, doChannelId, avId):
        if not doChannelId in self.msgChannels.keys():
            self.msgChannels[doChannelId] = set(avId)
        else:
            self.msgChannels[doChannelId].add(avId)
            
    def d_addChannelInterest(self, doChannelId, avId):
        self.sendUpdate('addChannelInterest', [doChannelId, avId])
            
    def b_addChannelInterest(self, doChannelId, avId):
        self.addChannelInterest(doChannelId, avId)
        self.d_addChannelInterest(doChannelId, avId)
            
    def removeChannelInterest(self, doChannelId, avId):
        if doChannelId in self.msgChannels.keys():
            try:
                self.msgChannels[doChannelId].remove(avId)
            except KeyError:
                # We tried to remove interest when the avId isn't in the set.
                pass

    def d_removeChannelInterest(self, doChannelId, avId):
        self.sendUpdate('removeChannelInterest', [doChannelId, avId])
            
    def b_removeChannelInterest(self, doChannelId, avId):
        self.removeChannelInterest(doChannelId, avId)
        self.d_removeChannelInterest(doChannelId, avId)
    
    def isInterestedIn(self, doChannelId, avId):
        if doChannelId in self.msgChannels.keys():
            return avId in self.msgChannels[doChannelId]
        return False
