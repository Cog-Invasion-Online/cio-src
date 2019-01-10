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
        self.avReady = False
        
    def announceGenerate(self):
        DistributedBattleZoneAI.announceGenerate(self)
        
        # Link up networked entities
        from src.coginvasion.szboss import (DistributedTriggerAI, DistributedFuncDoorAI, DistributedIndicatorLightAI,
                                            DistributedSZBossSuitAI, DistributedCutsceneAI, DistributedGoonAI,
                                            DistributedButtonAI, DistributedGeneratorAI, DistributedFuncRotatingAI, LogicCounter)
        self.bspLoader.linkServerEntityToClass("trigger_once",          DistributedTriggerAI.DistributedTriggerOnceAI)
        self.bspLoader.linkServerEntityToClass("trigger_multiple",      DistributedTriggerAI.DistributedTriggerMultipleAI)
        self.bspLoader.linkServerEntityToClass("func_door",             DistributedFuncDoorAI.DistributedFuncDoorAI)
        self.bspLoader.linkServerEntityToClass("npc_goon",              DistributedGoonAI.DistributedGoonAI)
        self.bspLoader.linkServerEntityToClass("npc_suit",              DistributedSZBossSuitAI.DistributedSZBossSuitAI)
        self.bspLoader.linkServerEntityToClass("info_cutscene",         DistributedCutsceneAI.DistributedCutsceneAI)
        self.bspLoader.linkServerEntityToClass("info_indicator_light",  DistributedIndicatorLightAI.DistributedIndicatorLightAI)
        self.bspLoader.linkServerEntityToClass("func_button",           DistributedButtonAI.DistributedButtonAI)
        self.bspLoader.linkServerEntityToClass("func_generator",        DistributedGeneratorAI.DistributedGeneratorAI)
        self.bspLoader.linkServerEntityToClass("func_rotating",         DistributedFuncRotatingAI.DistributedFuncRotatingAI)
        self.bspLoader.linkServerEntityToClass("logic_counter",         LogicCounter.LogicCounter)
        
    def delete(self):
        self.avId = None
        self.avReady = None
        DistributedBattleZoneAI.delete(self)
        
    def deadSuit(self, doId):
        suit = self.air.doId2do.get(doId)
        if suit and suit in self.suits:
            self.suits.remove(suit)

    def mapLoaded(self):
        self.sendUpdate('startLevel')

    def ready(self):
        avId = self.air.getAvatarIdFromSender()

        if self.avReady:
            self.notify.warning("Suspicious: received multiple ready() messages")
            return

        if avId == self.avId:
            self.avReady = True
            self.b_loadMap('phase_14/etc/sewer_entrance_room_indoors/sewer_entrance_room_indoors.bsp')
            #self.b_loadMap('phase_14/etc/testmats/testmats.bsp')
            #self.b_loadMap('phase_14/etc/estate_interior/estate_interior.bsp')
        else:
            self.notify.warning("Suspicious: avIds do not match in ready()")

    def b_loadMap(self, map):
        self.sendUpdate('loadMap', [map])
        self.loadMap(map)
    
    def loadMap(self, map):
        # We wouldn't really do anything on the AI side.
        # But maybe.
        if not self.bspLoader.read(map):
            self.notify.error("Could not read server side BSP file {0}".format(map))
        self.bspLoader.getResult().ls()
        self.setupNavMesh(self.bspLoader.getResult())
