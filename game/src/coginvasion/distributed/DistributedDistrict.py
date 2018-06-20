"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDistrict.py
@author Brian Lach
@date December 14, 2014

"""

from direct.distributed.DistributedObject import DistributedObject
from src.coginvasion.gui.WhisperPopup import WhisperPopup
from src.coginvasion.globals import CIGlobals, ChatGlobals

import math

class TempObjRequest:

    def __init__(self, context, do, callback):
        self.birthTime = globalClock.getFrameTime()
        self.context = context
        self.do = do
        self.callback = callback

class DistributedDistrict(DistributedObject):
    isDistrict = True

    def __init__(self, cr):
        try:
            self.DistributedDistrict_initialized
            return
        except:
            self.DistributedDistrict_initialized = 1
        DistributedObject.__init__(self, cr)
        self.available = 0
        self.population = 0
        self.popRecord = 0
        self.name = None

        self.pingStart = 0
        self.pingState = False

        return

    def d_ping(self):
        if self.pingState:
            # We are already waiting on a response to our last ping.
            return

        self.pingState = True
        self.pingStart = globalClock.getRealTime()
        self.sendUpdate('ping')

    def pingResp(self):
        now = globalClock.getRealTime()
        # ping in milliseconds
        self.cr.currentPing = (now - self.pingStart) * 1000.0
        self.pingState = False
        self.cr.handleNewPing()

    def setDistrictName(self, name):
        self.name = name

    def getDistrictName(self):
        return self.name

    def setPopRecord(self, record):
        self.popRecord = record

    def getPopRecord(self):
        return self.popRecord

    def setPopulation(self, population):
        self.population = population

    def getPopulation(self):
        return self.population

    def d_joining(self):
        self.sendUpdate('joining', [])

    def systemMessage(self, message):
        whisper = WhisperPopup('ADMIN: ' + message, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)

    def setAvailable(self, available):
        self.available = available

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.cr.activeDistricts[self.doId] = self

    def disable(self):
        DistributedObject.disable(self)
        self.available = 0
        if self.cr.myDistrict is self:
            self.cr.myDistrict = None
        else:
            del self.cr.activeDistricts[self.doId]

    def delete(self):
        DistributedObject.delete(self)
        del self.available
