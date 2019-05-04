from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait

class Jump(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'happy'), Wait(5.0))
