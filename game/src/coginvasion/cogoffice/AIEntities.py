from src.coginvasion.szboss.EntityAI import EntityAI

class SuitSpawn(EntityAI):
    
    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        self.spawned = []
    
    def unload(self):
        for suit in self.spawned:
            if not suit.isDeleted():
                suit.requestDelete()
        self.spawned = None
        
        EntityAI.unload(self)
    
    def Spawn(self, dept = None):
        from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
        from src.coginvasion.cog import Dept, SuitBank, Variant
        import random
        
        level, availableSuits = SuitBank.chooseLevelAndGetAvailableSuits(
            [1, 12], random.choice([Dept.BOSS, Dept.SALES, Dept.CASH, Dept.LAW]) if not dept else dept, False)

        plan = random.choice(availableSuits)
        suit = DistributedSuitAI(self.air)
        suit.setBattleZone(self.dispatch)
        variant = Variant.NORMAL
        suit.setLevel(level)
        suit.setSuit(plan, variant)
        suit.generateWithRequired(self.dispatch.zoneId)
        #suit.d_setHood(suit.hood)
        suit.b_setPlace(self.dispatch.zoneId)
        suit.b_setName(plan.getName())
        suit.setPos(self.cEntity.getOrigin())
        suit.setHpr(self.cEntity.getAngles())
        suit.spawnGeneric()
        self.spawned.append(suit)
        
        return suit

class SuitHangout(EntityAI):
    pass

class InfoCogOfficeFloor(EntityAI):

    def dispatch_OnCogGroupDead(self, group):
        self.dispatchOutput("OnCogGroupDead", [group])
    
    def dispatch_OnFloorBegin(self):
        self.dispatchOutput("OnFloorBegin")
        
    def dispatch_OnFloorEnd(self):
        self.dispatchOutput("OnFloorEnd")
        
    def ActivateCogGroup(self, group):
        group = int(group)
        self.dispatch.enterSection(group)
        
    def ActivateChairsInGroup(self, group):
        group = int(group)
        self.dispatch.activateChairSuits(group)
