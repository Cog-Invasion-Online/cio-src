from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.DistributedToonAI import DistributedToonAI
from DistributedEntityAI import DistributedEntityAI
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.cog.ai.tasks.BaseTaskAI import BaseTaskAI
from src.coginvasion.cog.ai.tasks.TasksAI import *
from src.coginvasion.cog.ai.ScheduleAI import Schedule
from src.coginvasion.cog.ai.ConditionsAI import *
from src.coginvasion.cog.ai.ScheduleResultsAI import *
from src.coginvasion.cog.ai.StatesAI import *

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
            print "Found hp barrel", closestBarrel
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
            
        print "Got path to hp barrel"

        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE
        
class Task_GrabHPBarrel(BaseTaskAI):
    
    def runTask(self):
        if not self.npc.hpBarrel:
            return SCHED_FAILED
            
        print "Grabbing barrel"
        self.npc.hpBarrel.requestGrab(self.npc.doId)
        return SCHED_COMPLETE
        
class Task_ClearHPBarrel(BaseTaskAI):
    
    def runTask(self):
        print "Clearing barrel"
        self.npc.hpBarrel = None
        return SCHED_COMPLETE

class DistributedSZBossToonAI(DistributedEntityAI, DistributedToonAI, BaseNPCAI):
    notify = directNotify.newCategory("NPCToonAI")

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedToonAI.__init__(self, air)
        BaseNPCAI.__init__(self, dispatch)
        self.setBattleZone(dispatch)

        from src.coginvasion.avatar.Attacks import ATTACK_GAG_WHOLECREAMPIE
        self.attackIds = [ATTACK_GAG_WHOLECREAMPIE]

        self.died = False
        
        self.hpBarrel = None
        
        self.schedules.update({
        
            "GET_HP_FROM_BARREL"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_RememberPosition(self), # remember where we were, we will return there after grabbing some HP
                    Task_FindBestHPBarrel(self),
                    Task_GetPathToHPBarrel(self),
                    Task_Speak(self, 0.5, ["I need more Laff points.", "I'm grabbing a Laff barrel!",
                                           "Hang on, I need this Laff barrel.", "I need Laff!"]),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_GrabHPBarrel(self),
                    Task_ClearHPBarrel(self),
                    Task_SetSchedule(self, "RETURN_TO_MEMORY_POSITION")
                ],
                interruptMask = COND_NEW_TARGET|COND_HEAVY_DAMAGE
            )
        
        })

    def setNPCState(self, state):
        if state != self.npcState:
            if state == STATE_COMBAT:
                # Speak when entering combat state
                task_oneOff(Task_Speak(self, 0.5, ["We've got trouble!",
                                                   "Grab your pies!"
                                                  "Who called these guys?",
                                                  "Gear up!",
                                                  "I'm SO scared!",
                                                  "Bring it on!",
                                                  "Special delivery!"]))

        BaseNPCAI.setNPCState(self, state)

    def delete(self):
        self.died = None
        self.hpBarrel = None
        taskMgr.remove(self.uniqueName('npcToonDie'))
        BaseNPCAI.delete(self)
        DistributedToonAI.delete(self)
        DistributedEntityAI.delete(self)
        
    def getSchedule(self):
        
        if self.npcState in [STATE_DEAD, STATE_NONE]:
            return BaseNPCAI.getSchedule(self)

        if self.npcState == STATE_COMBAT:
            if self.hasConditions(COND_TARGET_DEAD):
                task_oneOff(Task_Speak(self, 0.25, ["Got one!", "Take that!",
                                                    "Piece of cake!",
                                                    "That's going to leave a mark!",
                                                    "Rock and roll!"]))
        
        if not self.target and self.getHealthPercentage() <= self.LOW_HP_PERCT:
            # we need some health
            return self.getScheduleByName("GET_HP_FROM_BARREL")
        
        return BaseNPCAI.getSchedule(self)

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

        DistributedEntityAI.announceGenerate(self)
        DistributedToonAI.announceGenerate(self)

        self.b_setParent(CIGlobals.SPRender)
        self.startPosHprBroadcast()

        self.startAI()

        self.accept(self.getHealthChangeEvent(), self.__hpChange)
