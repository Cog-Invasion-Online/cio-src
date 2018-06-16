"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MGHoodAI.py
@author Brian Lach
@date January 05, 2015

"""

import HoodAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.globals import CIGlobals
from src.coginvasion.minigame.DistributedMinigameStationAI import DistributedMinigameStationAI
from src.coginvasion.battle.DistributedBattleTrolleyAI import DistributedBattleTrolleyAI
from src.coginvasion.cog import CogBattleGlobals
import ZoneUtil

class MGHoodAI(HoodAI.HoodAI):
    notify = directNotify.newCategory("MGHoodAI")
    notify.setInfo(True)
    minigames = [CIGlobals.RaceGame,
                CIGlobals.UnoGame,
                CIGlobals.GunGame,
                CIGlobals.CameraShyGame,
                CIGlobals.EagleGame,
                CIGlobals.FactoryGame,
                CIGlobals.DeliveryGame,
                CIGlobals.DodgeballGame]

    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air, ZoneUtil.MinigameAreaId,
                            ZoneUtil.MinigameArea)
        self.stations = []
        self.trolley = None
        self.startup()

    def startup(self):
        self.dnaFiles = []
        HoodAI.HoodAI.startup(self)
        
        # Trolley index 1 indicates minigame area trolley
        # which sends toons back to their last playground.
        trolley = DistributedBattleTrolleyAI(self.air, 0, 1)
        trolley.generateWithRequired(self.zoneId)
        trolley.b_setState('wait')
            
        self.trolley = trolley

        self.notify.info("Creating minigames...")

        if base.config.GetBool('want-minigames', True):

            if not base.config.GetBool('want-race-game', True):
                self.notify.info("Excluding %s" % CIGlobals.RaceGame)
                self.minigames.remove(CIGlobals.RaceGame)

            if not base.config.GetBool('want-uno-game', True):
                self.notify.info("Excluding %s" % CIGlobals.UnoGame)
                self.minigames.remove(CIGlobals.UnoGame)

            if not base.config.GetBool('want-toon-battle', True):
                self.notify.info("Excluding %s" % CIGlobals.GunGame)
                self.minigames.remove(CIGlobals.GunGame)

            if not base.config.GetBool('want-factory-sneak', True):
                self.notify.info("Excluding %s" % CIGlobals.FactoryGame)
                self.minigames.remove(CIGlobals.FactoryGame)

            if not base.config.GetBool('want-camera-shy', True):
                self.notify.info("Excluding %s" % CIGlobals.CameraShyGame)
                self.minigames.remove(CIGlobals.CameraShyGame)

            if not base.config.GetBool('want-eagle-game', True):
                self.notify.info("Excluding %s" % CIGlobals.EagleGame)
                self.minigames.remove(CIGlobals.EagleGame)

            if not base.config.GetBool('want-delivery-game', True):
                self.notify.info('Excluding %s' % CIGlobals.DeliveryGame)
                self.minigames.remove(CIGlobals.DeliveryGame)

            if not base.config.GetBool('want-dodgeball-game', True):
                self.notify.info("Excluding %s" % CIGlobals.DodgeballGame)
                self.minigames.remove(CIGlobals.DodgeballGame)

            for name in self.minigames:
                index = self.minigames.index(name)
                mg = DistributedMinigameStationAI(self.air)
                mg.generateWithRequired(self.zoneId)
                mg.b_setStation(name)
                mg.b_setLocationPoint(index)
                self.stations.append(mg)
        else:
            self.notify.info("Nevermind, config file says not to create any minigames.")

    def shutdown(self):
        self.notify.info("Shutting down minigames...")
        if self.trolley:
            self.trolley.requestDelete()
            self.trolley = None
        for station in self.stations:
            station.requestDelete()
            self.stations.remove(station)
            del station
        del self.stations
        HoodAI.HoodAI.shutdown(self)
