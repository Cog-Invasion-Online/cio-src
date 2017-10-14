"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BuildingSuitPlannerAI.py
@author Brian Lach
@date June 13, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog import CogBattleGlobals
from src.coginvasion.cog import Dept, SuitBank, Variant
from DistributedTakeOverSuitAI import DistributedTakeOverSuitAI
import SuitBuildingGlobals

import random

# One building suit planner per street.
class BuildingSuitPlannerAI:
    notify = directNotify.newCategory("BuildingSuitPlannerAI")

    def __init__(self, branchZone, streetName, hoodClass):
        self.branchZone = branchZone
        self.streetName = streetName
        self.hoodClass = hoodClass
        self.minBuildings = SuitBuildingGlobals.buildingMinMax[streetName][0]
        self.maxBuildings = SuitBuildingGlobals.buildingMinMax[streetName][1]
        self.spawnChance = SuitBuildingGlobals.buildingChances[streetName]
        self.numCogBuildings = 0
        self.suitsTakingOver = []
        self.__setupInitialBuildings()
        base.taskMgr.doMethodLater(random.randint(SuitBuildingGlobals.SPAWN_TIME_RANGE[0], SuitBuildingGlobals.SPAWN_TIME_RANGE[1]),
                                   self.__spawnNewBuilding, streetName + "-spawnNewBuilding")

    def takeOverBuilding(self, bldg = None, dept = None, suitLevel = None):
        if not bldg:
            bldg = random.choice(self.getToonBuildingsList())

        if not dept:
            dept = random.choice([Dept.SALES, Dept.CASH, Dept.LAW, Dept.BOSS])

        if not suitLevel:
            hoodName = self.hoodClass.hood
            if hoodName == CIGlobals.ToontownCentral:
                hoodName = CIGlobals.BattleTTC
            suitLevel = random.choice(CogBattleGlobals.HoodIndex2LevelRange[CogBattleGlobals.HoodId2HoodIndex[hoodName]])
        numFloors = self.chooseNumFloors(suitLevel)

        print "SuitBuildingPlannerAI.takeOverBuilding: hood - {0} | street - {1} | numFloors - {2} | dept - {3}".format(
            self.hoodClass.hood,
            self.streetName,
            numFloors,
            dept.getName()
        )

        if bldg.fsm.getCurrentState().getName() == 'toon':
            bldg.suitTakeOver(dept, 0, numFloors)
            self.numCogBuildings += 1

    def getToonBuildingsList(self):
        bldgs = []
        for bldg in self.hoodClass.buildings[self.branchZone]:
            if bldg.fsm.getCurrentState().getName() == 'toon' and bldg.takenBySuit is False:
                bldgs.append(bldg)
        return bldgs

    def deadSuit(self, doId):
        for suit in self.suitsTakingOver:
            if suit.doId == doId:
                self.suitsTakingOver.remove(suit)
                break

    def chooseNumFloors(self, suitLevel):
        chances = SuitBuildingGlobals.floorNumberChances[suitLevel]
        number = random.randint(1, 100)
        for chance in chances:
            numFloors = chances.index(chance) + 1
            if number in chance:
                return numFloors

    def __spawnNewBuilding(self, task):
        number = random.randint(1, 100)
        if number <= self.spawnChance and self.numCogBuildings < self.maxBuildings:
            # Let's spawn one!!!
            bldg = random.choice(self.getToonBuildingsList())
            # This building belongs to us!
            bldg.takenBySuit = True
            bldg.door.b_setSuitTakingOver(1)

            hoodName = self.hoodClass.hood
            if hoodName == CIGlobals.ToontownCentral:
                hoodName = CIGlobals.BattleTTC

            levelRange = CogBattleGlobals.HoodIndex2LevelRange[CogBattleGlobals.HoodId2HoodIndex[hoodName]]

            level, planList = SuitBank.chooseLevelAndGetAvailableSuits(levelRange,
                                                                       random.choice([Dept.SALES, Dept.CASH, Dept.LAW, Dept.BOSS]))

            plan = random.choice(planList)

            suit = DistributedTakeOverSuitAI(base.air, self, bldg, bldg.door.doId)
            suit.setManager(self)
            suit.generateWithRequired(bldg.zoneId)
            suit.b_setHood(self.hoodClass.hood)
            suit.b_setLevel(level)
            variant = Variant.NORMAL
            if CogBattleGlobals.hi2hi[hoodName] == CogBattleGlobals.WaiterHoodIndex:
                variant = Variant.WAITER
            suit.b_setSuit(plan, variant)
            suit.b_setPlace(bldg.zoneId)
            suit.b_setName(plan.getName())
            suit.initiateTakeOver()
            self.suitsTakingOver.append(suit)

        task.delayTime = random.randint(SuitBuildingGlobals.SPAWN_TIME_RANGE[0], SuitBuildingGlobals.SPAWN_TIME_RANGE[1])
        return task.again

    def __setupInitialBuildings(self):

        for _ in xrange(self.minBuildings):

            if self.numCogBuildings >= self.minBuildings:
                break

            self.takeOverBuilding()
