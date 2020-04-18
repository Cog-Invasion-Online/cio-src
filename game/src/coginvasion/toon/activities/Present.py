from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait, ActorInterval

class Present(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'off'), ActorInterval(self.avatar, 'righthand-start'), Func(self.avatar.loop, 'righthand'), Wait(1.0))
