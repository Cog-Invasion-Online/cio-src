from panda3d.bullet import BulletGhostNode, BulletSphereShape
from panda3d.core import NodePath, Point3, TransformState

from src.coginvasion.globals import CIGlobals

class WorldCollider(NodePath):

    def __init__(self, name, radius, collideEvent = None,
                 mask = CIGlobals.WorldGroup,
                 offset = Point3(0), needSelfInArgs = False,
                 startNow = True, myMask = CIGlobals.EventGroup,
                 exclusions = [], resultInArgs = False):

        NodePath.__init__(self, BulletGhostNode(name))

        self.needSelfInArgs = needSelfInArgs
        self.resultInArgs = resultInArgs
        self.event = collideEvent
        self.mask = mask
        self.exclusions = exclusions

        sphere = BulletSphereShape(radius)
        self.node().addShape(sphere, TransformState.makePos(offset))
        self.node().setKinematic(True)

        self.setCollideMask(myMask)

        if startNow:
            self.start()

    def getCollideEvent(self):
        if self.event:
            return self.event
        return self.node().getName() + str(id(self))

    def start(self):
        if self.isEmpty():
            return
            
        base.physicsWorld.attach(self.node())
        self.task = taskMgr.add(self.__collisionTick, "WorldCollider.collisionTick" + str(id(self)))

    def stop(self):
        if hasattr(self, 'task'):
            taskMgr.remove(self.task)
            del self.task
            
        if self.isEmpty():
            return
            
        base.physicsWorld.remove(self.node())

    def removeNode(self):
        if self.isEmpty():
            return
        self.stop()
        if hasattr(self, 'event'):
            del self.event
        NodePath.removeNode(self)

    def bitsIntersecting(self, a, b):
        return not (a & b).isZero()

    def __collisionTick(self, task):
        if self.isEmpty():
            return task.done

        result = base.physicsWorld.contactTest(self.node())
        for contact in result.getContacts():
            intoNode = contact.getNode1()
            if intoNode == self.node():
                intoNode = contact.getNode0()
            if intoNode.isOfType(BulletGhostNode.getClassType()):
                continue
            isExcluded = False
            for excl in self.exclusions:
                if excl.isAncestorOf(NodePath(intoNode)) or excl == NodePath(intoNode):
                    isExcluded = True
                    break
            if isExcluded:
                continue
            mask = intoNode.getIntoCollideMask()
            if self.bitsIntersecting(mask, self.mask):
                args = [NodePath(intoNode)]
                if self.needSelfInArgs:
                    args.insert(0, self)
                if self.resultInArgs:
                    args.insert(0, contact)
                messenger.send(self.getCollideEvent(), args)
                return task.done

        return task.cont
