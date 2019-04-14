from panda3d.core import Point3, Vec3

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta

from BaseGagAI import BaseGagAI
from WholeCreamPieShared import WholeCreamPieShared
from WholeCreamPieProjectileAI import WholeCreamPieProjectileAI
from src.coginvasion.attack.Attacks import ATTACK_GAG_WHOLECREAMPIE
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

class WholeCreamPieAI(BaseGagAI, WholeCreamPieShared):

    Name = GagGlobals.WholeCreamPie
    ID = ATTACK_GAG_WHOLECREAMPIE

    ThrowPower = 200.0

    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   0.5,
                                   self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.ammo = 100
        self.maxAmmo = 100

        self.__projs = []

        self.throwTime = 0

    def getBaseDamage(self):
        return 30

    def equip(self):
        if not BaseGagAI.equip(self):
            return False

        self.throwTime = globalClock.getFrameTime()

        # Draw the whole cream pie!
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

            throwVector = PhysicsUtils.getThrowVector(self.traceOrigin,
                                                      self.traceVector,
                                                      self.throwOrigin,
                                                      self.avatar,
                                                      self.avatar.getBattleZone().getPhysicsWorld())
            endPos = CIGlobals.extrude(self.throwOrigin, self.ThrowPower, throwVector) - (0, 0, 90)
            
            proj = WholeCreamPieProjectileAI(base.air)
            proj.setProjectile(2.5, self.throwOrigin, endPos, 1.07, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.onProjectileHit)
            proj.addExclusion(self.avatar)

            self.throwTime = globalClock.getFrameTime()
            
    def canUse(self):
        return self.hasAmmo() and (globalClock.getFrameTime() - self.throwTime >= 0.5)

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.throwOrigin = CIGlobals.getVec3(dgi)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.b_setAction(self.StateThrow)

    def npcUseAttack(self, target):
        #print "NPC Use attack:", self.avatar, self.action, self.getAmmo()
        if not self.canUse():
            #print "Can't use"
            return

        #print "using pie"

        #self.headsUp(target)
        self.throwOrigin = self.avatar.getPos(render) + (0, 0, self.avatar.getHeight() / 2.0)
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
        self.setNextAction(self.StateThrow)

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 10*10
