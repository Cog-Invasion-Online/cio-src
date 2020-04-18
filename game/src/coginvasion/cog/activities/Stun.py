from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, Wait, ActorInterval

class Stun(BaseActivity):

    def doActivity(self):
        return Sequence(
                        Func(self.avatar.animFSM.request, 'stunned', ['squirt-small']),
                        Wait(6.0))
