from panda3d.core import Vec3, Point3

from BombShared import BombShared
from BombProjectileAI import BombProjectileAI
from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.attack.Attacks import ATTACK_BOMB
from src.coginvasion.phys import PhysicsUtils

class Bomb_AI(BaseAttackAI, BombShared):
    ID = ATTACK_BOMB
    Name = "Blast"

    ThrowPower = 100.0
    FriendlyFire = True

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.maxAmmo = 2
        self.ammo = 2
        
    def getTauntChance(self):
        return 0.5
        
    def getTauntPhrases(self):
        return ["Bombs away!"]

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
            proj.generateWithRequired(self.avatar.getBattleZone().zoneId)
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
