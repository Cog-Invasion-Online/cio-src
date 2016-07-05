# Filename: SuitPursueToonBehavior.py
# Created by:  blach (29Dec15)

from panda3d.core import Vec2, Point2

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State

from SuitPathBehavior import SuitPathBehavior
import SuitUtils
import SuitAttacks

import random

class SuitPursueToonBehavior(SuitPathBehavior):
    notify = directNotify.newCategory('SuitPursueToonBehavior')

    RemakePathDistance = 20.0
    DivertDistance = 5.0
    MaxNonSafeDistance = 40.0

    def __init__(self, suit, pathFinder):
        SuitPathBehavior.__init__(self, suit, False)
        self.fsm = ClassicFSM.ClassicFSM('SuitPursueToonBehavior', [State.State('off', self.enterOff, self.exitOff),
         State.State('pursue', self.enterPursue, self.exitPursue),
         State.State('divert', self.enterDivert, self.exitDivert),
         State.State('attack', self.enterAttack, self.exitAttack)], 'off', 'off')
        self.fsm.enterInitialState()
        self.air = self.suit.air
        self.target = None
        self.targetId = None
        self.pathFinder = pathFinder
        self.suitList = None
        self.suitDict = None

    def setSuitList(self, sList):
        self.suitList = sList

    def setSuitDict(self, sDict):
        self.suitDict = sDict

    def enter(self):
        SuitPathBehavior.enter(self)
        self.pickTarget()
        # Choose a distance that is good enough to attack this target.
        self.attackSafeDistance = random.uniform(5.0, 19.0)
        # Now, chase them down!
        self.fsm.request('pursue')

    def setTarget(self, toon):
        self.targetId = toon.doId
        self.target = toon
        self.suit.sendUpdate('setChaseTarget', [self.targetId])

    def pickTarget(self):
        # Choose the toon that is the closest to this suit as the target.
        avIds = list(self.battle.avIds)

        # Temporary fix for district resets. TODO: Actually correct this.
        for avId in avIds:
            if self.air.doId2do.get(avId) is None:
                avIds.remove(avId)

        avIds.sort(key = lambda avId: self.air.doId2do.get(avId).getDistance(self.suit))

        # Make sure we found some avatars to pursue.
        if len(avIds) == 0:
            self.suit.getBrain().exitCurrentBehavior()
            self.fsm.enterInitialState()
            return

        self.targetId = avIds[0]
        self.target = self.air.doId2do.get(self.targetId)
        self.suit.sendUpdate('setChaseTarget', [self.targetId])

    def exit(self):
        self.fsm.request('off')
        self.target = None
        self.targetId = None
        self.suitList = None
        self.suitDict = None
        self.suit.sendUpdate('setChaseTarget', [0])
        SuitPathBehavior.exit(self)

    def unload(self):
        self.mgr = None
        self.battle = None
        self.target = None
        self.targetId = None
        self.air = None
        SuitPathBehavior.unload(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterAttack(self, useSafeDistance = True):
        taskMgr.add(self._attackTask, self.suit.uniqueName('attackToonTask'),
                    extraArgs = [useSafeDistance], appendTask = True)

    def _attackTask(self, useSafeDistance, task):
        if not self.isAvatarReachable(self.target):
            return task.done

        if useSafeDistance:
            safeDistance = self.attackSafeDistance
        else:
            safeDistance = SuitPursueToonBehavior.MaxNonSafeDistance

        if self.suit.getDistance(self.target) > safeDistance:
            # Nope, we're too far away! We need to chase them down!
            self.fsm.request('pursue')
            return task.done

        attack = SuitUtils.attack(self.suit, self.target)
        timeout = SuitAttacks.SuitAttackLengths[attack]

        task.delayTime = timeout
        return task.again

    def exitAttack(self):
        taskMgr.remove(self.suit.uniqueName('attackToonTask'))

    def enterDivert(self):
        moveVector = Vec2()

        currPos = Point2(self.suit.getX(render), self.suit.getY(render))
        if self.suitList is not None:
            data = self.suitList
        elif self.suitDict is not None:
            data = self.suitDict.values()
        for suit in data:
            if suit == self.suit:
                continue

            otherPos = Point2(suit.getX(render), suit.getY(render))

            moveAway = currPos - otherPos

            if moveAway.length() > self.DivertDistance:
                continue
            moveMag = 1.0 / max(moveAway.lengthSquared(), 0.1)
            moveAway.normalize()
            moveAway *= moveMag

            moveVector += moveAway

        moveVector.normalize()
        x, y = currPos + (moveVector * self.DivertDistance)
        self.createPath(pos = (x, y))

    def walkDone(self):
        if self.fsm.getCurrentState().getName() == 'divert':
            self.fsm.request('pursue')

    def exitDivert(self):
        self.clearWalkTrack()

    def enterPursue(self):
        # Make our initial path to the toon.
        if not self.isAvatarReachable(self.target):
            return
        self.lastCheckedPos = self.target.getPos(render)
        self.createPath(self.target)
        taskMgr.add(self._pursueTask, self.suit.uniqueName('pursueToonTask'))
        taskMgr.add(self._scanTask, self.suit.uniqueName('scanTask'))

    def _scanTask(self, task):
        if self.suitList is not None:
            data = self.suitList
        elif self.suitDict is not None:
            data = self.suitDict.values()
        else:
            return task.done

        for suit in data:
            if suit == self.suit:
                continue

            if suit.getLevel() < self.suit.getLevel():
                continue
            elif (suit.getLevel() == self.suit.getLevel() and
                  suit.doId > self.suit.doId):
                continue

            currPos = Point2(self.suit.getX(render), self.suit.getY(render))
            otherPos = Point2(suit.getX(render), suit.getY(render))
            if (currPos - otherPos).length() < self.DivertDistance:
                self.fsm.request('divert')
                return task.done

        return task.again

    def _pursueTask(self, task):
        if self.target:
            if self.target.isDead():
                self.fsm.request('off')
                self.pickTarget()
                return task.done
            currPos = self.target.getPos(render)
            if self.suit.getDistance(self.target) <= self.attackSafeDistance and not self.target.isDead():
                # We're a good distance to attack this toon. Let's do it.
                self.fsm.request('attack')
                return task.done
            elif (currPos.getXy() - self.lastCheckedPos.getXy()).length() >= SuitPursueToonBehavior.RemakePathDistance:
                # They're too far from where we're trying to go! Make a new path to where they are!
                self.lastCheckedPos = self.target.getPos(render)
                self.createPath(self.target)
        task.delayTime = 1.0
        return task.again

    def exitPursue(self):
        taskMgr.remove(self.suit.uniqueName('scanTask'))
        taskMgr.remove(self.suit.uniqueName('pursueToonTask'))
        if hasattr(self, 'lastCheckedPos'):
            del self.lastCheckedPos
        self.clearWalkTrack()

    def shouldStart(self):
        return True
