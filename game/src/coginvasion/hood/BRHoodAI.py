"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRHoodAI.py
@author Brian Lach
@date July 01, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import ToonHoodAI
import ZoneUtil
from playground import DistributedBRPondAI

class BRHoodAI(ToonHoodAI.ToonHoodAI):
	notify = directNotify.newCategory("BRHoodAI")

	def __init__(self, air):
		ToonHoodAI.ToonHoodAI.__init__(self, air, ZoneUtil.TheBrrrghId,
					ZoneUtil.TheBrrrgh)
		self.pond = None
		self.startup()

	def startup(self):
		self.notify.info("Creating hood {0}...".format(ZoneUtil.TheBrrrgh))
		self.dnaFiles = ['phase_8/dna/the_burrrgh_3100.pdna', 'phase_8/dna/the_burrrgh_3200.pdna',
            'phase_8/dna/the_burrrgh_3300.pdna', 'phase_8/dna/the_burrrgh_sz.pdna']
		ToonHoodAI.ToonHoodAI.startup(self)
		# The pond is broken right now without having a proper collisions system. No thanks.
		#self.pond = DistributedBRPondAI.DistributedBRPondAI(self.air)
		#self.pond.generateWithRequired(self.zoneId)
		self.notify.info("Finished creating hood %s" % ZoneUtil.TheBrrrgh)

	def shutdown(self):
		self.notify.info("Shutting down hood %s" % ZoneUtil.TheBrrrgh)
		if self.pond:
			self.pond.requestDelete()
			self.pond = None
		ToonHoodAI.ToonHoodAI.shutdown(self)
		self.notify.info("Finished shutting down hood %s" % ZoneUtil.TheBrrrgh)
