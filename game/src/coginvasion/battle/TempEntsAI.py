from panda3d.direct import STFloat64
from panda3d.core import Vec3

from direct.distributed.PyDatagram import PyDatagram

from src.coginvasion.globals import CIGlobals
from src.coginvasion.battle.TempEntsShared import *

import random

class TempEntsAI:
    
    def __init__(self, bzone):
        self.battleZone = bzone
        self.makers = {}
        
        self.addMaker(TE_EXPLOSION, self.makeExplosion)
        self.addMaker(TE_BULLET_RICOCHET, self.makeBulletRicochet)
        self.addMaker(TE_DECAL_TRACE, self.makeDecalTrace)
        self.addMaker(TE_LASER, self.makeLaser)
        
    def addMaker(self, te, func):
        self.makers[te] = func
        
    def makeTempEnt(self, te, *args, **kwargs):
        if te in self.makers:
            self.makers[te](*args, **kwargs)
        else:
            print "TempEntsAI: No maker for", TempEntsInverted[te]
        
    def cleanup(self):
        self.battleZone = None
        self.makers = None
        
    def sendTempEnt(self, te, dg):
        self.battleZone.d_sendTempEnt(te, dg.getMessage())
        
    def makeLaser(self, start, end, color, scale):
        dg = PyDatagram()
        CIGlobals.putVec3(dg, start)
        CIGlobals.putVec3(dg, end)
        CIGlobals.putVec3(dg, Vec3(color[0], color[1], color[2]))
        dg.addFloat64(scale)
        
        self.sendTempEnt(TE_LASER, dg)
        
    def makeDecalTrace(self, material, scale, rot, start, end):
        dg = PyDatagram()
        dg.addString(material)
        dg.addFloat64(scale)
        dg.addFloat64(rot)
        CIGlobals.putVec3(dg, start)
        CIGlobals.putVec3(dg, end)
        
        self.sendTempEnt(TE_DECAL_TRACE, dg)
    
    def makeExplosion(self, pos = (0, 0, 0), scale = 1, sound = True, shakeCam = True, duration = 1.0, soundVol = 1.0):
        dg = PyDatagram()
        CIGlobals.putVec3(dg, pos)
        dg.addFloat64(scale)
        dg.addUint8(int(sound))
        dg.addUint8(int(shakeCam))
        dg.addFloat64(duration)
        dg.addFloat64(soundVol)
        
        self.sendTempEnt(TE_EXPLOSION, dg)
        
    def makeBulletRicochet(self, pos, bulletDirection, surfaceNormal, scale = 3):
        dg = PyDatagram()
        CIGlobals.putVec3(dg, pos)
        CIGlobals.putVec3(dg,
            CIGlobals.reflect(bulletDirection, surfaceNormal) +
            Vec3(random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15))
        )
        dg.addFloat64(scale * random.uniform(0.15, 1.3))
        
        self.sendTempEnt(TE_BULLET_RICOCHET, dg)
        
        
