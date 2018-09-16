from panda3d.core import NodePath, Point3

from Entity import Entity

class FuncWater(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.waterNode = None

    def load(self):
        Entity.load(self)
        
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getEntnum()

        mins = Point3(0)
        maxs = Point3(0)
        self.cEntity.fillinBounds(mins, maxs)
        self.waterNode = base.waterReflectionMgr.addWaterNode(
            (mins.getX(), maxs.getX(), mins.getY(), maxs.getY()),
            (0, 0, maxs.getZ()),
            maxs.getZ() - mins.getZ())

    def unload(self):
        Entity.unload(self)
        if self.waterNode:
            base.waterReflectionMgr.clearWaterNode(self.waterNode)
            self.waterNode = None
