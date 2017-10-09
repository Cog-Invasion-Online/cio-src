"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonHoodAI.py
@author Brian Lach
@date January 05, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.battle.DistributedBattleTrolleyAI import DistributedBattleTrolleyAI
from src.coginvasion.suit import CogBattleGlobals
from src.coginvasion.npc.DistributedDisneyCharAI import DistributedDisneyCharAI
from src.coginvasion.npc.DisneyCharGlobals import *

from HoodAI import HoodAI

class ToonHoodAI(HoodAI):
    notify = directNotify.newCategory("ToonHoodAI")

    def __init__(self, air, zoneId, hood):
        HoodAI.__init__(self, air, zoneId, hood)
        self.gagShop = None
        self.suitManager = None
        self.cogStation = None
        self.dChar = None

    def startup(self):
        HoodAI.startup(self)
        #self.notify.info("Generating gag shop...")
        #self.gagShop = DistributedGagShopAI(self.air)
        #self.gagShop.generateWithRequired(self.zoneId)
        #x, y, z, h, p, r = self.hoodMgr.GagShopClerkPoints[self.hood]
        #self.gagShop.b_setPosHpr(x, y, z ,h, p, r)
        #if base.config.GetBool('want-suits', True):
        #	self.notify.info("Creating suit manager...")
        #	self.suitManager = DistributedSuitManagerAI(self.air)
        #	self.suitManager.generateWithRequired(self.zoneId)
        #else:
        #	self.notify.info("Won't create suits.")

        if HOOD2CHAR[self.hood] is not None:
            self.dChar = DistributedDisneyCharAI(self.air, HOOD2CHAR[self.hood])
            self.dChar.generateWithRequired(self.zoneId)

        hood = self.hood
        if CogBattleGlobals.HoodId2WantBattles[hood] is True:
            self.cogStation = DistributedBattleTrolleyAI(self.air, CIGlobals.MinigameAreaId, 0)
            self.cogStation.generateWithRequired(self.zoneId)
            self.cogStation.b_setState('waitCountdown')

    def shutdown(self):
        if self.gagShop:
            self.notify.info("Shutting down gag shop...")
            self.gagShop.requestDelete()
            self.gagShop = None
        if self.suitManager:
            self.notify.info("Shutting down suit manager...")
            self.suitManager.requestDelete()
            self.suitManager = None
        HoodAI.shutdown(self)
