# Filename: FactorySneakGuardSuit.py
# Created by:  blach (21Aug15)

from panda3d.core import PerspectiveLens, Spotlight, CollisionHandlerQueue, CollisionRay, CollisionNode, CollisionTraverser, BitMask32

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import LerpHprInterval

from src.coginvasion.globals import CIGlobals
from src.coginvasion.npc.NPCWalker import NPCLookInterval, NPCWalkInterval
from src.coginvasion.cog.Suit import Suit
#from src.coginvasion.suit import SuitPathFinder
import CogGuardGlobals as CGG

import random

class FactorySneakGuardSuit(Suit, FSM):
    notify = directNotify.newCategory("FactorySneakGuardSuit")

    SUIT = "mrhollywood"
    VIEW_DISTANCE_TASK_NAME = "ViewDistanceTask"
    MAX_VIEW_DISTANCE = 100.0
    GUARD_DIED_DELAY = 6.0
    MAX_HP = 200
    PROWLER_DISTANCE = 40.0

    IN_VIEW = "somethingInSight"
    HEARD = "heard"
    TRY_TO_CONFIRM_TIME = 5.0

    def __init__(self, world, guardKey):
        Suit.__init__(self)
        FSM.__init__(self, 'FactorySneakGuardSuit')
        self.gameWorld = world
        self.guardKey = guardKey
        self.viewDistanceTaskName = self.VIEW_DISTANCE_TASK_NAME + "-" + str(id(self))
        self.diedTaskName = "GuardDied-" + str(id(self))
        self.health = 0
        self.maxHealth = self.MAX_HP
        self.eyeLight = None
        self.eyeLens = None
        self.eyeNode = None
        self.moveTrack = None
        self.trav = None
        self.rayNP = None
        self.queue = None
        self.currentKey = self.guardKey
        self.firstPoint = CGG.GuardPointData[self.guardKey]
        self.walkTrack = None
        self.pathQueue = []
        self.currentPathIndex = 0

    def enterGuard(self):
        self.loop('neutral')
        pos, hpr = CGG.FactoryGuardPoints[self.guardKey]
        self.setHpr(hpr - (180, 0, 0))
        self.setPos(pos)

        base.taskMgr.add(self.__guard, self.taskName("guard"))

    def __checkToon(self):
        self.rayNP.lookAt(base.localAvatar)
        self.trav.traverse(render)
        if self.queue.getNumEntries() > 0:
            self.queue.sortEntries()
            hitObj = self.queue.getEntry(0).getIntoNodePath()
            print hitObj
            isLocalAvatar = hitObj.getParent().getPythonTag('localAvatar')
            if isLocalAvatar == 1:
                # Yes! We see the prowler!
                return 1
        return 0

    def __guard(self, task):
        # Let me check if the target is my frustrum, and if it's a close enough distance from me.
        if (self.eyeNode.node().isInView(base.localAvatar.getPos(self.eyeNode)) and
        self.getDistance(base.localAvatar) <= self.PROWLER_DISTANCE):
            # Now, let me check if the toon is standing right in front of me; not occluded.
            if self.__checkToon():
                # Yes! We see some one!
                self.request('SeekTarget', self.IN_VIEW)
                return task.done
        return task.cont

    def exitGuard(self):
        base.taskMgr.remove(self.taskName("guard"))

    def enterTurnToGuardSpot(self):
        self.loop('walk')
        _, hpr = CGG.FactoryGuardPoints[self.guardKey]
        self.moveTrack = LerpHprInterval(self, duration = 1.0, hpr = hpr, startHpr = self.getHpr())
        self.moveTrack.setDoneEvent(self.uniqueName('TurnedToGuardSpot'))
        self.acceptOnce(self.moveTrack.getDoneEvent(), self.request, ['Guard'])
        self.moveTrack.start()

    def exitTurnToGuardSpot(self):
        if self.moveTrack:
            self.ignore(self.moveTrack.getDoneEvent())
            self.moveTrack.finish()
            self.moveTrack = None

    def enterSeekTarget(self, event):
        dialogue = random.choice(CGG.GuardDialog[event])
        self.setChat(dialogue)

        self.loop('walk')
        self.moveTrack = NPCLookInterval(self, base.localAvatar)
        self.moveTrack.setDoneEvent(self.uniqueName("SeekLocalAvatar"))
        self.acceptOnce(self.moveTrack.getDoneEvent(), self.request, ['TryToConfirmTarget'])
        self.moveTrack.start()

    def exitSeekTarget(self):
        if self.moveTrack:
            self.ignore(self.moveTrack.getDoneEvent())
            self.moveTrack.finish()
            self.moveTrack = None

    def enterTryToConfirmTarget(self):
        self.loop('neutral')
        base.taskMgr.add(self.__tryToConfirmTarget, self.uniqueName('TryToConfirmTarget'))

    def __tryToConfirmTarget(self, task):
        if task.time >= self.TRY_TO_CONFIRM_TIME:
            # Hmm, I guess it was nothing.
            chat = random.choice(CGG.GuardDialog['disregard'])
            self.setChat(chat)
            self.request('TurnToGuardSpot')
            return task.done
        # Let me see the target again, so I know it's actually something.
        if (self.eyeNode.node().isInView(base.localAvatar.getPos(self.eyeNode)) and
        self.getDistance(base.localAvatar) <= self.PROWLER_DISTANCE):
            # Now, let me check if the toon is standing right in front of me; not occluded.
            if self.__checkToon():
                # There he is!
                chat = random.choice(CGG.GuardDialog['spot'])
                self.setChat(chat)
                self.request('Pursue')
                return task.done
        return task.cont

    def exitTryToConfirmTarget(self):
        base.taskMgr.remove(self.uniqueName('TryToConfirmTarget'))

    def enterGoBackToGuardSpot(self):
        self.walkBackToGuardSpot()

    def walkBackToGuardSpot(self):
        self.currentPathIndex = 0
        self.pathQueue = SuitPathFinder.find_path(CGG.FactoryWalkPoints, CGG.FactoryWayPointData, self.currentKey, self.guardKey)
        self.currentKey = self.guardKey
        self.walk(0.2)
        self.loop('walk')

    def exitGoBackToGuardSpot(self):
        pass

    def enterPursue(self):
        self.numTries = 0
        self.maxTries = 3
        self.runToClosestPoint()
        self.setPlayRate(1.5, 'walk')
        self.loop('walk')
        messenger.send('guardPursue')

    def getClosestPoint(self):
        # Return the key of the closest point to the localAvatar.
        closestPoint = None
        pointKey2range = {}
        for key, point in CGG.FactoryWalkPoints.items():
            dummyNode = render.attachNewNode('dummyNode')
            dummyNode.setPos(point)
            pointKey2range[key] = base.localAvatar.getDistance(dummyNode)
            dummyNode.removeNode()
        ranges = []
        for distance in pointKey2range.values():
            ranges.append(distance)
        ranges.sort()
        for key in pointKey2range.keys():
            distance = pointKey2range[key]
            if distance == ranges[0]:
                closestPoint = key
                break
        return closestPoint

    def runToClosestPoint(self):
        self.numTries += 1
        closestPoint = self.getClosestPoint()
        self.currentPathIndex = 0
        startKey = None
        if self.currentKey == self.guardKey:
            startKey = CGG.GuardPointData[self.firstPoint]
        else:
            startKey = self.currentKey
        self.pathQueue = SuitPathFinder.find_path(CGG.FactoryWalkPoints, CGG.FactoryWayPointData, startKey, closestPoint)
        if self.currentKey == self.guardKey:
            self.pathQueue.insert(0, 1)
        else:
            self.pathQueue.insert(0, 0)
        self.currentKey = closestPoint
        self.walk(0.1)

    def walk(self, speed = 0.2):
        self.currentPathIndex += 1
        if len(self.pathQueue) <= self.currentPathIndex:
            if self.getCurrentOrNextState() == 'Pursue':
                if self.getClosestPoint() != self.currentKey:
                    # Wow, the player ran off somewhere else! Go there!
                    if self.numTries >= self.maxTries:
                        # Dang it, give up, we can't get to them!
                        self.request('GoBackToGuardSpot')
                    else:
                        self.runToClosestPoint()
            elif self.getCurrentOrNextState() == 'GoBackToGuardSpot':
                self.request('Guard')
            return
        print self.pathQueue[self.currentPathIndex]
        if self.currentPathIndex == 1 and self.pathQueue[0] == 1:
            # We need to walk from our guard point to the first waypoint in our path
            startPoint = self.getPos(render)
            endPoint = CGG.FactoryWalkPoints[self.firstPoint]
        else:
            if self.pathQueue[0] == 0:
                self.pathQueue.remove(self.pathQueue[0])
            key = self.pathQueue[self.currentPathIndex]
            endPoint = CGG.FactoryWalkPoints[key]
            oldKey = self.pathQueue[self.currentPathIndex - 1]
            startPoint = CGG.FactoryWalkPoints[oldKey]
        self.walkTrack = NPCWalkInterval(self, endPoint, speed, startPoint)
        self.walkTrack.setDoneEvent(self.uniqueName('guardWalkDone'))
        self.acceptOnce(self.uniqueName('guardWalkDone'), self.walk)
        self.walkTrack.start()

    def exitPursue(self):
        self.setPlayRate(1.0, 'walk')
        del self.numTries
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.pause()
            self.walkTrack = None
        messenger.send('guardStopPursue')

    def uniqueName(self, name):
        return self.taskName(name)

    def taskName(self, name):
        return name + "-" + str(id(self))

    def setHealth(self, hp):
        self.health = hp

    def getHealth(self):
        return self.health

    def shot(self):
        dialogue = random.choice(CGG.GuardDialog['shot'])
        self.setChat(dialogue)

    def dead(self):
        self.request('Off')
        self.animFSM.request('die')
        base.taskMgr.doMethodLater(self.GUARD_DIED_DELAY, self.__diedDone, self.diedTaskName)

    def __diedDone(self, task):
        self.gameWorld.deleteGuard(self)
        return task.done

    def generate(self):
        data = CIGlobals.SuitBodyData[self.SUIT]
        type = data[0]
        team = data[1]
        self.generateSuit(type, self.SUIT, team, self.MAX_HP, 0, False)
        base.taskMgr.add(self.__viewDistance, self.viewDistanceTaskName)
        self.setPythonTag('guard', self)
        self.eyeLight = Spotlight('eyes')
        self.eyeLens = PerspectiveLens()
        self.eyeLens.setMinFov(90.0 / (4./3.))
        self.eyeLight.setLens(self.eyeLens)
        self.eyeNode = self.headModel.attachNewNode(self.eyeLight)
        self.eyeNode.setZ(-5)
        self.eyeNode.setY(-4.5)
        self.trav = CollisionTraverser(self.uniqueName('eyeTrav'))
        ray = CollisionRay(0, 0, 0, 0, 1, 0)
        rayNode = CollisionNode('ToonFPS.rayNode')
        rayNode.addSolid(ray)
        rayNode.setFromCollideMask(CGG.GuardBitmask | CIGlobals.WallBitmask)
        rayNode.setIntoCollideMask(BitMask32.allOff())
        self.rayNP = base.camera.attachNewNode(rayNode)
        self.rayNP.setZ(3)
        self.queue = CollisionHandlerQueue()
        self.trav.addCollider(self.rayNP, self.queue)
        self.trav.addCollider(self.gameWorld.mg.avatarBody, self.queue)
        self.request('Guard')

    def __viewDistance(self, task):
        # All the guards in the warehouse eat up a lot of frames.  This task will
        # hide the guard geometry if it's too far away.

        if self.getDistance(base.localAvatar) > self.MAX_VIEW_DISTANCE:
            if not self.isHidden():
                self.hide()
        else:
            if self.isHidden():
                self.show()

        task.delayTime = 1.0
        return task.again

    def disable(self):
        self.request('Off')
        base.taskMgr.remove(self.taskName("guard"))
        base.taskMgr.remove(self.diedTaskName)
        base.taskMgr.remove(self.viewDistanceTaskName)
        self.trav = None
        if self.rayNP:
            self.rayNP.removeNode()
            self.rayNP = None
        self.queue = None
        self.currentPathIndex = None
        if self.eyeNode:
            self.eyeNode.removeNode()
            self.eyeNode = None
            self.eyeLens = None
            self.eyeLight = None
        self.viewDistanceTaskName = None
        self.guardKey = None
        self.gameWorld = None
        self.pathQueue = None
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.finish()
            self.walkTrack = None
        Suit.disable(self)
