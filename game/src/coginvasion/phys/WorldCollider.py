from panda3d.bullet import BulletGhostNode, BulletSphereShape, BulletRigidBodyNode
from panda3d.core import NodePath, Point3, TransformState

from src.coginvasion.globals import CIGlobals

class WorldCollider(NodePath):

    WantNPInit = True

    def __init__(self, name, radius, collideEvent = None,
                 mask = CIGlobals.WorldGroup,
                 offset = Point3(0), needSelfInArgs = False,
                 startNow = True, myMask = CIGlobals.EventGroup,
                 exclusions = [], resultInArgs = False, useSweep = False,
                 world = None, initNp = True, useGhost = True):

        if self.WantNPInit:
            NodePath.__init__(self)
        if useGhost:
            node = BulletGhostNode(name)
        else:
            node = BulletRigidBodyNode(name)
        self.assign(NodePath(node))

        self.needSelfInArgs = needSelfInArgs
        self.resultInArgs = resultInArgs
        self.event = collideEvent
        self.mask = mask
        self.__exclusions = []
        self.useSweep = useSweep
        if not world and hasattr(base, 'physicsWorld'):
            world = base.physicsWorld
        self.world = world
        
        self.initialPos = Point3(0)
        self.lastPos = Point3(0)
        
        self.hitCallbacks = []

        sphere = BulletSphereShape(radius)
        self.node().addShape(sphere, TransformState.makePos(offset))
        self.node().setKinematic(True)
        if useSweep:
            self.node().setCcdMotionThreshold(1e-7)
            self.node().setCcdSweptSphereRadius(radius * 1.05)

        self.setCollideMask(myMask)

        if startNow:
            self.start()

    def addExclusion(self, excl):
        #print "Add exclusion", self, id(self), self.__exclusions, id(self.__exclusions)
        self.__exclusions.append(excl)
            
    def addHitCallback(self, cbk):
        self.hitCallbacks.append(cbk)

    def getCollideEvent(self):
        if self.event:
            return self.event
        return self.node().getName() + str(id(self))

    def getInitialPos(self):
        return self.initialPos

    def start(self):
        if self.isEmpty():
            return
            
        self.initialPos = self.getPos(render)
        self.lastPos = self.initialPos
            
        self.world.attach(self.node())
        self.task = taskMgr.add(self.tick, "WorldCollider.collisionTick" + str(id(self)))

    def stop(self):
        if hasattr(self, 'task'):
            taskMgr.remove(self.task)
            del self.task

        if hasattr(self, 'initialPos'):
            del self.initialPos
            del self.lastPos
            
        if self.isEmpty():
            return
            
        self.world.remove(self.node())

    def removeNode(self):
        if self.isEmpty():
            return
        self.stop()
        if hasattr(self, 'event'):
            del self.event
        NodePath.removeNode(self)

    def bitsIntersecting(self, a, b):
        return not (a & b).isZero()

    def tick(self, task):
        if self.isEmpty():
            return task.done
            
        currPos = self.getPos(render)
        
        intoNode = None
        
        if self.useSweep:
            #print "From", self.lastPos, "to", currPos
            #print "Exclusions", self.__exclusions
            # Sweep test ensures no slip-throughs, but is a bit more expensive.
            result = self.world.sweepTestClosest(self.node().getShape(0), TransformState.makePos(self.lastPos),
                                                 TransformState.makePos(currPos), self.mask)
            if result.hasHit():
                #print "has hit"
                intoNode = result.getNode()
                for excl in self.__exclusions:
                    if excl.isAncestorOf(NodePath(intoNode)) or excl == NodePath(intoNode):
                        #print "Collided with exclusion", excl
                        intoNode = None
                        break
                contact = result
            #else:
                #print "no hit"
        else:
            result = self.world.contactTest(self.node())
            for contact in result.getContacts():
                node = contact.getNode1()
                if node == self.node():
                    node = contact.getNode0()
                if node.isOfType(BulletGhostNode.getClassType()):
                    continue
                isExcluded = False
                for excl in self.__exclusions:
                    if excl.isAncestorOf(NodePath(node)) or excl == NodePath(node):
                        isExcluded = True
                        break
                if isExcluded:
                    continue
                    
                intoNode = node
                break
        
        if currPos != self.lastPos:
            self.lastPos = currPos
        
        if intoNode is None:
            return task.cont
        
        mask = intoNode.getIntoCollideMask()
        if self.bitsIntersecting(mask, self.mask):
            args = [NodePath(intoNode)]
            if self.needSelfInArgs:
                args.insert(0, self)
            if self.resultInArgs:
                args.insert(0, contact)
            messenger.send(self.getCollideEvent(), args)
            if hasattr(self, 'onCollide'):
                self.onCollide(*args)
            for clbk in self.hitCallbacks:
                clbk(*args)
            return task.done
            
        return task.cont
