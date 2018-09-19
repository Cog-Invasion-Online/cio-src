from direct.distributed.DistributedObject import DistributedObject

from Entity import Entity

class DistributedEntity(DistributedObject, Entity):
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        Entity.__init__(self)
        self.entnum = None
        
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        
    def setEntnum(self, entnum):
        self.entnum = entnum
        
        self.cEntity = base.bspLoader.getCEntity(self.entnum)
        base.bspLoader.linkCentToPyent(self.entnum, self)
        self.load()
        
    def getEntnum(self):
        return self.entnum
        
    def disable(self):
        self.entnum = None
        self.unload()
        DistributedObject.disable(self)
        
