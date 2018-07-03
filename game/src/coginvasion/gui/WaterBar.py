"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterBar.py
@author Brian Lach
@date July 3, 2018

"""

from panda3d.core import NodePath

from direct.gui.DirectGui import OnscreenImage, DirectWaitBar

class WaterBar(NodePath):

    def __init__(self):
        NodePath.__init__(self, 'waterBar')
        
        self.range = 100
        self.value = 100
        
        self.back = OnscreenImage("phase_14/maps/backv2.png", scale = (0.289, 1, 0.813), parent = self)
        self.bar = OnscreenImage("phase_14/maps/frontv2.png", scale = (0.233, 1, 0.740), parent = self)
        self.setTransparency(1)
        
        barSh = loader.loadShader("phase_14/models/shaders/progress_bar.sha")
        self.bar.setShader(barSh)
        self.bar.setShaderInput("tex", loader.loadTexture("phase_14/maps/frontv2.png"))
        self.bar.setShaderInput("perct", float(self.value) / float(self.range))
        self.bar.setShaderInput("dir", 0)
        self.bar.setShaderInput("alpha", 1.0)
        
        self.task = taskMgr.add(self.__update, "WaterBar.update")
        
    def removeNode(self):
        self.task.remove()
        self.task = None
        self.back.destroy()
        self.back = None
        self.bar.destroy()
        self.bar = None
        self.range = None
        self.value = None
        NodePath.removeNode(self)
        
    def setDirection(self, dir):
        self.bar.setShaderInput("dir", dir)
        
    def setBarAlpha(self, alpha):
        self.bar.setShaderInput("alpha", alpha)
        
    def __update(self, task):
        self.bar.setShaderInput("perct", float(self.value) / float(self.range))
        
        return task.cont