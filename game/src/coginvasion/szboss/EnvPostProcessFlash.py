from src.coginvasion.szboss.DistributedEntity import DistributedEntity

from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence, LerpFunc, Wait

class EnvPostProcessFlash(DistributedEntity):
    
    NeedNode = False

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.ival = None
        self.flashColor = Vec3(1)
        self.brightTime = 1.0
        self.darkTime = 1.0
        
    def setBrightTime(self, time):
        self.brightTime = time
        
    def setDarkTime(self, time):
        self.darkTime = time
        
    def disable(self):
        self.clearIval()
        self.flashColor = None
        self.brightTime = None
        self.darkTime = None
        DistributedEntity.disable(self)
        
    def setFlashColor(self, r, g, b):
        self.flashColor = Vec3(r, g, b)
        
    def clearIval(self):
        if self.ival:
            self.ival.finish()
        self.ival = None
        
    #def setEntityState(self, state):
    #    self.clearIval()
    #    
    #    if state == 1:
    #        
    #        def __changeFlashColor(mult):
    #            base.filters.setFlashColor(self.flashColor * mult)
    #            
    #        self.ival = Sequence(LerpFunc(__changeFlashColor, self.brightTime, 0.0, 1.0, blendType = 'easeOut'),
    #                             LerpFunc(__changeFlashColor, self.darkTime, 1.0, 0.0, blendType = 'easeIn'))
    #        self.ival.loop()
