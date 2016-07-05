# Filename: CTBRHood.py
# Created by:  blach (12Dec15)

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import BRHood
import CTBRSafeZoneLoader
import CTBRTownLoader

class CTBRHood(BRHood.BRHood):

	def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
		BRHood.BRHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
		self.safeZoneLoader = CTBRSafeZoneLoader.CTBRSafeZoneLoader
		self.townLoader = CTBRTownLoader.CTBRTownLoader
		self.titleColor = (0.5, 0.5, 0.5, 1.0)
