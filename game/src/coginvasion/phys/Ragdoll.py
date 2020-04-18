from panda3d.bullet import *
from panda3d.core import CharacterJoint, TransformState, NodePath, Vec3

from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Parallel

class RagdollJointDesc:

    def __init__(self, limbA, limbB, axis0, axis1, swing, twist):
        self.limbA = limbA
        self.limbB = limbB
        self.axis0 = axis0
        self.axis1 = axis1
        self.swing = swing
        self.twist = twist
        
        self.constraint = None

class RagdollLimbDesc:

    def __init__(self, jointName, mass, shapes):
        self.jointName = jointName
        self.mass = mass
        self.shapes = shapes
        self.bodyNode = None
        
# Limbs are capsules
class RagdollLimbShapeDesc:

    def __init__(self, length = 1, radius = 0.2, localPos = (0, 0, 0), localHpr = (0, 0, 0)):
        self.length = length
        self.radius = radius
        self.localPos = localPos
        self.localHpr = localHpr

class ActorJointDesc:
    
    def __init__(self, name):
        self.name = name
        self.parentName = None
        self.eNp = None
        self.cNp = None
        self.limb = None

        self.bodyNode = None
        
    def getParent(self, actorJoints):
        return actorJoints[actorJoints[self.name].parentName]

class Ragdoll(DirectObject):

    # Ragdoll mode
    RMRagdoll = 0
    RMKinematic = 1

    def __init__(self, actor, partName = "modelRoot"):
        self.actor = actor
        self.partName = partName
        self.mode = Ragdoll.RMKinematic
        self.actorJoints = {}
        self.joints = []
        self.jointsOrder = []
        self.limbs = {}
        self.attached = False
        self.enabled = False
        self.lastBlendTime = 0
        self.blendParallel = []
        self.blendActor = None
        self.updateTask = None
        
    def getMainLimb(self):
        return ""
        
    def applyForce(self, force, pos):
        for limb in self.limbs.values():
            mat = limb.bodyNode.getMat(render)
            mat.invertInPlace()
            limb.bodyNode.node().applyImpulse(force, mat.xformPoint(pos))
        
    def cleanup(self):
        if self.updateTask:
            self.updateTask.remove()
        self.updateTask = None
        if self.blendActor:
            self.blendActor.cleanup()
        self.blendActor = None
        self.blendParallel = None
        self.lastBlendTime = None
        self.enabled = None
        self.attached = None
        
        for joint in self.joints:
            if joint.constraint:
                base.physicsWorld.removeConstraint(joint.constraint)
        self.joints = None
        
        for limb in self.limbs.values():
            if limb.bodyNode:
                base.physicsWorld.remove(limb.bodyNode.node())
                limb.bodyNode.removeNode()
        self.limbs = None
        
        self.jointsOrder = None
        self.actorJoints = None
        self.mode = None
        self.partName = None
        self.actor = None

    def setup(self):
        self.setupLimbs()
        self.setupJoints()
        self.mode = Ragdoll.RMKinematic
        self.createActorJointsDesc(self.actor.getPartBundle(self.partName), None)
        self.exposeActorJoints()
        self.updateTask = base.taskMgr.add(self.__updateTask, "ragdoll-update" + str(id(self)))

    def setupLimbs(self):
        pass

    def setupJoints(self):
        pass

    def addJoint(self, limbA, limbB, axis0, axis1, swing = (0, 0), twist = 0):
        self.joints.append(RagdollJointDesc(limbA, limbB, axis0, axis1, swing, twist))

    def addLimb(self, jointName, mass = 1, shapes = [RagdollLimbShapeDesc()]):
        self.limbs[jointName] = RagdollLimbDesc(jointName, mass, shapes)

    def createActorJointsDesc(self, part, parentPart = None):
        eNp = None

        if isinstance(part, CharacterJoint):
            jointName = part.getName()
            jointDesc = ActorJointDesc(jointName)
            self.actorJoints[jointName] = jointDesc

        for child in part.getChildren():
            self.createActorJointsDesc(child, eNp)

    def exposeActorJoints(self):
        self.jointsOrder = []

        usedJointsTemp = []
        for limb in self.limbs.values():
            usedJointsTemp.append(limb.jointName)

        self.exposeActorJointsRec(usedJointsTemp, self.actor.getPartBundle(self.partName), None)

    def exposeActorJointsRec(self, usedJointsTemp, part, parentPart = None):
        eNp = None
        if isinstance(part, CharacterJoint):
            jointName = part.getName()
            jointDesc = self.actorJoints[jointName]
            if jointName in usedJointsTemp:
                self.jointsOrder.append(jointName)

                if parentPart is not None:
                    jointDesc.parentName = parentPart.getName()

                eNp = self.actor.exposeJoint(None, self.partName, jointName)
                jointDesc.eNp = eNp

        for child in part.getChildren():
            self.exposeActorJointsRec(usedJointsTemp, child, eNp)

    def createLimbs(self):
        # For each limbs desc, create a bullet capsule
        for limb in self.limbs.values():
            body = BulletRigidBodyNode("ragdoll-limb-" + limb.jointName)
            body.setMass(limb.mass)
            for i in xrange(len(limb.shapes)):
                shapeDesc = limb.shapes[i]
                capsule = BulletCapsuleShape(shapeDesc.radius, shapeDesc.length / 2.0, ZUp)
                body.addShape(capsule, TransformState.makePosHpr(shapeDesc.localPos, shapeDesc.localHpr))
            jointDesc = self.actorJoints[limb.jointName]
            eNp = jointDesc.eNp
            jointDesc.limb = limb
            bodyNp = NodePath(body)
            bodyNp.reparentTo(render)
            bodyNp.setTransform(render, eNp.getTransform(render))
            bodyNp.node().setTransformDirty()
            base.physicsWorld.attachRigidBody(body)
            limb.bodyNode = bodyNp

    def createJoints(self):
        for jointDesc in self.joints:
            limbA = self.limbs[jointDesc.limbA]
            limbB = self.limbs[jointDesc.limbB]
            a = self.limbs[jointDesc.limbA].bodyNode
            b = self.limbs[jointDesc.limbB].bodyNode
            jointA = self.actorJoints[jointDesc.limbA].eNp
            jointB = self.actorJoints[jointDesc.limbB].eNp
            frame0 = TransformState.makePosHpr(jointDesc.axis0[0], jointDesc.axis0[1])
            frame1 = TransformState.makePosHpr(jointDesc.axis1[0], jointDesc.axis1[1])
            constraint = BulletConeTwistConstraint(a.node(),
                                                   b.node(),
                                                   frame0, frame1)
            constraint.setLimit(float(jointDesc.swing[0]), float(jointDesc.swing[1]), float(jointDesc.twist))
            constraint.setEnabled(True)
            constraint.setDebugDrawSize(1.5)
            jointDesc.constraint = constraint
            base.physicsWorld.attachConstraint(constraint)

    def attachActor(self):
        if self.attached:
            for jointName in self.jointsOrder:
                jointDesc = self.actorJoints[jointName]
        else:
            self.attached = True
            for jointName in self.jointsOrder:
                jointDesc = self.actorJoints[jointName]
                if jointDesc.parentName is None:
                    cNp = jointDesc.eNp
                else:
                    cNp = jointDesc.getParent(self.actorJoints).eNp.attachNewNode(jointName)
                self.actor.controlJoint(cNp, self.partName, jointName)
                cNp.setMat(render, jointDesc.eNp.getMat(render))
                jointDesc.cNp = cNp

    def detachActor(self):
        if not self.attached:
            return
        self.attached = False

        for jointName in self.jointsOrder:
            jointDesc = self.actorJoints[jointName]
            if jointDesc.cNp is None:
                continue
            self.actor.releaseJoint(self.partName, jointName)
            if jointDesc.limb.bodyNode is not None:
                jointDesc.limb.bodyNode.node().removeAllChildren()
            jointDesc.cNp.removeNode()
            jointDesc.cNp = None

        self.exposeActorJoints()

    def setEnabled(self, flag):
        if self.enabled and flag:
            return

        self.enabled = flag
        if flag:
            self.createLimbs()
            self.createJoints()

    def setKinematicMode(self):
        self.mode = Ragdoll.RMKinematic
        self.setEnabled(True)

    def __updateTask(self, task):
        if not self.enabled:
            return task.cont

        if self.mode == Ragdoll.RMKinematic:
            for limb in self.limbs.values():
                eNp = self.actorJoints[limb.jointName].eNp
                limb.bodyNode.setTransform(render, eNp.getTransform(render))
                limb.bodyNode.node().setTransformDirty()
        elif self.mode == Ragdoll.RMRagdoll:
            for limb in self.limbs.values():
                cNp = self.actorJoints[limb.jointName].cNp
                cNp.setTransform(render, limb.bodyNode.getTransform(render))

        return task.cont

    def blendToKinematicMode(self, blendTime):
        time = globalClock.getFrameTime()
        if time - self.lastBlendTime < 0.5:
            return

        self.lastBlendTime = time
        if self.blendParallel is not None:
            self.blendParallel[0].pause()
            base.taskMgr.remove(self.blendParallel[1])
            self.blendParallel = None

        self.blendActor = Actor()
        self.blendActor.copyActor(self.actor, True)
        self.blendActor.pose(self.actor.getCurrentAnim(), self.actor.getCurrentFrame())
        self.blendActor.reparentTo(self.actor.getParent())
        
        for jointName in self.jointsOrder:
            self.blendActor.releaseJoint(self.partName, jointName)

        self.setKinematicMode()

        self.blendParallel = [Parallel(), base.taskMgr.doMethodLater(blendTime, self.__blendFinished, 'blendTask')]

        for jointName in self.jointsOrder:
            eNp = self.blendActor.exposeJoint(None, self.partName, jointName)
            jointDesc = self.actorJoints[jointName]
            if jointDesc.cNp is None:
                continue
            ival = jointDesc.cNp.posInterval(blendTime, eNp.getPos(render), other = render)
            self.blendParallel[0].append(ival)
            ival = jointDesc.cNp.quatInterval(blendTime, hpr = eNp.getHpr(render), other = render)
            self.blendParallel[0].append(ival)

        self.blendParallel[0].start()

        self.blendActor.cleanup()
        self.blendActor.removeNode()
        self.blendActor = None

    def __blendFinished(self, task):
        self.detachActor()
        return task.done
