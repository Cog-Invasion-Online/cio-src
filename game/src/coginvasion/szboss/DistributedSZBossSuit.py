from src.coginvasion.cog.DistributedSuit import DistributedSuit

from DistributedEntity import DistributedEntity

class DistributedSZBossSuit(DistributedSuit, DistributedEntity):
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        DistributedSuit.__init__(self, cr)
     
    def generateSuit(self, suitPlan, variant, voice = None, hideFirst = False):
        DistributedSuit.generateSuit(self, suitPlan, variant, voice = voice, hideFirst = False)
        
    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        DistributedSuit.announceGenerate(self)
        self.reparentTo(render)
        self.show()
        self.ls()
        self.unstash()
        #self.cleanupPropeller()
        #self.animFSM.request('neutral')
        
    def disable(self):
        DistributedEntity.disable(self)
        DistributedSuit.disable(self)
        
    def generate(self):
        DistributedEntity.generate(self)
        DistributedSuit.generate(self)
        
    def delete(self):
        DistributedEntity.delete(self)
        DistributedSuit.delete(self)
