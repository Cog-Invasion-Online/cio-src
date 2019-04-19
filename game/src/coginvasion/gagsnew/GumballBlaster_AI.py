from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta

from panda3d.core import Point3

from BaseHitscanAI import BaseHitscanAI
from src.coginvasion.attack.Attacks import ATTACK_GUMBALLBLASTER
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gagsnew.GumballProjectileAI import GumballProjectileAI
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.globals import CIGlobals

import random

class GumballBlaster_AI(BaseHitscanAI):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster

    FireDelay = 0.1
    AttackRange = 10000

    UsesAmmo = True
    HasClip = False

    FirePower = 300.0
    
    MIN_BURST_SIZE = 3
    MAX_BURST_SIZE = 15
    
    MIN_BURST_DELAY = 0.15
    MAX_BURST_DELAY = 0.30

    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateDraw: 0.7085,
                                   self.StateFire: 0.5417})
        self.ammo = 150
        self.maxAmmo = 150
        
        self.gumballsToFire = 0
        self.nextFireTime = 0.0
        self.target = None

        self.fireOrigin = Point3(0)

    def getBaseDamage(self):
        return 5

    def canUse(self):
        return self.hasAmmo() and self.action in [self.StateIdle, self.StateFire]

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.fireOrigin = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateFire)
        
    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.target = target
        self.setNextAction(self.StateFire)
        
    def calibrate(self, target):
        self.fireOrigin = self.avatar.getPos(render) + (0, 2.0, self.avatar.getHeight() / 2.0)
        self.traceOrigin = self.fireOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.fireOrigin).normalized()

    def onSetAction(self, action):
        self.nextFireTime = 0.0
        
        if action == self.StateFire:
            gumballs = 1
            
            if self.isAIUser():
                minGumballs = min(self.MIN_BURST_SIZE, self.getAmmo())
                maxGumballs = min(self.MAX_BURST_SIZE, self.getAmmo())
                gumballs = random.randint(minGumballs, maxGumballs)
                
                if (gumballs > self.getAmmo()):
                    gumballs = self.getAmmo()
            
            self.gumballsToFire = gumballs
        else:
            self.gumballsToFire = 0
            self.target = None
            
    def isActionComplete(self):
        if self.action == self.StateFire:
            return (self.gumballsToFire == 0 and BaseHitscanAI.isActionComplete(self))
        return BaseHitscanAI.isActionComplete(self)
    
    def think(self):
        BaseHitscanAI.think(self)
        
        if self.action == self.StateFire:
            
            if self.isAIUser():
                if CIGlobals.isNodePathOk(self.target):
                    self.avatar.headsUp(self.target)
                    self.calibrate(self.target)
                else: return
            
            if (self.gumballsToFire > 0 and globalClock.getFrameTime() >= self.nextFireTime):
            
                throwVector = PhysicsUtils.getThrowVector(self.traceOrigin,
                                                          self.traceVector,
                                                          self.fireOrigin,
                                                          self.avatar,
                                                          self.avatar.getBattleZone().getPhysicsWorld())

                endPos = CIGlobals.extrude(self.fireOrigin, self.FirePower, throwVector) - (0, 0, 90)
                
                if self.isAIUser():
                    endPos = endPos + Point3(random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5))
                
                self.takeAmmo(-1)
                self.fireProjectile(endPos)
                self.gumballsToFire = self.gumballsToFire - 1
                
                if (self.gumballsToFire > 0):
                    self.nextFireTime = globalClock.getFrameTime() + random.uniform(self.MIN_BURST_DELAY, self.MAX_BURST_DELAY)
                
    def fireProjectile(self, endPos):
        proj = GumballProjectileAI(base.air)
        proj.setProjectile(2.5, self.fireOrigin, endPos, 1.07, globalClockDelta.getFrameNetworkTime())
        proj.generateWithRequired(self.avatar.zoneId)
        proj.addHitCallback(self.onProjectileHit)
        proj.addExclusion(self.avatar)
            
    def checkCapable(self, dot, squaredDistance):
        return 10*10 <= squaredDistance <= 30*30
    
    def isAIUser(self):
        isAI = False
        
        try:
            from src.coginvasion.szboss.DistributedSZBossToonAI import DistributedSZBossToonAI
            isAI = isinstance(self.avatar, DistributedSZBossToonAI)
        except: pass
        
        return isAI
    
    def cleanup(self):
        del self.gumballsToFire
        del self.nextFireTime
        if self.target:
            self.target = None
        del self.target
        del self.fireOrigin
        BaseHitscanAI.cleanup(self)
