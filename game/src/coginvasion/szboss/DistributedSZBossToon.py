from DistributedEntity import DistributedEntity
from src.coginvasion.toon.DistributedToon import DistributedToon
from src.coginvasion.nametag import NametagGlobals

class DistributedSZBossToon(DistributedEntity, DistributedToon):

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        DistributedToon.__init__(self, cr)

    def setupNameTag(self, tempName = None):
        DistributedToon.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def load(self):
        self.reparentTo(render)
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())

    def generate(self):
        DistributedEntity.generate(self)
        DistributedToon.generate(self)

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        DistributedToon.announceGenerate(self)
        self.activateSmoothing(True, False)
        self.startSmooth()
        
        self.reparentTo(render)

        self.setAnimState('Happy')

    def disable(self):
        self.stopSmooth()
        DistributedEntity.disable(self)
        DistributedToon.disable(self)

    def delete(self):
        DistributedEntity.delete(self)
        DistributedToon.delete(self)
