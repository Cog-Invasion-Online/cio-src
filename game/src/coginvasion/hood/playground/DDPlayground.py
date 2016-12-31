# Filename: DDPlayground.py
# Created by:  blach (26Jul15)

from direct.interval.SoundInterval import SoundInterval

import Playground

import random
from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.globals import CIGlobals

class DDPlayground(Playground.Playground):
    
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.birdSfx = None
        
        # Let's handle the Christmas effects.
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            water = self.loader.geom.find('**/water')
            water.setCollideMask(CIGlobals.FloorBitmask)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        self.startBirds()

    def startBirds(self):
        taskMgr.add(self.birdTask, "DDPlayground-birdTask")

    def stopBirds(self):
        taskMgr.remove("DDPlayground-birdTask")
        if self.birdSfx:
            self.birdSfx.finish()
            self.birdSfx = None

    def birdTask(self, task):
        noiseFile = self.loader.birdNoise
        noise = base.loadSfx(noiseFile)
        if self.birdSfx:
            self.birdSfx.finish()
            self.birdSfx = None
        self.birdSfx = SoundInterval(noise)
        self.birdSfx.start()
        task.delayTime = random.random() * 20 + 1
        return task.again

    def exit(self):
        self.stopBirds()
        Playground.Playground.exit(self)
