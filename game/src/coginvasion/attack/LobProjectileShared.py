from direct.distributed.ClockDelta import globalClockDelta

from panda3d.core import Point3

from src.coginvasion.minigame.FlightProjectileInterval import FlightProjectileInterval

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
        self.ival = FlightProjectileInterval(self, startPos = Point3(*self.projStart), endPos = Point3(*self.projEnd),
                                                duration = self.projDuration, gravityMult = self.projGravity)
        self.ival.start(0)#ts)

    def getProjectile(self):
        return [self.projDuration, self.projStart, self.projEnd, self.projGravity, self.projTimestamp]

    def cleanup(self):
        del self.projDuration
        del self.projStart
        del self.projEnd
        del self.projGravity
        del self.projTimestamp
