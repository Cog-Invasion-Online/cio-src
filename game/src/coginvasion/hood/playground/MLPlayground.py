"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MLPlayground.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from Playground import Playground

class MLPlayground(Playground):
    notify = directNotify.newCategory("MLPlayground")

    def load(self):
        Playground.load(self)
        base.waterReflectionMgr.addWaterNode(20, (-0.5, -20, base.wakeWaterHeight), depth = 2.0)
