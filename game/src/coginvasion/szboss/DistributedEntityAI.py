from direct.distributed.DistributedObjectAI import DistributedObjectAI

from Entity import Entity

class DistributedEntityAI(DistributedObjectAI, Entity):
    
    def __init__(self, air, dispatch):
        DistributedObjectAI.__init__(self, air)
        Entity.__init__(self)
        self.dispatch = dispatch
        self.entnum = 0
        self.bspLoader = None
        
    def getEntnum(self):
        print "DistributedEntityAI.getEntnum():", str(self.entnum)
        return self.entnum
        
    def loadEntityValues(self):
        pass
        
    def load(self):
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)
        self.loadEntityValues()
        self.generateWithRequired(self.zoneId)
        
    def delete(self):
        self.unload()
        self.entnum = None
        self.bspLoader = None
        DistributedObjectAI.delete(self)
