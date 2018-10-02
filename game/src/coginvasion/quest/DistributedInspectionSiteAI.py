"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedInspectionSiteAI.py
@author Maverick Liberty
@date September 18, 2017

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.quest import InspectionSites

class DistributedInspectionSiteAI(DistributedNodeAI):
    
    def __init__(self, air, siteId, zoneId):
        DistributedNodeAI.__init__(self, air)
        self.notify = directNotify.newCategory('DistributedInspectionSiteAI[%d]' % siteId)
        self.siteId = siteId
        self.zoneId = zoneId
        self.siteData = None
        
        # This is the id of the avatar currently using this site.
        self.currentAvatarId = None
        
    def setSiteId(self, _id):
        self.siteId = _id
        
    def getSiteId(self):
        return self.siteId
    
    def setZoneId(self, _id):
        self.zoneId = _id
        
    def getZoneId(self):
        return self.zoneId
    
    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        self.siteData = InspectionSites.getSiteById(self.zoneId, self.siteId)
        
        if self.siteData:
            position = self.siteData.inspectionLoc
            self.b_setPosHpr(position.getX(), position.getY(), position.getZ(), 0, 0, 0)
            
    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId, None)
        
        if self.currentAvatarId == None and avatar:
            data = avatar.questManager.getInspectionQuest()
            
            if data and not data[2].isComplete():
                # Let's verify that the user has an incomplete objective to inspect this site.
                self.currentAvatarId = avId
                self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
                return
            
        # There aren't any other circumstances where we should accept this user. Reject their entry.
        self.sendUpdateToAvatarId(avId, 'enterRejected', [])
        
    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId, None)
        
        if self.currentAvatarId == avId:
            # Great, this is the avatar we're working with! Let's stop working with them.
            self.currentAvatarId = None
            self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
            return
        
        self.notify.warning("Suspicious: Avatar we're not working with tried to request exit! AvId: {0}".format(avId))
        self.sendUpdateToAvatarId(avId, 'exitRejected', [])
