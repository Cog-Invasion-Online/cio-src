from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.cog.ai.AIGlobal import *
from src.coginvasion.avatar.AvatarTypes import *
from src.coginvasion.avatar.Activities import *
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo

from panda3d.core import Vec3, Vec4, NodePath

GOON_STATE_ASLEEP = BASENPC_STATE_LAST + 1

class NPC_GoonAI(DistributedAvatarAI, BaseNPCAI):

    IdleEyeColor = [1, 1, 0.5]
    AttackEyeColor = [1.5, 0, 0]
    DeadEyeColor = [1, 1, 1]
    AsleepEyeColor = [0.5, 0.5, 0.5]

    AvatarType = AVATAR_SUIT
    Relationships = {
        AVATAR_SUIT: RELATIONSHIP_FRIEND,
        AVATAR_TOON: RELATIONSHIP_HATE
    }

    def __init__(self, air, dispatch):
        DistributedAvatarAI.__init__(self, air, dispatch)
        BaseNPCAI.__init__(self, dispatch)
        
        self.activities = {ACT_RANGE_ATTACK1    :   2.5}
        
        self.died = False
        
        self.laserVec = [Vec3(0), Vec3(0)]
        
        self.schedules.update( {
        
            "RANGE_ATTACK1" :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_FaceTarget(self),
                    Task_SetActivity(self, ACT_RANGE_ATTACK1),
                    Task_Func(self.setupLaserVec),
                    Task_Wait(0.635),
                    Task_Func(self.fireLaser),
                    Task_AwaitActivity(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED
            )
        
        } )

        self.patrolTime = 0.0
        self.patrolDur = 10.0
        
        self.surfaceProp = "metal"

        self.health = 25
        self.maxHealth = 25

        self.hatType = 0
        self.idealEyeColor = self.IdleEyeColor
        
        self.didFadeOut = False
        
        # height
        self.hitboxData[2] = 4.0
        
    def getEyePosition(self):
        return (0, 0, 3.25)
        
    def setupLaserVec(self):
        traceStart = self.getPos() + self.getEyePosition()
        if self.target:
            entPos = self.target.entity.getPos() + self.target.entity.getEyePosition()
            self.laserVec = [traceStart, entPos]
        else:
            self.laserVec = [traceStart, traceStart + self.getQuat().xform(Vec3.forward() * 50)]
        
    def fireLaser(self):
        result = PhysicsUtils.rayTestClosestNotMe(self, self.laserVec[0], self.laserVec[1],
            CIGlobals.WorldGroup | CIGlobals.CharacterGroup, self.getBattleZone().getPhysicsWorld())
        traceEnd = self.laserVec[1]
        if result:
            traceEnd = result.getHitPos()
            hitNode = NodePath(result.getNode())
            
            avNP = hitNode.getParent()
        
            for obj in base.air.avatars[self.getBattleZone().zoneId]:
                if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and 
                self.getBattleZone().getGameRules().canDamage(self, obj, None)):
                    
                    dmgInfo = TakeDamageInfo(self, -1,
                                        10,
                                        traceEnd, self.laserVec[0])
                    
                    obj.takeDamage(dmgInfo)
    
                    break
            
        self.getBattleZone().getTempEnts().makeLaser(self.laserVec[0], traceEnd, Vec4(1, 0, 0, 1), 1.0)
        
    def think(self):
        if self.npcState == STATE_DEAD:
            now = globalClock.getFrameTime()
            deadTime = now - self.npcStateTime
            if deadTime >= 5.0:
                self.setNextThink(-1)
                self.requestDelete()
            elif deadTime >= 4.0 and not self.didFadeOut:
                self.sendUpdate('fadeOut', [1.0])
                self.didFadeOut = True

    def getIdealState(self):
        
        BaseNPCAI.getIdealState(self)
        
        #if self.npcState == STATE_ALERT:
        #    if globalClock.getFrameTime() - self.patrolTime > self.patrolDur:
        #        self.idealState = STATE_IDLE
                
        return self.idealState
        
    def setNPCState(self, state, makeIdeal = True):
        if state != self.npcState:

            if state == STATE_ALERT:
                self.b_setIdealEyeColor(self.IdleEyeColor)
            #    self.patrolTime = globalClock.getFrameTime()
            #    self.patrolDur = random.uniform(10, 60)
                
            if state == STATE_COMBAT:
                self.b_setIdealEyeColor(self.AttackEyeColor)
                self.d_playSound("detect")

            elif state == STATE_IDLE:
                self.b_setIdealEyeColor(self.AsleepEyeColor)

            elif state == STATE_DEAD:
                messenger.send("goonie_die")
                self.b_setIdealEyeColor(self.DeadEyeColor)
                self.d_doRagdollMode()
                self.d_playSound("die")

        BaseNPCAI.setNPCState(self, state, makeIdeal)
        
    def checkAttacks(self, distSqr):
        """
        Builds a list of usable attacks for a target entity.
        """

        self.clearConditions(COND_CAN_RANGE_ATTACK1)
        
        if distSqr <= 50*50:
            self.setConditions(COND_CAN_RANGE_ATTACK1)

    def getSchedule(self):
        
        if self.npcState == STATE_NONE:
            return None
            
        if (self.npcState not in [STATE_SCRIPT, STATE_DEAD]) and self.hasConditions(COND_IN_WALL):
            # Get out of the wall
            return self.getScheduleByName("CLEAR_WALL")

        elif self.npcState == STATE_IDLE:
            if self.hasConditions(COND_HEAR_SOMETHING):
                return self.getScheduleByName("ALERT_FACE")
            return self.getScheduleByName("IDLE_STAND")

        elif self.npcState == STATE_ALERT:
            if self.hasConditions(COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE):
                return self.getScheduleByName("TAKE_COVER_FROM_ORIGIN")
            elif self.hasConditions(COND_HEAR_SOMETHING):
                return self.getScheduleByName("ALERT_FACE")
            return self.getScheduleByName("IDLE_STAND")

        elif self.npcState == STATE_COMBAT:
            if self.hasConditions(COND_TARGET_DEAD):
                self.clearTarget()
                if self.getTarget():
                    self.clearConditions(COND_TARGET_DEAD)
                    return self.getSchedule()
                else:
                    self.setNPCState(STATE_ALERT)
                    return self.getSchedule()
            if self.hasConditions(COND_NEW_TARGET) and not self.hasMemory(MEMORY_COMBAT_WAKE):
                return self.getScheduleByName("WAKE_ANGRY")
            elif self.hasConditions(COND_LIGHT_DAMAGE) and not self.hasMemory(MEMORY_FLINCHED):
                return self.getScheduleByName("SMALL_FLINCH")
            elif self.hasConditions(COND_HEAVY_DAMAGE):
                return self.getScheduleByName("TAKE_COVER_FROM_TARGET")
            elif not self.hasConditions(COND_SEE_TARGET):
                if not self.hasConditions(COND_TARGET_OCCLUDED):
                    return self.getScheduleByName("COMBAT_FACE")
                else:
                    return self.getScheduleByName("CHASE_TARGET")
            else:
                if self.hasConditions(COND_CAN_RANGE_ATTACK1):
                    return self.getScheduleByName("RANGE_ATTACK1")
                elif not self.isFacingIdeal():
                    return self.getScheduleByName("COMBAT_FACE")
                else:
                    return self.getScheduleByName("CHASE_TARGET")

        elif self.npcState == STATE_DEAD:
            return self.getScheduleByName("DIE")

    def getIdealEyeColor(self):
        return self.idealEyeColor

    def b_setIdealEyeColor(self, rgb):
        self.sendUpdate('setIdealEyeColor', rgb)
        self.idealEyeColor = rgb

    def getHatType(self):
        return self.hatType

    def loadEntityValues(self):
        DistributedAvatarAI.loadEntityValues(self)
        self.hatType = self.getEntityValueInt("hat")

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        if self.cEntity:
            self.setPos(self.cEntity.getOrigin())
            self.setHpr(self.cEntity.getAngles())
        self.startPosHprBroadcast()
        self.startAI()
        
    def delete(self):
        self.stopAI()
        self.stopPosHprBroadcast()
        self.didFadeOut = None
        self.idealEyeColor = None
        self.hatType = None
        self.patrolTime = None
        self.patrolDur = None
        DistributedAvatarAI.delete(self)
        
