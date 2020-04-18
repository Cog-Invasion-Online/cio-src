from src.coginvasion.cog.DistributedSuit import DistributedSuit

class DistributedSZBossSuit(DistributedSuit):
    
    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
     
    def generateSuit(self, suitPlan, variant, voice = None, hideFirst = False):
        DistributedSuit.generateSuit(self, suitPlan, variant, voice = voice, hideFirst = False)
        
    #def load(self):
        #DistributedEntity.load(self)
        #self.showNametagInMargins = self.getEntityValueBool("marginchat")
        
    def announceGenerate(self):
        DistributedSuit.announceGenerate(self)
        self.reparentTo(render)
        self.show()
        self.unstash()
        #self.cleanupPropeller()
        #self.animFSM.request('neutral')
