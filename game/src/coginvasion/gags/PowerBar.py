"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PowerBar.py
@author Brian Lach
@date June 29, 2018

"""

from panda3d.core import NodePath

from direct.gui.DirectGui import DirectWaitBar, DGG

import math

class PowerBar(NodePath):

    def __init__(self):
        NodePath.__init__(self, 'pbar')
        self.bar = DirectWaitBar(range = 150, frameColor = (1, 1, 1, 1), barColor = (0.286, 0.901, 1, 1), relief = DGG.RAISED,
                               borderWidth = (0.04, 0.04), pos = (0, 0, 0.85), scale = 0.2, hpr = (0, 0, 0),
                               parent = self, frameSize = (-0.85, 0.85, -0.12, 0.12))
        self.hide()
        self.reparentTo(aspect2d)
        self.speed = 0.2
        self.exponent = 0.75
        self.startTime = 0.0
        self.task = None
        
    def __getPower(self, time):
        elapsed = max(time - self.startTime, 0.0)
        t = elapsed / self.speed
        t = math.pow(t, self.exponent)
        power = int(t * 150) % 300
        if power > 150:
            power = 300 - power
        return power
        
    def getPower(self):
        return self.bar['value']
        
    def start(self):
        self.startTime = globalClock.getFrameTime()
        self.task = taskMgr.add(self.__powerBarUpdate, "powerBarUpdate-" + str(id(self)))
        self.show()
        
    def __powerBarUpdate(self, task):
        self.bar['value'] = self.__getPower(globalClock.getFrameTime())
        return task.cont
        
    def stop(self, hideAfter = -1):
        if self.task:
            self.task.remove()
        self.task = None
        if hideAfter != -1:
            taskMgr.doMethodLater(hideAfter, self.__hideBarTask, "hideBarTask-" + str(id(self)))
            
    def __hideBarTask(self, task):
        self.hide()
        return task.done
        
    def destroy(self):
        taskMgr.remove("hideBarTask-" + str(id(self)))
        self.stop()
        self.speed = None
        self.exponent = None
        self.startTime = None
        self.bar.destroy()
        self.bar = None
        self.removeNode()