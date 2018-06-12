from panda3d.core import NodePath, BitMask32, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode

from src.coginvasion.globals import CIGlobals

class PhysicsNodePath(NodePath):

    def __init__(self, *args, **kwargs):
        NodePath.__init__(self, *args, **kwargs)
        self.bodyNode = None
        self.bodyNP = None
        self.shapeGroup = BitMask32.allOn()
        self.underneathSelf = False
        self.shadow = None
        self.shadowPlacerTask = None

    def makeShadow(self, scale = 1):
        self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
        self.shadow.setScale(scale)
        self.shadow.flattenMedium()
        self.shadow.setBillboardAxis(4)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        self.shadow.reparentTo(self)

        self.shadowPlacerTask = taskMgr.add(self.__shadowPlacerTask, "shadowPlacerTask")

    def __shadowPlacerTask(self, task):
        if self.shadow.isEmpty():
            return task.done

        start = self.shadow.getPos(render)
        end = self.shadow.getPos(render) + (Vec3.down() * 500)
        result = base.physicsWorld.rayTestClosest(start, end)
        if result.hasHit():
            self.shadow.setPos(result.getHitPos())
        else:
            self.shadow.setPos(0, 0, 0)
        self.shadow.setHpr(render, 0, 0, 0)

        return task.cont

    def cleanupPhysics(self):
        if self.bodyNode:
            if self.bodyNode.isExactType(BulletGhostNode.getClassType()):
                base.physicsWorld.removeGhost(self.bodyNode)
            else:
                base.physicsWorld.removeRigidBody(self.bodyNode)
        if self.bodyNP and not self.bodyNP.isEmpty():
            if self.underneathSelf:
                self.bodyNP.removeNode()
            self.bodyNP = None
            self.bodyNode = None

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
            self.bodyNP.wrtReparentTo(self)
        if self.bodyNode.isExactType(BulletGhostNode.getClassType()):
            base.physicsWorld.attachGhost(self.bodyNode)
        else:
            base.physicsWorld.attachRigidBody(self.bodyNode)
            