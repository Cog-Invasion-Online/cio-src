"""

  Filename: RecoverSafeZoneLoader.py
  Created by: blach (03Apr15)

"""

from panda3d.core import TransparencyAttrib
from direct.directnotify.DirectNotifyGlobal import directNotify
from SafeZoneLoader import SafeZoneLoader
from RecoverPlayground import RecoverPlayground

class RecoverSafeZoneLoader(SafeZoneLoader):
    notify = directNotify.newCategory("RecoverSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = RecoverPlayground
        self.pgMusicFilename = None
        self.interiorMusicFilename = None
        self.battleMusicFile = None
        self.bossBattleMusicFile = None
        self.tournamentMusicFiles = None
        self.dnaFile = 'phase_5.5/dna/estate_1.dna'
        self.szStorageDNAFile = 'phase_5.5/dna/storage_estate.dna'

    def load(self):
        SafeZoneLoader.load(self)
        self.geom.find('**/Path').setTransparency(TransparencyAttrib.MBinary, 1)
