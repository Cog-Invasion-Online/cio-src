from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, ActorInterval

class Fall(BaseActivity):

    def doActivity(self):
        return Sequence(ActorInterval(self.avatar, 'fallf'))
