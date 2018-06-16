"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedToonAI.py
@author Brian Lach/Maverick Liberty
@date October 12, 2014

Revamped on June 15, 2018

"""

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.globals import CIGlobals
import ToonDNA

class DistributedToonAI(DistributedAvatarAI, DistributedSmoothNodeAI, ToonDNA.ToonDNA):
    notify = directNotify.newCategory('DistributedToonAI')

    def __init__(self, air):
        try:
            self.DistributedToonAI_initialized
            return
        except:
            self.DistributedToonAI_initialized = 1
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        ToonDNA.ToonDNA.__init__(self)
        self.avatarType = CIGlobals.Toon
        self.anim = "neutral"
        self.chat = ""
        self.health = 50
        self.height = 3
        self.gender = "boy"
        self.headtype = "dgm_skirt"
        self.head = "dog"
        self.legtype = "dgm"
        self.torsotype = "dgm_shorts"
        self.hr = 1
        self.hg = 1
        self.hb = 1
        self.tr = 1
        self.tg = 1
        self.tb = 1
        self.lr = 1
        self.lg = 1
        self.lb = 1
        self.shir = 1
        self.shig = 1
        self.shib = 1
        self.shor = 1
        self.shog = 1
        self.shob = 1
        self.shirt = "phase_3/maps/desat_shirt_1.jpg"
        self.short = "phase_3/maps/desat_shorts_1.jpg"
        self.sleeve = "phase_3/maps/desat_sleeve_1.jpg"
        self.isdying = False
        self.isdead = False
        self.toon_legs = None
        self.toon_torso = None
        self.toon_head = None
        return

    def setAnimState(self, anim, timestamp = 0):
        self.anim = anim

    def getAnimState(self):
        return self.anim

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        DistributedSmoothNodeAI.announceGenerate(self)

    def delete(self):
        try:
            self.DistributedToonAI_deleted
        except:
            self.DistributedToonAI_deleted = 1
            DistributedAvatarAI.delete(self)
            DistributedSmoothNodeAI.delete(self)
            self.avatarType = None
            self.anim = None
            self.chat = None
            self.height = None
            self.gender = None
            self.headtype = None
            self.head = None
            self.legtype = None
            self.torsotype = None
            self.hr = None
            self.hg = None
            self.hb = None
            self.tr = None
            self.tg = None
            self.tb = None
            self.lr = None
            self.lg = None
            self.lb = None
            self.shir = None
            self.shig = None
            self.shib = None
            self.shor = None
            self.shog = None
            self.shob = None
            self.shirt = None
            self.short = None
            self.sleeve = None
            self.isdying = None
            self.isdead = None
            self.toon_legs = None
            self.toon_torso = None
            self.toon_head = None
            del self.avatarType
            del self.anim
            del self.chat
            del self.height
            del self.gender
            del self.headtype
            del self.head
            del self.legtype
            del self.torsotype
            del self.hr
            del self.hg
            del self.hb
            del self.tr
            del self.tg
            del self.tb
            del self.lr
            del self.lg
            del self.lb
            del self.shir
            del self.shig
            del self.shib
            del self.shor
            del self.shog
            del self.shob
            del self.shirt
            del self.short
            del self.sleeve
            del self.isdying
            del self.isdead
            del self.toon_legs
            del self.toon_torso
            del self.toon_head
        return
