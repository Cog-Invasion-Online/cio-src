# Filename: BRHood.py
# Created by:  blach (01Jul15)

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

from playground import BRSafeZoneLoader
from street import BRTownLoader

import ToonHood

class BRHood(ToonHood.ToonHood):

	def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
		ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
		self.id = CIGlobals.TheBrrrgh
		self.safeZoneLoader = BRSafeZoneLoader.BRSafeZoneLoader
		self.townLoader = BRTownLoader.BRTownLoader
		self.abbr = "BR"
		self.storageDNAFile = "phase_8/dna/storage_BR.pdna"
		self.holidayDNAFile = None
		self.titleColor = (0.25, 0.25, 1.0, 1.0)
		self.loaderDoneEvent = 'BRHood-loaderDone'

	def load(self):
		ToonHood.ToonHood.load(self)
		self.parentFSM.getStateNamed('BRHood').addChild(self.fsm)

	def unload(self):
		self.parentFSM.getStateNamed('BRHood').removeChild(self.fsm)
		ToonHood.ToonHood.unload(self)
