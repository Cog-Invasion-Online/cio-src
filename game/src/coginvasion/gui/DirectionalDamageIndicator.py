from panda3d.core import NodePath
from direct.gui.DirectGui import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpColorScaleInterval

import math

DDIByPos = {}

class DirectionalDamageIndicator(NodePath):

    def __init__(self, damagePos):
        NodePath.__init__(self, 'dir-damage-indicator')
        self.reparentTo(aspect2d)
        self.damagePos = damagePos
        self.task = taskMgr.add(self.__update, 'ddi-update')
        self.img = OnscreenImage(image = 'materials/ui/damage_indicator.png', parent = self)
        self.setTransparency(True)
        self.setColorScale((1, 1, 1, 0.5))
        self.setScale(0.25)
        self.time = globalClock.getFrameTime()
        
        self.track = Sequence(
            Wait(1.5),
            LerpColorScaleInterval(self, 0.5, (1, 1, 1, 0), (1, 1, 1, 0.5)),
            Func(self.removeNode)
        )
        self.track.start()
        
        DDIByPos[self.damagePos] = self
        
    @staticmethod
    def make(damagePos):
        if damagePos in DDIByPos:
            DDIByPos[damagePos].removeNode()
        DirectionalDamageIndicator(damagePos)
        
    def removeNode(self):
        del DDIByPos[self.damagePos]
        
        self.track.pause()
        self.track = None
        self.img.destroy()
        self.img = None
        self.time = None
        self.damagePos = None
        self.task.remove()
        self.task = None
        NodePath.removeNode(self)
        
    def __update(self, task):
        camSpacePos = base.cam.getRelativePoint(render, self.damagePos)

        arrowRadians = math.atan2(camSpacePos[0], camSpacePos[1])
        arrowDegrees = (arrowRadians/math.pi) * 180
        self.setR(arrowDegrees)
        
        return task.cont
