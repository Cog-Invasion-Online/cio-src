"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file InspectionSites.py
@author Maverick Liberty
@date March 20, 2017

"""

from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TransparencyAttrib

class InspectionSite:

    # Requires 4 arguments.
    # siteId - The id of the inspection site.
    # inspectionLoc - A Point3 or Vec3 where the actual position of the site is.
    # sphereScale - Either a single integer for radius or a tuple for Sz values.
    # zoneId - The zone this inspection is going on in.
    # OPTIONAL: mustHitHotKey - Does the user have to hit the inspection 
    # hotkey to complete this?
    def __init__(self, siteId, inspectionLoc, sphereScale, zoneId, 
            mustHitHotKey = True, buildMethod = None):
        self.siteId = siteId
        self.inspectionLoc = inspectionLoc
        self.sphereScale = sphereScale
        self.zoneId = zoneId
        self.mustHitHotKey = mustHitHotKey
        self.buildMethod = buildMethod
        
        # The ground icon below the prop (if there is a prop)
        self.groundIcon = None
        
        # This is the pos and hpr for where the ground icon is located.
        self.groundIconPosHpr = None
        
        # Variables for the hovering inspect location element
        
        # This is the pos and hpr for where the BillboardPointEye icon is located.
        self.identifyPosHpr = None
        
        # When to start showing the billboard icon. (number)
        self.identifyRange = 0
        
        # The actual DirectFrame with the icon
        self.identifierIcon = None
        
    def _generateInspectIcon(self):
        icon = loader.loadTexture('phase_3.5/maps/inspect_location.png')
        inspectIcon = DirectFrame(parent = render, image = icon, frameColor = (0, 0, 0, 0))
        inspectIcon.setTransparency(TransparencyAttrib.MAlpha)
        inspectIcon.setTwoSided(1)
        return inspectIcon

# Inspection site dictionary.
# Key: zoneId, Value: List of inspection sites.

sites = {
    2300 : [
        #InspectionSite(0, )
    ]
}

# Fetches a site in a specified zone by its id.
def getSiteById(zoneId, siteId):
    if zoneId in sites:
        for site in sites[zoneId]:
            if site.siteId == siteId:
                return site
    
    return None
