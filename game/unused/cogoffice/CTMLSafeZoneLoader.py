# Filename: CTMLSafeZoneLoader.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.MLSafeZoneLoader import MLSafeZoneLoader

class CTMLSafeZoneLoader(MLSafeZoneLoader):
    notify = directNotify.newCategory("MLSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        MLSafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Entry_v1.ogg'
