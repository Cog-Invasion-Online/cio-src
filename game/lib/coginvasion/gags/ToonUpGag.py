"""

  Filename: ToonUpGag.py
  Created by: DecodedLogic (17Jul15)

"""

from direct.interval.IntervalGlobal import ActorInterval

from lib.coginvasion.gags.Gag import Gag
from lib.coginvasion.gags.GagType import GagType
from pandac.PandaModules import Point3
import random

class ToonUpGag(Gag):

    def __init__(self, name, model, minHeal, maxHeal, efficiency, healSfx, playRate, anim = None):
        Gag.__init__(self, name, model, 0, GagType.TOON_UP, healSfx, anim = anim, playRate = playRate, scale = 1, autoRelease = False)
        self.minHeal = minHeal
        self.maxHeal = maxHeal
        self.efficiency = efficiency
        self.lHandJoint = None
        self.hips = None
        self.PNTNEARZERO = Point3(0.01, 0.01, 0.01)
        self.PNTNORMAL = Point3(1, 1, 1)
        self.healAmount = None

    def start(self):
        Gag.start(self)
        if self.isLocal():
            self.startTimeout()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def equip(self):
        self.setupHandJoints()

    def setupHandJoints(self):
        if not self.handJoint or not self.lHandJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')
            self.lHandJoint = self.avatar.find('**/def_joint_left_hold')

    def setupHips(self):
        if not self.hips:
            self.hips = self.avatar.find('**/joint_hips')

    def setHealAmount(self):
        if random.randint(0, 100) < self.efficiency:
            healAmount = random.randint(self.minHeal, self.maxHeal)
        else:
            healAmount = random.randint(int(self.minHeal * 0.2), int(self.maxHeal * 0.2))
        self.healAmount = healAmount

    def healAvatar(self, avatar, anim = None):
        if anim:
            ActorInterval(avatar, anim).start()
        if not self.healAmount:
            self.setHealAmount()
        avatar.sendUpdate('toonUp', [self.healAmount, 1, 1])

    def getClosestAvatar(self, radius):
        avatars = {}
        distances = []
        for obj in base.cr.doId2do.values():
            if obj.__class__.__name__ == "DistributedToon":
                distance = self.avatar.getDistance(obj)
                if obj != self.avatar:
                    if distance <= radius:
                        avatars.update({obj : distance})
        for dist in avatars.values():
            distances.append(dist)
        distances.sort()
        for avatar in avatars.keys():
            distance = avatars.get(avatar)
            if distance == distances[0]:
                return avatar

    def healNearbyAvatars(self, radius):
        for obj in base.cr.doId2do.values():
            if obj.__class__.__name__ == "DistributedToon":
                if self.avatar.getDistance(obj) <= radius:
                    if obj.getHealth() < obj.getMaxHealth():
                        obj.sendUpdate('toonUp', [self.healAmount, 1, 1])
