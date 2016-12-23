# Filename: CTPlayground.py
# Created by:  blach (14Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.gui.DirectGui import DirectButton, DirectLabel

from src.coginvasion.hood.playground import Playground

import random

class CTPlayground(Playground.Playground):
    notify = directNotify.newCategory('CTPlayground')

    LightningRange = [15, 30]

    def enter(self, rs):
        Playground.Playground.enter(self, rs)
        self.loader.rain.start(parent = camera, renderParent = self.loader.rainRender)
        base.playSfx(self.loader.soundRain, looping = 1)
        render.setFog(self.loader.fog)
        waitTime = random.uniform(self.LightningRange[0], self.LightningRange[1])
        taskMgr.doMethodLater(waitTime, self.__lightningTask, 'CTPlayground.LightningTask')
        self.lightningTrack = None

    def __lightningTask(self, task):
        sound = random.choice(self.loader.thunderSounds)
        sound.play()
        self.lightningTrack = Sequence()
        numStrikes = random.randint(1, 3)
        for _ in range(numStrikes):
            self.lightningTrack.append(Func(self.loader.fog.setColor, 1.0, 1.0, 1.0))
            self.lightningTrack.append(Wait(0.1))
            self.lightningTrack.append(Func(self.loader.fog.setColor, 0.3, 0.3, 0.3))
            self.lightningTrack.append(Wait(0.1))
        self.lightningTrack.start()
        waitTime = random.uniform(self.LightningRange[0], self.LightningRange[1])
        task.delayTime = waitTime
        return task.again

    def exit(self):
        taskMgr.remove('CTPlayground.LightningTask')
        if self.lightningTrack:
            self.lightningTrack.finish()
            self.lightningTrack = None
        render.clearFog()
        self.loader.soundRain.stop()
        self.loader.rain.cleanup()
        Playground.Playground.exit(self)
