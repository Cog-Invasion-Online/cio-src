from src.coginvasion.cog.DistributedSuit import DistributedSuit

from DistributedEntity import DistributedEntity

class DistributedSZBossSuit(DistributedSuit, DistributedEntity):
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        DistributedSuit.__init__(self, cr)
        
    def load(self):
        self.reparentTo(render)
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        
    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        DistributedSuit.announceGenerate(self)
        self.show()
        
    def disable(self):
        DistributedEntity.disable(self)
        DistributedSuit.disable(self)
        
    def generate(self):
        DistributedEntity.generate(self)
        DistributedSuit.generate(self)
        
    def delete(self):
        DistributedEntity.delete(self)
        DistributedSuit.delete(self)