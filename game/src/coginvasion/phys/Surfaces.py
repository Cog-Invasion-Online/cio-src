from panda3d.core import NodePath

from direct.showbase.PythonUtil import invertDictLossless

from src.coginvasion.base.Precache import precacheMaterial, precacheSound

class SurfaceProperties:

    def __init__(self, bulletImpacts = [], hardImpacts = [], softImpacts = [], footsteps = [], impactDecals = []):
        self.bulletImpacts = bulletImpacts
        self.hardImpacts = hardImpacts
        self.softImpacts = softImpacts
        self.footsteps = footsteps
        self.impactDecals = impactDecals
        
    def getImpactDecals(self):
        return self.impactDecals
        
    def getFootsteps(self):
        return self.footsteps
        
    def getHardImpacts(self):
        return self.hardImpacts
        
    def getSoftImpacts(self):
        return self.softImpacts
        
    def getBulletImpacts(self):
        return self.bulletImpacts
        
Surfaces = {
    "default"   :   SurfaceProperties(impactDecals = ["materials/decals/concrete/shot1.mat",
                                                      "materials/decals/concrete/shot2.mat",
                                                      "materials/decals/concrete/shot3.mat",
                                                      "materials/decals/concrete/shot4.mat",
                                                      "materials/decals/concrete/shot5.mat"],
                                      bulletImpacts = ["sound/physics/concrete/concrete_impact_bullet1.wav",
                                                       "sound/physics/concrete/concrete_impact_bullet2.wav",
                                                       "sound/physics/concrete/concrete_impact_bullet3.wav",
                                                       "sound/physics/concrete/concrete_impact_bullet4.wav"]),
                                                       
    "glass" :   SurfaceProperties(impactDecals = ["materials/decals/glass/shot1.mat",
                                                  "materials/decals/glass/shot2.mat",
                                                  "materials/decals/glass/shot3.mat",
                                                  "materials/decals/glass/shot4.mat",
                                                  "materials/decals/glass/shot5.mat"],
                                  bulletImpacts = ["sound/physics/glass/glass_impact_bullet1.wav",
                                                   "sound/physics/glass/glass_impact_bullet2.wav",
                                                   "sound/physics/glass/glass_impact_bullet3.wav",
                                                   "sound/physics/glass/glass_impact_bullet4.wav"]),
    
    "metal" :   SurfaceProperties(bulletImpacts = ["phase_14/audio/sfx/metal_solid_impact_bullet1.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet2.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet3.wav",
                                                   "phase_14/audio/sfx/metal_solid_impact_bullet4.wav"],
                                  impactDecals = ["materials/decals/metal/shot1.mat",
                                                  "materials/decals/metal/shot2.mat",
                                                  "materials/decals/metal/shot3.mat",
                                                  "materials/decals/metal/shot4.mat",
                                                  "materials/decals/metal/shot5.mat"]),
                                                  
    "wood"  :   SurfaceProperties(bulletImpacts = ["sound/physics/wood/wood_solid_impact_bullet1.wav",
                                                   "sound/physics/wood/wood_solid_impact_bullet2.wav",
                                                   "sound/physics/wood/wood_solid_impact_bullet3.wav",
                                                   "sound/physics/wood/wood_solid_impact_bullet4.wav",
                                                   "sound/physics/wood/wood_solid_impact_bullet5.wav"],
                                  impactDecals = ["materials/decals/wood/shot1.mat",
                                                  "materials/decals/wood/shot2.mat",
                                                  "materials/decals/wood/shot3.mat",
                                                  "materials/decals/wood/shot4.mat",
                                                  "materials/decals/wood/shot5.mat"]),
                                                   
    "tossable"  :   SurfaceProperties(hardImpacts = ["phase_4/audio/sfx/Golf_Hit_Barrier_2.ogg"],
                                      softImpacts = ["phase_4/audio/sfx/Golf_Hit_Barrier_1.ogg"])
}

SurfaceNameByClass = invertDictLossless(Surfaces)

def getSurfaceName(surf):
    return SurfaceNameByClass.get(surf, "default")

def getSurfaceFromContact(contact, battleZone = None):
    if not battleZone:
        battleZone = base
        
    print battleZone
    
    hitNode = contact.getNode()
    
    if hasattr(contact, 'getTriangleIndex'):
        triangleIdx = contact.getTriangleIndex()
        if battleZone.bspLoader.hasBrushCollisionNode(hitNode):
            if battleZone.bspLoader.hasBrushCollisionTriangle(hitNode, triangleIdx):
                surfaceProp = battleZone.bspLoader.getBrushTriangleMaterial(hitNode, triangleIdx)
                return Surfaces.get(surfaceProp, Surfaces["default"])
            
    hitNp = NodePath(hitNode)
    return Surfaces.get(hitNp.getSurfaceProp(), Surfaces["default"])

def getSurface(name):
    return Surfaces.get(name, Surfaces["default"])
    
def precacheSurfaces():
    for name, surf in Surfaces.items():
        print "Precaching surface", name
        
        for bulletImpact in surf.bulletImpacts:
            precacheSound(bulletImpact)
            
        for impactDecal in surf.impactDecals:
            precacheMaterial(impactDecal)
            
        for footstep in surf.footsteps:
            precacheSound(footstep)
            
        for hardImpact in surf.hardImpacts:
            precacheSound(hardImpact)
            
        for softImpact in surf.softImpacts:
            precacheSound(softImpact)
