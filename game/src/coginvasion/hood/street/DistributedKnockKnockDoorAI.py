"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedKnockKnockDoorAI.py
@author Maverick Liberty
@date October 22, 2017

"""

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.hood.street import KnockKnockGlobals

import random

class DistributedKnockKnockDoorAI(DistributedObjectAI):
    
    def __init__(self, air, zoneId, blockNumber, branchZoneId):
        DistributedObjectAI.__init__(self, air)
        self.zoneId = zoneId
        self.block = blockNumber
        self.branchZoneId = branchZoneId
        
        # The id of the avatar listening to our joke.
        self.listenerId = None
    
    def avatarDitched(self):
        avId = self.air.getAvatarIdFromSender()
        
        if avId == self.listenerId:
            self.listenerId = None
            self.sendUpdate('stopJoke', [])
    
    def requestJoke(self):
        avId = self.air.getAvatarIdFromSender()

        timestamp = globalClockDelta.getFrameNetworkTime()
        self.listenerId = avId
        self.sendUpdate('playJoke', [avId, timestamp])
        
    def iHeardPunchline(self):
        avId = self.air.getAvatarIdFromSender()
        
        if avId == self.listenerId:
            avatar = self.air.doId2do.get(avId, None)
            data = KnockKnockGlobals.Zone2EntertainmentData.get(self.branchZoneId)
            chance = data[0]
            healRange = data[1]
            roll = random.randint(0, 100)
            laughterList = KnockKnockGlobals.Laughter
            
            if roll < chance and avatar.health < avatar.maxHealth:
                # Let's calculate how much to heal.
                heal = random.randint(healRange[0], healRange[1])
                laughterList = KnockKnockGlobals.HealedLaughter
                avatar.toonUp(heal)
                self.sendUpdate('avatarEntertained', [avId])
            msg = laughterList[random.randint(0, len(laughterList) - 1)] 
            base.taskMgr.doMethodLater(0.5, self.__showChatMessage, self.uniqueName('showChatMsg'), 
                extraArgs = [avatar, msg])
            
    def __showChatMessage(self, avatar, msg):
        avatar.d_setChat(msg)
            
    def playJoke(self, avId, timestamp):
        pass
    
    def stopJoke(self):
        pass
    
    def getData(self):
        return [self.zoneId, self.block]
