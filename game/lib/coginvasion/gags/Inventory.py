# Filename: Inventory.py
# Created by:  blach (20Jul15)

from direct.directNotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

class Inventory(DirectObject):
    notify = directNotify.newCategory("Inventory")

    def __init__(self):
        DirectObject.__init__(self)
        self.gags = None

    def setGags(self, gagArray, ammo):
        self.gags = {}
        for gag in gagArray:
            self.gags[gag] = ammo
        self.gags = gagArray
        self.gagAmmo = ammo

    def getGags(self):
        return self.gags

    def getGagAmmo(self):
        return self.gagAmmo

    def getAmmoOfGag(self, index):
        return self.getGagAmmo()[index]

    def cleanup(self):
        del self.gags
        del self.gagAmmo
