from panda3d.core import Vec3, NodePath

from BaseTaskAI import BaseTaskAI

from src.coginvasion.cog.ai.ScheduleResultsAI import SCHED_COMPLETE, SCHED_CONTINUE, SCHED_FAILED
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.cog.ai.ConditionsAI import COND_SEE_TARGET
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

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

    def __init__(self, func, args = []):
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
    
    def __init__(self, npc, attack = None):
        BaseTaskAI.__init__(self, npc)
        self.attack = attack

    def runTask(self):
        if len(self.npc.capableAttacks) == 0:
            return SCHED_FAILED
        
        if self.attack is None:
            attackID = random.choice(self.npc.capableAttacks)
        else:
            attackID = self.attack
        if attackID != self.npc.getEquippedAttack():
            self.npc.b_setEquippedAttack(attackID)
        return SCHED_COMPLETE
        
    def cleanup(self):
        del self.attack
        BaseTaskAI.cleanup(self)

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
        
class Task_TestAttackLOS(BaseTaskAI):
    
    def runTask(self):
        attack = self.npc.attacks[self.npc.getEquippedAttack()]
        losData = attack.npc_testAttackLOS(self.npc.getPos() + (0, 0, self.npc.getHeight() / 2.0),
                                           self.npc.target.entity.getPos() + (0, 0, self.npc.target.entity.getHeight() / 2.0))
        if not losData[0]:
            self.npc.attackLOSData = losData
            return SCHED_FAILED
        
        return SCHED_COMPLETE
        
class Task_GetPathAttackLOS(BaseTaskAI):
    
    def runTask(self):
        path = self.npc.battleZone.planPath(self.npc.getPos(), self.npc.getPos() + self.npc.attackLOSData[1])
        if len(path) < 2:
            return SCHED_FAILED
        self.npc.getMotor().setWaypoints(path)
        return SCHED_COMPLETE

class Task_FireAttack(BaseTaskAI):

    def runTask(self):
        if self.npc.getEquippedAttack() == -1:
            return SCHED_FAILED
        if self.npc.target is None:
            return SCHED_FAILED

        self.npc.attackFinished = False
        attack = self.npc.attacks[self.npc.getEquippedAttack()]
        if not attack.npcUseAttack(self.npc.target.entity):
            return SCHED_CONTINUE

        return SCHED_COMPLETE
        
class Task_MoveShoot(BaseTaskAI):
    
    def startTask(self):
        BaseTaskAI.startTask(self)
        self.npc.getMotor().startMotor(False, False)
    
    def runTask(self):
        hasTarget = self.npc.target and CIGlobals.isNodePathOk(self.npc.target.entity) and self.npc.hasConditions(COND_SEE_TARGET)
        target = self.npc.target
        motor = self.npc.getMotor()
        
        canAttack = False
        
        if hasTarget:
            # We have a target, look at the target while moving
            self.npc.makeIdealYaw(target.entity.getPos())
            
            if self.npc.getEquippedAttack() == -1:
                # No attack currently? Equip one, if we have one to use
                if len(self.npc.capableAttacks) > 0:
                    self.npc.b_setEquippedAttack(random.choice(self.npc.capableAttacks))
                    canAttack = True
            elif len(self.npc.capableAttacks) == 0:
                # No attacks to use
                if self.npc.getEquippedAttack() != -1:
                    self.npc.b_setEquippedAttack(-1)
            else:
                # We already have an equipped attack to use
                canAttack = True
            
        else:
            if self.npc.getEquippedAttack() != -1:
                self.npc.b_setEquippedAttack(-1)
            canAttack = False
            
        if canAttack and self.npc.isFacingIdeal(5.0):
            # Fire at the target while moving
            attack = self.npc.attacks[self.npc.getEquippedAttack()]
            attack.npcUseAttack(target.entity)
        elif not hasTarget and len(motor.waypoints) > 0:
            # Can't attack anything, just face the waypoint
            self.npc.makeIdealYaw(motor.waypoints[0])
            
        if not self.npc.isFacingIdeal():
            self.npc.changeYaw()
            
        if len(motor.waypoints) == 0:
            return SCHED_COMPLETE
        return SCHED_CONTINUE

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
    
    def __init__(self, npc, snapIdeal = False, turnThenRun = True):
        BaseTaskAI.__init__(self, npc)
        self.snapIdeal = snapIdeal
        self.turnThenRun = turnThenRun

    def runTask(self):
        self.npc.getMotor().startMotor(self.snapIdeal, self.turnThenRun)
        return SCHED_COMPLETE
        
    def cleanup(self):
        del self.snapIdeal
        del self.turnThenRun
        BaseTaskAI.cleanup(self)

class Task_ClearPath(BaseTaskAI):

    def runTask(self):
        self.npc.getMotor().clearWaypoints()
        return SCHED_COMPLETE

class Task_StopMoving(BaseTaskAI):

    def runTask(self):
        self.npc.getMotor().stopMotor()
        return SCHED_COMPLETE

class Task_AwaitMovement(BaseTaskAI):
    
    def __init__(self, npc, watchTarget = False, changeYaw = True, toTarget = False):
        BaseTaskAI.__init__(self, npc)
        self.watchTarget = watchTarget
        self.changeYaw = changeYaw
        self.toTarget = toTarget

    def runTask(self):
        if len(self.npc.getMotor().getWaypoints()) == 0:
            self.npc.getMotor().stopMotor()
            return SCHED_COMPLETE

        if self.npc.target:

            if self.toTarget:
                waypoints = self.npc.getMotor().getWaypoints()
                dest = waypoints[len(waypoints) - 1]
                if (dest - self.npc.target.lastKnownPosition).lengthSquared() > 25:
                    # We are chasing our target, and they have moved away from the destination waypoint.
                    # We need to refresh the path.

                    path = self.npc.getBattleZone().planPath(self.npc.getPos(), self.npc.target.lastKnownPosition)
                    if len(path) < 2:
                        return SCHED_FAILED

                    self.npc.getMotor().setWaypoints(path)
        
            if self.watchTarget:
                if self.npc.hasConditions(COND_SEE_TARGET):
                    if CIGlobals.isNodePathOk(self.npc.target.entity):
                        self.npc.makeIdealYaw(self.npc.target.entity.getPos())
                
        if self.changeYaw:
            # Continue looking in our ideal direction
            self.npc.changeYaw()

        return SCHED_CONTINUE
        
    def cleanup(self):
        del self.watchTarget
        del self.changeYaw
        del self.toTarget
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
        if self.npc.getEquippedAttack() == -1 or self.npc.attackFinished:
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
        if self.npc.blockAIChat:
            return SCHED_COMPLETE
            
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

class Task_SuggestState(BaseTaskAI):

    def __init__(self, npc, state):
        BaseTaskAI.__init__(self, npc)
        self.state = state

    def runTask(self):
        self.npc.idealState = self.state
        return SCHED_COMPLETE

    def cleanup(self):
        del self.state
        BaseTaskAI.cleanup(self)
        
class Task_GetPathToClearWall(BaseTaskAI):
    
    def runTask(self):
        
        currPos = self.npc.getPos()
        toWall = (self.npc.wallPoints[1].getXy() - currPos.getXy()).normalized()
        clearPos = currPos - (Vec3(toWall[0], toWall[1], 0.0) * 4)
        
        # Snap clear position to floor if we can
        result = PhysicsUtils.rayTestClosestNotMe(self.npc, clearPos, clearPos - (0, 0, 10),
            CIGlobals.WorldGroup, self.npc.getBattleZone().getPhysicsWorld())
        if result:
            clearPos = result.getHitPos()
        
        bestPath = self.npc.getBattleZone().planPath(currPos, clearPos)
        
        if bestPath:
            self.npc.getMotor().setWaypoints(bestPath)
            return SCHED_COMPLETE
            
        return SCHED_FAILED
        
class Task_SetFailSchedule(BaseTaskAI):
    
    def __init__(self, npc, failSched):
        BaseTaskAI.__init__(self, npc)
        self.failSched = failSched
    
    def runTask(self):
        self.npc.schedule.failSchedule = self.failSched
        return SCHED_COMPLETE
    
    def cleanup(self):
        del self.failSched
        BaseTaskAI.cleanup(self)
        

def task_oneOff(task):
    task.startTask()
    task.runTask()
    task.stopTask()
    task.cleanup()
