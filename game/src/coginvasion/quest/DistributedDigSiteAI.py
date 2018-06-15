"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDigSiteAI.py
@author Maverick Liberty
@date November 25, 2017

"""

from src.coginvasion.quest.DistributedInspectionSiteAI import DistributedInspectionSiteAI

class DistributedDigSiteAI(DistributedInspectionSiteAI):
    
    def __init__(self, air, siteId, zoneId):
        DistributedInspectionSiteAI.__init__(self, air, siteId, zoneId)
