from panda3d.core import (Point3, Vec3, Quat, GeomPoints, GeomVertexWriter, GeomVertexFormat,
                          GeomVertexData, GeomEnums, InternalName, TextureStage, TexGenAttrib,
                          Geom, GeomNode, BoundingSphere, CallbackNode, CallbackObject)

from src.coginvasion.globals import CIGlobals
from Entity import Entity

class PointSpotlight(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.spotlightWidth = 1.0
        self.spotlightLength = 1.0
        self.spotlightDir = Vec3(0)
        self.negSpotlightDir = Vec3(0)

        self.spotlight = None
        self.halo = None
        
    def setBeamHaloFactor(self, blend):
        if blend <= 0.001:
            self.spotlight.hide()
            self.halo.show()
        elif blend >= 0.999:
            self.spotlight.show()
            self.halo.hide()
        else:
            self.spotlight.show()
            self.halo.show()
        self.spotlight.setAlphaScale(1.0 - blend, 1)
        self.halo.setAlphaScale(blend, 1)

    def load(self):
        Entity.load(self)

        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        
        self.setColorScale(self.getEntityValueColor("_light") * 0.75, 1)
        
        beamAndHalo = loader.loadModel("phase_14/models/misc/light_beam_and_halo.bam")
        
        # Blend between halo and beam
        spotlightroot = self.attachNewNode('spotlightRoot')
        spotlightroot.setP(90)
        self.spotlight = beamAndHalo.find("**/beam")
        self.spotlight.setBillboardAxis()
        self.spotlight.reparentTo(spotlightroot)
        self.spotlight.setDepthWrite(False)
        
        self.halo = CIGlobals.makeSprite(
            "halo", loader.loadTexture("phase_14/maps/light_glow03.png"), 20.0)
        self.halo.reparentTo(self)
        
        beamAndHalo.removeNode()
        
        self.spotlightLength = self.getEntityValueFloat("SpotlightLength") / 16.0
        self.spotlightWidth = self.getEntityValueFloat("SpotlightWidth") / 16.0
        
        entPos = self.getPos()
        
        spotDir = self.getQuat().getForward()
        # User specified a max length, but clip that length so the spot effect doesn't appear to go through a floor or wall
        traceEnd = entPos + (spotDir * self.spotlightLength)
        endPos = self.bspLoader.clipLine(entPos, traceEnd)
        realLength = (endPos - entPos).length()
        self.spotlight.setSz(realLength)
        self.spotlight.setSx(self.spotlightWidth)
        
        self.spotlightDir = spotDir
        self.negSpotlightDir = -self.spotlightDir
        
        # Full beam, no halo
        self.setBeamHaloFactor(1.0)
        
        self.reparentTo(render)
        
        # Only update the spotlight if the object passes the Cull test.
        self.node().setFinal(True)
        clbk = CallbackNode('point_spotlight_callback')
        clbk.setCullCallback(CallbackObject.make(self.__spotlightThink))
        clbk.setBounds(BoundingSphere((0, 0, 0), 0))
        self.attachNewNode(clbk)

    def __spotlightThink(self, data):
        camToLight = self.getPos() - base.camera.getPos(render)
        camToLight.normalize()

        factor = abs(camToLight.dot(self.negSpotlightDir))
        
        self.setBeamHaloFactor(factor)
        
    def unload(self):
        self.spotlight.removeNode()
        self.spotlight = None
        self.halo.removeNode()
        self.halo = None
        self.spotlightWidth = None
        self.spotlightLength = None
        self.spotlightDir = None
        self.negSpotlightDir = None
        Entity.unload(self)
