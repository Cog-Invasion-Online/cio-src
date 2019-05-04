from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait

class Bow(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'bow'), Wait(5.0))
