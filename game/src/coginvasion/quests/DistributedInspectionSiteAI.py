"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedInspectionSiteAI.py
@author Maverick Liberty
@date September 18, 2017

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.quests import InspectionSites

class DistributedInspectionSiteAI(DistributedNodeAI):
    
    def __init__(self, air, siteId, zoneId):
        DistributedNodeAI.__init__(self, air)
        self.notify = directNotify.newCategory('DistributedInspectionSiteAI[%d]' % siteId)
        self.siteId = siteId
        self.zoneId = zoneId
        self.siteData = None
        
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
