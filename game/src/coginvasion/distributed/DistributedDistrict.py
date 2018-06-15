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

        self.tempObjContext = 0
        self.tempReqs = []

        return

    def d_spawnTemporaryObject(self, do, callback):
        ctx = TempObjRequest(self.tempObjContext, do, callback)
        self.tempObjContext += 1
        if self.tempObjContext > 255:
            self.tempObjContext = 0
        self.tempReqs.append(ctx)
        self.sendUpdate('spawnTemporaryObject', [ctx.context, do.dclass.getNumber()])

    def tempObjectOwnershipGranted(self, ctx, doId):
        print "ownership granted! for something"
        for tempReq in self.tempReqs:
            print tempReq.context
            print ctx
            if tempReq.context == ctx:
                tempReq.callback(doId)
                time = globalClock.getFrameTime() - tempReq.birthTime
                print "Took {0} seconds to get ownership of {1}".format(time, doId)
                self.tempReqs.remove(tempReq)
                break

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
