from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Func

from panda3d.core import Point3

from FlightProjectileInterval import FlightProjectileInterval

class LobProjectileShared:

    def __init__(self):
        self.projDuration = 0
        self.projStart = [0, 0, 0]
        self.projEnd = [0, 0, 0]
        self.projGravity = 1.0
        self.projTimestamp = 0.0

    def setProjectile(self, projDur, projStart, projEnd, projGravity, timestamp):
        self.projDuration = projDur
        self.projStart = projStart
        self.projEnd = projEnd
        self.projGravity = projGravity
        self.projTimestamp = timestamp

        self.setPos(*self.projStart)

    def playProjectile(self):
        ts = globalClockDelta.localElapsedTime(self.projTimestamp)
        p3Start = Point3(*self.projStart)
        p3End = Point3(*self.projEnd)
        self.setPos(p3Start)
        self.headsUp(p3End)
        self.ival = Sequence(FlightProjectileInterval(self, startPos = p3Start, endPos = p3End,
                                                duration = self.projDuration, gravityMult = self.projGravity),
                             Func(self.ivalFinished))
        self.ival.start(0)#ts)

    def getProjectile(self):
        return [self.projDuration, self.projStart, self.projEnd, self.projGravity, self.projTimestamp]

    def cleanup(self):
        del self.projDuration
        del self.projStart
        del self.projEnd
        del self.projGravity
        del self.projTimestamp
