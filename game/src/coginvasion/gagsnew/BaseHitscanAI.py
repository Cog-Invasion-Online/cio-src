from panda3d.core import Point3, Vec3
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from BaseGagAI import BaseGagAI
from BaseHitscanShared import BaseHitscanShared

from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.Attacks import ATTACK_NONE
from src.coginvasion.battle.SoundEmitterSystemAI import SOUND_COMBAT

class BaseHitscanAI(BaseGagAI, BaseHitscanShared):

    Name = 'BASE HITSCAN: DO NOT USE'
    ID = ATTACK_NONE
    HasClip = False
    UsesAmmo = False

    FireDelay = 0.1
    AttackRange = 100.0
    
    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateFire   :   1.0,
                                   self.StateDraw   :   0.1})
        self.maxAmmo = 1
        self.ammo = 1

        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

    def shouldGoToNextAction(self, complete):
        return ((complete) or
               (not complete and self.action == self.StateFire and
                self.getActionTime() >= self.FireDelay and self.nextAction == self.StateFire))
                                   
    def determineNextAction(self, completedAction):
        return self.StateIdle

    def doTraceAndDamage(self, traces = 1):
        return BaseGagAI.doTraceAndDamage(self, self.avatar.getViewOrigin(),
            self.avatar.getViewVector(1), self.AttackRange, traces)
        
    def onSetAction(self, action):
        
        if action == self.StateFire:
            if self.UsesAmmo:
                self.takeAmmo(-1)
            if self.HasClip:
                self.clip -= 1
                
            self.doTraceAndDamage()
            self.avatar.emitSound(SOUND_COMBAT, volume = 3.5, duration = 0.25)
            
    def canUse(self):
        # Hitscan gags do not have ammo, and thus, are always usable
        return self.action in [self.StateIdle, self.StateFire]
        
    def primaryFirePress(self, data):
        if not self.canUse():
            return

        self.setNextAction(self.StateFire)
        
    def equip(self):
        if not BaseGagAI.equip(self):
            return False
            
        self.b_setAction(self.StateDraw)
        
        return True
        
    def unEquip(self):
        if not BaseGagAI.unEquip(self):
            return False
        
        return True
