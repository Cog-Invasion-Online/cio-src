"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagShopInterior.py
@author Brian Lach
@date November 6, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from libpandadna import *
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.hood import ToonInteriorColors
from src.coginvasion.hood import DistributedToonInterior

import random

class DistributedGagShopInterior(DistributedToonInterior.DistributedToonInterior):
    notify = directNotify.newCategory('DistributedGagShopInterior')

    def makeInterior(self, roomIndex = None):
        self.dnaStore = self.cr.playGame.dnaStore
        self.generator = random.Random()
        self.generator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_4/models/modules/gagShop_interior.bam')
        self.interior.reparentTo(render)
        hoodId = ZoneUtil.getHoodId(self.zoneId, 1)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        door = self.dnaStore.findNode('door_double_round_ur')
        doorOrigin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(doorOrigin)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        doorColor = self.generator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, doorOrigin, self.dnaStore, self.block, doorColor)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(doorColor)
        del self.colors
        del self.dnaStore
        del self.generator
        self.addLightsForLamps()
