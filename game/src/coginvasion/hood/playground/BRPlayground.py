# Filename: BRPlayground.py
# Created by:  blach (01Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.SoundInterval import SoundInterval

import Playground
import BRWater

import random

class BRPlayground(Playground.Playground):
    notify = directNotify.newCategory("BRPlayground")
    InWaterZ = 0.93
    
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.windSfx = None
        self.water = None
        
    def enter(self, requestStatus):
        self.water = BRWater.BRWater(self)
        Playground.Playground.enter(self, requestStatus)
        
    def exit(self):
        self.water.fsm.requestFinalState()
        Playground.Playground.exit(self)
        
    def unload(self):
        self.water.cleanup()
        self.water = None
        Playground.Playground.unload(self)
        
    def startWaterWatch(self, enter = 1):
        taskMgr.add(self.__waterWatch, "BRPlayground-waterWatch", extraArgs = [enter], appendTask = True)
        
    def __waterWatch(self, enter, task):
        if enter:
            if base.localAvatar.getZ(render) <= self.InWaterZ:
                self.water.fsm.request('freezeUp')
                return task.done
        else:
            if base.localAvatar.getZ(render) > self.InWaterZ:
                if self.water.fsm.getCurrentState().getName() == 'freezeUp':
                    self.water.fsm.request('coolDown')
                    return task.done
        return task.cont
        
    def stopWaterWatch(self):
        taskMgr.remove('BRPlayground-waterWatch')
