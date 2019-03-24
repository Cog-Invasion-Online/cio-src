from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_SLAP

from BaseHitscanAI import BaseHitscanAI
from BaseHitscanShared import BaseHitscanShared

class SlapAI(BaseHitscanAI, BaseHitscanShared):

    Name = GagGlobals.Slap
    ID = ATTACK_SLAP
    FireDelay = 0.6
    AttackRange = 5.0
    
    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateFire   :   1.0,
                                   self.StateDraw   :   0.1})
