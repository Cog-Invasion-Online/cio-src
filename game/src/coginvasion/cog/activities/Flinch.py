from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import ActorInterval, Func, Sequence

class Flinch(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.doStunEffect), ActorInterval(self.avatar, 'pie'))
