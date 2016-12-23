########################################
# Filename: AdminPouch.py
# Created by: DecodedLogic (15Jul15)
########################################

from src.coginvasion.gags.backpack.Backpack import Backpack
from src.coginvasion.gags.GagManager import GagManager

class AdminPouch(Backpack):

    def __init__(self):
        Backpack.__init__(self)
        gagMgr = GagManager()
        for gag in gagMgr.getGags().values():
            gag = gag()
            self.setMaxSupply(255, gag.getName())
