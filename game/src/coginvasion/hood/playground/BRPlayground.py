"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRPlayground.py
@author Brian Lach
@date July 01, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import Playground

class BRPlayground(Playground.Playground):
    notify = directNotify.newCategory("BRPlayground")
    
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.windSfx = None

    def load(self):
        Playground.Playground.load(self)
        base.waterReflectionMgr.addWaterNode(20, (-58, -25, base.wakeWaterHeight), depth = 2.06)
        
    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        
    def exit(self):
        Playground.Playground.exit(self)
        
    def unload(self):
        Playground.Playground.unload(self)
