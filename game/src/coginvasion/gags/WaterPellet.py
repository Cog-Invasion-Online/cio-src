from panda3d.core import Point4

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from BaseProjectile import BaseProjectile

class WaterPellet(BaseProjectile):
    Name = 'water_pellet'
    HitSoundFile = 'phase_4/audio/sfx/Seltzer_squirt_2dgame_hit.ogg'

    def __init__(self, local = False):
        BaseProjectile.__init__(self, local)
        
        self.pelletNp = loader.loadModel("phase_14/models/props/waterpellet.bam")
        self.pelletNp.setScale(0.5)
        self.pelletNp.flattenStrong()
        self.pelletNp.reparentTo(self)

    def cleanup(self):
        if self.pelletNp and not self.pelletNp.isEmpty():
            self.pelletNp.removeNode()
            self.pelletNp = None
        BaseProjectile.cleanup(self)
        
    def removeNode(self):
        self.pelletNp.removeNode()
        self.pelletNp = None
        BaseProjectile.removeNode(self)

    def onHit(self, pos, intoNP):
        BaseProjectile.onHit(self, pos, intoNP)
        WATER_SPRAY_COLOR = Point4(0.3, 0.7, 0.9, 0.7)
        CIGlobals.makeSplat(pos, WATER_SPRAY_COLOR, 0.3)
        
        if self.local:
            avNP = intoNP.getParent()

            for obj in base.avatars:
                if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey():
                    gid = GagGlobals.getIDByName(GagGlobals.WaterGun)
                    obj.handleHitByToon(base.localAvatar, gid, (self.getPos(render) - self.initialPos).length())
        
        self.removeNode()
