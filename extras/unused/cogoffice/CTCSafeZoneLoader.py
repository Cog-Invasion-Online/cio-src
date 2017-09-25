########################################
# Filename: CTCSafeZoneLoader.py
# Created by: blach (14Dec14)
########################################

from panda3d.core import TransparencyAttrib
from lib.coginvasion.holiday.HolidayManager import HolidayType
import CTCPlayground
from lib.coginvasion.hood import SafeZoneLoader

class CTCSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = CTCPlayground.CTCPlayground
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Factory_v3.ogg'
        self.interiorMusicFilename = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.battleMusicFile = 'phase_3.5/audio/bgm/encntr_general_bg.ogg'
        self.invasionMusicFiles = [
            "phase_12/audio/bgm/BossBot_CEO_v1.ogg",
            "phase_9/audio/bgm/encntr_suit_winning.ogg"
        ]
        self.tournamentMusicFiles = [
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_1.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_2.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_3.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_4.ogg",
        ]
        self.bossBattleMusicFile = 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg'
        self.dnaFile = 'phase_4/dna/cog_toontown_central_sz.pdna'
        self.szStorageDNAFile = 'phase_4/dna/storage_TT_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_4/dna/winter_storage_TT_sz.pdna'
        self.telescope = None
        self.birdNoises = [
            'phase_4/audio/sfx/SZ_TC_bird1.ogg',
            'phase_4/audio/sfx/SZ_TC_bird2.ogg',
            'phase_4/audio/sfx/SZ_TC_bird3.ogg'
        ]

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.geom.find('**/hill').setTransparency(TransparencyAttrib.MBinary, 1)
        # It has to be to Toontown Central.
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.geom.find('**/mainFloor').setTexture(loader.loadTexture('winter/maps/winter_ground.jpg'), 1)
        #self.telescope = Actor(self.geom.find('**/*animated_prop_HQTelescopeAnimatedProp*'),
        #                    {"chan": "phase_3.5/models/props/HQ_telescope-chan.bam"}, copy=0)
        #self.telescope.reparentTo(self.geom.find('**/*toon_landmark_hqTT*'))
        #hq = self.geom.find('**/*toon_landmark_hqTT*')
        #hq.find('**/doorFrameHoleLeft_0').stash()
        #hq.find('**/doorFrameHoleRight_0').stash()
        #hq.find('**/doorFrameHoleLeft_1').stash()
        #hq.find('**/doorFrameHoleRight_1').stash()

    def unload(self):
        #self.telescope.cleanup()
        #self.telescope = None
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def createSafeZone(self, dnaFile):
        # We need to load the town storage for the Cog buildings.
        loader.loadDNAFile(self.hood.dnaStore, 'phase_5/dna/storage_town.pdna')
        SafeZoneLoader.SafeZoneLoader.createSafeZone(self, dnaFile)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)
        taskMgr.add(self.telescopeTask, "CTCSafeZoneLoader-telescopeTask")

    def telescopeTask(self, task):
        if self.telescope:
            self.telescope.play("chan")
            task.delayTime = 12.0
            return task.again
        else:
            return task.done

    def exit(self):
        taskMgr.remove("CTCSafeZoneLoader-telescopeTask")
        SafeZoneLoader.SafeZoneLoader.exit(self)
