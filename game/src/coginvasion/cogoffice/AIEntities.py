from src.coginvasion.szboss.EntityAI import EntityAI

class SuitSpawn(EntityAI):
    pass

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