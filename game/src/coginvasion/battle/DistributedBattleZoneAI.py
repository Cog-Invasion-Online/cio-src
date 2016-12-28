########################################
# Filename: DistributedBattleZoneAI.py
# Created by: DecodedLogic (22Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedBattleZoneAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBattleZoneAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.avIds = []

        # Stores the Cogs each avatar kills.
        # Key (Avatar Id)
        # Value (List of DeadCogData instances)
        self.cogKills = {}

    def delete(self):
        self._ignoreAvatarDeleteEvents()
        self._resetStats()

        self.avIds = None
        self.cogKills = None
        DistributedObjectAI.delete(self)

    def _resetStats(self):
        self.avIds = []
        self.cogKills = {}

    def _ignoreAvatarDeleteEvents(self):
        for avId in self.avIds:
            toon = self.air.doId2do.get(avId)
            self.ignore(toon.getDeleteEvent())
            break

    def _addAvatar(self, avId):
        self.avIds.append(avId)
        self.b_setAvatars(self.avIds)

    def _removeAvatar(self, avId):
        self.avIds.remove(avId)

        if avId in self.cogKills.keys():
            self.cogKills.pop(avId)
        self.b_setAvatars(self.avIds)

    # Send the distributed message and
    # set the avatars on here.
    def b_setAvatars(self, avIds):
        self.d_setAvatars(avIds)
        self.setAvatars(avIds)

    # Send the distributed message.
    def d_setAvatars(self, avIds):
        self.sendUpdate('setAvatars', [avIds])

    # Set the avatar ids array to a list of
    # avatar ids.
    def setAvatars(self, avIds):
        self.avIds = avIds

    # Get the avatar ids.
    def getAvatars(self):
        return self.avIds

    def _handleCogDeath(self, cog, killerId):
        cogData = DeadCogData(cog.getName(), cog.getDept(), cog.getLevel(), cog.getVariant())
        currentKills = []

        if killerId in self.cogKills.keys():
            currentKills = self.cogKills.get(killerId)
        currentKills.append(cogData)

        # Add the Cog kill into the player's dictionary.
        self.cogKills.update({killerId : currentKills})

class DeadCogData:

    def __init__(self, name, dept, level, variant):
        self.name = name
        self.dept = dept
        self.level = level
        self.variant = variant

    def getName(self):
        return self.name

    def getDept(self):
        return self.dept

    def getLevel(self):
        return self.level

    def getVariant(self):
        return self.variant
