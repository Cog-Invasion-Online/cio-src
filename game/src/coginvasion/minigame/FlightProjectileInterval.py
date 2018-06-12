# Filename: FlightProjectileInterval.py
# Created by:  blach (08Jul15)

from panda3d.core import Vec3
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import ProjectileInterval
from direct.task import Task

import math

class FlightProjectileInterval(ProjectileInterval):
    # This class will make the NodePath's pitch change according to the velocity.

    notify = directNotify.newCategory("FlightProjectileInterval")

    def __startPitchTask(self):
        taskMgr.add(self.__calcPitch, "FlightProjectileInterval-calcPitch" + str(id(self)))

    def __stopPitchTask(self):
        taskMgr.remove("FlightProjectileInterval-calcPitch" + str(id(self)))

    def start(self, startT = 0.0, endT = -1.0, playRate = 1.0):
        ProjectileInterval.start(self, startT, endT, playRate)
        self.__startPitchTask()

    def loop(self, startT = 0.0, endT = -1.0, playRate = 1.0):
        ProjectileInterval.loop(self, startT, endT, playRate)
        self.__startPitchTask()

    def pause(self):
        ProjectileInterval.pause(self)
        self.__stopPitchTask()

    def finish(self):
        ProjectileInterval.finish(self)
        self.__stopPitchTask()

    def __toDegrees(self, angle):
        return angle * 360.0 / (2.0 * math.pi)

    def getVel(self, t):
        tt = t - self.getStartT()
        return Vec3(self.startVel[0], self.startVel[1], self.startVel[2] + self.zAcc * tt)

    def __calcPitch(self, task):
        if self.node.isEmpty():
            return Task.done

        t = min(self.getT(), self.getDuration())
        vel = self.getVel(t)
        run = math.sqrt(vel[0] * vel[0] + vel[1] * vel[1])
        rise = vel[2]
        theta = self.__toDegrees(math.atan(rise / run))
        self.node.setP(theta)

        return Task.cont
