# Filename: CTDLHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from CTHoodAI import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTDLHoodAI(CTHoodAI):
    notify = directNotify.newCategory('DLHoodAI')

    def __init__(self, air):
        self.dnaFiles = ['phase_8/dna/donalds_dreamland_9100.pdna', 'phase_8/dna/donalds_dreamland_9200.pdna']
        CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.DonaldsDreamland], CIGlobals.DonaldsDreamland)
