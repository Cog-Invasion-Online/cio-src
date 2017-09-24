"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedInspectionSiteAI.py
@author Maverick Liberty
@date 2017-09-18

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedInspectionSiteAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedInspectionSiteAI')
    
    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.siteId = 0
        
    def setSiteId(self, siteId):
        self.siteId = siteId
        
    def getSiteId(self):
        return self.siteId
