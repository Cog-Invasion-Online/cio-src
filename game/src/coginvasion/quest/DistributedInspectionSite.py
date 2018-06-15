"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedInspectionSite.py
@author Maverick Liberty
@date March 20, 2017

"""

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify

from direct.interval.IntervalGlobal import Sequence, LerpPosInterval
from direct.gui.DirectGui import DirectFrame, OnscreenText

from panda3d.core import TransparencyAttrib, CardMaker
from panda3d.core import CollisionNode, CollisionSphere

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quest import InspectionSites

class DistributedInspectionSite(DistributedNode):
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        
        #######################################################
        # The below attributes are required at generation time.
        #######################################################
        # The site id is the unique id associated with the data
        # for the inspection site.
        #######################################################
        self.siteId = -1
        self.zoneId = -1
        #######################################################
        self.siteData = None
        
        self.distanceTask = None
        self.interactCollSphereNP = None
        self.interactCollSphere = None
        self.identifierIcon = None
        self.floorMarker = None
        
        self.iconSequence = None
        self.fadeSequence = None
        self.text = None
        
    def setSiteId(self, _id):
        self.siteId = _id
    
    def getSiteId(self):
        return self.siteId
    
    def setZoneId(self, _id):
        self.zoneId = _id
        
    def getZoneId(self):
        return self.zoneId
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.setName('InspectionSite-%d' % self.siteId)
        self.notify = directNotify.newCategory('DistributedInspectionSite[%d]' % self.siteId)
        self.siteData = InspectionSites.getSiteById(self.zoneId, self.siteId)
        
        if self.siteData:
            interactKey = base.inputStore.Interact.upper()
            self.text = OnscreenText(
                text = 'Press \'%s\' to %s' % (interactKey, self.siteData.type),
                pos = (0, -0.75), font = CIGlobals.getToonFont(), fg = (1, 1, 1, 1),
                shadow = (0, 0, 0, 1)
            )
            self.text.hide()
            self.distanceTask = base.taskMgr.add(self.__calculateDistance, self.uniqueName('calculateAvDistance'))
            self.generateCollision()
            self.generateIconAndMarker()
            self.accept('enter' + self.interactCollSphereNP.getName(), self.onEnter)
            self.accept('exit' + self.interactCollSphereNP.getName(), self.onExit)
        self.reparentTo(render)
        
    def __calculateDistance(self, task):
        dist = float(base.localAvatar.getPos(self).length())
        fullAlphaDist = 15.0
        noAlphaDist = 105.0
        alpha = 1.0
        
        if 10 < dist < noAlphaDist:
            alpha = float(fullAlphaDist / dist)
            if alpha < 0.0:
                alpha = 0.0
        elif dist >= noAlphaDist:
            alpha = 0.0
            
        self.identifierIcon.setColorScale(1.0, 1.0, 1.0, alpha)
        self.floorMarker.setColorScale(1.0, 1.0, 1.0, alpha)
        return task.cont
        
    def generateCollision(self):
        self.interactCollSphere = CollisionSphere(0, 0, 0, 4)
        self.interactCollSphere.setTangible(0)
        ss = CollisionNode('inspectionSensor')
        ss.addSolid(self.interactCollSphere)
        
        self.interactCollSphereNP = self.attachNewNode(ss)
        self.interactCollSphereNP.setCollideMask(CIGlobals.EventBitmask)

    def generateIconAndMarker(self):
        icon = loader.loadTexture('phase_5/maps/inspect_location.png')
        self.identifierIcon = DirectFrame(parent = self, image = icon, frameColor = (0, 0, 0, 0))
        self.identifierIcon.setTransparency(TransparencyAttrib.MAlpha)
        self.identifierIcon.setTwoSided(1)
        self.identifierIcon.setBillboardPointEye()
        self.identifierIcon.setZ(2.0)
        
        self.iconSequence = Sequence(
            LerpPosInterval(self.identifierIcon, 1.0, pos = (0, 0, 6.0), startPos = (0, 0, 3.0),
                blendType = 'easeInOut', name = ('inspSite%d-in' % self.siteId)),
            LerpPosInterval(self.identifierIcon, 1.0, pos = (0, 0, 3.0), startPos = (0, 0, 6.0),
                blendType = 'easeInOut', name = ('inspSite%d-out' % self.siteId))
        )
        
        self.iconSequence.loop()
        
        cm = CardMaker('marker')
        self.floorMarker = self.attachNewNode(cm.generate())
        self.floorMarker.setTexture(icon)
        self.floorMarker.setTransparency(TransparencyAttrib.MAlpha)
        self.floorMarker.setTwoSided(1)
        self.floorMarker.setPosHpr(-2.50, 2.53, -0.01, 0.0, 90.0, 0.0)
        self.floorMarker.setScale(5.0)
        
    def requestEnter(self):
        pass
    
    def canEnter(self):
        place = base.cr.playGame.getPlace()
        return place and place.fsm.getCurrentState().getName() == 'walk'
        
    def onEnter(self, _):
        self.text.show()
        self.acceptOnce(base.inputStore.Interact, self.requestEnter)
        
    def onExit(self, _):
        self.text.hide()
        self.ignore(base.inputStore.Interact)

    def disable(self):
        DistributedNode.disable(self)
        base.taskMgr.remove(self.distanceTask)
        if self.iconSequence:
            self.iconSequence.finish()
            self.iconSequence = None
        if self.fadeSequence:
            self.fadeSequence.finish()
            self.fadeSequence = None
        if self.text:
            self.text.hide()

        self.ignoreAll()
        
    def delete(self):
        if self.siteData:
            self.siteData = None
        if self.identifierIcon:
            self.identifierIcon.destroy()
            self.identifierIcon = None
        if self.distanceTask:
            self.distanceTask = None
        if self.interactCollSphereNP:
            self.interactCollSphereNP.removeNode()
            self.interactCollSphereNP = None
            self.interactCollSphere = None
        if self.floorMarker:
            self.floorMarker.removeNode()
            self.floorMarker = None
        if self.text:
            self.text.hide()
            self.text.destroy()
            self.text = None
        del self.siteData
        del self.identifierIcon
        del self.distanceTask
        del self.interactCollSphereNP
        del self.interactCollSphere
        del self.floorMarker
        del self.text
        DistributedNode.delete(self)
