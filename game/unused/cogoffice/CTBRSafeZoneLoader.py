# Filename: CTBRSafeZoneLoader.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood import BRSafeZoneLoader

class CTBRSafeZoneLoader(BRSafeZoneLoader.BRSafeZoneLoader):
    notify = directNotify.newCategory("CTBRSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        BRSafeZoneLoader.BRSafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg'
