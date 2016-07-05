"""

  Filename: SuitJellybeanDropper.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeanAI import DistributedDroppableCollectableJellybeanAI
from DistributedDroppableCollectableJellybeanJarAI import DistributedDroppableCollectableJellybeanJarAI
from DistributedDroppableCollectableBackpackAI import DistributedDroppableCollectableBackpackAI
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals
import random

class SuitJellybeanDropper:
    notify = directNotify.newCategory("SuitJellybeanDropper")
    MAX_BEAN_VALUE = 5
    MAX_HEALTH_2_BP = {
        42: [13, 12, 7, 1, 4, 5],
        90: [10, 9, 0, 2],
        132: [6, 11, 8, 3]
    }

    def __init__(self, suit):
        self.suit = suit

    def calculate(self):
        if not self.suit.head in ["vp"]:
            minimum = 0
            if 1:
                maximum = 30

            elif self.suit.getMaxHealth() <= 42:
                maximum = 20
            elif self.suit.getMaxHealth() > 42 and self.suit.getMaxHealth() <= 90:
                maximum = 30
            elif self.suit.getMaxHealth() > 90 and self.suit.getMaxHealth() <= 132:
                maximum = 40

            random_drop = random.randint(minimum, maximum)
            if random_drop == maximum:
                # Backpack
                self.dropType = 1
            else:
                # Jellybeans
                self.dropType = 0

        if self.dropType == 0:
            self.value = int(self.suit.getMaxHealth() / CIGlobals.SuitAttackDamageFactors['clipontie'])
            self.numDrops = 1
            if self.value <= self.MAX_BEAN_VALUE:
                self.beanClass = DistributedDroppableCollectableJellybeanAI
            else:
                self.beanClass = DistributedDroppableCollectableJellybeanJarAI
            if self.suit.head in ["vp"]:
                self.numDrops = 5
                self.value /= 5
        elif self.dropType == 1:
            gags = list(GagGlobals.gagIds.keys())
            self.gagsInBp = []
            for _ in range(4):
                gagId = random.choice(gags)
                self.gagsInBp.append(gagId)
                gags.remove(gagId)

    def drop(self):
        if self.dropType == 0:
            for i in range(self.numDrops):
                drop = self.beanClass(self.suit.air)
                drop.generateWithRequired(self.suit.zoneId)
                drop.setValue(self.value)
                drop.d_setX(self.suit.getX(render))
                drop.d_setY(self.suit.getY(render))
                drop.d_setZ(self.suit.getZ(render))
                if self.numDrops > 1 and i > 0:
                    drop.d_setX(self.suit.getX(render) + random.uniform(-5.0, 5.0))
                    drop.d_setY(self.suit.getY(render) + random.uniform(-5.0, 5.0))
                drop.b_setParent(CIGlobals.SPRender)
        elif self.dropType == 1:
            drop = DistributedDroppableCollectableBackpackAI(self.suit.air)
            drop.setSuitMgr(self.suit.getManager())
            drop.generateWithRequired(self.suit.zoneId)
            drop.b_setBP(self.gagsInBp)
            drop.d_setX(self.suit.getX(render))
            drop.d_setY(self.suit.getY(render))
            drop.d_setZ(self.suit.getZ(render))
            drop.b_setParent(CIGlobals.SPRender)
            drop.startTimer()
        self.suit.getManager().drops.append(drop)

    def cleanup(self):
        self.suit = None
        self.gagsInBp = None
        self.value = None
        self.numDrops = None
        self.beanClass = None
