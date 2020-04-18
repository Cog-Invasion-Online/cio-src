from Entity import Entity

class InfoPlayerStart(Entity):
    
    NeedNode = False
    
    def __init__(self, air = None, dispatch = None):
        Entity.__init__(self)
        
    def load(self):
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)

    def putPlayerAtSpawn(self, player):
        player.setPos(self.cEntity.getOrigin())
        player.setHpr(self.cEntity.getAngles())
        player.b_clearSmoothing()
        player.sendCurrentPosition()
        self.dispatchOutput("OnPlayerSpawn")
