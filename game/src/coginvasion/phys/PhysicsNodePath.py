from panda3d.core import NodePath, BitMask32, Vec3, Point3
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode

from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import Surfaces

class BasePhysicsObject:
    
    ContactSoundIval = 0.2

    def __init__(self):
        self.bodyNode = None
        self.bodyNP = None
        self.shapeGroup = BitMask32.allOn()
        self.underneathSelf = False
        self.worlds = []
        self.__physicsSetup = False
        
        self.__lastPos = Point3(0)
        
        self.waterCheckTask = None
        
        self.surfaceProp = "default"
        self.needsWaterCheck = False
        self.needsSurfaceContactTest = False
        self.lastSoundTime = 0.0
        
    def startWaterCheck(self):
        self.stopWaterCheck()
        self.waterCheckTask = taskMgr.add(self.__checkForWater, "checkForWater-" + str(id(self)))
        
    def stopWaterCheck(self):
        if self.waterCheckTask:
            self.waterCheckTask.remove()
            self.waterCheckTask = None
        
    def __checkForWater(self, task):
        
        if self.needsWaterCheck:
            if not hasattr(base, 'waterReflectionMgr'):
                return task.cont
                
            currPos = self.getPos(render)
            data = base.waterReflectionMgr.doesLineGoUnderwater(self.__lastPos, currPos)
            if data[0]:
                splPos = currPos
                splPos[2] = data[1].height
                CIGlobals.makeSplash(splPos, data[1].spec.splashTint, 1.0)
            self.__lastPos = currPos
            
        #if self.needsSurfaceContactTest:
        #    if self.bodyNode:
        #        result = base.air.getPhysicsWorld(self.zoneId).contactTest(self.bodyNode)
        #        surface = Surfaces.getSurface(self.surfaceProp)
        #        bz = base.air.getBattleZone(self.zoneId)
        #        now = globalClock.getFrameTime()
        #        if result.getNumContacts() > 0 and now - self.lastSoundTime >= self.ContactSoundIval:
        #            veloMag2 = self.bodyNode.getLinearVelocity().length()
        #            #print veloMag2
        #            if veloMag2 >= 10:
        #                bz.d_emitSound(surface.getHardImpacts(), self.bodyNP.getPos(render))
        #                self.lastSoundTime = now
        #            elif veloMag2 >= 3:
        #                bz.d_emitSound(surface.getSoftImpacts(), self.bodyNP.getPos(render))
        #                self.lastSoundTime = now
        
        return task.cont
        
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
        self.needsWaterCheck = False
        self.needsSurfaceContactTest = False
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
        self.bodyNP.setSurfaceProp(self.surfaceProp)
        self.bodyNP.setCollideMask(self.shapeGroup)
        if not underneathSelf:
            self.reparentTo(self.bodyNP)
            self.assign(self.bodyNP)
        else:
            self.bodyNP.reparentTo(self)
        if hasattr(base, 'physicsWorld'):
            self.needsWaterCheck = True
            self.addToPhysicsWorld(base.physicsWorld)
        elif bodyNode.getMass() > 0:
            self.needsSurfaceContactTest = True
        self.startWaterCheck()
            
        self.__physicsSetup = True

class PhysicsNodePath(BasePhysicsObject, NodePath):

    def __init__(self, *args, **kwargs):
        BasePhysicsObject.__init__(self)
        NodePath.__init__(self, *args, **kwargs)
            
