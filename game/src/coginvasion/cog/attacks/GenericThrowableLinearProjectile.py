"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GenericThrowableLinearProjectile.py
@author Maverick Liberty
@date April 5, 2019

Repeating code over and over sucks, I've created this class for all those boring, generic throw attacks Cogs have.
This will make our lives easier and our workspace cleaner.

"""

from panda3d.core import Point3

from src.coginvasion.attack.LinearProjectile import LinearProjectile

class GenericThrowableLinearProjectile(LinearProjectile):
    
    ThrowSoundPath = None
    
    def __init__(self, cr):
        LinearProjectile.__init__(self, cr)
        self.throwSound = None
        self.attackID = -1
        
    def setData(self, attackID):
        attackCls = base.attackMgr.getAttackClassByID(attackID)()
        
        if hasattr(attackCls, 'ThrowSoundPath'):
            self.ThrowSoundPath = attackCls.ThrowSoundPath
            
        if hasattr(attackCls, 'ImpactSoundPath'):
            self.ImpactSoundPath = attackCls.ImpactSoundPath
        
        if hasattr(attackCls, 'ModelPath'):
            self.ModelPath = attackCls.ModelPath
        
        if hasattr(attackCls, 'ModelScale'):
            self.ModelScale = attackCls.ModelScale
            
        if hasattr(attackCls, 'ModelAngles'):
            self.ModelAngles = attackCls.ModelAngles
        
        if hasattr(attackCls, 'ModelOrigin'):
            self.ModelOrigin = attackCls.ModelOrigin
            
    def getData(self):
        return self.attackID
    
    def announceGenerate(self):
        LinearProjectile.announceGenerate(self)

        if self.ThrowSoundPath and not self.throwSound:
            self.throwSound = base.loadSfxOnNode(self.ThrowSoundPath, self)
        if self.throwSound:  self.throwSound.play()

        vecEnd = Point3(*self.linearStart)
        vecStart = Point3(*self.linearEnd)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], 0, 0)

    def impact(self, _):
        if self.impactSound:
            base.audio3d.attachSoundToObject(self.impactSound, self)
            self.impactSound.play()
    
    def disable(self):
        if self.throwSound:
            base.audio3d.detachSound(self.throwSound)
        self.throwSound = None

        if self.impactSound:
            base.audio3d.detachSound(self.impactSound)
        self.impactSound = None

        LinearProjectile.disable(self)
    