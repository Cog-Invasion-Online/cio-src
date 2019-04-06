from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func

from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT
from src.coginvasion.cog.SuitType import SuitType
from src.coginvasion.base.Precache import precacheSound

class GenericThrowAttack(BaseAttack):
    Hold = ATTACK_HOLD_RIGHT
    PlayRate = 1.0
    ThrowAnim = 'throw-paper'
    
    def __init__(self, sharedMetadata = None):
        BaseAttack.__init__(self, sharedMetadata)
        
        self.suitType2ReleaseFrame = {
            SuitType.A : {'throw-paper' : 73, 'throw-object' : 73},
            SuitType.B : {'throw-paper' : 73, 'throw-object' : 75},
            SuitType.C : {'throw-paper' : 57, 'throw-object' : 56}
        }
        
    def equip(self):
        if not BaseAttack.equip(self):
            return False

        return True
        
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
            
        self.avatar.doingActivity = False
            
        return True
    
    @classmethod
    def doPrecache(cls):
        super(GenericThrowAttack, cls).doPrecache()
        
        if hasattr(cls, 'ImpactSoundPath') and cls.ImpactSoundPath:
            precacheSound(cls.ImpactSoundPath)
        
        if hasattr(cls, 'ThrowSoundPath') and cls.ThrowSoundPath:
            precacheSound(cls.ThrowSoundPath)
    
    def onSetAction(self, action):
        self.model.show()
        
        if hasattr(self, 'WantLight') and not self.WantLight:
            self.model.setLightOff(1)

        self.avatar.doingActivity = False

        if action == self.StateThrow:
            self.avatar.doingActivity = True
            
            releaseFrame = self.suitType2ReleaseFrame.get(self.avatar.suitPlan.getSuitType()).get(self.ThrowAnim)
            avatarTrack = self.getAnimationTrack(self.ThrowAnim, endFrame = releaseFrame, playRate = self.PlayRate, fullBody = False)

            self.setAnimTrack(
                Parallel(
                    Sequence(
                        avatarTrack,
                        self.getAnimationTrack(self.ThrowAnim, startFrame = releaseFrame, playRate = self.PlayRate, fullBody = False)
                    ),
                    Sequence(Wait(self.ThrowAfterTime / self.PlayRate), Func(self.model.hide))
                ),
            startNow = True)
