"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Lighting.py
@author Brian Lach
@date September 25, 2017

"""

from panda3d.core import Point3

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood.SkyUtil import SkyUtil
from src.coginvasion.hood.SnowEffect import SnowEffect
from src.coginvasion.base.ShadowCaster import ShadowCaster

class LightingConfig:
    ActiveConfig = None

    def __init__(self, ambient):
        self.ambient = ambient
        self.ambientNP = None
        self.shadows = None

    @staticmethod
    def makeDefault():
        return LightingConfig(DEFAULT_AMBIENT)
        
    def setupAndApply(self):
        self.setup()
        self.apply()
        
    def unapplyAndRemove(self):
        self.unapply()
        self.remove()

    def setup(self):
        self.ambientNP = CIGlobals.makeAmbientLight('config', self.ambient)

    def apply(self):
        if metadata.USE_LIGHTING and not metadata.USE_RENDER_PIPELINE:
            render.setLight(self.ambientNP)
            #if self.shadows:
            #    self.shadows.enable()
        LightingConfig.ActiveConfig = self

    def unapply(self):
        if metadata.USE_LIGHTING and not metadata.USE_RENDER_PIPELINE:
            render.clearLight(self.ambientNP)
            #if self.shadows:
            #    self.shadows.disable()
        if LightingConfig.ActiveConfig == self:
            LightingConfig.ActiveConfig = None

    def remove(self):
        if self.ambientNP:
            self.ambientNP.removeNode()
        self.ambientNP = None
        self.shadows = None

    def cleanup(self):
        self.unapply()
        self.remove()
        self.ambient = None

class OutdoorLightingConfig(LightingConfig):

    ActiveConfig = None

    # Sky types:
    STNone    = 0
    STMidday  = 1
    STCloudy  = 2
    STEvening = 3
    STNight   = 4
    STCog     = 5

    SkyData = {STMidday:    ["phase_3.5/models/props/TT_sky.bam",   True],
               STCloudy:    ["phase_3.5/models/props/BR_sky.bam",   False],
               STEvening:   ["phase_6/models/props/MM_sky.bam",     False],
               STNight:     ["phase_8/models/props/DL_sky.bam",     False],
               STCog:       ["phase_9/models/cogHQ/cog_sky.bam",    False]}

    def __init__(self, ambient, sun, sunAngle, fog, fogDensity, skyType, snow):
        LightingConfig.__init__(self, ambient)
        self.sun = sun
        self.sunAngle = sunAngle
        self.fog = fog
        self.fogDensity = fogDensity
        self.setSkyType(skyType)
        self.fogNode = None
        self.sunNP = None
        self.skyNP = None

        self.skyEffect = None
        self.snowEffect = None

        self.snow = snow if not base.cr.isChristmas() else True

        # During winter, we will need to override the fog created here with the fog from snow effect.
        # This flag specifies whether or not we are going to be overriding the fog created here.
        # If it's true, we won't even create or apply any fog to the scene in this class.
        self.winterOverride = base.cr.isChristmas()

    def setSkyType(self, skyType):
        self.skyType = skyType
        if base.cr.isChristmas() and skyType != OutdoorLightingConfig.STNone:
            self.skyType = OutdoorLightingConfig.STCloudy
        if skyType != OutdoorLightingConfig.STNone:
            self.skyData = OutdoorLightingConfig.SkyData[self.skyType]

    def modifyFog(self, color, density):
        render.clearFog()
        self.fogNode = CIGlobals.makeFog('config', color, density)
        render.setFog(self.fogNode)

    def resetFog(self):
        render.clearFog()
        self.fogNode = CIGlobals.makeFog('config', self.fog, self.fogDensity)
        render.setFog(self.fogNode)

    @staticmethod
    def makeDefault():
        envConfig = base.loader.envConfig

        return OutdoorLightingConfig(envConfig.defaultOutdoorAmbientColor,
                                     envConfig.defaultSunColor,
                                     envConfig.defaultSunAngle,
                                     envConfig.defaultFogColor,
                                     envConfig.defaultFogDensity,
                                     envConfig.defaultSkyType,
                                     False)

    def setup(self):
        LightingConfig.setup(self)
        self.sunNP = CIGlobals.makeDirectionalLight('config', self.sun, self.sunAngle)
        
        #self.shadows = ShadowCaster(self.sunNP)
        if not self.winterOverride:
            self.fogNode = CIGlobals.makeFog('config', self.fog, self.fogDensity)

        if self.skyType != OutdoorLightingConfig.STNone:
            self.skyEffect = SkyUtil()
            self.skyNP = loader.loadModel(self.skyData[0])

        if self.snow:
            self.snowEffect = SnowEffect()
            self.snowEffect.load()

        OutdoorLightingConfig.ActiveConfig = self

    def apply(self):
        if metadata.USE_RENDER_PIPELINE:
            return
        LightingConfig.apply(self)
        
        if metadata.USE_LIGHTING:
            render.setLight(self.sunNP)
            print self.sunNP.node().getDirection()

            # Maybe apply PSSM shadows with this sun light?
            if metadata.USE_REAL_SHADOWS:
                base.shaderGenerator.setSunLight(self.sunNP)

            #base.filters.setVolumetricLighting(self.sunNP)
            if not self.winterOverride:
                render.setFog(self.fogNode)

        if self.skyType != OutdoorLightingConfig.STNone:
            self.skyNP.reparentTo(camera)
            self.skyNP.setZ(0.0)
            self.skyNP.setHpr(0.0, 0.0, 0.0)
            self.skyNP.setLightOff(1)
            self.skyNP.setFogOff(1)
            self.skyNP.setShaderOff(1)
            self.skyNP.setMaterialOff(1)
            self.skyNP.setCompass()
            self.skyNP.hide(CIGlobals.ShadowCameraBitmask)

            self.skyEffect.startSky(self.skyNP)
        
        if self.snow and self.snowEffect:
            self.snowEffect.start()

    def unapply(self):
        if metadata.USE_RENDER_PIPELINE:
            return
        #base.filters.delVolumetricLighting()
        LightingConfig.unapply(self)
        if metadata.USE_LIGHTING:
            render.clearLight(self.sunNP)
            if not self.winterOverride:
                render.clearFog()

        if self.skyType != OutdoorLightingConfig.STNone:
            self.skyNP.reparentTo(hidden)

            self.skyEffect.stopSky()
            
        if self.snow and self.snowEffect:
            self.snowEffect.stop()

    def remove(self):
        LightingConfig.remove(self)
        if self.skyNP:
            self.skyNP.removeNode()
        self.skyNP = None
        if self.sunNP:
            self.sunNP.removeNode()
        self.sunNP = None
        if self.snowEffect:
            self.snowEffect.unload()
        self.snowEffect = None
        if self.skyEffect:
            self.skyEffect.stopSky()
            self.skyEffect.cleanup()
        self.skyEffect = None

        if OutdoorLightingConfig.ActiveConfig == self:
            OutdoorLightingConfig.ActiveConfig = None

    def cleanup(self):
        LightingConfig.cleanup(self)
        self.sun = None
        self.sunAngle = None
        self.fog = None
        self.fogDensity = None
        self.fogNode = None
        self.winterOverride = None
        self.skyType = None
        self.skyData = None
        self.snow = None

class IndoorLightingConfig(LightingConfig):

    def __init__(self, ambient, light, lights):
        LightingConfig.__init__(self, ambient)
        self.light = light
        self.lights = lights
        self.lightNPs = []
        self.visLights = False

    @staticmethod
    def makeDefault():
        envConfig = base.loader.envConfig
        
        return IndoorLightingConfig(envConfig.defaultIndoorAmbientColor,
                                    envConfig.defaultInteriorLightColor,
                                    [Point3(0, 10, 11.5 / 2.0)])

    def setup(self):
        LightingConfig.setup(self)
        for lightPos in self.lights:
            if len(lightPos) == 2:
                pos = lightPos[0]
                falloff = lightPos[1]
            else:
                pos = lightPos
                falloff = 0.3
            light = CIGlobals.makePointLight('config', self.light, pos, falloff)
            self.lightNPs.append(light)
            if self.visLights:
                vis = loader.loadModel("models/smiley.egg.pz")
                vis.reparentTo(light)

    def apply(self):
        if metadata.USE_RENDER_PIPELINE:
            return
        LightingConfig.apply(self)
        if metadata.USE_LIGHTING:
            for light in self.lightNPs:
                render.setLight(light)

    def unapply(self):
        if metadata.USE_RENDER_PIPELINE:
            return
        LightingConfig.unapply(self)
        if metadata.USE_LIGHTING:
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
        self.visLights = None
        self.lightNPs = None