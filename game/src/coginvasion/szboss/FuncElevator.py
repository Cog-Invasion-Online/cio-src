from src.coginvasion.szboss.DistributedEntity import DistributedEntity

class FuncElevator(DistributedEntity):

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        
        self.startSmooth()
