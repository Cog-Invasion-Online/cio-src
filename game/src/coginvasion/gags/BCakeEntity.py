from panda3d.core import Point3, Vec3

from direct.actor.Actor import Actor

from src.coginvasion.globals import CIGlobals

import math

class BCakeEntity(Actor):

    def __init__(self):
        Actor.__init__(self, 'phase_5/models/props/birthday-cake-mod.bam')

        self.flames = []
        numFlames = 6
        for flameNum in xrange(numFlames):
            joint = self.controlJoint(None, "modelRoot", "joint_scale_flame{0}".format(flameNum + 1))
            data = {'joint': joint,
                    'lastPos': Point3(0, 0, 0),
                    'lastHpr': Vec3(0, 0, 0),
                    'idealHpr': joint.getHpr()}
            self.flames.append(data)

        taskMgr.add(self.__animateFlames, "animateFlamesTask")

    def __animateFlames(self, task):

        if self.isEmpty():
            del self.flames
            return task.done

        for flame in self.flames:
            pos = flame['joint'].getPos(render)
            lastPos = flame['lastPos']
            delta = (pos - lastPos)
            dir = delta.normalized()
            lagX = math.atan2(delta[0], delta[1]) * 100
            lagY = math.atan2(delta[2], math.sqrt((delta[0] * delta[0]) + (delta[1] * delta[1]))) * 100
            hprGoal = Vec3(0, lagY, lagX)
            flame['lastHpr'] = CIGlobals.lerpWithRatio(hprGoal, flame['lastHpr'], 0.7)
            flame['lastPos'] = pos
            flame['joint'].setHpr(flame['lastHpr'])
            #print flame['joint'].getHpr()

        return task.cont