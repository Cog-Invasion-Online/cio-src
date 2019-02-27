"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSewer.py
@author Brian Lach
@date July 12, 2018

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.battle.DistributedBattleZone import DistributedBattleZone
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.base.Lighting import OutdoorLightingConfig
from src.coginvasion.hood.SkyUtil import SkyUtil
from src.coginvasion.globals import BSPUtility

class DistributedSewer(DistributedBattleZone):
    notify = directNotify.newCategory("DistributedSewer")

    def __init__(self, cr):
        DistributedBattleZone.__init__(self, cr)
        self.skyNP = None
        self.skyEffect = None

    def loadMap(self, mapFile):
        self.stopPlayer()

        base.transitions.fadeScreen(1.0)

        base.bspLoader.read(mapFile)
        base.bspLevel = base.bspLoader.getResult()
        base.bspLoader.doOptimizations()
        base.materialData = PhysicsUtils.makeBulletCollFromGeoms(base.bspLevel.find("**/model-0"))
        for prop in base.bspLevel.findAllMatches("**/+BSPProp"):
            base.createAndEnablePhysicsNodes(prop)
        #base.setupNavMesh(base.bspLevel.find("**/model-0"))
        base.bspLevel.prepareScene(base.win.getGsg())
        
        for entnum in xrange(base.bspLoader.getNumEntities()):
            classname = base.bspLoader.getEntityValue(entnum, "classname")
            if classname == "worldspawn":
                skyType = 1#base.bspLoader.getEntityValueInt(entnum, "skytype")
                if True:#skyType != OutdoorLightingConfig.STNone:
                    self.skyNP = loader.loadModel(OutdoorLightingConfig.SkyData[skyType][0])
                    self.skyNP.reparentTo(camera)
                    self.skyNP.setZ(-300)
                    self.skyNP.setHpr(0, 0, 0)
                    self.skyNP.setLightOff(1)
                    self.skyNP.setFogOff(1)
                    BSPUtility.applyUnlitOverride(self.skyNP)
                    self.skyNP.setMaterialOff(1)
                    self.skyNP.setCompass()
                    if OutdoorLightingConfig.SkyData[skyType][1]:
                        self.skyEffect = SkyUtil()
                        self.skyEffect.startSky(self.skyNP)

        self.sendUpdate('mapLoaded')

    def stopPlayer(self):
        base.localAvatar.stopPlay()

    def startPlayer(self):
        #render.setRenderModeWireframe()
        
        #base.bspLevel.writeBamFile("bspLevel.bam")
    
        base.localAvatar.startPlay(gags = True, laff = True)

    def startLevel(self):
        base.bspLevel.reparentTo(render)
        self.putPlayerAtStart()
        self.startPlayer()

        base.transitions.irisIn()

    def putPlayerAtStart(self):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.collisionsOff()
        if base.localAvatar.walkControls.getCollisionsActive():
            base.localAvatar.walkControls.setCollisionsActive(0)

        for entnum in xrange(base.bspLoader.getNumEntities()):
            classname = base.bspLoader.getEntityValue(entnum, "classname")
            if classname == "info_player_start":
                origin = base.bspLoader.getEntityValueVector(entnum, "origin")
                angles = base.bspLoader.getEntityValueVector(entnum, "angles")
                base.localAvatar.setPos(origin / 16.0)
                base.localAvatar.setHpr(angles[1] - 90, angles[0], angles[2])
                base.localAvatar.walkControls.controller.placeOnGround()

    def announceGenerate(self):
        DistributedBattleZone.announceGenerate(self)
        self.linkSewerEntities()
        self.sendUpdate('ready')

    def disable(self):
        base.bspLoader.cleanup()
        if base.bspLevel and not base.bspLevel.isEmpty():
            base.disableAndRemovePhysicsNodes(base.bspLevel)
            base.bspLevel.removeNode()
        base.bspLevel = None
        base.materialData = {}
        if self.skyEffect:
            self.skyEffect.stopSky()
            self.skyEffect.cleanup()
            self.skyEffect = None
        if self.skyNP:
            self.skyNP.removeNode()
            self.skyNP = None
        DistributedBattleZone.disable(self)

    def linkSewerEntities(self):
        # Purely client-sided entities

        from src.coginvasion.szboss import AmbientGeneric, FuncWater, Ropes, InfoBgm, InfoPlayerRelocate, EnvLightGlow, EnvParticleSystem
        #base.bspLoader.linkEntityToClass("ambient_generic", AmbientGeneric.AmbientGeneric)
        base.bspLoader.linkEntityToClass("func_water", FuncWater.FuncWater)
        base.bspLoader.linkEntityToClass("rope_begin", Ropes.RopeBegin)
        base.bspLoader.linkEntityToClass("rope_keyframe", Ropes.RopeKeyframe)
        base.bspLoader.linkEntityToClass("info_bgm", InfoBgm.InfoBgm)
        base.bspLoader.linkEntityToClass("info_player_relocate", InfoPlayerRelocate.InfoPlayerRelocate)
        base.bspLoader.linkEntityToClass("env_lightglow", EnvLightGlow.EnvLightGlow)
        base.bspLoader.linkEntityToClass("env_particlesystem", EnvParticleSystem.EnvParticleSystem)
