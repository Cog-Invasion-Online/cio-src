from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta

from panda3d.core import Point3

from BaseHitscanAI import BaseHitscanAI
from src.coginvasion.attack.Attacks import ATTACK_GUMBALLBLASTER
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gagsnew.GumballProjectileAI import GumballProjectileAI
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.globals import CIGlobals

class GumballBlaster_AI(BaseHitscanAI):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster

    FireDelay = 0.1
    AttackRange = 10000

    UsesAmmo = True
    HasClip = False

    FirePower = 200.0

    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateDraw: 0.7085,
                                   self.StateFire: 0.5417})
        self.ammo = 150
        self.maxAmmo = 150
        self.baseDamage = 5

        self.fireOrigin = Point3(0)

    def canUse(self):
        return self.hasAmmo() and self.action in [self.StateIdle, self.StateFire]

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.fireOrigin = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateFire)

    def __onProjectileHit(self, contact, collider, intoNP):
        avNP = intoNP.getParent()

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                 self.calcDamage((currProj - collider.getInitialPos()).length()),
                                 currProj, collider.getInitialPos())

        for obj in base.air.avatars[self.avatar.zoneId]:
            if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND:
                obj.takeDamage(dmgInfo)
                break

        collider.requestDelete()

    def onSetAction(self, action):
        if action == self.StateFire:
            #self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(self.traceOrigin,
                                                      self.traceVector,
                                                      self.fireOrigin,
                                                      self.avatar,
                                                      self.avatar.getBattleZone().getPhysicsWorld())
            endPos = CIGlobals.extrude(self.fireOrigin, self.FirePower, throwVector) - (0, 0, 90)
            
            proj = GumballProjectileAI(base.air)
            proj.setProjectile(2.5, self.fireOrigin, endPos, 1.07, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.__onProjectileHit)
            proj.addExclusion(self.avatar)
