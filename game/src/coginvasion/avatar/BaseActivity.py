from direct.interval.IntervalGlobal import Sequence

class BaseActivity:

    def __init__(self, avatar):
        self.avatar = avatar

    def shouldLoop(self):
        return False

    def doActivity(self):
        return Sequence()

    def cleanup(self):
        del self.avatar
