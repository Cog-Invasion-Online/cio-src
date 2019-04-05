from direct.interval.IntervalGlobal import Sequence, Func, Parallel, Wait

from src.coginvasion.cog.attacks import ClipOnTieShared
from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT

class ClipOnTie(BaseAttack):
    Hold = ATTACK_HOLD_RIGHT

    ReleasePlayRateMultiplier = 1.0
    ThrowObjectFrame = 68
    PlayRate = 1.5
    
    def __init__(self):
        BaseAttack.__init__(self, ClipOnTieShared)

    def equip(self):
        if not BaseAttack.equip(self):
            return False

        return True
        
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
            
        self.avatar.doingActivity = False
            
        return True

    def onSetAction(self, action):
        self.model.show()
        self.model.setR(180)

        self.avatar.doingActivity = False

        if action == self.StateThrow:

            self.avatar.doingActivity = True
            
            time = 0.0#3.0 * 0.667
            sf = self.ThrowObjectFrame#0

            self.setAnimTrack(
                Parallel(self.getAnimationTrack('throw-paper', startFrame=sf,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier), fullBody = False),
                         Sequence(Wait(time), Func(self.model.hide))),
                startNow = True)
