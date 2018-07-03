"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TossTrapGag.py
@author Maverick Liberty
@date July 24, 2015

"""

from src.coginvasion.gags.TrapGag import TrapGag
from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.CIParticleEffect import CIParticleEffect
from direct.interval.IntervalGlobal import ProjectileInterval
from panda3d.core import NodePath, BitMask32, CollisionSphere, CollisionNode, CollisionHandlerEvent

class TossTrapGag(TrapGag):

    def __init__(self, name, model, damage, hitSfx, idleSfx = None, particlesFx = None, anim = None, wantParticles = True):
        TrapGag.__init__(self, name, model, damage, hitSfx, anim)
        self.wantParticles = wantParticles
        self.particles = None
        self.particlesFx = particlesFx
        self.idleSfx = None
        self.timeout = 5.0

        if game.process == 'client':
            if idleSfx:
                self.idleSfx = base.audio3d.loadSfx(idleSfx)

    def startTrap(self):
        TrapGag.startTrap(self)
        if not self.gag:
            self.build()
            self.setHandJoint()
        self.gag.reparentTo(self.handJoint)
        self.avatar.play('toss', fromFrame = 22)

    def build(self):
        self.buildParticles()
        self.setHandJoint()
        return TrapGag.build(self)

    def buildParticles(self):
        self.cleanupParticles()
        if hasattr(self, 'wantParticles') and hasattr(self, 'particlesFx'):
            if self.wantParticles and self.particlesFx:
                self.particles = CIParticleEffect()
                self.particles.loadConfig(self.particlesFx)

    def buildCollisions(self):
        TrapGag.buildCollisions(self)
        gagSph = CollisionSphere(0, 0, 0, 1)
        gagSph.setTangible(0)
        gagNode = CollisionNode('gagSensor')
        gagNode.addSolid(gagSph)
        gagNP = self.entity.attachNewNode(gagNode)
        gagNP.setScale(0.75, 0.8, 0.75)
        gagNP.setPos(0.0, 0.1, 0.5)
        gagNP.setCollideMask(BitMask32.bit(0))
        gagNP.node().setFromCollideMask(CIGlobals.FloorBitmask)

        event = CollisionHandlerEvent()
        event.setInPattern("%fn-into")
        event.setOutPattern("%fn-out")
        base.cTrav.addCollider(gagNP, event)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def onCollision(self, entry):
        TrapGag.onCollision(self, entry)
        x, y, z = self.entity.getPos(render)
        base.localAvatar.sendUpdate('setGagPos', [self.getID(), x, y, z])

    def release(self):
        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.avatar)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, 160, -120)
        throwPath.setHpr(0, 90, 0)

        if not self.gag:
            self.build()
            
        self.entity = self.gag
        self.gag = None
        self.entity.wrtReparentTo(render)
        self.entity.setHpr(throwPath.getHpr(render))

        self.setHandJoint()
        self.track = ProjectileInterval(self.entity, startPos = self.handJoint.getPos(render), endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        self.track.start()
        
        if self.isLocal():
            self.startTimeout()
            self.buildCollisions()
            self.avatar.acceptOnce('gagSensor-into', self.onCollision)
        
        self.reset()
        TrapGag.release(self)

    def delete(self):
        TrapGag.delete(self)
        self.cleanupParticles()

    def unEquip(self):
        TrapGag.unEquip(self)
        self.cleanupParticles()

    def cleanupParticles(self):
        if self.particles:
            self.particles.cleanup()
            self.particles = None
