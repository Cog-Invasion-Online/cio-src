"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRHoodAI.py
@author Brian Lach
@date July 01, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import ToonHoodAI
from playground import DistributedBRPondAI
from src.coginvasion.globals import CIGlobals

class BRHoodAI(ToonHoodAI.ToonHoodAI):
	notify = directNotify.newCategory("BRHoodAI")

	def __init__(self, air):
		ToonHoodAI.ToonHoodAI.__init__(self, air, CIGlobals.TheBrrrghId,
					CIGlobals.TheBrrrgh)
		self.pond = None
		self.startup()

	def startup(self):
		self.notify.info("Creating hood {0}...".format(CIGlobals.TheBrrrgh))
		self.dnaFiles = ['phase_8/dna/the_burrrgh_3100.pdna', 'phase_8/dna/the_burrrgh_3200.pdna',
            'phase_8/dna/the_burrrgh_3300.pdna', 'phase_8/dna/the_burrrgh_sz.pdna']
		ToonHoodAI.ToonHoodAI.startup(self)
		self.pond = DistributedBRPondAI.DistributedBRPondAI(self.air)
		self.pond.generateWithRequired(self.zoneId)
		self.notify.info("Finished creating hood %s" % CIGlobals.TheBrrrgh)

	def shutdown(self):
		self.notify.info("Shutting down hood %s" % CIGlobals.TheBrrrgh)
		if self.pond:
			self.pond.requestDelete()
			self.pond = None
		ToonHoodAI.ToonHoodAI.shutdown(self)
		self.notify.info("Finished shutting down hood %s" % CIGlobals.TheBrrrgh)
