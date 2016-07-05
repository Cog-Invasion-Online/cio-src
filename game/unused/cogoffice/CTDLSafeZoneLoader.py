# Filename: CTDLSafeZoneLoader.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.DLSafeZoneLoader import DLSafeZoneLoader

class CTDLSafeZoneLoader(DLSafeZoneLoader):
    notify = directNotify.newCategory("CTDLSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        DLSafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Factory_v2.ogg'
