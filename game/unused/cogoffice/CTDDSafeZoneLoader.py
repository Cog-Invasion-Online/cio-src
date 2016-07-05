# Filename: CTDDSafeZoneLoader.py
# Created by:  blach (12Dec15)

from lib.coginvasion.hood import DDSafeZoneLoader

class CTDDSafeZoneLoader(DDSafeZoneLoader.DDSafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        DDSafeZoneLoader.DDSafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.pgMusicFilename = 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg'
