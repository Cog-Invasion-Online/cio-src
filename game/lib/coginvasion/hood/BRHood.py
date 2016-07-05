# Filename: BRHood.py
# Created by:  blach (01Jul15)

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.holiday.HolidayManager import HolidayType

import BRSafeZoneLoader
import BRTownLoader
import ToonHood

class BRHood(ToonHood.ToonHood):

	def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
		ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
		self.id = CIGlobals.TheBrrrgh
		self.safeZoneLoader = BRSafeZoneLoader.BRSafeZoneLoader
		self.townLoader = BRTownLoader.BRTownLoader
		self.storageDNAFile = "phase_8/dna/storage_BR.pdna"
		self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
		self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
		self.holidayDNAFile = None
		self.titleColor = (0.25, 0.25, 1.0, 1.0)
		self.loaderDoneEvent = 'BRHood-loaderDone'

	def load(self):
		ToonHood.ToonHood.load(self)
		self.parentFSM.getStateNamed('BRHood').addChild(self.fsm)

	def unload(self):
		self.parentFSM.getStateNamed('BRHood').removeChild(self.fsm)
		ToonHood.ToonHood.unload(self)
