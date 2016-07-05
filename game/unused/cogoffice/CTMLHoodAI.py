# Filename: CTMLHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from CTHoodAI import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTMLHoodAI(CTHoodAI):
    notify = directNotify.newCategory('CTMLHoodAI')

    def __init__(self, air):
        self.dnaFiles = ['phase_6/dna/minnies_melody_land_4100.pdna', 'phase_6/dna/minnies_melody_land_4200.pdna',
            'phase_6/dna/minnies_melody_land_4300.pdna']
        CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.MinniesMelodyland], CIGlobals.MinniesMelodyland)
