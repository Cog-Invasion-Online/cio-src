from Entity import Entity

class InfoPlayerStart(Entity):
    
    def __init__(self, air = None, dispatch = None):
        Entity.__init__(self)
        
    def load(self):
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)
