from src.coginvasion.szboss.DistributedEntity import DistributedEntity

from panda3d.core import Point3
from direct.interval.IntervalGlobal import Sequence, Wait, LerpPosInterval

def getRideElevatorInterval():
    ival = Sequence(Wait(0.5), LerpPosInterval(base.cam, 0.5, Point3(0, 0, -0.2), startPos=Point3(0, 0, 0), blendType='easeOut'),
        LerpPosInterval(base.cam, 0.5, Point3(0, 0, 0), startPos=Point3(0, 0, -0.2)),
        Wait(1), LerpPosInterval(base.cam, 0.5, Point3(0, 0, 0.2), startPos=Point3(0, 0, 0), blendType='easeOut'),
        LerpPosInterval(base.cam, 1, Point3(0, 0, 0), startPos=Point3(0, 0, 0.2)))
    return ival

class EnvElevatorCamera(DistributedEntity):
    
    NeedNode = False
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.ival = None
        
    def clearIval(self):
        if self.ival:
            self.ival.finish()
        self.ival = None
        
    def setEntityState(self, state):
        self.clearIval()
        
        if state == 1:
            self.ival = getRideElevatorInterval()
            self.ival.loop()

    def disable(self):
        self.clearIval()
        DistributedEntity.disable(self)
