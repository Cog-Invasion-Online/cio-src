from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

from src.coginvasion.phys.PhysicsNodePath import BasePhysicsObject
from Entity import Entity

class DistributedEntity(DistributedSmoothNode, BasePhysicsObject, Entity):
    
    def __init__(self, cr, initNode = True):
        DistributedSmoothNode.__init__(self, cr)
        Entity.__init__(self, initNode)
        BasePhysicsObject.__init__(self)
        self.entnum = 0
        
    def setIsMapEnt(self, mapEnt):
        self.mapEnt = bool(mapEnt)
        
    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)

        self.enableThink()

        if self.mapEnt:
            from libpandabsp import CPointEntity
            if isinstance(self.cEntity, CPointEntity):
                self.setPos(render, self.cEntity.getOrigin())
                self.setHpr(render, self.cEntity.getAngles())
               
            self.tryEntityParent()
        
    def setEntnum(self, entnum):
        self.entnum = entnum
        
        if self.mapEnt:
            self.cEntity = base.bspLoader.getCEntity(self.entnum)
        self.preLinkLoad()
        if self.mapEnt:
            from libpandabsp import CBrushEntity
            if isinstance(self.cEntity, CBrushEntity):
                self.assign(self.cEntity.getModelNp())
                #self.setupBrushEntityPhysics()
            base.bspLoader.linkCentToPyent(self.entnum, self)
        self.load()
        
    def preLinkLoad(self):
        pass
        
    def getEntnum(self):
        return self.entnum
        
    def disable(self):
        self.cleanupPhysics()
        self.entnum = None
        self.unload()
        DistributedSmoothNode.disable(self)
        
