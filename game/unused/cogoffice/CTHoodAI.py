# Filename: CTHoodAI.py
# Created by:  blach (13Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit import CogBattleGlobals
from lib.coginvasion.suit.DistributedCogStationAI import DistributedCogStationAI
from lib.coginvasion.distributed.HoodMgr import HoodMgr
from lib.coginvasion.cog import Dept
from DistributedBuildingAI import DistributedBuildingAI
from lib.coginvasion.dna.DNALoader import *

import random

class CTHoodAI:
    notify = directNotify.newCategory('CTHoodAI')

    def __init__(self, air, zoneId, hood):
        self.air = air
        self.zoneId = zoneId
        self.hood = hood
        self.hoodMgr = HoodMgr()
        self.cogStation = None
        self.air.hoods[zoneId] = self
        self.buildings = []
        self.startup()

    def startup(self):
        if CogBattleGlobals.HoodId2WantBattles.get(self.hood, False) is True:
            self.notify.info('Making station in {0}'.format(self.hood))
            hoodIndex = CogBattleGlobals.HoodId2HoodIndex[self.hood]
            self.cogStation = DistributedCogStationAI(self.air)
            self.cogStation.setHoodIndex(hoodIndex)
            self.cogStation.generateWithRequired(self.zoneId)
            self.cogStation.b_setLocationPoint(hoodIndex)
        else:
            self.notify.info("Battles not available in {0}".format(self.hood))

        self.notify.info('Making buildings...')
        for dnaFile in self.dnaFiles:
            zoneId = 0
            if 'sz' in dnaFile:
                zoneId = self.zoneId
            else:
                for segment in dnaFile.split('_'):
                    if segment.endswith('dna'):
                        segment = segment[:4]
                        if segment.isdigit():
                            zoneId = int(segment)
                            break
            zoneId += CIGlobals.CTZoneDifference
            dnaStore = DNAStorage()
            dnaData = loadDNAFileAI(dnaStore, dnaFile)
            self.air.dnaStoreMap[zoneId] = dnaStore
            self.air.dnaDataMap[zoneId] = dnaData
            blockZoneByNumber = {}
            for i in range(dnaStore.get_num_block_numbers()):
                blockNumber = dnaStore.get_block_number_at(i)
                blockZoneByNumber[blockNumber] = dnaStore.get_zone_from_block_number(blockNumber) + CIGlobals.CTZoneDifference
            for block, exteriorZone in blockZoneByNumber.items():
                buildingType = dnaStore.get_block_building_type(block)
                if not buildingType in ['animbldg', 'hq']:
                    bldg = DistributedBuildingAI(self.air, block, exteriorZone, zoneId, self.hood)
                    bldg.generateWithRequired(exteriorZone)
                    bldg.suitTakeOver(random.choice([Dept.SALES, Dept.CASH, Dept.LAW, Dept.BOSS]), 0, 0)
                    self.buildings.append(bldg)

    def shutdown(self):
        if self.cogStation:
            self.cogStation.requestDelete()
            self.cogStation = None
        self.hoodMgr = None
        self.air = None
        self.zoneId = None
        self.hood =  None
