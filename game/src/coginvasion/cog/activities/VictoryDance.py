from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait

class VictoryDance(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'win'), Wait(9.0))
