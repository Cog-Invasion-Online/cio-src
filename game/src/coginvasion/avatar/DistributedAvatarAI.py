"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedAvatarAI.py
@author Brian Lach
@date November 02, 2014

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedSmoothNodeAI

class DistributedAvatarAI(DistributedSmoothNodeAI.DistributedSmoothNodeAI):
    notify = directNotify.newCategory("DistributedAvatarAI")

    def __init__(self, air):
        try:
            self.DistributedAvatarAI_initialized
            return
        except:
            self.DistributedAvatarAI_initialized = 1
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.__init__(self, air)
        self.health = 0
        self.maxHealth = 0
        self.moveBits = 0
        self._name = ""
        self.place = 0
        self.hood = ""
        self.battleZone = None
        return

    def setMoveBits(self, bits):
        self.moveBits = bits

    def getMoveBits(self):
        return self.moveBits
        
    def takeDamage(self, dmg):
        hp = self.getHealth() - dmg
        if hp < 0:
            hp = 0
        self.b_setHealth(hp)
        self.d_announceHealth(0, -dmg)

    def setHood(self, hood):
        self.hood = hood

    def d_setHood(self, hood):
        self.sendUpdate('setHood', [hood])

    def b_setHood(self, hood):
        self.d_setHood(hood)
        self.setHood(hood)

    def getHood(self):
        return self.hood

    def d_setChat(self, chat):
        self.sendUpdate('setChat', [chat])

    def setName(self, name):
        self._name = name

    def d_setName(self, name):
        self.sendUpdate("setName", [name])

    def b_setName(self, name):
        self.d_setName(name)
        self.setName(name)

    def getName(self):
        return self._name

    def setMaxHealth(self, health):
        self.maxHealth = health

    def d_setMaxHealth(self, health):
        self.sendUpdate("setMaxHealth", [health])

    def b_setMaxHealth(self, health):
        self.d_setMaxHealth(health)
        self.setMaxHealth(health)

    def getMaxHealth(self):
        return self.maxHealth

    def setPlace(self, place):
        self.place = place

    def b_setPlace(self, place):
        self.sendUpdate("setPlace", [place])
        self.setPlace(place)

    def getPlace(self):
        return self.place

    def isDead(self):
        return self.health <= 0

    def setHealth(self, health):
        #if health > self.maxHealth:
            #base.air.logServerEvent("suspicious", "self.health is greater than self.maxHealth: avId %s" % self.doId)
            #base.air.sendKickMessage(self.doId)
        self.health = health

    def d_setHealth(self, health):
        self.sendUpdate("setHealth", [health])

    def b_setHealth(self, health):
        self.d_setHealth(health)
        self.setHealth(health)

    def getHealth(self):
        return self.health

    def d_announceHealth(self, level, hp, extraId = -1):
        # There's no need to announce when the avatar's health doesn't change.
        if hp != 0:
            self.sendUpdate('announceHealth', [level, hp, extraId])

    def disable(self):
        self.health = None
        self.maxHealth = None
        self._name = None
        self.place = None
        self.hood = None
        self.battleZone = None
        return
    
    def delete(self):
        del self.health
        del self.maxHealth
        del self._name
        del self.place
        del self.hood
        del self.battleZone
        return
