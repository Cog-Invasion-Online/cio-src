"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CogOfficePursueToonBehaviorAI.py
@author Brian Lach
@date March 07, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.cog.SuitPathBehaviorAI import SuitPathBehaviorAI
from src.coginvasion.cog.SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI

import random

class CogOfficePursueToonBehaviorAI(SuitPursueToonBehaviorAI):
    notify = directNotify.newCategory('CogOfficePursueToonBehaviorAI')

    def enter(self):
        SuitPathBehaviorAI.enter(self)
        self.pickTarget()
        # Choose a distance that is good enough to attack this target.
        self.attackSafeDistance = random.uniform(5.0, 19.0)
        # Now, chase them down!
        self.fsm.request('pursue')

    def pickTarget(self):
        # Pick a new toon target
        avIds = list(self.suit.battle.getAvatars())
        # We need to target the toon who has the least amount of attackers.
        avIds.sort(key = lambda avId: len(self.suit.battle.toonId2suitsTargeting[avId]))
        # The toon to target is the avId at the top of the list since it's been sorted.
        self.targetId = avIds[0]
        self.target = self.air.doId2do.get(self.targetId)
        # Add myself to the targets list for this toon
        self.suit.battle.toonId2suitsTargeting[self.targetId].append(self.suit.doId)

    def exit(self):
        # Remove myself from the targets list for my target
        if (self.targetId is not None and self.targetId in self.suit.battle.toonId2suitsTargeting.keys() and
            self.suit.doId in self.suit.battle.toonId2suitsTargeting[self.targetId]):
            self.suit.battle.toonId2suitsTargeting[self.targetId].remove(self.suit.doId)
        SuitPursueToonBehaviorAI.exit(self)
