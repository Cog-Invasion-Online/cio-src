"""

  Filename: MGSafeZoneLoader.py
  Created by: blach (05Jan15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
import SafeZoneLoader
import MGPlayground

class MGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    notify = directNotify.newCategory("MGSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = MGPlayground.MGPlayground
        self.pgMusicFilename = 'phase_13/audio/bgm/minigame_area.ogg' #['phase_13/audio/bgm/party_original_theme.ogg',
                                #'phase_13/audio/bgm/party_generic_theme.ogg',
                                #'phase_13/audio/bgm/party_generic_theme_jazzy.ogg',
                                #'phase_13/audio/bgm/party_polka_dance.ogg',
                                #'phase_13/audio/bgm/party_swing_dance.ogg',
                                #'phase_13/audio/bgm/party_waltz_dance.ogg']
        self.interiorMusicFilename = None
        self.battleMusicFile = None
        self.invasionMusicFiles = None
        self.tournamentMusicFiles = None
        self.bossBattleMusicFile = None
        self.dnaFile = 'phase_13/dna/party_sz.pdna'
        self.szStorageDNAFile = ['phase_4/dna/storage_TT.pdna',
								 'phase_4/dna/storage_TT_sz.pdna',
								 
								 'phase_6/dna/storage_MM.pdna',
								 'phase_6/dna/storage_MM_sz.pdna',
								 
								 'phase_6/dna/storage_DD.pdna',
								 'phase_6/dna/storage_DD_sz.pdna',
								 
								 'phase_8/dna/storage_DG.pdna',
								 'phase_8/dna/storage_DG_sz.pdna',
								 
								 'phase_8/dna/storage_DL.pdna',
								 'phase_8/dna/storage_DL_sz.pdna',
								 
								 'phase_8/dna/storage_BR.pdna',
								 'phase_8/dna/storage_BR_sz.pdna',
								 
								 'phase_13/dna/storage_party_sz.pdna']
