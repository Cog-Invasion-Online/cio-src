from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait

class Die(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'die'), Wait(6.0))
