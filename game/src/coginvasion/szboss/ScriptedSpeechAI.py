"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ScriptedSpeechAI.py
@author Brian Lach
@date March 25, 2019

@desc An entity used by level designers to make an NPC speak.

"""

from src.coginvasion.szboss.EntityAI import EntityAI

class ScriptedSpeechAI(EntityAI):

    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        self.speech = None
        self.targetEnt = None

    def load(self):
        EntityAI.load(self)

        self.speech = self.getEntityValue("speech")
        self.targetEnt = self.bspLoader.getPyEntityByTargetName(self.getEntityValue("targetEntity"))

    def Speak(self):
        self.targetEnt.d_setChat(self.speech)
        self.dispatchOutput("OnSpeak")

    def unload(self):
        del self.speech
        del self.targetEnt
        EntityAI.unload(self)
