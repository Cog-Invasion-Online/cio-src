"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBRPondAI.py
@author Maverick Liberty
@date March 1, 2018
@desc Distributed version of the BRWater.py system that Brian Lach made a couple years ago.

"""

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

class DistributedBRPondAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBRPondAI')
    
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        
        # A dictionary containing the last states of avatar ids.
        # Format: {avId : [last state id, timestamp]}
        self.lastStates = {}
    
    def requestState(self, stateId):
        """ This message originates from a client asking to broadcast a state to everyone """
        avId = self.air.getAvatarIdFromSender()
        lastStateId, ts = self.__getLastStateData(avId)
        
        if avId not in self.lastStates.keys():
            avatar = self.air.doId2do.get(avId, None)
            if avatar:
                self.acceptOnce(avatar.getDeleteEvent(), self.__forgetStateData, [avId])
        
        # Let's set the last state id to the new one.
        self.__setLastStateId(avId, stateId)
        
        # Let's broadcast the message to everyone!
        self.sendUpdate('processStateRequest', [avId, stateId, lastStateId, ts])
        
    def requestAvatarStates(self):
        """ This message originates from a client and it simply asks the AI to send the state of all frozen toons """
        requesterId = self.air.getAvatarIdFromSender()
        for avId, stateData in self.lastStates.iteritems():
            if stateData[0] != 5:
                self.sendUpdateToAvatarId(requesterId, 'processStateRequest', [avId, 
                    stateData[0], stateData[0], stateData[1]])
        
    def __setLastStateId(self, avId, stateId):
        if stateId != 6:
            ts = globalClockDelta.getFrameNetworkTime()
            # Let's set the last state id to the new one.
            self.lastStates.update({avId : [stateId, ts]})
        else:
            # We don't need to keep tracking the avatar's last state once they reach the final one.
            del self.lastStates[avId]
            
    def __getLastStateId(self, avId):
        if avId in self.lastStates.keys():
            return self.lastStates[avId][0]
        return 5
    
    def __getLastStateData(self, avId):
        if avId in self.lastStates.keys():
            data = self.lastStates[avId]
            return data[0], data[1]
        # 5 is not a state, it's just a random out of range number meaning that
        # there isn't a last state.
        return 5, 0
    
    def __forgetStateData(self, avId):
        """ When an avatar leaves BR, we need to clear their state data in the pond. """
        lastStateId = self.__getLastStateId(avId)
        if avId in self.lastStates.keys():
            del self.lastStates[avId]
        self.sendUpdate('processStateRequest', [avId, 5, lastStateId, 0])
