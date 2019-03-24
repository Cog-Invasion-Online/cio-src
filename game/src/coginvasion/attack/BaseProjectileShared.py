class BaseProjectileShared:
    
    def __init__(self):
        self.ival = None

    def cleanup(self):
        if self.ival:
            self.ival.finish()
            self.ival = None
