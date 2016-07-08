# Filename: DGSafeZoneLoader.py
# Created by:  blach (24Jul15)

from lib.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import DGPlayground

class DGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = DGPlayground.DGPlayground
        self.pgMusicFilename = 'phase_8/audio/bgm/DG_nbrhood.mid'
        self.interiorMusicFilename = 'phase_8/audio/bgm/DG_SZ.mid'
        self.battleMusicFile = 'phase_3.5/audio/bgm/encntr_general_bg.mid'
        self.invasionMusicFiles = [
            "phase_12/audio/bgm/BossBot_CEO_v1.mid",
            "phase_9/audio/bgm/encntr_suit_winning.mid"
        ]
        self.tournamentMusicFiles = [
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_1.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_2.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_3.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_4.ogg",
        ]
        self.bossBattleMusicFile = 'phase_7/audio/bgm/encntr_suit_winning_indoor.mid'
        self.dnaFile = 'phase_8/dna/daisys_garden_sz.pdna'
        self.szStorageDNAFile = 'phase_8/dna/storage_DG_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_8/dna/winter_storage_DG_sz.pdna'
        self.telescope = None
        self.birdNoises = [
            'phase_8/audio/sfx/SZ_DG_bird_01.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_02.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_03.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_04.ogg'
        ]

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqDG*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()
