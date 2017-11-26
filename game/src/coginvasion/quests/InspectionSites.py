"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file InspectionSites.py
@author Maverick Liberty
@date March 20, 2017

"""

from panda3d.core import Point3

class SiteType:
    INSPECT = 'inspect'
    DIG = 'dig'

class InspectionSite:

    # Requires 4 arguments.
    # siteId - The id of the inspection site.
    # inspectionLoc - A Point3 or Vec3 where the actual position of the site is.
    # sphereScale - Either a single integer for radius or a tuple for Sz values.
    # zoneId - The zone this inspection is going on in.
    # OPTIONAL: mustHitHotKey - Does the user have to hit the inspection 
    # hotkey to complete this?
    def __init__(self, siteId, inspectionLoc, sphereScale, zoneId, 
            _type = SiteType.INSPECT, mustHitHotKey = True, buildMethod = None):
        self.siteId = siteId
        self.inspectionLoc = inspectionLoc
        self.sphereScale = sphereScale
        self.zoneId = zoneId
        self.mustHitHotKey = mustHitHotKey
        self.buildMethod = buildMethod
        self.type = _type
        
        # The ground icon below the prop (if there is a prop)
        self.groundIcon = None
        
        # This is the pos and hpr for where the ground icon is located.
        self.groundIconPosHpr = None
        
        # Variables for the hovering inspect location element
        
        # This is the pos and hpr for where the BillboardPointEye icon is located.
        self.identifyPosHpr = None
        
        # When to start showing the billboard icon. (number)
        self.identifyRange = 0

# Inspection site dictionary.
# Key: zoneId, Value: List of inspection sites.

sites = {
    2000 : [
        InspectionSite(0, Point3(-3, 12, 0.01), 16, 2000, SiteType.DIG)
    ]
}

# Fetches a site in a specified zone by its id.
def getSiteById(zoneId, siteId):
    if zoneId in sites.keys():
        for site in sites.get(zoneId):
            if site.siteId == siteId:
                return site
    
    return None
