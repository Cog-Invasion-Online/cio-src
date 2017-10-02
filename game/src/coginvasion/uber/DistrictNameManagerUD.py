# Filename: DistrictNameManagerUD.py
# Created by:  blach (23Jul15)

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals.CIGlobals import DistrictNames
import random

class DistrictNameManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory("DistrictNameManagerUD")

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.availableNames = []

    def shuttingDown(self, name):
        # This district is shutting down.. make their name available.
        self.notify.info("Freeing up District name: {0}".format(name))
        self.availableNames.append(name)

    def requestDistrictName(self):
        sender = self.air.getMsgSender()
        # Let's give them a random available name.
        if len(self.availableNames) > 0:
            name = self.availableNames[random.randint(0, len(self.availableNames) - 1)]
            self.sendUpdateToChannel(sender, 'claimDistrictName', [name])
            self.availableNames.remove(name)
        else:
            self.sendUpdateToChannel(sender, 'noAvailableNames', [])

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.availableNames = list(DistrictNames)

    def delete(self):
        self.availableNames = None
        DistributedObjectGlobalUD.delete(self)
