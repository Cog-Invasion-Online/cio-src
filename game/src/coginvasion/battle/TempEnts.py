from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from src.coginvasion.globals import CIGlobals
from src.coginvasion.battle.TempEntsShared import *

class TempEnts:
    
    def __init__(self, bzone):
        self.battleZone = bzone
        self.makers = {}
        
        self.addMaker(TE_EXPLOSION, self.makeExplosion)
        self.addMaker(TE_BULLET_RICOCHET, self.makeBulletRicochet)
        self.addMaker(TE_DECAL_TRACE, self.makeDecalTrace)
        self.addMaker(TE_LASER, self.makeLaser)
        
    def makeLaser(self, dgi):
        start = CIGlobals.getVec3(dgi)
        end = CIGlobals.getVec3(dgi)
        color = CIGlobals.getVec3(dgi)
        scale = dgi.getFloat64()
        
        laser = loader.loadModel("phase_14/models/props/laser.egg")
        laser.find("**/laser").setBillboardAxis()
        laser.setLightOff(1)
        laser.setMaterialOff(1)
        laser.setTwoSided(True)
        laser.setPos(start)
        laser.lookAt(end)
        laser.setP(laser.getP() + 90)
        laser.reparentTo(render)
        
        dist = (end - start).length()
        laser.setScale(scale, scale, dist)
        
        from direct.interval.IntervalGlobal import Sequence, Func, Parallel, Wait
        
        ival = Sequence(
            Wait(0.5),
            Parallel(laser.posInterval(0.1, end, start),
                     laser.scaleInterval(0.1, (scale, scale, 0.001), (scale, scale, dist))),
            Func(laser.removeNode)
        )
        ival.start()
        
    def makeDecalTrace(self, dgi):
        material = dgi.getString()
        scale = dgi.getFloat64()
        rot = dgi.getFloat64()
        start = CIGlobals.getVec3(dgi)
        end = CIGlobals.getVec3(dgi)
        base.bspLoader.traceDecal(material, scale, rot, start, end)
        
    def makeExplosion(self, dgi):
        pos = CIGlobals.getVec3(dgi)
        scale = dgi.getFloat64()
        sound = bool(dgi.getUint8())
        shakeCam = bool(dgi.getUint8())
        duration = dgi.getFloat64()
        soundVol = dgi.getFloat64()
        CIGlobals.makeExplosion(pos, scale, sound, shakeCam, duration, soundVol)
        
    def makeBulletRicochet(self, dgi):
        pos = CIGlobals.getVec3(dgi)
        dir = CIGlobals.getVec3(dgi)
        scale = dgi.getFloat64()
        
        start = (0, 0, 0)
        end = dir * scale
        
        from panda3d.core import LineSegs, Vec4
        from direct.interval.IntervalGlobal import Sequence, Func, Parallel
        lines = LineSegs()
        lines.setColor(Vec4(1, 1, 1, 1))
        lines.setThickness(1)
        lines.moveTo(start)
        lines.drawTo(end)
        np = render.attachNewNode(lines.create())
        np.setLightOff(1)
        np.setPos(pos)
        Sequence(Parallel(np.posInterval(0.1, pos + end, pos), np.scaleInterval(0.1, (0.001, 0.001, 0.001), (1, 1, 1))), Func(np.removeNode)).start()
        
        import random
        soundDir = "sound/weapons/ric{0}.wav"
        soundIdx = random.randint(1, 5)
        CIGlobals.emitSound(soundDir.format(soundIdx), pos)
        
    def cleanup(self):
        self.battleZone = None
        self.makers = None
        
    def addMaker(self, te, func):
        self.makers[te] = func
        
    def recvTempEnt(self, te, data):
        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        if te in self.makers:
            self.makers[te](dgi)
        else:
            print "TempEnts: No maker for", TempEntsInverted[te]
