#

from panda3d.core import Fog

from direct.interval.IntervalGlobal import SoundInterval

from src.coginvasion.toon import ParticleLoader

import random

class SnowEffect:

    def __init__(self, hood = None):
        self.hood = hood
        self.particles = None
        self.particlesRender = None
        self.fog = None
        self.windSfx = None
        self.loaded = False
        self.windNoises = [
            'phase_8/audio/sfx/SZ_TB_wind_1.ogg',
            'phase_8/audio/sfx/SZ_TB_wind_2.ogg',
            'phase_8/audio/sfx/SZ_TB_wind_3.ogg'
        ]

    def startWind(self):
        taskMgr.add(self.windTask, "BRPlayground-windTask")

    def stopWind(self):
        taskMgr.remove("BRPlayground-windTask")
        if self.windSfx:
            self.windSfx.finish()
            self.windSfx = None

    def windTask(self, task):
        noiseFile = random.choice(self.windNoises)
        noise = base.loadSfx(noiseFile)
        if self.windSfx:
            self.windSfx.finish()
            self.windSfx = None
        self.windSfx = SoundInterval(noise)
        self.windSfx.start()
        task.delayTime = random.random() * 20 + 1
        return task.again

    def load(self):
        if self.loaded:
            return
            
        
        self.particlesRender = render.attachNewNode('snowRender')
        self.particlesRender.setDepthWrite(0)
        self.particlesRender.setBin('fixed', 1)
        self.particlesRender.setLightOff(1)
        self.particlesRender.setMaterialOff(1)
        self.fog = Fog('snowFog')
        self.fog.setColor(0.486, 0.784, 1)
        self.fog.setExpDensity(0.003)
        
        self.loaded = True

    def start(self):
        self.particles = ParticleLoader.loadParticleEffect('phase_8/etc/snowdisk.ptf')
        self.particles.setPos(0, 0, 5)
        self.particles.start(parent = camera, renderParent = self.particlesRender)

        # Only use the fog if it's christmas.
        # This class is used by the Brrrgh all the time, but
        # it will use the OutdoorLightingConfig fog.
        if base.cr.isChristmas():
            base.render.setFog(self.fog)

        self.startWind()

    def stop(self):
        self.stopWind()
        if self.particles:
            self.particles.softStop()
            self.particles = None
        if base.cr.isChristmas():
            base.render.clearFog()

    def unload(self):
        if not self.loaded:
            return

        base.render.clearFog()
        self.fog = None

        if self.particlesRender:
            self.particlesRender.removeNode()
            self.particlesRender = None
            
        if self.particles:
            self.particles.cleanup()
            self.particles = None
            
        self.loaded = False