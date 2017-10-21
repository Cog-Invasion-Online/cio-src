"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedInspectionSite.py
@author Maverick Liberty
@date March 20, 2017

"""

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import NodePath
from panda3d.core import CollisionNode, CollisionSphere, BitMask32

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quests import InspectionSites

class DistributedInspectionSite(DistributedNode):
    notify = directNotify.newCategory('DistributedInspectionSite')
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'inspection_site')
        self.collSphereNP = None
        self.collSphere = None
        self.identifierIcon = None
        self.identifyPosHpr = None
        self.siteId = 0
        self.siteData = None
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.siteData = InspectionSites.getSiteById(self.zoneId, self.siteId)
        position = self.siteData.inspectionLoc
        print 'HELLO!'
        print self.zoneId
        print self.siteId
        
        #try:
        radius = self.siteData.sphereScale if isinstance(self.siteData.sphereScale, int) else 1
        self.collSphere = CollisionSphere(position.getX(), position.getY(), position.getZ(), radius)
        self.collSphere.setTangible(0)
        sphereSensor = CollisionNode('inspectionSensor')
        sphereSensor.addSolid(self.collSphere)
        sphereSensor.setIntoCollideMask(CIGlobals.WallBitmask)
        
        self.collSphereNP = self.attachNewNode(sphereSensor)
        self.collSphereNP.setCollideMask(BitMask32(0))
        self.collSphereNP.show()
        
        if isinstance(self.siteData.sphereScale, tuple):
            scaling = list(self.siteData.sphereScale)
            self.collSphereNP.setSx(scaling[0])
            self.collSphereNP.setSy(scaling[1])
            self.collSphereNP.setSz(scaling[2])
            
        self.accept('enter' + self.collSphereNP.getName(), self.__handleCollision)
        self.identifyPosHpr = (position.getX(), position.getY(), position.getZ() + 2.0)
        self.generateIdentifierIcon(None)
        print 'Hey now, brown cow!'
        #except Exception:
            #self.notify.info('Could not generate InspectionSite for site %d in zoneId %d because data could not be obtained.'
            #% (self.siteId, self.zoneId))

    def generateIdentifierIcon(self, parent):
        self.identifierIcon = self.siteData._generateInspectIcon()
        self.identifierIcon.setBillboardPointEye()
        self.identifierIcon.setPosHpr(0.492697, 11.4054, 0.5, 0, 0, 0)
        
    def __handleCollision(self, coll):
        pass
        
    def setSiteId(self, siteId):
        self.siteId = siteId
        
    def getSiteId(self):
        return self.siteId
 
    def disable(self):
        DistributedNode.disable(self)
        self.ignoreAll()
        
    def delete(self):
        if self.collSphereNP:
            self.collSphereNP.removeNode()
            self.collSphereNP = None
            self.collSphere = None
        del self.collSphereNP
        del self.collSphere
        DistributedNode.delete(self)
