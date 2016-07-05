########################################
# Filename: Dept.py
# Created by: DecodedLogic (31Jul15)
########################################

from panda3d.core import VBase4

class Dept:

    def __init__(self, name, handColor, tieName, clothPrefix, medallionColor):
        self.name = name
        self.handColor = handColor
        self.tieName = tieName
        self.clothPrefix = clothPrefix
        self.medallionColor = medallionColor

    def getMedallionColor(self):
        return self.medallionColor

    def getHandColor(self):
        return self.handColor

    def getTie(self):
        return self.tieName

    def getClothingPrefix(self):
        return self.clothPrefix

    def getName(self):
        return self.name

BOSS = Dept('Bossbot', VBase4(0.95, 0.75, 0.75, 1), 'boss', 'c', VBase4(0.863, 0.776, 0.769, 1.0))
LAW = Dept('Lawbot', VBase4(0.75, 0.75, 0.95, 1.0), 'legal', 'l', VBase4(0.749, 0.776, 0.824, 1.0))
CASH = Dept('Cashbot', VBase4(0.65, 0.95, 0.85, 1.0), 'money', 'm', VBase4(0.749, 0.769, 0.749, 1.0))
SALES = Dept('Sellbot', VBase4(0.95, 0.75, 0.95, 1.0), 'sales', 's', VBase4(0.843, 0.745, 0.745, 1.0))
