from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.DistributedToonAI import DistributedToonAI
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.cog.ai.tasks.BaseTaskAI import BaseTaskAI
from src.coginvasion.cog.ai.tasks.TasksAI import *
from src.coginvasion.cog.ai.ScheduleAI import Schedule
from src.coginvasion.cog.ai.ConditionsAI import *
from src.coginvasion.cog.ai.ScheduleResultsAI import *
from src.coginvasion.cog.ai.StatesAI import *
from src.coginvasion.avatar.Activities import *
from src.coginvasion.attack.Attacks import ATTACK_GAG_WHOLECREAMPIE

class Task_FireHealAttack(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() == -1:
            return SCHED_FAILED
        if not CIGlobals.isNodePathOk(self.npc.followTarget):
            return SCHED_FAILED

        self.npc.attackFinished = False
        attack = self.npc.attacks[self.npc.getEquippedAttack()]
        if not attack.npcUseAttack(self.npc.followTarget):
            return SCHED_CONTINUE

        return SCHED_COMPLETE

class Task_GetPathToFollowTarget(BaseTaskAI):
    
    def runTask(self):
        if not CIGlobals.isNodePathOk(self.npc.followTarget):
            return SCHED_FAILED
            
        path = self.npc.getBattleZone().planPath(self.npc.getPos(), self.npc.followTarget.getPos())
        if len(path) < 2:
            return SCHED_FAILED

        self.npc.getMotor().setWaypoints(path)
        
        return SCHED_COMPLETE
        
class Task_FaceFollowTarget(BaseTaskAI):
    
    def runTask(self):
        if not CIGlobals.isNodePathOk(self.npc.followTarget):
            return SCHED_FAILED
        
        self.npc.makeIdealYaw(self.npc.followTarget.getPos())
        
        if self.npc.isFacingIdeal():
            return SCHED_COMPLETE
            
        self.npc.changeYaw()
        
        return SCHED_CONTINUE
        
class Task_RunToFollowTarget(BaseTaskAI):
    
    def runTask(self):
        if not CIGlobals.isNodePathOk(self.npc.followTarget):
            return SCHED_FAILED
        
        if len(self.npc.getMotor().waypoints) == 1 and self.npc.getDistance(self.npc.followTarget) <= 5:
            return SCHED_COMPLETE
            
        return SCHED_CONTINUE

class Task_FindBestHPBarrel(BaseTaskAI):
    
    def runTask(self):
        barrels = self.npc.dispatch.bspLoader.findAllEntities("item_laffbarrel")
        closestBarrel = None
        closest = 999999999
        npcPos = self.npc.getPos()
        for i in xrange(len(barrels)):
            barrel = barrels[i]
            len2 = (npcPos - barrel.getPos()).lengthSquared()
            if len2 < closest and barrel.hp > 0:
                closest = len2
                closestBarrel = barrel
        if closestBarrel:
            self.npc.hpBarrel = closestBarrel
            return SCHED_COMPLETE
            
        return SCHED_FAILED
        
class Task_GetPathToHPBarrel(BaseTaskAI):
    
    def runTask(self):
        if not self.npc.hpBarrel:
            return SCHED_FAILED
            
        path = self.npc.getBattleZone().planPath(self.npc.getPos(), self.npc.hpBarrel.getPos())
        if len(path) < 2:
            return SCHED_FAILED

        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE
        
class Task_GrabHPBarrel(BaseTaskAI):
    
    def runTask(self):
        if not self.npc.hpBarrel:
            return SCHED_FAILED
            
        self.npc.hpBarrel.requestGrab(self.npc.doId)
        return SCHED_COMPLETE
        
class Task_ClearHPBarrel(BaseTaskAI):
    
    def runTask(self):
        self.npc.hpBarrel = None
        return SCHED_COMPLETE
        
class Task_MaintainFollowTarget(BaseTaskAI):
    
    def runTask(self):
        if not CIGlobals.isNodePathOk(self.npc.followTarget):
            return SCHED_FAILED
            
        wps = self.npc.getMotor().getWaypoints()
        if len(wps) >= 0:
            if len(wps) > 0:
                dest = wps[len(wps) - 1]
                dist = 5*5
            else:
                dest = self.npc.getPos()
                dist = 15*15
            if (dest - self.npc.followTarget.getPos()).lengthSquared() > dist:
                self.npc.planPath(self.npc.followTarget.getPos())
                self.npc.getMotor().startMotor()
            elif (self.npc.followTarget.getPos() - self.npc.getPos()).lengthSquared() <= 10*10 and self.npc.isPlayerVisible(self.npc.followTarget):
                if len(wps) > 0:
                    self.npc.getMotor().stopMotor()
                    self.npc.getMotor().clearWaypoints()
                # Do we need to stop and heal our friend?
                if self.npc.followTarget.getHealth() < self.npc.followTarget.getMaxHealth():
                    return SCHED_COMPLETE
            
        self.npc.makeIdealYaw(self.npc.followTarget.getPos())
        if not self.npc.isFacingIdeal():
            self.npc.changeYaw()
            
        return SCHED_CONTINUE

class DistributedSZBossToonAI(DistributedToonAI, BaseNPCAI):
    notify = directNotify.newCategory("NPCToonAI")
    
    RulesAndResponses = {
        "HealedByFriend"    :   [["Thanks!", "Thanks a million!", "Tee Hee", "Ha Ha Ha"], 0.5],
        "VPJumping"         :   ["Jump!", 0.5]
    }

    def __init__(self, air, dispatch):
        DistributedToonAI.__init__(self, air)
        BaseNPCAI.__init__(self, dispatch)
        self.setDispatch(dispatch)
        self.setBattleZone(dispatch)

        from src.coginvasion.attack.Attacks import ATTACK_GAG_WHOLECREAMPIE
        self.attackIds = [ATTACK_GAG_WHOLECREAMPIE]

        self.died = False
        
        self.hpBarrel = None
        
        self.followTarget = None
        
        self.schedules.update({
        
            "HEAL_FOLLOW_TARGET"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_FaceFollowTarget(self),
                    Task_Speak(self, 0.75, ["Patch yourself up!", "Here, this'll help!", "Let me help you out!", "Heads up!"]),
                    Task_EquipAttack(self, ATTACK_GAG_WHOLECREAMPIE),
                    Task_FireHealAttack(self),
                    Task_AwaitAttack(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_NEW_TARGET|COND_VP_JUMPING
            ),
        
            "GET_HP_FROM_BARREL"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_RememberPosition(self), # remember where we were, we will return there after grabbing some HP
                    Task_FindBestHPBarrel(self),
                    Task_GetPathToHPBarrel(self),
                    Task_Speak(self, 0.5, ["I need more Laff points.", "I'm grabbing a Laff barrel!",
                                           "Hang on, I need this Laff barrel.", "I need Laff!"]),
                    Task_MoveShoot(self),
                    Task_GrabHPBarrel(self),
                    Task_ClearHPBarrel(self),
                    Task_SetSchedule(self, "RETURN_TO_MEMORY_POSITION")
                ],
                interruptMask = COND_VP_JUMPING|COND_HEAVY_DAMAGE |COND_IN_WALL
            ),
            
            "RUN_TO_FOLLOW_TARGET"   :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_GetPathToFollowTarget(self),
                    Task_RunPath(self),
                    Task_RunToFollowTarget(self),
                    Task_FaceFollowTarget(self)
                ],
                interruptMask = COND_NEW_TARGET|COND_SCHEDULE_DONE|COND_TASK_FAILED|COND_IN_WALL
            ),
            
            "FOLLOW_TARGET_FACE"    :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_FaceFollowTarget(self)
                ],
                interruptMask = COND_NEW_TARGET|COND_SCHEDULE_DONE|COND_TASK_FAILED
            ),
            
            "MAINTAIN_FOLLOW_TARGET"    :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_MaintainFollowTarget(self)
                ],
                interruptMask = COND_VP_JUMPING|COND_SEE_FEAR|COND_NEW_TARGET|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_HEAR_DANGER|COND_HEAR_HATE|COND_FRIEND_IN_WAY|COND_HEAR_SOMETHING|COND_IN_WALL
            ),
            
            "VP_JUMP_DODGE" :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_Wait(0.5),
                    Task_SetActivity(self, ACT_JUMP),
                    Task_AwaitActivity(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED
            ),
            
            "VP_JUMP_REACT" :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_SetActivity(self, ACT_TOON_FALL),
                    Task_AwaitActivity(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED
            ),
        
        })
        
        self.schedules["YIELD_TO_FRIEND"].prependTask(
            Task_Speak(self, 0.4, ["Sorry.", "Let me get out of your way.", "Excuse me."])
        )
        
        self.schedules["IDLE_STAND"].interruptMask |= COND_VP_JUMPING
        self.schedules["COMBAT_FACE"].interruptMask |= COND_VP_JUMPING
        self.schedules["TAKE_COVER_FROM_ORIGIN"].interruptMask |= COND_VP_JUMPING
        self.schedules["TAKE_COVER_FROM_TARGET"].interruptMask |= COND_VP_JUMPING
        self.schedules["CHASE_TARGET"].interruptMask |= COND_VP_JUMPING
        self.schedules["ATTACK"].interruptMask |= COND_VP_JUMPING
        self.schedules["MAKE_ATTACK_LOS"].interruptMask |= COND_VP_JUMPING
        self.schedules["ALERT_FACE"].interruptMask |= COND_VP_JUMPING
        self.schedules["RETURN_TO_MEMORY_POSITION"].interruptMask |= COND_VP_JUMPING
        
    def onHitByVPJump(self):
        self.changeSchedule(self.getScheduleByName("VP_JUMP_REACT"))
        
    def use(self):
        if not self.isDead():
            avId = self.air.getAvatarIdFromSender()
            av = self.air.doId2do.get(avId, None)
            if av:
                if self.followTarget == av:
                    print("no longer following", av)
                    self.followTarget = None
                else:
                    print("now following", av)
                    self.followTarget = av
                    
    def setFollowTarget(self, tgt):
        self.followTarget = tgt

    def setNPCState(self, state, makeIdeal = True):
        if state != self.npcState:
            if state == STATE_COMBAT:
                # Speak when entering combat state
                task_oneOff(Task_Speak(self, 0.5, ["We've got trouble!",
                                                   "Grab your pies!",
                                                  "Who called these guys?",
                                                  "Gear up!",
                                                  "I'm SO scared!",
                                                  "Bring it on!",
                                                  "Special delivery!"]))

        BaseNPCAI.setNPCState(self, state, makeIdeal)

    def delete(self):
        self.died = None
        self.hpBarrel = None
        taskMgr.remove(self.uniqueName('npcToonDie'))
        BaseNPCAI.delete(self)
        DistributedToonAI.delete(self)
        
    def getSchedule(self):
        
        if self.npcState in [STATE_DEAD, STATE_NONE]:
            return BaseNPCAI.getSchedule(self)
            
        if self.hasConditions(COND_VP_JUMPING):
            return self.getScheduleByName("VP_JUMP_DODGE")    

        if self.npcState == STATE_COMBAT:
            if self.hasConditions(COND_TARGET_DEAD):
                self.clearConditions(COND_TARGET_DEAD)
                task_oneOff(Task_Speak(self, 0.25, ["Got one!", "Take that!",
                                                    "Piece of cake!",
                                                    "That's going to leave a mark!",
                                                    "Rock and roll!"]))
        
        if (self.getHealthPercentage() <= self.LOW_HP_PERCT):
            # we need some health
            return self.getScheduleByName("GET_HP_FROM_BARREL")
            
        if self.hasConditions(COND_SEE_FEAR):
            return self.getScheduleByName("TAKE_COVER_FROM_ORIGIN")
            
        if self.npcState in [STATE_IDLE, STATE_ALERT]:
            
            if self.hasConditions(COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE):
                return self.getScheduleByName("TAKE_COVER_FROM_ORIGIN")
            elif self.hasConditions(COND_HEAR_SOMETHING):
                return self.getScheduleByName("ALERT_FACE")
            
            sched = self.getScheduleByName("MAINTAIN_FOLLOW_TARGET")
            if CIGlobals.isNodePathOk(self.followTarget) and not self.followTarget.isDead():
                if self.getDistance(self.followTarget) <= 15.0 and self.followTarget.getHealth() < self.followTarget.getMaxHealth():
                    return self.getScheduleByName("HEAL_FOLLOW_TARGET")
                if not self.hasConditions(sched.interruptMask):
                    return sched
        
        return BaseNPCAI.getSchedule(self)
        
    def look(self):
        BaseNPCAI.look(self)
        
        self.clearConditions(COND_SEE_FEAR)
        
        for av in self.avatarsInSight:
            if av.__class__.__name__ == 'NPC_VPAI':
                if self.isPlayerInVisionCone_FromPlayer(av) and av.getActivity()[0] == ACT_VP_THROW:
                    self.setConditions(COND_SEE_FEAR)

    def __die(self, task):
        self.requestDelete()
        return task.done

    def __hpChange(self, new, old):
        if new <= 0 and not self.died:
            # ded
            taskMgr.doMethodLater(7.0, self.__die, self.uniqueName('npcToonDie'))
            self.died = True

    def announceGenerate(self):
        npcName = self.getEntityValue("name")
        if len(npcName) == 0:
            npcId = self.getEntityValueInt("npcId")
        else:
            npcId = NPCGlobals.getNPCIDByName(npcName)

        name = NPCGlobals.NPCToonDict[npcId][1]
        dna = NPCGlobals.NPCToonDict[npcId][2]
        self.b_setName(name)
        self.b_setDNAStrand(dna)
        self.b_setHealth(self.getMaxHealth())

        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())

        DistributedToonAI.announceGenerate(self)

        #self.b_setParent(CIGlobals.SPRender)
        self.startPosHprBroadcast()

        self.startAI()

        self.accept(self.getHealthChangeEvent(), self.__hpChange)
