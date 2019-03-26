"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ScriptedSequenceAI.py
@author Brian Lach
@date March 25, 2019

@desc An entity used by level designers to make an NPC move and play an animation.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.avatar import Activities
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.cog.ai.StatesAI import STATE_SCRIPT, STATE_IDLE
from src.coginvasion.szboss.EntityAI import EntityAI

class ScriptedSequenceAI(EntityAI):
    notify = directNotify.newCategory("ScriptedSequenceAI")
    
    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        
        self.targetEnt = None
        self.nextScript = None

        self.entryAnimation = None
        self.actionAnimation = None
        self.loopAction = False
        self.exitAnimation = None
        self.moveToPosition = True

        self.shouldRestartAI = True

        self.seq = None
        
    def load(self):
        EntityAI.load(self)
        
        entname = self.getEntityValue("targetEnt")
        self.targetEnt = self.bspLoader.getPyEntityByTargetName(entname)
        if not self.targetEnt:
            self.notify.error("target entity `{0}` not found!".format(entname))
        elif not isinstance(self.targetEnt, BaseNPCAI):
            self.notify.error("target entity `{0}` is not an NPC!".format(entname))

        self.nextScript = self.bspLoader.getPyEntityPyTargetName(self.getEntityValue("nextScript"))

        self.entryAnimation = Activities.getActivityByName(self.getEntityValue("entryAnimation"))
        self.actionAnimation = Activities.getActivityByName(self.getEntityValue("actionAnimation"))
        self.exitAnimation = Activities.getActivityByName(self.getEntityValue("exitAnimation"))

        self.loopAction = self.getEntityValueBool("loopAction")

        # Should we move to the location of this entity before performing the scripted sequence?
        self.moveToPosition = self.getEntityValueBool("moveToPosition")

    def __maybeStartNextScript(self):
        if self.nextScript:
            # A script to start after we finish was specified.
            self.nextScript.Start()
            self.shouldRestartAI = False

    def __awaitMovement(self, task):
        if self.targetEnt.isDead():
            return task.done

        if len(self.targetEnt.getMotor().getWaypoints()) == 0:
            self.__performSequence()
            return task.done

        return task.cont

    def __performSequence(self):
        seq = Sequence(
            Func(self.targetEnt.b_setActivity, self.entryAnimation.value),
            Wait(self.targetEnt.getActivityDuration(self.entryAnimation)),

            Func(self.targetEnt.b_setActivity, self.actionAnimation.value),
            Wait(self.targetEnt.getActivityDuration(self.actionAnimation)),

            Func(self.targetEnt.b_setActivity, self.exitAnimation.value),
            Wait(self.targetEnt.getActivityDuration(self.exitAnimation)),

            Func(self.__maybeStartNextScript),
            Func(self.StopSequence)
        )
        seq.start()

        self.seq = seq

    def StartSequence(self):
        # Disable the AI on this entity
        self.targetEnt.setNPCState(STATE_SCRIPT)

        if self.moveToPosition:
            self.targetEnt.planPath(self.cEntity.getOrigin())
            self.targetEnt.getMotor().startMotor()
            taskMgr.add(self.__awaitMovement, self.entityTaskName("awaitMovement"))
        else:
            self.__performSequence()

        self.dispatchOutput("OnStartSequence")

    def StopSequence(self):
        if self.shouldRestartAI:
            self.targetEnt.setNPCState(STATE_IDLE)
        if self.seq:
            self.seq.pause()
        self.seq = None
        
    def unload(self):
        if self.seq:
            self.seq.pause()
        self.seq = None

        self.targetEnt = None
        self.nextScript = None
        self.entryAnimation = None
        self.actionAnimation = None
        self.loopAction = None
        self.exitAnimation = None
        self.moveToPosition = None
        self.shouldRestartAI = None

        EntityAI.unload(self)
