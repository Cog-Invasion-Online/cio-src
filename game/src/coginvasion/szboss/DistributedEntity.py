from direct.distributed.DistributedObject import DistributedObject

from Entity import Entity

class DistributedEntity(DistributedObject, Entity):
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        Entity.__init__(self)
        self.entnum = None
        
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)

        from panda3d.bsp import CPointEntity
        if isinstance(self.cEntity, CPointEntity):
            self.setPos(self.cEntity.getOrigin())
            self.setHpr(self.cEntity.getAngles())
            
        self.reparentTo(render)
        
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
        
