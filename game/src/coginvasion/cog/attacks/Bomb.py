from direct.interval.IntervalGlobal import Func, Sequence, Wait, Parallel

from BombShared import BombShared
from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.Attacks import ATTACK_BOMB, ATTACK_HOLD_RIGHT

class Bomb(BaseAttack, BombShared):
    ID = ATTACK_BOMB
    Name = "Blast"

    ModelPath = "phase_14/models/props/cog_bomb.bam"
    Hold = ATTACK_HOLD_RIGHT

    ReleasePlayRateMultiplier = 1.0
    ThrowObjectFrame = 68
    PlayRate = 1.5

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

        self.avatar.doingActivity = False

        if action == self.StateThrow:

            self.avatar.doingActivity = True
            
            time = 0.0#3.0 * 0.667
            sf = self.ThrowObjectFrame#0

            self.setAnimTrack(
                Parallel(self.getAnimationTrack('throw-object', startFrame=sf,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier), fullBody = False),
                         Sequence(Wait(time), Func(self.model.hide))),
                startNow = True)
