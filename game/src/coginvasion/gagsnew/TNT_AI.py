from panda3d.core import Vec3, Point3
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from BaseGagAI import BaseGagAI
from TNTShared import TNTShared
from TNTProjectileAI import TNTProjectileAI
from src.coginvasion.attack.Attacks import ATTACK_GAG_TNT
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class TNT_AI(BaseGagAI, TNTShared):
    ID = ATTACK_GAG_TNT
    Name = GagGlobals.TNT

    ThrowPower = 100.0
    
    Cost = 500

    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   0.71,
                                   self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)
        
    def getBaseDamage(self):
        return 180
        
    def getDamageMaxDistance(self):
        return 10

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

    def onSetAction(self, action):
        if action == self.StateThrow:
            self.takeAmmo(-1)
            
            av = self.getAvatar()

            throwVector = PhysicsUtils.getThrowVector(
                self.traceOrigin,
                self.traceVector,
                self.throwOrigin,
                av,
                av.getBattleZone().getPhysicsWorld()) + (0, 0, 0.1)

            proj = TNTProjectileAI(base.air, self.avatar, self)
            proj.generateWithRequired(self.avatar.getBattleZone().zoneId)
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
