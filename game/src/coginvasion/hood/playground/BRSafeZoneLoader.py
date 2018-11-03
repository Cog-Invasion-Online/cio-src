"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRSafeZoneLoader.py
@author Brian Lach
@date July 01, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.toon import ParticleLoader
from src.coginvasion.globals import CIGlobals
import SafeZoneLoader
import BRPlayground

class BRSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    notify = directNotify.newCategory("BRSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = BRPlayground.BRPlayground
        self.safeZoneSong = 'TB_nbrhood'
        self.interiorSong = 'TB_SZ_activity'
        self.dnaFile = 'phase_8/dna/the_burrrgh_sz.pdna'
        self.szStorageDNAFile = 'phase_8/dna/storage_BR_sz.pdna'
        self.szHolidayDNAFile = None
        self.telescope = None
        base.wakeWaterHeight = 1.8

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqBR*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()
        
    def doFlatten(self):
        self.geom.find("**/the_burrrgh_anchor").flattenStrong()
        
        brprops = self.geom.attachNewNode('brprops')
        CIGlobals.moveNodes(self.geom, "*snow_pile*_DNARoot", brprops)
        CIGlobals.moveNodes(self.geom, "prop_three*_DNARoot", brprops)
        CIGlobals.moveNodes(self.geom, "*icecube*_DNARoot", brprops)
        CIGlobals.moveNodes(self.geom, "prop_post_three*_DNARoot", brprops)
        CIGlobals.moveNodes(self.geom, "prop_snow_tree*_DNARoot", brprops)
        CIGlobals.moveNodes(self.geom, "prop_stovepipe*_DNARoot", brprops)
        CIGlobals.removeDNACodes(brprops)
        brprops.clearModelNodes()
        brprops.flattenStrong()
    
        SafeZoneLoader.SafeZoneLoader.doFlatten(self)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)
