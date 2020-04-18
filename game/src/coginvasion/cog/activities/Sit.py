from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func

class Sit(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.loop, 'sit'))
