# Filename: SuitItemDropper.py
# Created by:  DecodedLogic (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.DistributedDroppableCollectableBackpackAI import DistributedDroppableCollectableBackpackAI as DBackpackAI
from lib.coginvasion.suit.DistributedDroppableCollectableJellybeanAI import DistributedDroppableCollectableJellybeanAI as DJellybeanAI
from lib.coginvasion.suit.DistributedDroppableCollectableJellybeanJarAI import DistributedDroppableCollectableJellybeanJarAI as DJellybeanJarAI
import random
import SuitAttacks

class SuitItemDropper:
    notify = directNotify.newCategory('SuitItemDropper')
    possibleDrops = {DJellybeanAI : {}, DJellybeanJarAI : {}}
    #DBackpackAI : {'chance' : 4, 'maxGags' : 4},
    jarMinSize = 10

    def __init__(self, suit):
        self.suit = suit
        self.numDrops = 1
        self.suitDrops = []
        self.isTutorialDrop = False

    def calculate(self, tutDrop = None):
        if self.suit.getMaxHealth() <= 48:
            #self.setDropChance(DBackpackAI, 2)
            """
            self.numDrops = 5
            self.setDropChance(DBackpackAI, 0)
            """
        for _ in xrange(self.numDrops):
            chance = random.randint(1, 100)
            drop = None
            for constructor, values in self.possibleDrops.iteritems():
                if 'chance' in values:
                    dropChance = values.get('chance')
                    if chance <= dropChance:
                        drop = self.generateDrop(constructor)
                        gags = list(GagGlobals.gagIds.keys())
                        maxGags = values.get('maxGags')
                        backpackGags = []
                        for _ in xrange(maxGags):
                            choice = random.choice(gags)
                            backpackGags.append(choice)
                            gags.remove(choice)
                        drop.b_setBP(backpackGags)
                else:
                    jellybeans = int(self.suit.getMaxHealth() / SuitAttacks.SuitAttackDamageFactors['glowerpower'])
                    constructor = DJellybeanAI
                    if jellybeans > self.jarMinSize:
                        constructor = DJellybeanJarAI
                    drop = self.generateDrop(constructor)
                    drop.setValue(jellybeans)
            if not drop:
                self.notify.warning('Could not find a drop.')
                return
            drop.setTutDrop(tutDrop)
            drop.setSuitManager(self.suit.getManager())
            self.suitDrops.append(drop)

    def generateDrop(self, constructor):
        drop = constructor(self.suit.air)
        drop.generateWithRequired(self.suit.zoneId)
        return drop

    def drop(self):
        for i in xrange(len(self.suitDrops)):
            drop = self.suitDrops[i]
            x, y, z = self.suit.getPos(render)
            if i > 0:
                x += random.uniform(-2.5, 2.5)
                y += random.uniform(-5.0, 5.0)
            drop.d_setX(x)
            drop.d_setY(y)
            drop.d_setZ(z)
            drop.b_setParent(CIGlobals.SPRender)
            if hasattr(drop, 'startTimer'):
                drop.startTimer()
            if self.suit.getManager():
                self.suit.getManager().drops.append(drop)

    def setDropChance(self, drop, chance):
        values = self.possibleDrops.get(drop)
        values['chance'] = chance

    def getDropChance(self, drop):
        return self.possibleDrops.get(drop)['chance']

    def cleanup(self):
        self.suit = None
        self.suitDrops = []
        self.numDrops = 0
