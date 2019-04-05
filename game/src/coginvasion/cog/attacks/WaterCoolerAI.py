
from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.cog.attacks.WaterCoolerShared import WaterCoolerShared
from src.coginvasion.attack.Attacks import ATTACK_WATER_COOLER

class WaterCoolerAI(BaseAttackAI, WaterCoolerShared):
    Name = "Water Cooler"
    ID = ATTACK_WATER_COOLER
    
    WaitForSprayTime = 2.76
    AttackRange = 40.0
    
    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateAttack  : 5.2852})
        
        self.ammo = 100
        self.maxAmmo = 100
        self.baseDamage = 4.0

        self.traceOrigin = None
        self.traceVector = None
        self.didAttack = False
        
    def cleanup(self):
        del self.traceOrigin
        del self.traceVector
        BaseAttackAI.cleanup(self)
        
    def think(self):
        BaseAttackAI.think(self)
        
        if (self.action == self.StateAttack and 
            self.getActionTime() >= self.WaitForSprayTime and 
            not self.didAttack):
            
            self.didAttack = True
            self.doTraceAndDamage(self.traceOrigin, self.traceVector, self.AttackRange)
            
    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 20*20 and squaredDistance > 8*8

    def canUse(self):
        return self.getAction() == self.StateIdle
        
    def onSetAction(self, action):
        if action == self.StateAttack:
            self.didAttack = False

    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.traceOrigin = self.avatar.getPos() + (0, 0, self.avatar.getHeight() / 2)
        self.traceVector = ((target.getPos() + (0, 0, target.getHeight() / 2.0)) - self.traceOrigin).normalized()
        self.setNextAction(self.StateAttack)
