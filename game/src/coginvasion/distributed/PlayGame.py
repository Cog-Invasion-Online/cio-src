"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PlayGame.py
@author Brian Lach
@date November 28, 2014

"""

from src.coginvasion.globals import CIGlobals
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.hood import ZoneUtil

from src.coginvasion.hood import TTHood
from src.coginvasion.hood import MGHood
from src.coginvasion.hood import BRHood
from src.coginvasion.hood import DLHood
from src.coginvasion.hood import MLHood
from src.coginvasion.hood import DGHood
from src.coginvasion.hood import DDHood
from src.coginvasion.hood import CTCHood
from src.coginvasion.cogtropolis import CTHood

from src.coginvasion.hood.QuietZoneState import QuietZoneState

from src.coginvasion.dna.DNALoader import *

class PlayGame(StateData):
    notify = directNotify.newCategory('PlayGame')

    Hood2HoodClass = {ZoneUtil.ToontownCentral: TTHood.TTHood,
                ZoneUtil.MinigameArea: MGHood.MGHood,
                ZoneUtil.TheBrrrgh: BRHood.BRHood,
                ZoneUtil.DonaldsDreamland: DLHood.DLHood,
                ZoneUtil.MinniesMelodyland: MLHood.MLHood,
                ZoneUtil.DaisyGardens: DGHood.DGHood,
                ZoneUtil.DonaldsDock: DDHood.DDHood,
                ZoneUtil.BattleTTC: CTCHood.CTCHood,
                ZoneUtil.CogTropolis: CTHood.CTHood}
    Hood2HoodState = {ZoneUtil.ToontownCentral: 'TTHood',
                ZoneUtil.MinigameArea: 'MGHood',
                ZoneUtil.TheBrrrgh: 'BRHood',
                ZoneUtil.DonaldsDreamland: 'DLHood',
                ZoneUtil.MinniesMelodyland: 'MLHood',
                ZoneUtil.DaisyGardens: 'DGHood',
                ZoneUtil.DonaldsDock: 'DDHood',
                ZoneUtil.BattleTTC: 'CTCHood',
                ZoneUtil.CogTropolis: 'CTHood'}

    def __init__(self, parentFSM, doneEvent):
        StateData.__init__(self, "playGameDone")
        self.doneEvent = doneEvent
        self.fsm = ClassicFSM('World', [State('off', self.enterOff, self.exitOff, ['quietZone']),
                State('quietZone', self.enterQuietZone, self.exitQuietZone, ['TTHood',
                    'BRHood', 'DLHood', 'MLHood', 'DGHood', 'DDHood', 'MGHood', 'CTCHood', 'CTHood']),
                State('TTHood', self.enterTTHood, self.exitTTHood, ['quietZone']),
                State('BRHood', self.enterBRHood, self.exitBRHood, ['quietZone']),
                State('DLHood', self.enterDLHood, self.exitDLHood, ['quietZone']),
                State('MLHood', self.enterMLHood, self.exitMLHood, ['quietZone']),
                State('DGHood', self.enterDGHood, self.exitDGHood, ['quietZone']),
                State('DDHood', self.enterDDHood, self.exitDDHood, ['quietZone']),
                State('MGHood', self.enterMGHood, self.exitMGHood, ['quietZone']),
                State('CTCHood', self.enterCTCHood, self.exitCTCHood, ['quietZone']),
                State('CTHood', self.enterCTHood, self.exitCTHood, ['quietZone'])],
                'off', 'off')
        self.fsm.enterInitialState()

        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('playGame').addChild(self.fsm)

        self.hoodDoneEvent = 'hoodDone'
        self.hood = None
        self.quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.quietZoneStateData = None
        self.place = None
        self.lastHood = None
        self.suitManager = None

    def enter(self, hoodId, zoneId, avId):
        StateData.enter(self)
        whereName = ZoneUtil.getWhereName(zoneId)
        loaderName = ZoneUtil.getLoaderName(zoneId)
        self.fsm.request('quietZone', [{'zoneId': zoneId,
            'hoodId': hoodId,
            'where': whereName,
            'how': 'teleportIn',
            'avId': avId,
            'shardId': None,
            'loader': loaderName}])

    def exit(self):
        StateData.exit(self)

    def getCurrentWorldName(self):
        return self.fsm.getCurrentState().getName()

    def enterOff(self):
        pass

    def exitOff(self):
        pass
        
    def enterCTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitCTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.CogTropolis

    def enterCTCHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitCTCHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.ToontownCentral

    def enterDDHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDDHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.DonaldsDock

    def enterDGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.DaisyGardens

    def enterMLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.MinniesMelodyland

    def enterDLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.DonaldsDreamland

    def enterBRHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitBRHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.TheBrrrgh

    def enterTTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitTTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.ToontownCentral

    def enterMGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = ZoneUtil.MinigameArea

    def handleHoodDone(self):
        doneStatus = self.hood.getDoneStatus()
        if doneStatus['zoneId'] is None:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.fsm.request('quietZone', [doneStatus])

    def loadDNAStore(self):
        if hasattr(self, 'dnaStore'):
            self.dnaStore.reset_nodes()
            self.dnaStore.reset_hood_nodes()
            self.dnaStore.reset_place_nodes()
            self.dnaStore.reset_hood()
            self.dnaStore.reset_fonts()
            self.dnaStore.reset_DNA_vis_groups()
            self.dnaStore.reset_materials()
            self.dnaStore.reset_block_numbers()
            self.dnaStore.reset_block_zones()
            self.dnaStore.reset_suit_points()
            del self.dnaStore

        self.dnaStore = DNAStorage()
        loadDNAFile(self.dnaStore, 'phase_4/dna/storage.pdna')
        self.dnaStore.storeFont('humanist', CIGlobals.getToonFont())
        self.dnaStore.storeFont('mickey', CIGlobals.getMickeyFont())
        self.dnaStore.storeFont('suit', CIGlobals.getSuitFont())
        loadDNAFile(self.dnaStore, 'phase_3.5/dna/storage_interior.pdna')

    def enterQuietZone(self, requestStatus):
        self.acceptOnce(self.quietZoneDoneEvent, self.handleQuietZoneDone, [requestStatus])
        self.acceptOnce('enteredQuietZone', self.handleEnteredQuietZone, [requestStatus])
        self.quietZoneStateData = QuietZoneState(self.quietZoneDoneEvent, 0)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def handleEnteredQuietZone(self, requestStatus):
        hoodId = requestStatus['hoodId']
        if self.Hood2HoodClass.has_key(hoodId):
            hoodClass = self.Hood2HoodClass[hoodId]
            base.transitions.noTransitions()
            loader.beginBulkLoad('hood', hoodId, 100)
            self.loadDNAStore()
            self.hood = hoodClass(self.fsm, self.hoodDoneEvent, self.dnaStore, hoodId)
            self.hood.load()

            hoodState = self.Hood2HoodState[hoodId]
            self.fsm.request(hoodState, [requestStatus], exitCurrent = 0)
        self.quietZoneStateData.fsm.request('waitForSetZoneResponse')

    def handleQuietZoneDone(self, requestStatus):
        if self.hood:
            self.hood.enterTheLoader(requestStatus)
            self.hood.loader.enterThePlace(requestStatus)
            loader.endBulkLoad('hood')
        self.exitQuietZone()

    def exitQuietZone(self):
        if self.quietZoneStateData:
            self.ignore('enteredQuietZone')
            self.ignore(self.quietZoneDoneEvent)
            self.quietZoneStateData.exit()
            self.quietZoneStateData.unload()
            self.quietZoneStateData = None

    def setPlace(self, place):
        self.place = place

    def getPlace(self):
        return self.place
