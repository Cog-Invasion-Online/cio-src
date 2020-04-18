from panda3d.core import NodePath, Point3

from src.coginvasion.globals import CIGlobals
from BasePhysicsObjectShared import BasePhysicsObjectShared
        
class BasePhysicsObject(BasePhysicsObjectShared):

    def __init__(self):
        BasePhysicsObjectShared.__init__(self)
        
        self.waterCheckTask = None
        self.needsWaterCheck = False
        self.__lastPos = Point3(0)
        
    def startWaterCheck(self):
        self.stopWaterCheck()
        self.waterCheckTask = taskMgr.add(self.__checkForWater, "checkForWater-" + str(id(self)))
        
    def stopWaterCheck(self):
        if self.waterCheckTask:
            self.waterCheckTask.remove()
            self.waterCheckTask = None
            
    def setupPhysics(self, bodyNode, underneathSelf = None):
        BasePhysicsObjectShared.setupPhysics(self, bodyNode, underneathSelf)
        if hasattr(base, 'physicsWorld'):
            self.needsWaterCheck = True
            self.addToPhysicsWorld(base.physicsWorld)
        self.startWaterCheck()
        
    def __checkForWater(self, task):
        
        if self.needsWaterCheck:
                
            currPos = self.getPos(render)
            data = base.waterReflectionMgr.doesLineGoUnderwater(self.__lastPos, currPos)
            if data[0]:
                splPos = currPos
                splPos[2] = data[1].height
                CIGlobals.makeSplash(splPos, data[1].spec.splashTint, 1.0)
            self.__lastPos = currPos
        
        return task.cont
        
    def cleanupPhysics(self):
        self.needsWaterCheck = False
        self.needsSurfaceContactTest = False
        if self.bodyNode and hasattr(base, 'physicsWorld'):
            self.removeFromPhysicsWorld(base.physicsWorld)
            self.stopWaterCheck()
            
        BasePhysicsObjectShared.cleanupPhysics(self)

class PhysicsNodePath(BasePhysicsObject, NodePath):

    def __init__(self, *args, **kwargs):
        BasePhysicsObject.__init__(self)
        NodePath.__init__(self, *args, **kwargs)
