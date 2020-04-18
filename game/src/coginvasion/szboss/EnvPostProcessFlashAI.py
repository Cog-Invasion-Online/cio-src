from panda3d.core import Vec3

from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class EnvPostProcessFlashAI(DistributedEntityAI):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.flashColor = Vec3(1)
        self.brightTime = 1.0
        self.darkTime = 1.0
        
    def getFlashColor(self):
        return [self.flashColor[0], self.flashColor[1], self.flashColor[2]]
        
    def getBrightTime(self):
        return self.brightTime
        
    def getDarkTime(self):
        return self.darkTime
        
    def delete(self):
        self.flashColor = None
        self.brightTime = None
        self.darkTime = None
        DistributedEntityAI.delete(self)
        
    def loadEntityValues(self):
        self.flashColor = self.getEntityValueColor("color")
        self.brightTime = self.getEntityValueFloat("brightTime")
        self.darkTime = self.getEntityValueFloat("darkTime")

    def Enable(self):
        self.b_setEntityState(1)
        
    def Disable(self):
        self.b_setEntityState(0)
