# Filename: DGPlayground.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.SoundInterval import SoundInterval

import Playground

import random

class DGPlayground(Playground.Playground):
    notify = directNotify.newCategory("DGPlayground")

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.birdSfx = None

    def enter(self, requestStatus):
        self.startBirds()
        Playground.Playground.enter(self, requestStatus)

    def startBirds(self):
        taskMgr.add(self.birdTask, "DGPlayground-birdTask")

    def stopBirds(self):
        taskMgr.remove("DGPlayground-birdTask")
        if self.birdSfx:
            self.birdSfx.finish()
            self.birdSfx = None

    def birdTask(self, task):
        noiseFile = random.choice(self.loader.birdNoises)
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
