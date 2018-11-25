"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DDSafeZoneLoader.py
@author Brian Lach
@date July 26, 2015

"""

from panda3d.core import ModelNode

from src.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import DDPlayground

from src.coginvasion.globals import CIGlobals

class DDSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = DDPlayground.DDPlayground
        self.safeZoneSong = 'DD_nbrhood'
        self.interiorSong = 'DD_SZ_activity'
        self.dnaFile = 'phase_6/dna/donalds_dock_sz.pdna'
        self.szStorageDNAFile = 'phase_6/dna/storage_DD_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_6/dna/winter_storage_DD_sz.pdna'
        self.telescope = None
        self.birdNoise = 'phase_6/audio/sfx/SZ_DD_Seagull.ogg'

        self.wRefl = None

        base.wakeWaterHeight = 1.64415

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqDD*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()
        
    def doFlatten(self):
        self.geom.find("**/top_surface").removeNode()
        self.geom.find("**/bottom_surface").removeNode()

        boatMdl = self.geom.find('**/*donalds_boat*')
        boatMdl.setMaterial(CIGlobals.getShinyMaterial())
        wheel = boatMdl.find("**/wheel")
        wheelMdl = wheel.getParent().attachNewNode(ModelNode('wheelNode'))
        wheel.wrtReparentTo(wheelMdl)
        wheelMdl.flattenStrong()
        boat = boatMdl.getParent().attachNewNode(ModelNode('ddBoatRoot'))
        boat.setTransform(boatMdl.getTransform())
        boatMdl1 = boat.attachNewNode(ModelNode('ddBoatMdl1'))
        boatMdl.clearTransform()
        boatMdl.reparentTo(boatMdl1)
        
        self.geom.find("**/donalds_dock_anchor").flattenStrong()
        
        ddprops = self.geom.attachNewNode('ddprops')
        CIGlobals.moveNodes(self.geom, "*streetlight_DD*_DNARoot", ddprops)
        CIGlobals.moveNodes(self.geom, "prop_crate_DNARoot", ddprops)
        CIGlobals.moveNodes(self.geom, "prop_stovepipe_DNARoot", ddprops)
        CIGlobals.moveNodes(self.geom, "prop_chimney_DNARoot", ddprops)
        CIGlobals.moveNodes(self.geom, "*palm_tree*_DNARoot", ddprops)
        CIGlobals.removeDNACodes(ddprops)
        ddprops.clearModelNodes()
        ddprops.flattenStrong()
        
        SafeZoneLoader.SafeZoneLoader.doFlatten(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)
        #self.hood.setWhiteFog()

    def exit(self):
        #self.hood.setNoFog()
        SafeZoneLoader.SafeZoneLoader.exit(self)
