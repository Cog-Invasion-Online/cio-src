from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_SLAP
from src.coginvasion.battle.SoundEmitterSystemAI import SOUND_COMBAT

from BaseHitscanAI import BaseHitscanAI
from BaseHitscanShared import BaseHitscanShared

class SlapAI(BaseHitscanAI, BaseHitscanShared):

    Name = GagGlobals.Slap
    ID = ATTACK_SLAP
    FireDelay = 0.6 / 1.5
    AttackRange = 10.0
    
    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateFire   :   1.0 / 1.5,
                                   self.StateDraw   :   0.1})
                                   
        self.didSlap = False
        
    def canUse(self):
        if self.action == self.StateIdle:
            return True
        elif self.action == self.StateFire:
            if self.getActionTime() >= self.FireDelay:
                return True
        return False
        
    def onSetAction(self, action):
        if action == self.StateFire:
            self.didSlap = False
            
    def think(self):
        BaseHitscanAI.think(self)
        if self.getAction() == self.StateFire:
            if self.getActionTime() > 0.4 / 1.5 and not self.didSlap:
                self.doTraceAndDamage()
                self.avatar.emitSound(SOUND_COMBAT, volume = 3.5, duration = 0.25)
                self.didSlap = True
                
    def cleanup(self):
        self.didSlap = None
        BaseHitscanAI.cleanup(self)
