"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SZBossSuit.py
@author Brian Lach
@date August 27, 2018

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.cog.Suit import Suit
from src.coginvasion.cog import SuitBank, Variant, Voice, SuitGlobals

class SZBossSuit(Suit, Entity):
    notify = directNotify.newCategory("SZBossSuit")

    def __init__(self):
        Entity.__init__(self)
        Suit.__init__(self)
        self.level = 0

    #def handleHitByToon(self, player, gagId, distance):    

    def load(self):
        Entity.load(self)
        entnum = self.cEntity.getEntnum()
        suitId = base.bspLoader.getEntityValueInt(entnum, "suitPlan")
        self.level = base.bspLoader.getEntityValueInt(entnum, "level")
        suitPlan = SuitBank.getSuitById(suitId)
        Suit.generate(self, suitPlan, Variant.NORMAL, Voice.NORMAL, False)

        classAttrs = suitPlan.getCogClassAttrs()
        self.maxHealth = classAttrs.baseHp
        self.maxHealth += SuitGlobals.calculateHP(self.level)
        self.maxHealth *= classAttrs.hpMod

        self.health = self.maxHealth

        if self.level == 0:
            self.maxHealth = 1
            self.health = self.maxHealth

        self.reparentTo(render)
        
        origin = self.cEntity.getOrigin()
        angles = self.cEntity.getAngles()
        self.setPos(origin)
        self.setHpr(angles)

        self.cleanupPropeller()
        self.animFSM.request('neutral')
