"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedRestockBarrel.py
@author Maverick Liberty
@date February 28, 2016

"""

from pandac.PandaModules import CollisionSphere, CollisionNode, NodePath

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval, Func

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals

class DistributedRestockBarrel(DistributedNode):
    notify = directNotify.newCategory('DistributedRestockBarrel')
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'restock_barrel')
        self.grabSfx = None
        self.rejectSfx = None
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.animTrack = None
        self.barrelScale = 0.5
        self.sphereRadius = 3.2
        self.playSoundForRemoteToons = 1
        self.barrel = None
        self.gagNode = None
        self.gagModel = None
        
        # Collision nodes
        self.collSphere = None
        self.collNode = None
        self.collNodePath = None
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.build()
        
        # Build collisions
        self.collSphere = CollisionSphere(0, 0, 0, self.sphereRadius)
        self.collSphere.setTangible(0)
        self.collNode = CollisionNode(self.uniqueName('barrelSphere'))
        self.collNode.setIntoCollideMask(CIGlobals.WallBitmask)
        self.collNode.addSolid(self.collSphere)
        self.collNodePath = self.attachNewNode(self.collNode)
        self.collNodePath.hide()
        self.accept('enter' + self.collNodePath.getName(), self.__handleCollision)
        
        self.setParent(CIGlobals.SPRender)
        
    def disable(self):
        DistributedNode.disable(self)
        self.ignoreAll()
        
        if self.animTrack:
            self.animTrack.pause()
            self.animTrack = None
        return
    
    def delete(self):
        self.gagNode.removeNode()
        self.barrel.removeNode()
        del self.barrel
        del self.gagNode
        del self.grabSfx
        del self.rejectSfx
        del self.grabSoundPath
        del self.rejectSoundPath
        del self.animTrack
        del self.barrelScale
        del self.sphereRadius
        del self.playSoundForRemoteToons
        del self.gagModel
        del self.collNode
        del self.collNodePath
        del self.collSphere
        DistributedNode.delete(self)
        
    def setLabel(self, labelId):
        if labelId == 0:
            self.gagModel = loader.loadModel('phase_4/models/props/icecream.bam')
            self.gagModel.reparentTo(self.gagNode)
            self.gagModel.find('**/p1_2').clearBillboard()
            self.gagModel.setScale(0.6)
            self.gagModel.setPos(0, -0.1, -0.1 - 0.6)
        elif labelId == 1:
            purchaseModels = loader.loadModel('phase_4/models/gui/purchase_gui.bam')
            self.gagModel = purchaseModels.find('**/Jar')
            self.gagModel.reparentTo(self.gagNode)
            self.gagModel.setScale(3.0)
            self.gagModel.setPos(0, -0.1, 0)
            purchaseModels.removeNode()
        else:
            gagId = labelId - 2
            iconName = GagGlobals.InventoryIconByName.get(GagGlobals.getGagByID(gagId))
            invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam').find('**/%s' % iconName)
            if invModel:
                self.gagModel = invModel
                self.gagModel.reparentTo(self.gagNode)
                self.gagModel.setScale(13.0)
                self.gagModel.setPos(0, -0.1, 0)
            else:
                self.notify.warning('Failed to find gag label %s.' % (str(labelId)))
        
    def __handleCollision(self, entry = None):
        self.sendUpdate('requestGrab', [])
        
    def setGrab(self, avId):
        local = (avId == base.localAvatar.getDoId())
        if local:
            self.ignore(self.uniqueName('enterbarrelSphere'))
            self.barrel.setColorScale(0.5, 0.5, 0.5, 1)
        if self.playSoundForRemoteToons or local:
            base.playSfx(self.grabSfx)
        if self.animTrack:
            self.animTrack.finish()
            self.animTrack = None
        self.animTrack = Sequence(LerpScaleInterval(self.barrel, 0.2, 1.1 * self.barrelScale, blendType='easeInOut'), LerpScaleInterval(self.barrel, 0.2, self.barrelScale, blendType='easeInOut'), Func(self.reset), name=self.uniqueName('animTrack'))
        self.animTrack.start()
        
    def setReject(self):
        base.playSfx(self.rejectSfx)
        self.notify.warning('Pickup rejected.')
        
    def build(self):
        self.grabSfx = base.loadSfx(self.grabSoundPath)
        self.rejectSfx = base.loadSfx(self.rejectSoundPath)
        self.barrel = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
        self.barrel.setScale(self.barrelScale)
        self.barrel.reparentTo(self)
        
        # Set the label background color.
        lblBg = self.barrel.find('**/gagLabelDCS')
        lblBg.setColor(0.15, 0.15, 0.1)
        
        self.gagNode = self.barrel.attachNewNode('gagNode')
        self.gagNode.setPosHpr(0.0, -2.62, 4.0, 0, 0, 0)
        self.gagNode.setColorScale(0.7, 0.7, 0.6, 1)
        
    def reset(self):
        self.barrel.setScale(self.barrelScale)
        self.accept(self.uniqueName('enterbarrelSphere'), self.__handleCollision)
        