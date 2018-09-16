from direct.distributed.DistributedObject import DistributedObject

from Entity import Entity

class DistributedEntity(DistributedObject, Entity):
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        Entity.__init__(self)
        self.entnum = None
        
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        print "DistributedEntity.announceGenerate:", self.__class__.__name__
        
    def setEntnum(self, entnum):
        print "DistributedEntity.setEntnum:", self.__class__.__name__
        self.entnum = entnum
        
        self.cEntity = base.bspLoader.getCEntity(self.entnum)
        self.load()
        
    def getEntnum(self):
        return self.entnum
        
    def disable(self):
        self.entnum = None
        self.unload()
        DistributedObject.disable(self)
        
