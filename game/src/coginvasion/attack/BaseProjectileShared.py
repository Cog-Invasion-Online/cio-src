class BaseProjectileShared:
    
    def __init__(self):
        self.ival = None

    def ivalFinished(self):
        pass

    def cleanup(self):
        if self.ival:
            self.ival.pause()
            self.ival = None
