from panda3d.core import NodePath, BitMask32, Vec3, Point3
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode

from src.coginvasion.globals import CIGlobals

class BasePhysicsObject:

    def __init__(self):
        self.bodyNode = None
        self.bodyNP = None
        self.shapeGroup = BitMask32.allOn()
        self.underneathSelf = False
        self.worlds = []
        self.__physicsSetup = False
        
        self.__lastPos = Point3(0)
        
        self.waterCheckTask = None
        
    def startWaterCheck(self):
        self.stopWaterCheck()
        self.waterCheckTask = taskMgr.add(self.__checkForWater, "checkForWater-" + str(id(self)))
        
    def stopWaterCheck(self):
        if self.waterCheckTask:
            self.waterCheckTask.remove()
            self.waterCheckTask = None
        
    def __checkForWater(self, task):
        if not hasattr(base, 'waterReflectionMgr'):
            return task.done
            
        currPos = self.getPos(render)
        data = base.waterReflectionMgr.doesLineGoUnderwater(self.__lastPos, currPos)
        if data[0]:
            splPos = currPos
            splPos[2] = data[1].height
            CIGlobals.makeSplash(splPos, data[1].spec.splashTint, 1.0)
        self.__lastPos = currPos
        
        return task.cont
        
    def addToPhysicsWorld(self, world):
        print self.__class__.__name__, "Adding", self.bodyNode, "to physics world", world
        if self.bodyNode and world:
            world.attach(self.bodyNode)
            self.worlds.append(world)

    def removeFromPhysicsWorld(self, world, andRemove = True):
        if self.bodyNode and world:
            world.remove(self.bodyNode)
            if andRemove and world in self.worlds:
                self.worlds.remove(world)
                
    def arePhysicsSetup(self):
        return self.__physicsSetup

    def cleanupPhysics(self):
        if self.bodyNode and hasattr(base, 'physicsWorld'):
            self.removeFromPhysicsWorld(base.physicsWorld)
            self.stopWaterCheck()
        for world in self.worlds:
            self.removeFromPhysicsWorld(world, False)
        self.worlds = []
        if self.bodyNP and not self.bodyNP.isEmpty():
            if self.underneathSelf:
                self.bodyNP.removeNode()
            self.bodyNP = None
            self.bodyNode = None
            
        self.__physicsSetup = False

    def setupPhysics(self, bodyNode, underneathSelf = False):
        self.cleanupPhysics()

        self.underneathSelf = underneathSelf

        self.bodyNode = bodyNode

        assert self.bodyNode is not None

        parent = self.getParent()
        self.bodyNP = parent.attachNewNode(self.bodyNode)
        self.bodyNP.setCollideMask(self.shapeGroup)
        if not underneathSelf:
            self.reparentTo(self.bodyNP)
            self.assign(self.bodyNP)
        else:
            self.bodyNP.reparentTo(self)
        if hasattr(base, 'physicsWorld'):
            self.addToPhysicsWorld(base.physicsWorld)
            self.startWaterCheck()
            
        self.__physicsSetup = True

class PhysicsNodePath(BasePhysicsObject, NodePath):

    def __init__(self, *args, **kwargs):
        BasePhysicsObject.__init__(self)
        NodePath.__init__(self, *args, **kwargs)
            
