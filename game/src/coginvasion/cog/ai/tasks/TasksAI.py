from panda3d.core import Vec3

from BaseTaskAI import BaseTaskAI

from src.coginvasion.cog.ai.ScheduleResultsAI import SCHED_COMPLETE, SCHED_CONTINUE, SCHED_FAILED
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.cog.ai.ConditionsAI import COND_SEE_TARGET
from src.coginvasion.globals import CIGlobals

import random

"""
A Task is the smallest atomic action that can be performed by an NPC.
"""

class Task_SetActivity(BaseTaskAI):

    def __init__(self, npc, activity):
        BaseTaskAI.__init__(self, npc)
        self.activity = activity

    def runTask(self):
        self.npc.b_setActivity(self.activity)
        return SCHED_COMPLETE

    def cleanup(self):
        del self.activity
        BaseTaskAI.cleanup(self)

class Task_AwaitActivity(BaseTaskAI):

    def runTask(self):
        if self.npc.isDoingActivity():
            return SCHED_CONTINUE

        return SCHED_COMPLETE

class Task_Wait(BaseTaskAI):

    def __init__(self, seconds):
        BaseTaskAI.__init__(self, None)
        self.seconds = seconds

    def runTask(self):
        if self.seconds < 0:
            # indefinite wait
            return SCHED_CONTINUE

        if self.getElapsedTime() >= self.seconds:
            return SCHED_COMPLETE
        return SCHED_CONTINUE

    def cleanup(self):
        del self.seconds
        BaseTaskAI.cleanup(self)

class Task_Func(BaseTaskAI):

    def __init__(self, func, args):
        BaseTaskAI.__init__(self, None)
        self.func = func
        self.args = args

    def runTask(self):
        self.func(*self.args)
        return SCHED_COMPLETE

    def cleanup(self):
        del self.func
        del self.args
        BaseTaskAI.cleanup(self)

class Task_EquipAttack(BaseTaskAI):

    def runTask(self):
        if len(self.npc.capableAttacks) == 0:
            return SCHED_FAILED

        attackID = random.choice(self.npc.capableAttacks)
        if attackID != self.npc.getEquippedAttack():
            self.npc.b_setEquippedAttack(attackID)
        return SCHED_COMPLETE

class Task_StopAttack(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() != -1:
            self.npc.b_setEquippedAttack(-1)
        return SCHED_COMPLETE
        
class Task_SpeakAttack(BaseTaskAI):
    
    def runTask(self):
        if self.npc.getEquippedAttack() == -1:
            return SCHED_FAILED
            
        attack = self.npc.attacks[self.npc.getEquippedAttack()]
        phrases = attack.getTauntPhrases()
        chance = attack.getTauntChance()
        
        if len(phrases) == 0 or chance <= 0:
            return SCHED_COMPLETE
            
        if random.random() <= chance:
            phrase = random.choice(phrases)
            self.npc.d_setChat(phrase)
            
        return SCHED_COMPLETE

class Task_FireAttack(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() == -1:
            return SCHED_FAILED
        if self.npc.target is None:
            return SCHED_FAILED

        self.npc.attacks[self.npc.getEquippedAttack()].npcUseAttack(self.npc.target.entity)

        return SCHED_COMPLETE

class Task_FaceTarget(BaseTaskAI):

    def runTask(self):
        if not self.npc.target:
            #print "fail: no target"
            return SCHED_FAILED

        # Determine a yaw to look at the target and move that way
        self.npc.makeIdealYaw(self.npc.target.lastKnownPosition)
        self.npc.changeYaw()

        #print "Ideal is", self.npc.idealYaw

        if self.npc.isFacingIdeal():
            #print "complete: facing ideal"
            return SCHED_COMPLETE

        return SCHED_CONTINUE

class Task_FaceIdeal(BaseTaskAI):

    def runTask(self):

        if self.npc.isFacingIdeal():
            return SCHED_COMPLETE
        
        # Simply turn towards whatever self.npc.idealYaw is
        self.npc.changeYaw()

        return SCHED_CONTINUE

class Task_GetPathToTarget(BaseTaskAI):

    def runTask(self):
        if not self.npc.target:
            return SCHED_FAILED

        path = self.npc.getBattleZone().planPath(self.npc.getPos(), self.npc.target.lastKnownPosition)
        if len(path) < 2:
            return SCHED_FAILED

        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE

class Task_RunPath(BaseTaskAI):

    def runTask(self):
        self.npc.getMotor().startMotor()
        return SCHED_COMPLETE

class Task_ClearPath(BaseTaskAI):

    def runTask(self):
        self.npc.getMotor().clearWaypoints()
        return SCHED_COMPLETE

class Task_StopMoving(BaseTaskAI):

    def runTask(self):
        self.npc.getMotor().stopMotor()
        return SCHED_COMPLETE

class Task_AwaitMovement(BaseTaskAI):
    
    def __init__(self, npc, watchTarget = False):
        BaseTaskAI.__init__(self, npc)
        self.watchTarget = watchTarget

    def runTask(self):
        if len(self.npc.getMotor().getWaypoints()) == 0:
            self.npc.getMotor().stopMotor()
            return SCHED_COMPLETE
        
        if self.watchTarget:
            if self.npc.hasConditions(COND_SEE_TARGET) and self.npc.target:
                if CIGlobals.isNodePathOk(self.npc.target.entity):
                    self.npc.makeIdealYaw(self.npc.target.entity.getPos())
                
        # Continue looking in our ideal direction
        self.npc.changeYaw()

        return SCHED_CONTINUE
        
    def cleanup(self):
        del self.watchTarget
        BaseTaskAI.cleanup(self)

class Task_FindCoverFromTarget(BaseTaskAI):

    def runTask(self):
        if self.npc.target:
            coverFrom = self.npc.target.entity
        else:
            coverFrom = self.npc

        threatPos = coverFrom.getPos()
        viewOffset = coverFrom.getEyePosition()

        if self.npc.findLateralCover(threatPos, viewOffset):
            # Try lateral first
            return SCHED_COMPLETE
        elif self.npc.findCover(threatPos, viewOffset, 0, self.npc.getCoverRadius()):
            # Then try for plain cover
            return SCHED_COMPLETE

        #print "Didn't find cover!"
        # No cover :(
        return SCHED_FAILED

class Task_FindCoverFromOrigin(BaseTaskAI):

    def runTask(self):
        if self.npc.findCover(self.npc.getPos(), self.npc.getEyePosition(), 0, self.npc.getCoverRadius()):
            return SCHED_COMPLETE
        return SCHED_FAILED

class Task_Remember(BaseTaskAI):

    def __init__(self, npc, bits):
        BaseTaskAI.__init__(self, npc)
        self.bits = bits

    def runTask(self):
        self.npc.remember(self.bits)
        return SCHED_COMPLETE

    def cleanup(self):
        del self.bits
        BaseTaskAI.cleanup(self)

class Task_Forget(BaseTaskAI):

    def __init__(self, npc, bits):
        BaseTaskAI.__init__(self, npc)
        self.bits = bits

    def runTask(self):
        self.npc.forget(self.bits)
        return SCHED_COMPLETE

    def cleanup(self):
        del self.bits
        BaseTaskAI.cleanup(self)

class Task_AwaitAttack(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() == -1 or self.npc.attacks[self.npc.getEquippedAttack()].getAction() == 0:
            return SCHED_COMPLETE
        return SCHED_CONTINUE
        
class Task_SetSchedule(BaseTaskAI):
    
    def __init__(self, npc, schedName):
        BaseTaskAI.__init__(self, npc)
        self.schedName = schedName
    
    def runTask(self):
        sched = self.npc.getScheduleByName(self.schedName)
        if not sched:
            return SCHED_FAILED
            
        self.npc.changeSchedule(sched)
        return SCHED_COMPLETE
        
    def cleanup(self):
        del self.schedName
        BaseTaskAI.cleanup(self)
        
class Task_RestartLastSchedule(BaseTaskAI):
    
    def runTask(self):
        if self.npc.lastSchedule is None:
            return SCHED_FAILED
            
        self.npc.changeSchedule(self.npc.lastSchedule)
        return SCHED_COMPLETE
        
class Task_RememberPosition(BaseTaskAI):
    
    def runTask(self):
        self.npc.memoryPosition = self.npc.getPos()
        return SCHED_COMPLETE
        
class Task_ForgetPosition(BaseTaskAI):
    
    def runTask(self):
        self.npc.memoryPosition = None
        return SCHED_COMPLETE
        
class Task_GetPathToMemoryPosition(BaseTaskAI):
    
    def runTask(self):
        if not self.npc.memoryPosition:
            return SCHED_FAILED
            
        path = self.npc.getBattleZone().planPath(self.npc.getPos(), self.npc.memoryPosition)
        if len(path) < 2:
            return SCHED_FAILED

        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE

class Task_SetPostAttackSchedule(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() == -1:
            return SCHED_FAILED
        schedName = self.npc.attacks[self.npc.getEquippedAttack()].getPostAttackSchedule()
        if not schedName:
            return SCHED_FAILED
        sched = self.npc.getScheduleByName(schedName)
        if not sched:
            return SCHED_FAILED
        self.npc.changeSchedule(sched)
        return SCHED_COMPLETE

class Task_Speak(BaseTaskAI):

    def __init__(self, npc, chance, phrases):
        BaseTaskAI.__init__(self, npc)
        self.chance = chance
        self.phrases = phrases

    def runTask(self):
        chance = random.random()
        if chance <= self.chance:
            if isinstance(self.phrases, list):
                phrase = random.choice(self.phrases)
            else:
                phrase = self.phrases
            self.npc.d_setChat(phrase)
        return SCHED_COMPLETE

    def cleanup(self):
        del self.chance
        del self.phrases
        BaseTaskAI.cleanup(self)
        
class Task_GetPathYieldToFriend(BaseTaskAI):
    
    def runTask(self):
        moveVector = Vec3()
        currPos = self.npc.getPos()
        for i in xrange(len(self.npc.avatarsInSight)):
            av = self.npc.avatarsInSight[i]
            if self.npc.getRelationshipTo(av) != RELATIONSHIP_FRIEND:
                continue
            otherPos = av.getPos()
            moveAway = currPos - otherPos
            
            if moveAway.length() > self.npc.getYieldDistance():
                continue
            moveMag = 1.0 / max(moveAway.lengthSquared(), 0.1)
            moveAway.normalize()
            moveAway *= moveMag

            moveVector += moveAway

        moveVector.normalize()
        newPos = currPos + (moveVector * self.npc.getYieldDistance())
        
        path = self.npc.getBattleZone().planPath(currPos, newPos)
        if len(path) < 2:
            return SCHED_FAILED

        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE

def task_oneOff(task):
    task.startTask()
    task.runTask()
    task.stopTask()
    task.cleanup()
