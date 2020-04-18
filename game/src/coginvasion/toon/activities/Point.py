from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait, ActorInterval

class Point(BaseActivity):

    def doActivity(self):
        return Sequence(Func(self.avatar.animFSM.request, 'off'), ActorInterval(self.avatar, 'rightpoint-start'), Func(self.avatar.loop, 'rightpoint'), Wait(1.0))
