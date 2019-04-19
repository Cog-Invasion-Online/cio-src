
from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.cog.attacks.WaterCoolerShared import WaterCoolerShared
from src.coginvasion.attack.Attacks import ATTACK_WATER_COOLER
from src.coginvasion.globals import CIGlobals

class WaterCoolerAI(BaseAttackAI, WaterCoolerShared):
    Name = "Water Cooler"
    ID = ATTACK_WATER_COOLER
    
    WaitForSprayTime = 3.11
    StopLockOnTime = 2.5
    AttackRange = 40.0
    
    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateAttack  : 5.2852})
        
        self.ammo = 100
        self.maxAmmo = 100

        self.traceOrigin = None
        self.traceVector = None
        self.didAttack = False
        self.calibrated = False

        self.target = None

    def getBaseDamage(self):
        return 12.0
        
    def cleanup(self):
        del self.traceOrigin
        del self.traceVector
        del self.target
        del self.didAttack
        del self.calibrated
        BaseAttackAI.cleanup(self)

    def calibrate(self):
        self.traceOrigin = self.avatar.getPos() + (0, 0, self.avatar.getHeight() / 2)

        if CIGlobals.isNodePathOk(self.target):
            self.traceVector = ((self.target.getPos() + (0, 0, self.target.getHeight() / 2.0)) - self.traceOrigin).normalized()
        else:
            self.traceVector = self.avatar.getQuat().getForward()
        
    def think(self):
        BaseAttackAI.think(self)
        
        if (self.action == self.StateAttack and 
            self.getActionTime() >= self.WaitForSprayTime and 
            not self.didAttack):
            
            self.didAttack = True
            self.doTraceAndDamage(self.traceOrigin, self.traceVector, self.AttackRange)
            self.target = None

        elif (self.action == self.StateAttack and
              self.getActionTime() < self.StopLockOnTime):

            if CIGlobals.isNodePathOk(self.target):
                self.avatar.headsUp(self.target)

        elif (self.action == self.StateAttack and
              not self.calibrated):

            self.calibrate()
            self.calibrated = True

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 20*20 and squaredDistance > 8*8

    def canUse(self):
        return self.getAction() == self.StateIdle
        
    def onSetAction(self, action):
        if action == self.StateAttack:
            self.didAttack = False
            self.calibrated = False

    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.setNextAction(self.StateAttack)
        self.target = target
    
    def getTauntChance(self):
        return 0.75
    
    def getTauntPhrases(self):
        return ['This ought to cool you off.',
            "Isn't this refreshing?",
            "I deliver.",
            "Straight from the tap - into your lap.",
            "What's the matter, it's just spring water.",
            "Don't worry, it's purified.",
            "Ah, another satisfied customer.",
            "It's time for your daily delivery.",
            "Hope your colors don't run.",
            "Care for a drink?",
            "It all comes out in the wash.",
            "The drink's on you."]
