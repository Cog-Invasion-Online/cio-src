"""

  Filename: RecoverHood.py
  Created by: blach (03Apr15)

"""

from ToonHood import ToonHood
from RecoverSafeZoneLoader import RecoverSafeZoneLoader
from SkyUtil import SkyUtil
from lib.coginvasion.globals import CIGlobals
from panda3d.core import TransparencyAttrib
from direct.directnotify.DirectNotifyGlobal import directNotify

class RecoverHood(ToonHood):
    notify = directNotify.newCategory("RecoverHood")
    
    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.RecoverArea
        self.safeZoneLoader = RecoverSafeZoneLoader
        self.skyUtil = SkyUtil()
        self.storageDNAFile = None
        self.skyFilename = "phase_3.5/models/props/TT_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.loaderDoneEvent = 'RecoverHood-loaderDone'
        
    def startSky(self):
        ToonHood.startSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.skyUtil.startSky(self.sky)
        
    def stopSky(self):
        ToonHood.ToonHood.stopSky(self)
        self.skyUtil.stopSky()
