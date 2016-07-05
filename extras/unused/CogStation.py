# Filename: CogStation.py
# Created by:  blach (11Jun15)

from direct.gui.DirectGui import DirectLabel

from lib.coginvasion.minigame.GroupStation import GroupStation
from lib.coginvasion.globals import CIGlobals

class CogStation(GroupStation):
    Slots = 8
    Title = "Cog Battle"

    def __init__(self):
        GroupStation.__init__(self)
        self.locations = {"pos": {0: (71.86, -151.85, 2.50),
                            1: (32.35, 70.06, 6.20),
                            2: (93.11, 38.94, -15.94)},
                        "hpr": {0: (3.12, 0.00, 0.00),
                            1: (135.15, 0.00, 0.00),
                            2: (90.0, 0.0, 3.0)}}

    def delete(self):
        try:
            self.CogStation_deleted
        except:
            self.CogStation_deleted = 1
            self.removeStation()
            GroupStation.delete(self)
        return

    def createTimer(self):
        GroupStation.createTimer(self)
        self.timer['text_fg'] = (0.4, 0.4, 0.4, 1.0)

    def generateStation(self):
        GroupStation.generateStation(self, self.Slots)
        circleTexture = loader.loadTexture("phase_13/maps/stand_here_cog.png")
        for circle in self.circles:
            circle.setTexture(circleTexture, 1)
        title = DirectLabel(text=self.Title, relief=None, text_fg=(0.5, 0.5, 0.5, 1.0),
                            text_decal=True, text_font=CIGlobals.getMickeyFont(), text_pos = (0, 0),
                            parent=self.sign.find('**/signText_locator'), text_scale=0.3,
                            text_wordwrap=7.0)
        title.setBillboardAxis(2)
