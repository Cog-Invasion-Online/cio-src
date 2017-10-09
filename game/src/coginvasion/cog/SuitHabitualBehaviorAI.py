"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitHabitualBehaviorAI.py
@author Maverick Liberty
@date September 03, 2015

"""

from src.coginvasion.cog.SuitBehaviorBaseAI import SuitBehaviorBaseAI

class SuitHabitualBehaviorAI(SuitBehaviorBaseAI):
    
    def __init__(self, suit, doneEvent = None):
        if doneEvent == None:
            doneEvent = 'suit%s-behaviorDone' % (suit.doId)
        SuitBehaviorBaseAI.__init__(self, suit, doneEvent)
        self.isEntered = 0