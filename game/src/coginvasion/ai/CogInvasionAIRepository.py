########################################
# Filename: CogInvasionAIRepository.py
# Created by: blach (14Feb14)
########################################

from src.coginvasion.distributed.CogInvasionInternalRepository import CogInvasionInternalRepository
from src.coginvasion.distributed.DistributedDistrictAI import DistributedDistrictAI

from direct.distributed.TimeManagerAI import TimeManagerAI
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import STATESERVER_OBJECT_SET_AI

from src.coginvasion.hood.TTHoodAI import TTHoodAI
from src.coginvasion.hood.MGHoodAI import MGHoodAI
from src.coginvasion.hood.BRHoodAI import BRHoodAI
from src.coginvasion.hood.DLHoodAI import DLHoodAI
from src.coginvasion.hood.MLHoodAI import MLHoodAI
from src.coginvasion.hood.DGHoodAI import DGHoodAI
from src.coginvasion.hood.DDHoodAI import DDHoodAI
from src.coginvasion.cogtropolis.CTHoodAI import CTHoodAI

from pandac.PandaModules import UniqueIdAllocator
from src.coginvasion.globals import CIGlobals
from AIZoneData import AIZoneDataStore
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.distributed.CogInvasionDoGlobals import DO_ID_DISTRICT_NAME_MANAGER, DO_ID_HOLIDAY_MANAGER, DO_ID_UNIQUE_INTEREST_NOTIFIER

#PStatClient.connect()

class CogInvasionAIRepository(CogInvasionInternalRepository):
    notify = directNotify.newCategory("CogInvasionAIRepository")

    def __init__(self, baseChannel, stateServerChannel):
        CogInvasionInternalRepository.__init__(
            self, baseChannel, stateServerChannel,
            ['resources/phase_3/etc/direct.dc', 'resources/phase_3/etc/toon.dc'], dcSuffix = 'AI'
        )
        self.notify.setInfo(True)
        self.district = None
        self.zoneAllocator = UniqueIdAllocator(CIGlobals.DynamicZonesBegin,
                                            CIGlobals.DynamicZonesEnd)
        self.zoneDataStore = AIZoneDataStore()
        self.hoods = {}
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        self.districtNameMgr = self.generateGlobalObject(DO_ID_DISTRICT_NAME_MANAGER, 'DistrictNameManager')
        self.holidayMgr = self.generateGlobalObject(DO_ID_HOLIDAY_MANAGER, 'HolidayManager')
        self.uin = self.generateGlobalObject(DO_ID_UNIQUE_INTEREST_NOTIFIER, 'UniqueInterestNotifier')
        
    def handleCrash(self, e):
        raise e

    def gotDistrictName(self, name):
        self.notify.info("This District will be called: %s" % name)
        self.districtId = self.allocateChannel()
        self.notify.info("Generating shard; id = %s" % self.districtId)
        self.district = DistributedDistrictAI(self)
        self.district.generateWithRequiredAndId(
            self.districtId, self.getGameDoId(), 3
        )
        self.notify.info("Claiming ownership; channel = %s" % self.districtId)
        self.claimOwnership(self.districtId)
        self.notify.info('Setting District name %s' % name)
        self.district.b_setDistrictName(name)
        self.district.b_setPopRecord(0)

        self.notify.info("Generating time manager...")
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

        self.areas = [TTHoodAI, BRHoodAI, DLHoodAI, MLHoodAI, DGHoodAI, DDHoodAI, CTHoodAI, MGHoodAI]
        self.areaIndex = 0

        taskMgr.add(self.makeAreasTask, 'makeAreasTask')

    def makeAreasTask(self, task):
        if self.areaIndex >= len(self.areas):
            self.done()
            return task.done
        area = self.areas[self.areaIndex]
        area(self)
        self.areaIndex += 1
        task.delayTime = 0.5
        return task.again

    def done(self):
        self.notify.info("Setting shard available.")
        self.district.b_setAvailable(1)
        self.notify.info("Done.")

    def noDistrictNames(self):
        self.notify.error("Cannot create District: There are no available names!")

    def handleConnected(self):
        CogInvasionInternalRepository.handleConnected(self)
        self.districtNameMgr.d_requestDistrictName()
        self.holidayMgr.d_srvRequestHoliday()

    def toonsAreInZone(self, zoneId):
        numToons = 0
        for obj in self.doId2do.values():
            if obj.__class__.__name__ == "DistributedToonAI":
                if obj.zoneId == zoneId:
                    numToons += 1
        return numToons > 0

    def shutdown(self):
        for hood in self.hoods.values():
            hood.shutdown()
        if self.timeManager:
            self.timeManager.requestDelete()
            self.timeManager = None
        if self.district:
            self.district.b_setAvailable(0)
            self.district.requestDelete()

    def claimOwnership(self, channel):
        dg = PyDatagram()
        dg.addServerHeader(channel, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        dg.addChannel(self.ourChannel)
        self.send(dg)

    def allocateZone(self):
        return self.zoneAllocator.allocate()

    def deallocateZone(self, zone):
        self.zoneAllocator.free(zone)

    def getZoneDataStore(self):
        return self.zoneDataStore
