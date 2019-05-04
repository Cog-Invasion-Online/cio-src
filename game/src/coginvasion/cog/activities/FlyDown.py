from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait

class FlyDown(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'flyDown'), Wait(9.0))

