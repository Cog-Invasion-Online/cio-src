from panda3d.core import Vec3, Point3
from panda3d.bullet import BulletCylinderShape, BulletRigidBodyNode, ZUp

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.interval.IntervalGlobal import ActorInterval, Func
from direct.actor.Actor import Actor

from BaseGag import BaseGag, BaseGagAI
from src.coginvasion.avatar.Attacks import ATTACK_GAG_TNT, ATTACK_HOLD_RIGHT
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.phys.DistributedPhysicsEntity import DistributedPhysicsEntity
from src.coginvasion.phys.DistributedPhysicsEntityAI import DistributedPhysicsEntityAI

import random

class TNTProjectile(DistributedPhysicsEntity):
    
    def __init__(self, cr):
        DistributedPhysicsEntity.__init__(self)
        self.tnt = None
        self.tntSound = None
        self.particle = None

    def getPhysBody(self):
        shape = BulletCylinderShape(0.3925, 1.4, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(shape)
        body.setKinematic(True)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.3925)
        return body

    def explode(self):
        self.tntSound.stop()
        self.hide()
        self.particle.softStop()
        self.cleanupPhysics()
        CIGlobals.makeExplosion(self.getPos(render) + (0, 0, 5.0), 0.7, True)

    def announceGenerate(self):
        self.tnt = Actor('phase_14/models/props/tnt.bam', {'chan': 'phase_5/models/props/tnt-chan.bam'})
        self.tnt.reparentTo(self)
        self.tnt.play('chan')
        self.tnt.setP(97.492)
        self.tnt.setY(0.38)
        self.tntSound = base.loadSfxOnNode("phase_14/audio/sfx/dynamite_loop.ogg", self.tnt)
        self.tntSound.setLoop(True)
        self.particle = loader.loadParticleEffect("phase_14/etc/tnt_spark.ptf")
        self.particle.start(self.tnt.find('**/joint_attachEmitter'), CIGlobals.getParticleRender())

        DistributedPhysicsEntity.announceGenerate(self)

        self.tntSound.play()

    def disable(self):
        if self.tnt:
            self.tnt.cleanup()
            self.tnt.removeNode()
        self.tnt = None
        if self.tntSound:
            self.tntSound.stop()
        self.tntSound = None
        if self.particle:
            self.particle.softStop()
        self.particle = None

        DistributedPhysicsEntity.disable(self)

class TNTProjectileAI(DistributedPhysicsEntityAI):

    def __init__(self, air, avatar, attack):
        DistributedPhysicsEntityAI.__init__(self, air)
        self.avatar = avatar
        self.attack = attack
    
    def getPhysBody(self):
        shape = BulletCylinderShape(0.3925, 1.4, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(shape)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.3925)
        body.setKinematic(False)
        body.setMass(5.0)
        body.setAngularDamping(0.3)
        body.setLinearDamping(0.8)
        return body

    def announceGenerate(self):
        DistributedPhysicsEntityAI.announceGenerate(self)
        taskMgr.doMethodLater(2.1, self.__explodeTask, self.uniqueName('TNT_explodeTask'))

    def delete(self):
        taskMgr.remove(self.uniqueName('TNT_explodeTask'))
        self.avatar = None
        self.attack = None
        DistributedPhysicsEntityAI.delete(self)

    def __explodeTask(self, task):
        self.sendUpdate('explode')

        for obj in self.air.avatars[self.zoneId]:
            if CIGlobals.isAvatar(obj):
                dist = obj.getDistance(self)
                if dist <= GagGlobals.TNT_RANGE:
                    info = TakeDamageInfo(self.avatar, ATTACK_GAG_TNT, self.attack.calcDamage(dist), self.getPos())
                    obj.takeDamage(info)

        self.requestDelete()
        return task.done

class TNTShared:
    StateDraw = 1
    StateThrow = 2

class TNT(BaseGag, TNTShared):
    ID = ATTACK_GAG_TNT
    Name = GagGlobals.TNT

    ModelPath = "phase_14/models/props/tnt.bam"
    ModelAnimPath = "phase_5/models/props/tnt-chan.bam"
    Hold = ATTACK_HOLD_RIGHT

    ModelVMOrigin = (-0.23, 0.26, 0.05)
    ModelVMAngles = (321.45, 55.74, 120.67)
    ModelVMScale = 0.5

    def getViewPunch(self):
        return Vec3(random.uniform(.5, 1), random.uniform(-.5, -1), 0)

    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, self.avatar.getRightHandNode().getPos(render))
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
        print "Added data"

    def setAction(self, action):
        BaseGag.setAction(self, action)

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()
            vmGag = self.getVMGag()
            vmGag.show()

        if action == self.StateDraw:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(ActorInterval(vm, 'tnt_draw'))
            self.doDrawNoHold('toss', 0, 30)

        elif action == self.StateIdle:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(Func(vm.loop, 'tnt_idle'))
            self.doHold('toss', 30, 30, 1.0)

        elif action == self.StateThrow:
            if self.isFirstPerson():
                vmGag.hide()
                fpsCam.addViewPunch(self.getViewPunch())
                fpsCam.setVMAnimTrack(ActorInterval(vm, 'tnt_throw', startFrame = 27))
            self.setAnimTrack(self.getAnimationTrack('toss', 60), startNow = True)

class TNT_AI(BaseGagAI, TNTShared):
    ID = ATTACK_GAG_TNT
    Name = GagGlobals.TNT

    ThrowPower = 100.0

    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   1.0,
                                   self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

    def equip(self):
        if not BaseGagAI.equip(self):
            return False

        self.b_setAction(self.StateDraw)

        return True

    def determineNextAction(self, completedAction):
        if completedAction == self.StateDraw:
            return self.StateIdle
        elif completedAction == self.StateThrow:
            return self.StateDraw

        return self.StateIdle

    def setAction(self, action):
        BaseGagAI.setAction(self, action)

        if action == self.StateThrow:
            self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(
                self.traceOrigin,
                self.traceVector,
                self.throwOrigin,
                self.getAvatar(),
                self.getAvatar().getBattleZone().getPhysicsWorld())

            proj = TNTProjectileAI(base.air, self.avatar, self)
            proj.generateWithRequired(self.avatar.zoneId)
            proj.setPos(self.throwOrigin)
            proj.lookAt(throwVector)
            proj.node().setLinearVelocity(throwVector * self.ThrowPower)
            proj.d_clearSmoothing()
            proj.d_broadcastPosHpr()

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.throwOrigin = CIGlobals.getVec3(dgi)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateThrow)
