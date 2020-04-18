from src.coginvasion.toon.DistributedToon import DistributedToon
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.szboss.Useable import Useable

class DistributedSZBossToon(DistributedToon, Useable):

    def __init__(self, cr):
        DistributedToon.__init__(self, cr)
        Useable.__init__(self)
        
    def startUse(self):
        Useable.startUse(self)
        self.sendUpdate('use')

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
        DistributedToon.generate(self)

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        
        self.bodyNP.setPythonTag('useableObject', self)
        
        self.startSmooth()
        
        self.reparentTo(render)

        self.setAnimState('Happy')

    def disable(self):
        self.stopSmooth()
        DistributedToon.disable(self)

    def delete(self):
        DistributedToon.delete(self)
