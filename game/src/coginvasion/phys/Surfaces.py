class SurfaceProperties:

    def __init__(self, bulletImpacts = [], hardImpacts = [], softImpacts = []):
        self.bulletImpacts = bulletImpacts
        self.hardImpacts = hardImpacts
        self.softImpacts = softImpacts
        
    def getHardImpacts(self):
        return self.hardImpacts
        
    def getSoftImpacts(self):
        return self.softImpacts
        
    def getBulletImpacts(self):
        return self.bulletImpacts
        
Surfaces = {
    "metal" :   SurfaceProperties(bulletImpacts = ["phase_14/audio/sfx/metal_solid_impact_bullet1.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet2.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet3.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet4.wav"]),
                                                   
    "tossable"  :   SurfaceProperties(hardImpacts = "phase_4/audio/sfx/Golf_Hit_Barrier_2.ogg",
                                      softImpacts = "phase_4/audio/sfx/Golf_Hit_Barrier_1.ogg")
}

def getSurface(name):
    return Surfaces.get(name, SurfaceProperties())
