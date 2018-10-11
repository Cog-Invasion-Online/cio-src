from Entity import Entity

class EntityAI(Entity):

    def __init__(self, air = None, dispatch = None):
        Entity.__init__(self)
        self.air = air
        self.dispatch = dispatch

    def requestDelete(self):
        self.unload()

    def unload(self):
        self.air = None
        self.dispatch = None
        Entity.unload(self)

    def load(self):
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)
