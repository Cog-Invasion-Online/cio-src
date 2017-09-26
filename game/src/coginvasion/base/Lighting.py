"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Lighting.py
@author Brian Lach
@date September 25, 2017

"""

from panda3d.core import VBase4, Vec3, Point3

from src.coginvasion.globals import CIGlobals

DEFAULT_AMBIENT = VBase4(172 / 255.0, 196 / 255.0, 202 / 255.0, 1.0)

class LightingConfig:

    def __init__(self, ambient):
        self.ambient = ambient
        self.ambientNP = None

    @staticmethod
    def makeDefault():
        return LightingConfig(DEFAULT_AMBIENT)

    def setup(self):
        self.ambientNP = CIGlobals.makeAmbientLight('config', self.ambient)

    def apply(self):
        render.setLight(self.ambientNP)

    def unapply(self):
        render.clearLight(self.ambientNP)

    def remove(self):
        if self.ambientNP:
            self.ambientNP.removeNode()
            self.ambientNP = None

    def cleanup(self):
        self.unapply()
        self.remove()
        self.ambient = None

class OutdoorLightingConfig(LightingConfig):

    def __init__(self, ambient, sun, sunPos, fog, fogDensity):
        LightingConfig.__init__(self, ambient)
        self.sun = sun
        self.sunPos = sunPos
        self.fog = fog
        self.fogDensity = fogDensity
        self.fogNode = None
        self.sunNP = None

        # During winter, we will need to override the fog created here with the fog from snow effect.
        # This flag specifies whether or not we are going to be overriding the fog created here.
        # If it's true, we won't even create or apply any fog to the scene in this class.
        self.winterOverride = False

    @staticmethod
    def makeDefault():
        return OutdoorLightingConfig(DEFAULT_AMBIENT,
                                     VBase4(252 / 255.0, 239 / 255.0, 209 / 255.0, 1.0),
                                     Vec3(-150, 50, 500),
                                     VBase4(0.8, 0.8, 1.0, 1.0),
                                     0.001)

    def setup(self):
        LightingConfig.setup(self)
        self.sunNP = CIGlobals.makeDirectionalLight('config', self.sun, self.sunPos)
        if not self.winterOverride:
            self.fogNode = CIGlobals.makeFog('config', self.fog, self.fogDensity)

    def apply(self):
        LightingConfig.apply(self)
        render.setLight(self.sunNP)
        if not self.winterOverride:
            render.setFog(self.fogNode)

    def unapply(self):
        LightingConfig.unapply(self)
        render.clearLight(self.sunNP)
        if not self.winterOverride:
            render.clearFog()

    def remove(self):
        LightingConfig.remove(self)
        if self.sunNP:
            self.sunNP.removeNode()
            self.sunNP = None

    def cleanup(self):
        LightingConfig.cleanup(self)
        self.sun = None
        self.sunPos = None
        self.fog = None
        self.fogDensity = None
        self.fogNode = None
        self.winterOverride = None

class IndoorLightingConfig(LightingConfig):

    def __init__(self, ambient, light, lights):
        LightingConfig.__init__(self, ambient)
        self.light = light
        self.lights = lights
        self.lightNPs = []

    @staticmethod
    def makeDefault():
        return IndoorLightingConfig(VBase4(252 / 255.0, 239 / 255.0, 209 / 255.0, 1.0),
                                    VBase4(0.7, 0.7, 0.7, 1.0),
                                    [Point3(0, 10, 11.5)])

    def setup(self):
        LightingConfig.setup(self)
        for lightPos in self.lights:
            light = CIGlobals.makePointLight('config', self.light, lightPos)
            self.lightNPs.append(light)

    def apply(self):
        LightingConfig.apply(self)
        for light in self.lightNPs:
            render.setLight(light)

    def unapply(self):
        LightingConfig.unapply(self)
        for light in self.lightNPs:
            render.clearLight(light)

    def remove(self):
        LightingConfig.remove(self)

        for light in self.lightNPs:
            if not light.isEmpty():
                light.removeNode()

        self.lightNPs = []

    def cleanup(self):
        LightingConfig.cleanup(self)
        self.lights = None
        self.light = None