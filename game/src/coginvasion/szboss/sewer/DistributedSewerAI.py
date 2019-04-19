"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSewerAI.py
@author Brian Lach
@date July 12, 2018

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.battle import BattleGlobals
from src.coginvasion.battle.DistributedBattleZoneAI import DistributedBattleZoneAI

class DistributedSewerAI(DistributedBattleZoneAI):
    notify = directNotify.newCategory("DistributedSewerAI")

    battleType = BattleGlobals.BTSewer

    def __init__(self, air, avId):
        DistributedBattleZoneAI.__init__(self, air)
        # The avatar that is playing in this sewer.
        self.avId = avId
        self.setAvatars([avId])
        self.suits = []
        
    def generate(self):
        DistributedBattleZoneAI.generate(self)
        
        # Link up networked entities
        from src.coginvasion.szboss import (DistributedIndicatorLightAI,
                                            DistributedSZBossSuitAI, DistributedCutsceneAI, DistributedGoonAI,
                                            DistributedGeneratorAI,
                                            DistributedSZBossToonAI)
        from src.coginvasion.cogoffice.AIEntities import (SuitSpawn)
        from src.coginvasion.battle.DistributedHPBarrelAI import DistributedHPBarrelAI
        from src.coginvasion.battle.DistributedGagBarrelAI import DistributedGagBarrelAI
        #self.bspLoader.linkServerEntityToClass("npc_goon",              DistributedGoonAI.DistributedGoonAI)
        self.bspLoader.linkServerEntityToClass("npc_suit",              DistributedSZBossSuitAI.DistributedSZBossSuitAI)
        self.bspLoader.linkServerEntityToClass("info_cutscene",         DistributedCutsceneAI.DistributedCutsceneAI)
        self.bspLoader.linkServerEntityToClass("info_indicator_light",  DistributedIndicatorLightAI.DistributedIndicatorLightAI)
        self.bspLoader.linkServerEntityToClass("func_generator",        DistributedGeneratorAI.DistributedGeneratorAI)
        self.bspLoader.linkServerEntityToClass("npc_toon",              DistributedSZBossToonAI.DistributedSZBossToonAI)
        self.bspLoader.linkServerEntityToClass("cogoffice_suitspawn",   SuitSpawn)
        self.bspLoader.linkServerEntityToClass("item_gagbarrel",            DistributedGagBarrelAI)
        self.bspLoader.linkServerEntityToClass("item_laffbarrel",           DistributedHPBarrelAI)
        
    def delete(self):
        self.avId = None
        DistributedBattleZoneAI.delete(self)
        
    def deadSuit(self, doId):
        suit = self.air.doId2do.get(doId)
        if suit and suit in self.suits:
            self.suits.remove(suit)

    def loadedMap(self):
        self.sendUpdate('startLevel')

    def handleAvatarsReady(self):
        #self.b_loadMap('phase_14/etc/sewer_entrance_room_indoors/sewer_entrance_room_indoors.bsp')
        #self.b_loadMap('phase_14/etc/testmats/testmats.bsp')
        #self.b_loadMap('phase_14/etc/estate_interior/estate_interior.bsp')
        #self.b_loadMap("phase_14/etc/test_attacks/test_attacks.bsp")
        self.b_setMap('test_ai_arena')
