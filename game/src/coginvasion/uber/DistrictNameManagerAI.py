# Filename: DistrictNameManagerAI.py
# Created by:  blach (23Jul15)

from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistrictNameManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory("DistrictNameManagerAI")

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

    def d_requestDistrictName(self):
        self.sendUpdate('requestDistrictName', [])

    def claimDistrictName(self, name):
        self.air.gotDistrictName(name)

    def noAvailableNames(self):
        self.air.noDistrictNames()

    def d_shuttingDown(self, name):
        self.sendUpdate('shuttingDown', [name])
