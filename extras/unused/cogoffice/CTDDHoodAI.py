# Filename: CTDDHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from CTHoodAI import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTDDHoodAI(CTHoodAI):
    notify = directNotify.newCategory('CTDDHoodAI')

    def __init__(self, air):
        self.dnaFiles = ['phase_6/dna/donalds_dock_1100.pdna', 'phase_6/dna/donalds_dock_1200.pdna',
            'phase_6/dna/donalds_dock_1300.pdna']
        CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.DonaldsDock], CIGlobals.DonaldsDock)
