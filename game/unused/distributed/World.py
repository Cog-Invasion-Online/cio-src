# Filename: World.py
# Created by:  blach (12Dec15)

from panda3d.core import *

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.StateData import StateData
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.QuietZoneState import QuietZoneState
from lib.coginvasion.dna.DNALoader import *

class World(StateData):
    notify = directNotify.newCategory('World')

    def __init__(self, doneEvent):
        StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM('World', [State('off', self.enterOff, self.exitOff, ['quietZone']),
                State('quietZone', self.enterQuietZone, self.exitQuietZone, ['TTHood',
                    'BRHood', 'DLHood', 'MLHood', 'DGHood', 'DDHood']),
                State('TTHood', self.enterTTHood, self.exitTTHood, ['quietZone']),
                State('BRHood', self.enterBRHood, self.exitBRHood, ['quietZone']),
                State('DLHood', self.enterDLHood, self.exitDLHood, ['quietZone']),
                State('MLHood', self.enterMLHood, self.exitMLHood, ['quietZone']),
                State('DGHood', self.enterDGHood, self.exitDGHood, ['quietZone']),
                State('DDHood', self.enterDDHood, self.exitDDHood, ['quietZone'])],
                'off', 'off')
        self.fsm.enterInitialState()
        self.hoodDoneEvent = 'hoodDone'
        self.hood = None
        self.quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.quietZoneStateData = None
        self.place = None
        self.lastHood = None

    def enter(self, requestStatus):
        StateData.enter(self)
        self.fsm.request('quietZone', [requestStatus])

    def exit(self):
        StateData.exit(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def loadDNAStore(self):
        if hasattr(self, 'dnaStore'):
            self.dnaStore.reset_nodes()
            self.dnaStore.reset_hood_nodes()
            self.dnaStore.reset_place_nodes()
            self.dnaStore.reset_hood()
            self.dnaStore.reset_fonts()
            self.dnaStore.reset_DNA_vis_groups()
            self.dnaStore.reset_textures()
            self.dnaStore.reset_block_numbers()
            self.dnaStore.reset_block_zones()
            self.dnaStore.reset_suit_points()
            del self.dnaStore

        self.dnaStore = DNAStorage()
        loadDNAFile(self.dnaStore, 'phase_4/dna/storage.pdna')
        self.dnaStore.storeFont('humanist', CIGlobals.getToonFont())
        self.dnaStore.storeFont('mickey', CIGlobals.getMickeyFont())
        self.dnaStore.storeFont('suit', CIGlobals.getSuitFont())
        base.cr.playGame.dnaStore = self.dnaStore
        loadDNAFile(self.dnaStore, 'phase_3.5/dna/storage_interior.pdna')

    def enterQuietZone(self, requestStatus):
        self.acceptOnce(self.quietZoneDoneEvent, self.handleQuietZoneDone, [requestStatus])
        self.acceptOnce('enteredQuietZone', self.handleEnteredQuietZone, [requestStatus])
        self.quietZoneStateData = QuietZoneState(self.quietZoneDoneEvent, 0)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def handleEnteredQuietZone(self, requestStatus):
        hoodId = requestStatus['hoodId']
        hoodClass = self.Hood2HoodClass[hoodId]
        base.transitions.noTransitions()
        loader.beginBulkLoad('hood', hoodId, 100)
        self.loadDNAStore()
        self.hood = hoodClass(self.fsm, self.hoodDoneEvent, self.dnaStore, hoodId)
        base.cr.playGame.hood = self.hood
        self.hood.load()

        hoodId = requestStatus['hoodId']
        hoodState = self.Hood2HoodState[hoodId]
        self.fsm.request(hoodState, [requestStatus], exitCurrent = 0)
        self.quietZoneStateData.fsm.request('waitForSetZoneResponse')

    def handleQuietZoneDone(self, requestStatus):
        self.hood.enterTheLoader(requestStatus)
        self.hood.loader.enterThePlace(requestStatus)
        loader.endBulkLoad('hood')
        self.exitQuietZone()

    def exitQuietZone(self):
        self.ignore('enteredQuietZone')
        self.ignore(self.quietZoneDoneEvent)
        self.quietZoneStateData.exit()
        self.quietZoneStateData.unload()
        self.quietZoneStateData = None

    def setPlace(self, place):
        self.place = place

    def getPlace(self):
        return self.place
