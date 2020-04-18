from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

from src.coginvasion.phys.PhysicsNodePathAI import BasePhysicsObjectAI
from src.coginvasion.phys import PhysicsUtils
from Entity import Entity

class DistributedEntityAI(DistributedSmoothNodeAI, BasePhysicsObjectAI, Entity):
    
    SOLID_MESH = 0
    SOLID_BBOX = 1
    
    def __init__(self, air, dispatch = None):
        DistributedSmoothNodeAI.__init__(self, air)
        Entity.__init__(self)
        BasePhysicsObjectAI.__init__(self)
        self.dispatch = dispatch
        
        self.__dynamicEntity = True
        self.__unloaded = False
        self.__isBrushEntity = False
        
        self.mass = 1.0
        self.solidType = self.SOLID_BBOX
        
    def transitionXform(self, destLandmarkNP, mat):
        print "Transition xform:", destLandmarkNP, mat
        Entity.transitionXform(self, destLandmarkNP, mat)
        #if self.posHprBroadcastStarted():
        #    print "And clear smoothing"
        self.b_clearSmoothing()
        self.sendCurrentPosition()

    def isPreservable(self):
        return (not self.__unloaded) and self.__dynamicEntity
        
    def emitSound(self, soundType, pos = None, volume = 1.0, duration = 1.0):
        if not pos:
            pos = self.getPos()
        battleZone = self.air.getBattleZone(self.getZoneId())
        if battleZone:
            battleZone.soundEmitterSystem.emitSound(soundType, self, pos, volume, duration)

    def setDispatch(self, disp):
        self.dispatch = disp
    
    def setMass(self, mass):
        self.mass = mass
        
    def setSolid(self, solidType):
        self.solidType = solidType
        
    def initPhysics(self):
        self.setupPhysics(self.getPhysBody(), False)
        self.addToPhysicsWorld(self.air.getPhysicsWorld(self.zoneId))

    def getPhysBody(self):
        from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
        from panda3d.core import TransformState
        
        bnode = BulletRigidBodyNode('entity-phys')
        bnode.setMass(self.mass)

        bnode.setCcdMotionThreshold(1e-7)
        bnode.setCcdSweptSphereRadius(0.5)
        
        if self.solidType == self.SOLID_MESH:
            convexHull = PhysicsUtils.makeBulletConvexHullFromCollisionSolids(self.model.find("**/+CollisionNode").node())
            bnode.addShape(convexHull)
        elif self.solidType == self.SOLID_BBOX:
            mins = Point3()
            maxs = Point3()
            self.calcTightBounds(mins, maxs)
            extents = PhysicsUtils.extentsFromMinMax(mins, maxs)
            tsCenter = TransformState.makePos(PhysicsUtils.centerFromMinMax(mins, maxs))
            shape = BulletBoxShape(extents)
            bnode.addShape(shape, tsCenter)
        
        return bnode

    def d_playSound(self, soundName):
        self.sendUpdate('playSound', [soundName])

    def d_loopSound(self, soundName):
        self.sendUpdate('loopSound', [soundName])

    def d_stopSound(self, soundName):
        self.sendUpdate('stopSound', [soundName])
        
    def b_setModel(self, model, animating = False):
        self.setModel(model, animating)
        self.sendUpdate('setModel', self.getModel())
        
    def b_setModelOrigin(self, org):
        self.setModelOrigin(org)
        self.sendUpdate('setModelOrigin', [self.getModelOrigin()])
        
    def b_setModelAngles(self, ang):
        self.setModelAngles(ang)
        self.sendUpdate('setModelAngles', [self.getModelAngles()])
        
    def b_setModelScale(self, scale):
        self.setModelScale(scale)
        self.sendUpdate('setModelScale', [self.getModelScale()])

    def enableModelCollisions(self):
        if self.model:
            PhysicsUtils.makeBulletCollFromPandaColl(self.model)
            PhysicsUtils.attachBulletNodes(self.model, self.air.getPhysicsWorld(self.getZoneId()))
            
    def disableModelCollisions(self):
        if self.model:
            PhysicsUtils.detachBulletNodes(self.model, self.air.getPhysicsWorld(self.getZoneId()))
        
    def b_setEntityState(self, state):
        self.sendUpdate('setEntityState', [state])
        self.setEntityState(state)
        
    def getZoneId(self):
        if self.dispatch:
            return self.dispatch.zoneId
        return self.zoneId
        
    def getEntZoneId(self):
        return self.zoneId
        
    def loadEntityValues(self):
        pass
        
    def setupBrushEntityPhysics(self):
        #self.dispatch.brushCollisionMaterialData.update(
        #    PhysicsUtils.makeBulletCollFromGeoms(self.cEntity.getModelNp(), world=self.dispatch.physicsWorld))
        #PhysicsUtils.attachBulletNodes(self.cEntity.getModelNp(), self.dispatch.physicsWorld)
        
        #print self.dispatch.brushCollisionMaterialData
        pass
        
    def load(self):
        self.__dynamicEntity = False
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)
        
        from panda3d.bsp import CBrushEntity
        if isinstance(self.cEntity, CBrushEntity):
            self.assign(self.cEntity.getModelNp())
            #self.setupBrushEntityPhysics()
            self.__isBrushEntity = True
            
        self.tryEntityParent()
        self.loadEntityValues()
        self.generateWithRequired(self.zoneId)
        
        render.ls()

    def announceGenerate(self):
        DistributedSmoothNodeAI.announceGenerate(self)
        if self.__dynamicEntity:
            battleZone = self.air.battleZones.get(self.zoneId)
            if battleZone:
                self.bspLoader = battleZone.bspLoader
                self.bspLoader.addDynamicEntity(self)
        self.enableThink()

    def unload(self):
        self.__unloaded = True
        self.requestDelete()
        Entity.unload(self)
        
    def delete(self):
        if (not self.__unloaded) and self.__dynamicEntity and self.bspLoader:
            self.bspLoader.removeDynamicEntity(self)
        #if self.__isBrushEntity:
        #    PhysicsUtils.detachBulletNodes(self.cEntity.getModelNp(), self.dispatch.physicsWorld)
        self.cleanupPhysics()
        self.solidType = None
        self.mass = None
        self.__isBrushEntity = None
        Entity.unload(self)
        DistributedSmoothNodeAI.delete(self)
        self.dispatch = None
        self.__dynamicEntity = None
        self.__unloaded = None
