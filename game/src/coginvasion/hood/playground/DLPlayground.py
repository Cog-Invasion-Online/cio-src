"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLPlayground.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from Playground import Playground

class DLPlayground(Playground):
    notify = directNotify.newCategory("DLPlayground")

    def load(self):
        Playground.load(self)
        base.waterReflectionMgr.addWaterNode(20, (160, 0.35, base.wakeWaterHeight), depth = 2.1)

    def enter(self, requestStatus):
        for lamp in self.loader.lampLights:
            render.setLight(lamp)
        base.prepareScene()
        Playground.enter(self, requestStatus)

    def exit(self):
        for lamp in self.loader.lampLights:
            render.clearLight(lamp)
        Playground.exit(self)
