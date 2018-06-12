from panda3d.bullet import BulletGhostNode, BulletSphereShape
from panda3d.core import NodePath, Point3, TransformState

from src.coginvasion.globals import CIGlobals

class WorldCollider(NodePath):

    def __init__(self, name, radius, collideEvent,
                 mask = CIGlobals.FloorGroup | CIGlobals.WallGroup,
                 offset = Point3(0), needSelfInArgs = False):

        NodePath.__init__(self, BulletGhostNode(name))

        self.needSelfInArgs = needSelfInArgs
        self.event = collideEvent
        self.mask = mask

        sphere = BulletSphereShape(radius)
        self.node().addShape(sphere, TransformState.makePos(offset))
        self.node().setKinematic(True)

        self.setCollideMask(CIGlobals.EventGroup)

        base.physicsWorld.attach(self.node())

        self.task = taskMgr.add(self.__collisionTick, "WorldCollider.collisionTick" + str(id(self)))

    def removeNode(self):
        if hasattr(self, 'task'):
            taskMgr.remove(self.task)
            del self.task
            del self.event

        if self.isEmpty():
            return

        base.physicsWorld.remove(self.node())
        print "removeNode of WorldCollider"
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
            print intoNode
            mask = intoNode.getIntoCollideMask()
            if self.bitsIntersecting(mask, self.mask):
                print "WorldCollider collision! sending event", self.event
                args = [NodePath(intoNode)]
                if self.needSelfInArgs:
                    args.insert(0, self)
                messenger.send(self.event, args)
                return task.done

        return task.cont
