from panda3d.core import Point3, Vec3

from direct.showbase.DirectObject import DirectObject
from direct.fsm.StateData import StateData
from direct.interval.IntervalGlobal import Func, LerpHprInterval

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog.BaseBehaviorAI import BaseBehaviorAI

import random

GBInvalid = -1
GBSleep = 0
GBWakeUp = 1
GBChase = 2
GBAttack = 3
GBFlee = 4
GBScan = 5
GBPatrol = 6

class Behavior(StateData, BaseBehaviorAI):
    ID = GBInvalid # Must be overridden in each behavior

    def __init__(self, brain):
        StateData.__init__(self, 'behaviorDone')
        self.brain = brain
        self.goon = self.brain.goon
        self.suit = self.goon
        self.battle = self.goon.dispatch
        self.bspLoader = self.goon.cEntity.getLoader()
        self.air = self.goon.air
        self.behaviorStartTime = 0
        self.avIds = self.goon.dispatch.getAvatars()

    def enter(self):
        self.behaviorStartTime = globalClock.getFrameTime()

    def getElapsedTime(self):
        """Returns the time in seconds since the behavior was entered."""
        return globalClock.getFrameTime() - self.behaviorStartTime

    def shouldEnter(self):
        """Called each frame to perform logic and determine if this
        behavior should be entered. Does not necessarily mean it will,
        if no direct transition exists or another behavior with a
        higher priority should enter."""
        return True

    def getPlayer(self, plyrId):
        return self.air.doId2do.get(plyrId)

    def determineNextBehavior(self):
        """Called each frame when this behavior is running.
        It is the job of the current behavior to decide which one to do next."""
        return self.ID

class SleepBehavior(Behavior):
    ID = GBSleep

    def __init__(self, *args):
        Behavior.__init__(self, *args)
        self.startHearingPlyrTime = 0
        self.canHearPlyr = False
        self.timeUntilWakeUp = 0
        self.weaponWasShot = False
        self.wasHit = False

    def __handleWeaponShot(self):
        self.weaponWasShot = True

    def __handleWasHit(self):
        self.wasHit = True

    def enter(self):
        Behavior.enter(self)
        self.accept('playerFiredWeapon', self.__handleWeaponShot)
        self.goon.d_doAsleep()

    def exit(self):
        self.ignore('playerFiredWeapon')
        Behavior.exit(self)

    def determineNextBehavior(self):
        time = globalClock.getFrameTime()
        
        hearsAnyPlyr = False

        for avId in self.avIds:
            # We are sleeping, the only thing we can do is wake up.
            # So, should we wake up?
            plyr = self.air.doId2do.get(avId)
            if not plyr:
                continue
            if self.isPlayerAudible(plyr):
                # We can potentially hear them, they are relatively close. good start
                # I'm sleeping so I have to be woken up. If they are not crouching
                # I can definitely hear their footsteps.
                moveBits = plyr.getMoveBits()
                if moveBits & CIGlobals.MB_Moving and not (moveBits & CIGlobals.MB_Crouching):
                    if not hearsAnyPlyr:
                        # I'm not going to instantly wake up as soon as I hear you.
                        # That's unrealistic. Have a small time variation.
                        # Also gives the player a bit of leeway to quickly quiet down.
                        if not self.canHearPlyr:
                            self.startHearingPlyrTime = time
                            self.timeUntilWakeUp = random.uniform(0.35, 1.5)
                        hearsAnyPlyr = True

        self.canHearPlyr = hearsAnyPlyr

        if time - self.startHearingPlyrTime >= self.timeUntilWakeUp and self.canHearPlyr:
            return GBWakeUp
        elif self.weaponWasShot:
            # Wake up immediately if I heard a weapon fire.
            return GBWakeUp

        self.weaponWasShot = False

        # Stay in this behavior
        return GBSleep

class WakeUpBehavior(Behavior):
    ID = GBWakeUp

    def enter(self):
        Behavior.enter(self)
        self.goon.d_wakeup()

    def determineNextBehavior(self):
        if self.getElapsedTime() >= 2.0:
            # The full wakeup animation and sound finished playing.
            return GBPatrol

        return GBWakeUp

class MoveBehavior(Behavior):
    """Behavior in which the Goon moves around the world."""

    def __init__(self, *args):
        Behavior.__init__(self, *args)
        self.moveTrack = None
        self.moving = False
        self.moveFinished = False
        self.moveFinishedTime = 0

    def enter(self):
        Behavior.enter(self)
        self.moveFinished = False
        self.moving = False

    def exit(self):
        Behavior.exit(self)
        self.d_clearMoveTrack()
        self.clearMoveTrack()
        self.moveFinished = False
        self.moving = False
        
    def d_clearMoveTrack(self):
        self.goon.sendUpdate('clearMoveTrack')

    def clearMoveTrack(self):
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None

    def _moveTrackFinished(self):
        # Does nothing here.
        self.moveFinished = True
        self.moving = False
        self.moveFinishedTime = globalClock.getFrameTime()

    def doMoveTrack(self, path, turnToFirstWP = True, speed = 3.0, doWalkAnims = True):
        self.goon.d_doMoveTrack(path, turnToFirstWP, speed, doWalkAnims)

        self.clearMoveTrack()

        self.moveTrack = CIGlobals.getMoveIvalFromPath(self.goon, path, speed)

        if turnToFirstWP:
            turnHpr = CIGlobals.getHeadsUpAngle(self.goon, path[1])
            turnDist = CIGlobals.getHeadsUpDistance(self.goon, path[1])
            self.moveTrack.insert(1, LerpHprInterval(self.goon, duration = turnDist / (speed * 30), hpr = turnHpr))

        self.moveTrack.append(Func(self._moveTrackFinished))
        self.moveTrack.start()
        self.moving = True


class PatrolBehavior(MoveBehavior):
    ID = GBPatrol

    def __init__(self, *args):
        MoveBehavior.__init__(self, *args)
        self.nextMoveIval = 0

    def enter(self):
        MoveBehavior.enter(self)
        self.goon.d_doIdle()

    def exit(self):
        self.goon.d_stopIdle()
        MoveBehavior.exit(self)

    def determineNextBehavior(self):
        time = globalClock.getFrameTime()

        if self.moveFinished:
            doIt = random.randint(0, 2)
            if doIt == 0:
                return GBScan
            else:
                self.nextMoveIval = random.uniform(1.0, 5.0)

        for avId in self.avIds:
            plyr = self.getPlayer(avId)
            if not plyr:
                continue
            if self.isPlayerVisible(plyr) and self.isPlayerAlive(plyr):
                self.goon.d_doDetectStuff()
                return (GBChase, [plyr])

        if (not self.moveTrack or not self.moveTrack.isPlaying()) and (time - self.moveFinishedTime) >= self.nextMoveIval:
            path = []
            pos = self.goon.getPos(render)
            while len(path) < 2:
                # Pick a random point on a radius, walk to it, but make sure we can.
                radius = random.uniform(10, 30)
                dir = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), 0)
                endPos = pos + (dir * radius)
                path = self.goon.dispatch.planPath(pos, endPos)
            self.doMoveTrack(path)

        self.moveFinished = False

        return GBPatrol

class ScanBehavior(Behavior):
    ID = GBScan

    def enter(self):
        Behavior.enter(self)
        self.goon.d_doScan()

    def determineNextBehavior(self):
        if self.getElapsedTime() >= 6.0:
            # Didn't find anyone, return to patrolling.
            return GBPatrol

        elif self.getElapsedTime() >= 1.5:

            for avId in self.avIds:
                plyr = self.getPlayer(avId)
                if not plyr:
                    continue
                if self.isPlayerVisible(plyr) and self.isPlayerAlive(plyr):
                    self.goon.d_doDetectStuff()
                    return (GBChase, [plyr])

        return GBScan

class ChaseBehavior(MoveBehavior):
    ID = GBChase

    def __init__(self, *args):
        MoveBehavior.__init__(self, *args)
        self.targetPos = Point3(0)

    def enter(self, target):
        MoveBehavior.enter(self)
        self.target = target
        self.attackDistance = random.uniform(5, 15)

    def exit(self):
        MoveBehavior.exit(self)

    def determineNextBehavior(self):
        if self.target.isDead():
            self.goon.d_doUndetectGlow()
            return GBPatrol

        if self.isPlayerVisible(self.target) and self.goon.getDistance(self.target) <= self.attackDistance:
            # We're close enough to attack
            return (GBAttack, [self.target])

        plPos = self.target.getPos(render)
        replanPath = (plPos - self.targetPos).length() > 5.0
        if not self.moving or replanPath:
            pos = self.goon.getPos(render)
            self.targetPos = plPos
            path = self.goon.dispatch.planPath(pos, self.targetPos)
            if len(path) < 2:
                self.goon.d_doUndetectGlow()
                return GBPatrol
            #if not self.moving and not replanPath:
            #    self.goon.playIdleAnim()

            self.doMoveTrack(path, True, 7.5, True)

        return GBChase

class AttackBehavior(Behavior):
    ID = GBAttack

    def enter(self, target):
        Behavior.enter(self)
        self.target = target
        self.goon.d_watchTarget(target.doId)
        self.goon.d_shoot(target.doId)
        
    def exit(self):
        self.goon.d_stopWatchingTarget()
        Behavior.exit(self)

    def determineNextBehavior(self):
        if self.getElapsedTime() >= 3.0:
            return (GBChase, [self.target])

        return GBAttack

class GoonAI(DirectObject):
    """Manages all of the Goon's artificial intelligence behaviors."""

    def __init__(self, goon):
        self.goon = goon
        self.behaviors = {}
        self.currentBehavior = None
        self.thinkTask = None

    def addBehavior(self, cls):
        self.behaviors[cls.ID] = cls(self)
        self.behaviors[cls.ID].load()

    def setupBehaviors(self):
        self.addBehavior(SleepBehavior)
        self.addBehavior(WakeUpBehavior)
        self.addBehavior(ScanBehavior)
        self.addBehavior(PatrolBehavior)
        self.addBehavior(ChaseBehavior)
        self.addBehavior(AttackBehavior)

    def start(self):
        self.thinkTask = taskMgr.add(self.__think, "GoonAI.think")

    def stop(self):
        if self.thinkTask:
            taskMgr.remove(self.thinkTask)
            self.thinkTask = None
        self.exitCurrentBehavior()

    def exitCurrentBehavior(self):
        if self.currentBehavior:
            self.currentBehavior.exit()
            self.currentBehavior = None

    def enterBehavior(self, idx, args = []):
        if idx == GBInvalid or not self.behaviors.has_key(idx):
            print "GoonAI: tried to enter invalid behavior ID", idx
            return

        self.exitCurrentBehavior()
        beh = self.behaviors[idx]
        beh.enter(*args)
        self.currentBehavior = beh

    def __think(self, task):
        if self.currentBehavior:
            nextBeh = self.currentBehavior.determineNextBehavior()
            args = []
            if isinstance(nextBeh, tuple):
                nextBeh, args = nextBeh
            if nextBeh != self.currentBehavior.ID:
                self.enterBehavior(nextBeh, args)

        return task.cont
