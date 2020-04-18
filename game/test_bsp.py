from src.coginvasion.standalone.StandaloneToon import *

loader.mountMultifile("resources/museum.mf")

from panda3d.core import *
from libpandabsp import *
from direct.actor.Actor import Actor
from src.coginvasion.toon.Toon import Toon
from direct.interval.IntervalGlobal import *

base.enableMouse()

render.setShaderAuto()


import random

from src.coginvasion.globals import CIGlobals

from src.coginvasion.szboss import FuncWater, EnvLightGlow, EnvParticleSystem, PointSpotlight, InfoBgm, Ropes
base.bspLoader.linkEntityToClass("func_water", FuncWater.FuncWater)
base.bspLoader.linkEntityToClass("env_lightglow", EnvLightGlow.EnvLightGlow)
base.bspLoader.linkEntityToClass("env_particlesystem", EnvParticleSystem.EnvParticleSystem)
base.bspLoader.linkEntityToClass("point_spotlight", PointSpotlight.PointSpotlight)
#base.bspLoader.linkEntityToClass("info_bgm", InfoBgm.InfoBgm)
base.bspLoader.linkEntityToClass("rope_begin", Ropes.RopeBegin)
base.bspLoader.linkEntityToClass("rope_keyframe", Ropes.RopeKeyframe)
base.bspLoader.setWantLightmaps(True)
#base.bspLoader.setVisualizeLeafs(True)

lvl = "sellbot_floor_2"
#base.loadBSPLevel("resources/museum/maps/{0}/{0}.bsp".format(lvl))
base.loadBSPLevel("resources/phase_14/etc/{0}/{0}.bsp".format(lvl))
base.bspLevel.reparentTo(render)
#base.skyBox.reparentTo(hidden)
#base.bspLoader.setWireframe(True)
#base.skyBox.hide()
#base.setBackgroundColor(0,0,0)

base.enableMouse()

#base.setPhysicsDebug(True)

def buildCubemaps():
    # Don't render any existing/default cubemaps when building
    loadPrcFileData("", "mat_envmaps 0")
    base.win.getGsg().getShaderGenerator().rehashGeneratedShaders()

    base.bspLoader.buildCubemaps()
    
def decalTheWorld(mat):
    base.bspLoader.traceDecal(mat, 2.0, random.uniform(0, 360), camera.getPos(), camera.getPos() + camera.getQuat().getForward() * 10000)

base.accept('b', buildCubemaps)

base.camLens.setMinFov(60.0 / (4./3.))

base.accept('l', render.ls)

def shaderQuality_low():
    print "Setting shader quality to low"
    base.shaderGenerator.setShaderQuality(SHADERQUALITY_LOW)
    
def shaderQuality_med():
    print "Setting shader quality to medium"
    base.shaderGenerator.setShaderQuality(SHADERQUALITY_MEDIUM)
    
def shaderQuality_high():
    print "Setting shader quality to high"
    base.shaderGenerator.setShaderQuality(SHADERQUALITY_HIGH)

base.accept('1', shaderQuality_low)
base.accept('2', shaderQuality_med)
base.accept('3', shaderQuality_high)

pie = loader.loadModel("phase_14/models/props/creampie.bam")
#pie.reparentTo(render)
pie.setZ(3)
pie.setY(-10)

launch = loader.loadModel("phase_14/models/props/gumballShooter.bam")
launch.setScale(0.2)
launch.setZ(3)
launch.setY(-20)
#launch.reparentTo(render)

#base.oobe()

#def aab():
    #prop.setAmbientBoost()
    #prop.setZ(0.1)
    
#base.accept('a', aab)

#prop.place()

base.run()
