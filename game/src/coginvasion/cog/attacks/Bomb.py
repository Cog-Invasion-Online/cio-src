from panda3d.core import Vec3, Point3, TransformState
from panda3d.bullet import BulletCylinderShape, BulletSphereShape, BulletRigidBodyNode, ZUp

from direct.interval.IntervalGlobal import Func, Sequence, Wait, Parallel
from direct.actor.Actor import Actor

from src.coginvasion.avatar.BaseAttacks import BaseAttack, BaseAttackAI
from src.coginvasion.avatar.Attacks import ATTACK_BOMB, ATTACK_HOLD_RIGHT
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.phys.DistributedPhysicsEntity import DistributedPhysicsEntity
from src.coginvasion.phys.DistributedPhysicsEntityAI import DistributedPhysicsEntityAI

import random

class BombProjectile(DistributedPhysicsEntity):
    
    def __init__(self, cr):
        DistributedPhysicsEntity.__init__(self, cr)
        self.tnt = None
        self.tntSound = None
        self.particle = None

    def getPhysBody(self):
        bsph = BulletSphereShape(0.6)
        bcy = BulletCylinderShape(0.25, 0.35, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(bsph, TransformState.makePosHpr((0.05, 0, 0.43), (86.597, 24.5539, 98.1435)))
        body.addShape(bcy, TransformState.makePosHpr((0.05, 0.655, 0.35), (86.597, 24.5539, 98.1435)))
        body.setKinematic(True)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.6)
        return body

    def explode(self):
        self.tntSound.stop()
        self.hide()
        self.particle.softStop()
        self.cleanupPhysics()
        CIGlobals.makeExplosion(self.getPos(render) + (0, 0, 5.0), 0.7, True)

    def announceGenerate(self):
        self.tnt = Actor('phase_14/models/props/cog_bomb.bam', {'chan': 'phase_5/models/props/tnt-chan.bam'})
        self.tnt.reparentTo(self)
        self.tnt.play('chan')

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

class BombProjectileAI(DistributedPhysicsEntityAI):

    def __init__(self, air, avatar, attack):
        DistributedPhysicsEntityAI.__init__(self, air)
        self.avatar = avatar
        self.attack = attack
    
    def getPhysBody(self):
        bsph = BulletSphereShape(0.6)
        bcy = BulletCylinderShape(0.25, 0.35, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(bsph, TransformState.makePosHpr((0.05, 0, 0.43), (86.597, 24.5539, 98.1435)))
        body.addShape(bcy, TransformState.makePosHpr((0.05, 0.655, 0.35), (86.597, 24.5539, 98.1435)))
        body.setKinematic(False)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.6)
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
            if CIGlobals.isAvatar(obj) and not CIGlobals.avatarsAreFriends(self.avatar, obj):
                dist = obj.getDistance(self)
                if dist <= 10.0:
                    info = TakeDamageInfo(self.avatar, ATTACK_BOMB, self.attack.calcDamage(dist), self.getPos())
                    obj.takeDamage(info)

        self.requestDelete()
        return task.done

class BombShared:
    StateThrow = 1

class Bomb(BaseAttack, BombShared):
    ID = ATTACK_BOMB
    Name = "Blast"

    ModelPath = "phase_14/models/props/cog_bomb.bam"
    Hold = ATTACK_HOLD_RIGHT

    ReleasePlayRateMultiplier = 1.0
    ThrowObjectFrame = 68
    PlayRate = 1.5

    def equip(self):
        if not BaseAttack.equip(self):
            return False

        return True
        
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
            
        self.avatar.doingActivity = False
            
        return True

    def onSetAction(self, action):
        self.model.show()

        self.avatar.doingActivity = False

        if action == self.StateThrow:

            self.avatar.doingActivity = True
            
            time = 0.0#3.0 * 0.667
            sf = self.ThrowObjectFrame#0

            self.setAnimTrack(
                Parallel(self.getAnimationTrack('throw-object', startFrame=sf,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier), fullBody = False),
                         Sequence(Wait(time), Func(self.model.hide))),
                startNow = True)

class Bomb_AI(BaseAttackAI, BombShared):
    ID = ATTACK_BOMB
    Name = "Blast"

    ThrowPower = 100.0

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.maxAmmo = 2
        self.ammo = 2

    def getPostAttackSchedule(self):
        # Take cover after we throw our bomb
        return "TAKE_COVER_FROM_ORIGIN"

    def equip(self):
        if not BaseAttackAI.equip(self):
            return False

        self.b_setAction(self.StateIdle)

        return True

    def determineNextAction(self, completedAction):
        return self.StateIdle

    def onSetAction(self, action):
        if action == self.StateThrow:
            self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(
                self.traceOrigin,
                self.traceVector,
                self.throwOrigin,
                self.getAvatar(),
                self.getAvatar().getBattleZone().getPhysicsWorld()) + (0, 0, 0.1)

            proj = BombProjectileAI(base.air, self.avatar, self)
            proj.generateWithRequired(self.avatar.zoneId)
            proj.setPos(self.throwOrigin)
            proj.lookAt(throwVector)
            proj.node().setLinearVelocity(throwVector * self.ThrowPower)
            proj.d_clearSmoothing()
            proj.d_broadcastPosHpr()

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance >= 25*25 and squaredDistance <= 50*50

    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.throwOrigin = (self.avatar.getPos(render) + (0, 0, self.avatar.getHeight() / 2.0)) + (self.avatar.getQuat().getForward() * 2)
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
        self.setNextAction(self.StateThrow)

