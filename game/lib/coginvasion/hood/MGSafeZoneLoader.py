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
        self.szStorageDNAFile = 'phase_13/dna/storage_party_sz.pdna'
