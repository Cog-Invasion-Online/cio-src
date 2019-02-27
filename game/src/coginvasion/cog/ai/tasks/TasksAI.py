from BaseTaskAI import BaseTaskAI

from src.coginvasion.cog.ai.ScheduleResultsAI import SCHED_COMPLETE, SCHED_CONTINUE, SCHED_FAILED
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

        attack = random.choice(self.npc.capableAttacks)
        if attack.getID() != self.npc.getEquippedAttack():
            self.npc.b_setEquippedAttack(attack.getID())
        return SCHED_COMPLETE

class Task_StopAttack(BaseTaskAI):

    def runTask(self):
        self.npc.b_setEquippedAttack(-1)
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

    def runTask(self):
        if len(self.npc.getMotor().getWaypoints()) == 0:
            self.npc.getMotor().stopMotor()
            return SCHED_COMPLETE

        # Continue looking in our ideal direction
        self.npc.changeYaw()

        return SCHED_CONTINUE

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
            print "Await attack done"
            return SCHED_COMPLETE
        return SCHED_CONTINUE