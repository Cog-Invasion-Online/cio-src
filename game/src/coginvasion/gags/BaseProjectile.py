from panda3d.core import NodePath, VBase4
from panda3d.bullet import BulletGhostNode, BulletSphereShape, BulletClosestHitSweepResult

from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.globals import CIGlobals

import math

class BaseProjectile(WorldCollider):
    Radius = 0.3
    MaxDistance = 1024.0 / 16.0
    MaxTravel = 500.0
    BaseDamage = 20
    Name = 'projectile'
    HitSoundFile = 'phase_3/audio/sfx/null.ogg'

    def __init__(self, local = False):
        WorldCollider.__init__(self, self.Name, self.Radius,
                               resultInArgs = True, useSweep = True,
                               startNow = False)
        
        self.local = local
        
        self.maxTravelSqr = self.MaxTravel * self.MaxTravel

        self.checkCollTask = None
        self.hitSound = base.audio3d.loadSfx(self.HitSoundFile)
        base.audio3d.attachSoundToObject(self.hitSound, self)

    def removeNode(self):
        self.hitSound = None
        self.initialPos = None
        if self.checkCollTask:
            taskMgr.remove(self.checkCollTask)
            self.checkCollTask = None
        WorldCollider.removeNode(self)

    def addToWorld(self, initialPos = None, initialAngles = None, lookAt = None, velo = None):
        self.reparentTo(render)

        if initialPos:
            self.setPos(initialPos)
        if initialAngles:
            self.setHpr(initialAngles)
        if lookAt:
            self.lookAt(lookAt)
        self.initialPos = self.getPos(render)
        
        self.velo = velo

        self.start()

    def calcDamage(self, distance):
        return CIGlobals.calcAttackDamage(distance, self.BaseDamage, self.MaxDistance)

    def onHit(self, pos, intoNP):
        self.hitSound.play()
        
    def onCollide(self, contact, intoNP):
        if isinstance(contact, BulletClosestHitSweepResult):
            pos = contact.getHitPos()
        else:
            pos = self.getPos(render)
        self.onHit(pos, intoNP)
        
    def tick(self, task):
        if self.isEmpty():
            return task.done
        
        pos = self.getPos(render)
        dist = (pos - self.initialPos).lengthSquared()
        if dist > self.maxTravelSqr:
            print "Stopping at distance {0}, squared {1}".format(math.sqrt(dist), dist)
            # Oh well, didn't hit anything
            self.removeNode()
            return task.done
        
        dt = globalClock.getDt()
        
        if self.velo is not None:
            self.setPos(render, pos + self.getQuat(render).xform(self.velo * dt))
            
        return WorldCollider.tick(self, task)
