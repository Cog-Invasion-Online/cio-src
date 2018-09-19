from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from DistributedEntityAI import DistributedEntityAI
from src.coginvasion.gags import GagGlobals

from GoonAI import GoonAI, GBSleep, GBPatrol

class DistributedGoonAI(DistributedEntityAI, DistributedAvatarAI):

    StartsAsleep = 1

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedAvatarAI.__init__(self, air)
        self.brain = None
        self.spawnflags = 0
        
        self.health = 25
        self.maxHealth = 25

    def d_doDetectStuff(self):
        self.sendUpdate('doDetectStuff')

    def d_doUndetectGlow(self):
        self.sendUpdate('doUndetectGlow')

    def d_shoot(self, targetId):
        self.sendUpdate('shoot', [targetId])

    def d_watchTarget(self, targetId):
        self.sendUpdate('watchTarget', [targetId])

    def d_stopWatchingTarget(self):
        self.sendUpdate('stopWatchingTarget')

    def d_wakeup(self):
        self.sendUpdate('wakeup')

    def d_doIdle(self):
        self.sendUpdate('doIdle')

    def d_doAsleep(self):
        self.sendUpdate('doAsleep')

    def d_stopIdle(self):
        self.sendUpdate('stopIdle')

    def d_doScan(self):
        self.sendUpdate('doScan')
        
    def d_doRagdollMode(self):
        self.sendUpdate('doRagdollMode')

    def d_doMoveTrack(self, path, turnToFirstWP = True, speed = 3.0, doWalkAnims = True):
        self.sendUpdate('doMoveTrack', [path, turnToFirstWP, speed, doWalkAnims])
        
    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        DistributedEntityAI.announceGenerate(self)
        
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles() - (180, 0, 0))
        pos = self.getPos()
        hpr = self.getHpr()
        self.d_setPosHpr(pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
        
        self.brain = GoonAI(self)
        self.brain.setupBehaviors()
        self.brain.start()
        if self.spawnflags & self.StartsAsleep:
            self.brain.enterBehavior(GBSleep)
        else:
            self.brain.enterBehavior(GBPatrol)
            
    def Wakeup(self):
        self.brain.enterBehavior(GBWakeUp)
        
    def Patrol(self):
        self.brain.enterBehavior(GBPatrol)
            
    def hitByGag(self, gagId, distance):
        if self.isDead():
            return
            
        avId = self.air.getAvatarIdFromSender()
        player = self.air.doId2do.get(avId, None)
        if not player:
            return
            
        gagName = GagGlobals.getGagByID(gagId)
        data = dict(GagGlobals.getGagData(gagId))
        data['distance'] = distance
        baseDmg = GagGlobals.calculateDamage(player, gagName, data)
        hp = self.health - baseDmg
        self.b_setHealth(hp)
        self.d_announceHealth(0, baseDmg, -1)
        if self.isDead():
            self.dispatchOutput("OnDie")
            self.brain.stop()
            self.d_doRagdollMode()
        
    def delete(self):
        if self.brain:
            self.brain.stop()
            self.brain = None
        DistributedEntityAI.delete(self)
        DistributedAvatarAI.delete(self)

    def loadEntityValues(self):
        self.spawnflags = self.bspLoader.getEntityValueInt(self.entnum, "spawnflags")
