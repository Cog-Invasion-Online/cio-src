"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MGPlayground.py
@author Brian Lach
@date January 05, 2015

"""

from Playground import Playground
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

class MGPlayground(Playground):
    notify = directNotify.newCategory("MGPlayground")

    def load(self):
        Playground.load(self)
        #spec = base.waterReflectionMgr.getDefaultSpec('ttcPond')
        #base.waterReflectionMgr.addWaterNode((-200, 200, -100, 100), (313.22, 486.94, 18.58082),
        #                                     depth = 8.5, spec = spec)
        #base.waterReflectionMgr.addWaterNode(200, (-315.522, -275.181, 24.37695),
        #                                     depth = 16.94695, spec = spec)
