# Filename: CTBRTownLoader.py
# Created by:  blach (12Dec15)

from lib.coginvasion.hood import BRTownLoader
import CTBRStreet

class CTBRTownLoader(BRTownLoader.BRTownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        BRTownLoader.BRTownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = CTBRStreet.CTBRStreet
