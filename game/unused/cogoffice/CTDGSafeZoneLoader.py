# Filename: CTDGSafeZoneLoader.py
# Created by:  blach (12Dec15)

from lib.coginvasion.hood import DGSafeZoneLoader

class CTDGSafeZoneLoader(DGSafeZoneLoader.DGSafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        DGSafeZoneLoader.DGSafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Factory_v1.ogg'
