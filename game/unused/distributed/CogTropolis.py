# Filename: CogTropolis.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cthood import CTCHood
from lib.coginvasion.cthood import CTBRHood
from lib.coginvasion.cthood import CTDLHood
from lib.coginvasion.cthood import CTMLHood
from lib.coginvasion.cthood import CTDGHood
from lib.coginvasion.cthood import CTDDHood
from World import World

class CogTropolis(World):
    notify = directNotify.newCategory('CogTropolis')
    Hood2HoodClass = {CIGlobals.CogTropCentral: CTCHood.CTCHood,
                CIGlobals.TheBrrrgh: CTBRHood.CTBRHood,
                CIGlobals.DonaldsDreamland: CTDLHood.CTDLHood,
                CIGlobals.MinniesMelodyland: CTMLHood.CTMLHood,
                CIGlobals.DaisyGardens: CTDGHood.CTDGHood,
                CIGlobals.DonaldsDock: CTDDHood.CTDDHood}
    Hood2HoodState = {CIGlobals.CogTropCentral: 'TTHood',
                CIGlobals.TheBrrrgh: 'BRHood',
                CIGlobals.DonaldsDreamland: 'DLHood',
                CIGlobals.MinniesMelodyland: 'MLHood',
                CIGlobals.DaisyGardens: 'DGHood',
                CIGlobals.DonaldsDock: 'DDHood'}

    def __init__(self, parentFSM, doneEvent):
        World.__init__(self, doneEvent)
        self.fsm.setName(CIGlobals.CogTropolis)
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed(CIGlobals.CogTropolis).addChild(self.fsm)

    def enterDDHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDDHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DonaldsDock

    def enterDGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DaisyGardens

    def enterMLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.MinniesMelodyland

    def enterDLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DonaldsDreamland

    def enterBRHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitBRHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.TheBrrrgh

    def enterTTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitTTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.ToontownCentral

    def handleHoodDone(self):
        doneStatus = self.hood.getDoneStatus()
        if doneStatus['zoneId'] == None or doneStatus['world'] != CIGlobals.CogTropolis:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.fsm.request('quietZone', [doneStatus])
