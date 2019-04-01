from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Func
from direct.distributed.ClockDelta import globalClockDelta

from panda3d.core import Point3

class LinearProjectileShared:

    def __init__(self):
        self.linearDuration = 0.0
        self.linearStart = [0, 0, 0]
        self.linearEnd = [0, 0, 0]
        self.linearTimestamp = 0.0

    def setLinear(self, linearDuration, linearStart, linearEnd, timestamp):
        self.linearDuration = linearDuration
        self.linearStart = linearStart
        self.linearEnd = linearEnd
        self.linearTimestamp = timestamp

        self.setPos(*self.linearStart)

    def playLinear(self):
        ts = globalClockDelta.localElapsedTime(self.linearTimestamp)
        self.ival = Sequence(LerpPosInterval(self, self.linearDuration, Point3(*self.linearEnd), Point3(*self.linearStart)),
                             Func(self.ivalFinished))
        self.ival.start(0)#ts)

    def getLinear(self):
        return [self.linearDuration, self.linearStart, self.linearEnd, self.linearTimestamp]

    def cleanup(self):
        del self.linearDuration
        del self.linearStart
        del self.linearEnd
        del self.linearTimestamp