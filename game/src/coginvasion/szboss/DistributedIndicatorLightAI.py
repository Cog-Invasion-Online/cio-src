from DistributedEntityAI import DistributedEntityAI

class DistributedIndicatorLightAI(DistributedEntityAI):

    StartsOn = 1

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.lightState = 0
        self.lightColor = (1.0, 1.0, 0.75)
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        
        if self.spawnflags & self.StartsOn:
            self.b_setLightState(1)
        
    def b_setLightColor(self, color):
        self.lightColor = color
        self.sendUpdate('setLightColor', [color[0], color[1], color[2]])
        
    def getLightColor(self):
        return self.lightColor
        
    def b_setLightState(self, state):
        self.lightState = state
        self.sendUpdate('setLightState', [state])
        
    def getLightState(self):
        return self.lightState
        
    def loadEntityValues(self):
        lightColor = self.getEntityValueColor("_light")
        self.lightColor = (lightColor[0], lightColor[1], lightColor[2])
        self.spawnflags = self.getEntityValueInt("spawnflags")
        
    ######## Inputs ########
        
    def SetLightColor(self, color):
        r, g, b = color.split('/')
        r = float(r)
        g = float(g)
        b = float(b)
        r /= 255.0
        g /= 255.0
        b /= 255.0
        
        self.b_setLightColor((r, g, b))
        
    def TurnOn(self):
        self.b_setLightState(1)
        
    def TurnOff(self):
        self.b_setLightState(0)