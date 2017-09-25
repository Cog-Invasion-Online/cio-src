# Filename: CTBRHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTBRHoodAI(CTHoodAI.CTHoodAI):
	notify = directNotify.newCategory("CTBRHoodAI")

	def __init__(self, air):
		self.dnaFiles = ['phase_8/dna/the_burrrgh_3100.pdna', 'phase_8/dna/the_burrrgh_3200.pdna',
            'phase_8/dna/the_burrrgh_3300.pdna']
		CTHoodAI.CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.TheBrrrgh], CIGlobals.TheBrrrgh)
