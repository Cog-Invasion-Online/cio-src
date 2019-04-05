"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FireHoseAI.py
@author Brian Lach
@date April 04, 2019

"""

from panda3d.core import Quat, lookAt

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.Attacks import ATTACK_GAG_FIREHOSE
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gagsnew.BaseHitscanAI import BaseHitscanAI

from FireHoseShared import FireHoseShared

class FireHoseAI(BaseHitscanAI, FireHoseShared):

    ID = ATTACK_GAG_FIREHOSE
    Name = GagGlobals.FireHose

    AttackRange = 50.0

    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths = {self.StateIdle: -1,
                              self.StateDraw: 1.0,
                              self.StateFire: -1}

        self.lastSprayTraceTime = 0.0

    def shouldGoToNextAction(self, complete):
        return complete

    def onSetAction(self, action):
        pass

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        if self.action != self.StateFire:
            self.setNextAction(self.StateFire)

    def primaryFireRelease(self, data):
        self.setNextAction(self.StateIdle)

    def think(self):
        BaseHitscanAI.think(self)

        if self.action == self.StateFire:

            if not self.hasAmmo():
                self.primaryFireRelease(None)
                return

            now = globalClock.getFrameTime()
            if now - self.lastSprayTraceTime >= self.SprayTraceIval:
                #self.takeAmmo(-1)
                self.doTraceAndDamage()
                self.lastSprayTraceTime = now

    def cleanup(self):
        del self.lastSprayTraceTime
        BaseHitscanAI.cleanup(self)
