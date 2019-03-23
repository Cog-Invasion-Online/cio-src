from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.avatar.AvatarTypes import *
from src.coginvasion.cog.ai.RelationshipsAI import *
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.cog.ai.StatesAI import STATE_IDLE, STATE_ALERT
from src.coginvasion.avatar.Activities import ACT_WAKE_ANGRY, ACT_SMALL_FLINCH, ACT_DIE
from DistributedEntityAI import DistributedEntityAI
from src.coginvasion.gags import GagGlobals

class DistributedGoonAI(DistributedEntityAI, DistributedAvatarAI, BaseNPCAI):

    StartsAsleep = 1
    
    AvatarType = AVATAR_SUIT
    Relationships = {
        AVATAR_CCHAR    :   RELATIONSHIP_DISLIKE,
        AVATAR_SUIT     :   RELATIONSHIP_NONE,
        AVATAR_TOON     :   RELATIONSHIP_HATE
    }

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedAvatarAI.__init__(self, air)
        BaseNPCAI.__init__(self, dispatch)
        
        self.activities = {ACT_WAKE_ANGRY   :   2.0,
                           ACT_DIE          :   -1}
        
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
        
        self.startPosHprBroadcast()
        
        self.startAI()
        
        if self.spawnflags & self.StartsAsleep:
            self.setNPCState(STATE_IDLE)
        else:
            self.setNPCState(STATE_ALERT)
            
    def Wakeup(self):
        #self.brain.enterBehavior(GBWakeUp)
        pass
        
    def Patrol(self):
        #self.brain.enterBehavior(GBPatrol)
        pass
            
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
        self.stopPosHprBroadcast()
        if self.brain:
            self.brain.stop()
            self.brain = None
        DistributedEntityAI.delete(self)
        DistributedAvatarAI.delete(self)

    def loadEntityValues(self):
        self.spawnflags = self.bspLoader.getEntityValueInt(self.entnum, "spawnflags")
