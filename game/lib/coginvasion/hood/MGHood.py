"""

  Filename: MGHood.py
  Created by: blach (05Jan15)

"""

from lib.coginvasion.globals import CIGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from pandac.PandaModules import TransparencyAttrib
import ToonHood
import MGSafeZoneLoader
import SkyUtil

class MGHood(ToonHood.ToonHood):
    notify = directNotify.newCategory("MGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.fsm.addState(State('minigame', self.enterMinigame, self.exitMinigame))
        self.fsm.getStateNamed('quietZone').addTransition('minigame')
        self.id = CIGlobals.MinigameArea
        self.abbr = "MG"
        self.safeZoneLoader = MGSafeZoneLoader.MGSafeZoneLoader
        self.skyUtil = SkyUtil.SkyUtil()
        self.storageDNAFile = None
        self.holidayDNAFile = None
        self.skyFilename = "phase_3.5/models/props/TT_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
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

    def exitMinigame(self):
        if self.mgWantsLaffMeter:
            base.localAvatar.disableLaffMeter()
            self.mgWantsLaffMeter = None
        base.localAvatar.stopPosHprBroadcast()

    def startSky(self):
        ToonHood.ToonHood.startSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.skyUtil.startSky(self.sky)

    def stopSky(self):
        ToonHood.ToonHood.stopSky(self)
        self.skyUtil.stopSky()
