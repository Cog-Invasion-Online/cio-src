from panda3d.core import NodePath, Point3

from Entity import Entity

class FuncWater(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.waterNode = None

    def load(self):
        Entity.load(self)
        
        specname = self.getEntityValue("waterspec")
        spec = base.waterReflectionMgr.getDefaultSpec(specname)

        mins = Point3(0)
        maxs = Point3(0)
        self.cEntity.fillinBounds(mins, maxs)
        
        pos = Point3((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, maxs[2])
        
        self.waterNode = base.waterReflectionMgr.addWaterNode(
            (mins.getX() - pos[0], maxs.getX() - pos[0], mins.getY() - pos[1], maxs.getY() - pos[1]),
            pos,
            maxs.getZ() - mins.getZ(), spec = spec)

    def unload(self):
        Entity.unload(self)
        if self.waterNode:
            base.waterReflectionMgr.clearWaterNode(self.waterNode)
            self.waterNode = None
