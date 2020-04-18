from panda3d.core import BitMask32

class BasePhysicsObjectShared:

    def __init__(self):
        self.bodyNode = None
        self.bodyNP = None
        self.shapeGroup = BitMask32.allOn()
        self.underneathSelf = False
        self.worlds = []
        self.__physicsSetup = False
        
        self.surfaceProp = "default"

    def getPhysNP(self):
        return self.bodyNP
    
    def getPhysNode(self):
        return self.bodyNode
        
    def addToPhysicsWorld(self, world):
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
        for world in self.worlds:
            self.removeFromPhysicsWorld(world, False)
        self.worlds = []
        if self.bodyNP and not self.bodyNP.isEmpty():
            if self.underneathSelf:
                self.bodyNP.removeNode()
            self.bodyNP = None
            self.bodyNode = None
            
        self.__physicsSetup = False

    def setupPhysics(self, bodyNode, underneathSelf = None):
        self.cleanupPhysics()

        if underneathSelf is not None:
            self.underneathSelf = underneathSelf
        else:
            underneathSelf = self.underneathSelf

        self.bodyNode = bodyNode

        assert self.bodyNode is not None

        parent = self.getParent()
        self.bodyNP = parent.attachNewNode(self.bodyNode)
        self.bodyNP.setSurfaceProp(self.surfaceProp)
        self.bodyNP.setCollideMask(self.shapeGroup)
        if not underneathSelf:
            self.reparentTo(self.bodyNP)
            self.assign(self.bodyNP)
        else:
            self.bodyNP.reparentTo(self)
            
        self.__physicsSetup = True