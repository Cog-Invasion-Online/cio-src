"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonUpGag.py
@author Maverick Liberty
@date July 17, 2015

"""

from direct.interval.IntervalGlobal import ActorInterval

from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals.CIGlobals import ToonClasses
from panda3d.core import Point3
import random

class ToonUpGag(Gag):
    
    minHeal =1.0
    maxHeal = 1.0
    efficiency = 1.0
    gagType = GagType.TOON_UP

    def __init__(self):
        Gag.__init__(self)
        self.lHandJoint = None
        self.hips = None
        self.PNTNEARZERO = Point3(0.01, 0.01, 0.01)
        self.PNTNORMAL = Point3(1, 1, 1)
        self.healAmount = None

    def start(self):
        Gag.start(self)
        if self.isLocal():
            self.startTimeout()
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
            if obj.__class__.__name__ in ToonClasses:
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
            if obj.__class__.__name__ in ToonClasses:
                if self.avatar.getDistance(obj) <= radius:
                    if obj.getHealth() < obj.getMaxHealth():
                        obj.sendUpdate('toonUp', [self.healAmount, 1, 1])
