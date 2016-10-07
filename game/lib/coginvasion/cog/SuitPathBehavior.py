########################################
# Filename: SuitPathBehavior.py
# Created by: DecodedLogic (03Sep15)
########################################

from pandac.PandaModules import Point3, Point2

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.interval.IntervalGlobal import Sequence, Func

from SuitPathDataAI import *
from SuitUtils import getMoveIvalFromPath

import random

class SuitPathBehavior(SuitBehaviorBase):

    def __init__(self, suit, exitOnWalkFinish = True):
        SuitBehaviorBase.__init__(self, suit)
        self.walkTrack = None
        self.exitOnWalkFinish = exitOnWalkFinish
        self.isEntered = 0
        self.pathFinder = None

    def exit(self):
        self.clearWalkTrack()
        SuitBehaviorBase.exit(self)

    def unload(self):
        del self.exitOnWalkFinish
        del self.walkTrack
        SuitBehaviorBase.unload(self)

    def createPath(self, node = None, durationFactor = 0.2, fromCurPos = False, pos = None):
        if node is not None and pos is None:
            x1, y1 = node.getX(render), node.getY(render)
            z = node.getZ(render)
        elif pos is not None and node is None:
            x1, y1 = pos
            z = self.suit.getZ(render)
        x2, y2 = self.suit.getX(render), self.suit.getY(render)
        path = self.pathFinder.planPath((x2, y2), (x1, y1))
        if path is None:
            return
        if len(path) < 2:
            path.insert(0, (x2, y2))
        self.startPath(path, z, durationFactor)

    def startPath(self, path, z, durationFactor):
        correctedPath = []
        for i in xrange(len(path)):
            waypoint = path[i]
            correctedPath.append([waypoint[0], waypoint[1], z])
        self.suit.d_setWalkPath(correctedPath)
        self.path = correctedPath
        self._doWalk(durationFactor)

    def _doWalk(self, durationFactor):
        self.walkTrack = getMoveIvalFromPath(self.suit, self.path, 0.0, False, 'suitMoveIval')
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.startFollow()

    def clearWalkTrack(self, andTurnAround = 0):
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.pause()
            self.walkTrack = None
            if hasattr(self, 'suit'):
                self.suit.d_stopMoveInterval(andTurnAround)

    def startFollow(self):
        if self.walkTrack:
            self.acceptOnce(self.walkTrack.getDoneEvent(), self.walkDone)
            self.walkTrack.start()

    def walkDone(self):
        if not self.suit.isDead():
            if self.exitOnWalkFinish == True:
                self.exit()

    def getWalkTrack(self):
        return self.walkTrack

    def isWalking(self):
        if self.walkTrack:
            return self.walkTrack.isPlaying()
        return False
