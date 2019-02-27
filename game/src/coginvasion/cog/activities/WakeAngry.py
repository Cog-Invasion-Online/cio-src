from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, ActorInterval, Parallel, LerpPosInterval

class WakeAngry(BaseActivity):

    def doActivity(self):
        pr = 5.0
        jump = ActorInterval(self.avatar, 'land', startFrame = 50, endFrame = 20, playRate = pr * 2)
        jumpDur = jump.getDuration()
        curr = self.avatar.getPos(render)
        return Sequence(ActorInterval(self.avatar, 'land', startFrame = 60, endFrame = 50, playRate = pr),
                 Parallel(Sequence(LerpPosInterval(self.avatar, jumpDur / 2, curr + (0, 0, 1), curr),
                                   LerpPosInterval(self.avatar,  jumpDur / 2, curr, curr + (0, 0, 1))),
                          jump),
                 ActorInterval(self.avatar, 'land', startFrame = 20, endFrame = 60, playRate = pr))
