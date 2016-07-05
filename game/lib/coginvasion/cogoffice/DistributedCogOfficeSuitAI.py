# Filename: DistributedCogOfficeSuitAI.py
# Created by:  blach (17Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from lib.coginvasion.cog.SuitBrainAI import SuitBrain
from lib.coginvasion.cog.SuitPursueToonBehavior import SuitPursueToonBehavior
from lib.coginvasion.globals import CIGlobals
from CogOfficeConstants import POINTS
from CogOfficePathDataAI import *
import random

CHAIR_2_BATTLE_TIME = 9.0

class DistributedCogOfficeSuitAI(DistributedSuitAI):
    notify = directNotify.newCategory('DistributedSuitAI')

    def __init__(self, air, battle, initPointData, isChair, hood):
        DistributedSuitAI.__init__(self, air)
        self.hood = hood
        self.battle = battle
        self.battleDoId = self.battle.doId
        self.flyToPoint = None
        self.initPointIndex = initPointData[0]
        initPoint = initPointData[1]
        self.floorSection = initPoint[0]
        self.initPoint = initPoint[1]
        if isChair:
            self.flyToPoint = initPoint[2]
        self.isChair = isChair
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeSuitAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('guard', self.enterGuard, self.exitGuard, ['think']),
         State.State('think', self.enterThink, self.exitThink, ['off']),
         State.State('chair', self.enterChair, self.exitChair, ['chair2battle']),
         State.State('chair2battle', self.enterChair2Battle, self.exitChair2Battle, ['think'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.stateExtraArgs = []

    def monitorHealth(self, task):
        if not hasattr(self, 'battle') or hasattr(self, 'battle') and self.battle is None:
            return task.done

        if self.isDead():
            self.battle.suitHPAtZero(self.doId)
        return DistributedSuitAI.monitorHealth(self, task)

    def isActivated(self):
        return (self.fsm.getCurrentState().getName() == 'think')

    def canGetHit(self):
        if not self.allowHits:
            return False
        else:
            return (not self.isChair) or (self.isChair and self.fsm.getCurrentState().getName() == 'think')

    def getBattleDoId(self):
        return self.battleDoId

    def getPoints(self, name):
        if self.battle.currentRoom in self.battle.UNIQUE_FLOORS:
            points = POINTS[self.battle.deptClass][self.battle.currentRoom][name]
        else:
            points = POINTS[self.battle.currentFloor][name]
        return points

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterGuard(self):
        self.setPosHpr(*self.initPoint)
        self.b_setAnimState('neutral')

    def activate(self):
        self.b_setState('think')

    def exitGuard(self):
        pass

    def enterThink(self):
        if self.brain is not None:
            self.brain.startThinking()

    def exitThink(self):
        if self.brain is not None:
            self.brain.stopThinking()

    def enterChair(self):
        self.setPosHpr(*self.initPoint)
        self.b_setAnimState('sit')

    def allStandSuitsDead(self):
        if self.fsm.getCurrentState().getName() == 'chair':
            self.b_setState('chair2battle', [self.initPointIndex])

    def exitChair(self):
        pass

    def enterChair2Battle(self):
        taskMgr.remove(self.uniqueName('monitorHealth'))
        taskMgr.doMethodLater(CHAIR_2_BATTLE_TIME, self.chair2BattleTask, self.uniqueName('chair2BattleTask'))
        self.setPosHpr(*self.flyToPoint)

    def chair2BattleTask(self, task):
        self.b_setState('think')
        return task.done

    def exitChair2Battle(self):
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def setState(self, state, extraArgs = []):
        self.fsm.request(state)
        self.stateExtraArgs = extraArgs

    def b_setState(self, state, extraArgs = []):
        self.d_setState(state, extraArgs)
        self.setState(state, extraArgs)

    def d_setState(self, state, extraArgs):
        timestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, extraArgs, timestamp])

    def getState(self):
        return [self.fsm.getCurrentState().getName(), self.stateExtraArgs, globalClockDelta.getRealNetworkTime()]

    def spawn(self):
        self.brain = SuitBrain(self)
        pursue = SuitPursueToonBehavior(self, getPathFinder(self.battle.currentRoom))
        pursue.setSuitList(self.getManager().guardSuits)
        pursue.battle = self.battle
        self.brain.addBehavior(pursue, priority = 1)
        if not self.isChair:
            self.b_setState('guard', [self.initPointIndex])
        else:
            self.b_setState('chair', [self.initPointIndex])
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def delete(self):
        del self.isChair
        self.fsm.requestFinalState()
        del self.fsm
        del self.battle
        del self.stateExtraArgs
        DistributedSuitAI.delete(self)
