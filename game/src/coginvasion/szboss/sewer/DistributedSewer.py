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

    def setMap(self, mapFile):
        self.stopPlayer()
        base.transitions.fadeScreen(1.0)

        DistributedBattleZone.setMap(self, mapFile)

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
        
