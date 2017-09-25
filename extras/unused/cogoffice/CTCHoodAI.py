# Filename: CTCHoodAI.py
# Created by:  blach (13Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from CTHoodAI import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTCHoodAI(CTHoodAI):
    notify = directNotify.newCategory('CTCHoodAI')

    def __init__(self, air):
        self.dnaFiles = ['phase_5/dna/toontown_central_2100.pdna', 'phase_5/dna/toontown_central_2200.pdna',
            'phase_5/dna/toontown_central_2300.pdna']
        CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.CogTropCentral], CIGlobals.CogTropCentral)
