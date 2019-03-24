from panda3d.core import Vec3

from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.avatar.AvatarTypes import *

from src.coginvasion.cog.ai.AIGlobal import (BaseNPCAI, STATE_IDLE, STATE_ALERT, STATE_COMBAT, BaseTaskAI,
                                             RELATIONSHIP_DISLIKE, RELATIONSHIP_NONE, RELATIONSHIP_HATE,
                                             Task_StopMoving, Task_RunPath, Task_AwaitMovement,
                                             Task_SetActivity, Task_AwaitActivity, COND_NEW_TARGET,
                                             COND_LIGHT_DAMAGE, COND_HEAVY_DAMAGE, STATE_DEAD,
                                             Schedule, STATE_NONE, SCHED_COMPLETE, SCHED_FAILED)

from src.coginvasion.avatar.Activities import ACT_WAKE_ANGRY, ACT_SMALL_FLINCH, ACT_DIE, ACT_GOON_SCAN
from DistributedEntityAI import DistributedEntityAI
from src.coginvasion.gags import GagGlobals

import random

class Task_GetRandomPath(BaseTaskAI):
    
    def runTask(self):
        attemps = 0
        
        path = []
        pos = self.npc.getPos()
        while len(path) < 2 and attemps < 10:
            # Pick a random point on a radius, walk to it, but make sure we can.
            radius = random.uniform(10, 30)
            dir = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), 0)
            endPos = pos + (dir * radius)
            path = self.npc.getBattleZone().planPath(pos, endPos)
            attemps += 1
            
        if len(path) < 2:
            return SCHED_FAILED
            
        self.npc.getMotor().setWaypoints(path)
            
        return SCHED_COMPLETE

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
        
        self.patrolTime = 0.0
        self.patrolDur = 10.0
        
        self.activities = {ACT_WAKE_ANGRY   :   2.0,
                           ACT_DIE          :   -1,
                           ACT_GOON_SCAN    :   6.0}
                           
        self.schedules.update({
            "SCAN_AREA" :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_GetRandomPath(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_SetActivity(self, ACT_GOON_SCAN),
                    Task_AwaitActivity(self)
                ],
                interruptMask = COND_NEW_TARGET|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE
            )
        
        })
        
        self.brain = None
        self.spawnflags = 0
        
        self.health = 25
        self.maxHealth = 25
        
    def takeDamage(self, dmgInfo):
        DistributedAvatarAI.takeDamage(self, dmgInfo)
        if self.isDead():
            self.cleanupPhysics()
        
    def getIdealState(self):
        
        BaseNPCAI.getIdealState(self)
        
        if self.npcState == STATE_ALERT:
            if globalClock.getFrameTime() - self.patrolTime > self.patrolDur:
                self.idealState = STATE_IDLE
                
        return self.idealState
        
    def setNPCState(self, state):
        if state != self.npcState:
            if state == STATE_ALERT:
                self.patrolTime = globalClock.getFrameTime()
                self.patrolDur = random.uniform(10, 60)
                
            if state == STATE_COMBAT:
                self.d_doDetectStuff()
            elif self.npcState == STATE_COMBAT:
                self.d_doUndetectGlow()
        BaseNPCAI.setNPCState(self, state)
        
    def getSchedule(self):
        if self.npcState in [STATE_DEAD, STATE_NONE]:
            return BaseNPCAI.getSchedule(self)
            
        if self.npcState == STATE_ALERT:
            # Walk around and scan the area for trespassers
            return self.getScheduleByName("SCAN_AREA")
            
        return BaseNPCAI.getSchedule(self)

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
