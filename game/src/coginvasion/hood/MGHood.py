"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MGHood.py
@author Brian Lach
@date January 05, 2015

"""

from src.coginvasion.globals import CIGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from panda3d.core import TransparencyAttrib
import ToonHood
from playground import MGSafeZoneLoader

class MGHood(ToonHood.ToonHood):
    notify = directNotify.newCategory("MGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.fsm.addState(State('minigame', self.enterMinigame, self.exitMinigame))
        self.fsm.getStateNamed('quietZone').addTransition('minigame')
        self.id = CIGlobals.MinigameArea
        self.abbr = "MG"
        self.safeZoneLoader = MGSafeZoneLoader.MGSafeZoneLoader
        self.storageDNAFile = None
        self.holidayDNAFile = None
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.loaderDoneEvent = 'MGHood-loaderDone'
        self.mgWantsLaffMeter = None

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('MGHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('MGHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enterMinigame(self, requestStatus):
        if requestStatus['wantLaffMeter']:
            self.mgWantsLaffMeter = True
            base.localAvatar.createLaffMeter()
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.createChatInput()

    def exitMinigame(self):
        if self.mgWantsLaffMeter:
            base.localAvatar.disableLaffMeter()
            self.mgWantsLaffMeter = None
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.disableChatInput()
