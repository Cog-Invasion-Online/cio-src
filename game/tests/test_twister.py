from src.coginvasion.standalone.StandaloneToon import *
from src.coginvasion.dna.DNALoader import *
from src.coginvasion.globals import CIGlobals

base.localAvatar.find("**/torso-top").setTexture(loader.loadTexture("resources/phase_3/maps/desat_shirt_overalls.jpg"), 1)
base.localAvatar.find("**/torso-bot").setTexture(loader.loadTexture("resources/phase_3/maps/desat_shorts_overalls.jpg"), 1)
base.localAvatar.find("**/sleeves").setTexture(loader.loadTexture("resources/phase_3/maps/desat_sleeve_overalls.jpg"), 1)

smiley = loader.loadModel("models/smiley.egg.pz")
smiley.ls()
smiley.reparentTo(render)
for np in smiley.findAllMatches("**/+GeomNode"):
    for i in xrange(np.node().getNumGeoms()):
        gs = np.node().getGeomState(i)
        print gs.hasAttrib(TextureAttrib.getClassType())

render.setAntialias(AntialiasAttrib.MMultisample)

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT_sz.pdna")
node = loadDNAFile(ds, "phase_4/dna/new_ttc_sz.pdna")

if node.getNumParents() == 1:
    geom = NodePath(node.getParent(0))
    geom.reparentTo(hidden)
else:
    geom = hidden.attachNewNode(node)
gsg = base.win.getGsg()
if gsg:
    geom.prepareScene(gsg)
geom.setName('toontown_central')
geom.reparentTo(render)
children = geom.findAllMatches('**/*doorFrameHole*')

for child in children:
    child.hide()
geom.find('**/toontown_central_beta_DNARoot').setTwoSided(1)
geom.find('**/ground_center').setBin('ground', 18)
geom.find('**/ground_sidewalk').setBin('ground', 18)
geom.find('**/ground').setBin('ground', 18)
geom.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
geom.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)
for tunnel in geom.findAllMatches('**/linktunnel_tt*'):
    tunnel.find('**/tunnel_floor_1').setTexture(loader.loadTexture('phase_4/models/neighborhoods/tex/sidewalkbrown.jpg'), 1)
for tree in geom.findAllMatches('**/prop_green_tree_*_DNARoot'):
    newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
    newShadow.reparentTo(tree)
    newShadow.setScale(1.5)
    newShadow.setBillboardAxis(2)
    newShadow.setColor(0, 0, 0, 0.5, 1)
sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
sky.reparentTo(render)
sky.setScale(5)
sky.find('**/cloud1').setSz(0.65)
sky.find('**/cloud2').removeNode()

tor2scale = {'f1': 0.5, 'f2': 1.25, 'f3': 2.0, 'f4': 3.0, 'f5': 4.0}
tor = 'f1'

ended = False

bgm = base.loadMusic('phase_4/audio/bgm/TC_nbrhood.mid')
base.playMusic(bgm, volume = 0.8, looping = 1)

from direct.actor.Actor import Actor
from src.coginvasion.cogtropolis.NURBSMopath import NURBSMopath

tornado = Actor('phase_14/models/props/ci_twister.egg', {'testmove': 'phase_14/models/props/ci_twister-testmove.egg'}, flattenable = 0)
tornado.setScale(tor2scale[tor])
tornado.setSz(1.0)
tornado.reparentTo(hidden)
tornado.setPlayRate(0.5, 'testmove')
tornado.loop('testmove')
tornado.ls()
tornado.setY(150)
tornado.setX(150)
tornado.setZ(6.8)
tornado.setColorScale(1.0, 1.0, 1.0, 0.8)

path = NURBSMopath('phase_14/models/paths/ci_twister_tt_path_1.egg')

botbone = tornado.exposeJoint(None, 'modelRoot', 'bottom_bone')

from src.coginvasion.toon import ParticleLoader



renNode = botbone.attachNewNode('renNode')
renNode.setP(-90)
renNode.setScale(0.1)
dirt = ParticleLoader.loadParticleEffect('phase_14/etc/ci_tw_dirt.ptf')
dirt.setDepthWrite(False)
dirt.setTransparency(TransparencyAttrib.MDual)
dirt.start(parent = renNode, renderParent = render)

from direct.interval.IntervalGlobal import *

ts = TextureStage('tornado_ts')
ts.setMode(TextureStage.MReplace)
tex = loader.loadTexture('phase_14/maps/ci_twister.png')
tornado.setTexture(ts, tex)
tornado.setTransparency(True)

def changeTask(task):
    tornado.setTexOffset(ts, task.time, 0)
    return task.cont

taskMgr.add(changeTask, 'changeTask')

#tornado.place()



amblight = AmbientLight('amb')
amblight.setColor(VBase4(1, 1, 1, 1))
ambnode = render.attachNewNode(amblight)
render.setLight(ambnode)

fog = Fog('CogTropolis-fog')
fog.setColor(0.3, 0.3, 0.3)
fog.setExpDensity(0.0)
render.setFog(fog)

def change_amb_light(val):
    amblight.setColor(VBase4(val, val, val, 1.0))

def change_fog(val):
    fog.setExpDensity(val)

from src.coginvasion.base.ShakeCamera import ShakeCamera
shake = ShakeCamera(10.0, duration = 10.0)

import random
premusic = base.loadMusic('phase_14/audio/bgm/ci_tw_prestorm' + random.choice(['', '2']) + '.ogg')
appmusic = base.loadMusic('phase_14/audio/bgm/ci_tw_appear.ogg')
progmusic = base.loadMusic('phase_14/audio/bgm/ci_tw_storm_in_progress' + random.choice(['', '2', '3']) + '.ogg')
endmusic = base.loadMusic('phase_14/audio/bgm/ci_tw_storm_ended' + random.choice(['', '2', '3']) + '.ogg')
rumble = base.loadSfx('phase_14/audio/sfx/tornado_rumble.ogg')
creak = base.loadSfx('phase_14/audio/sfx/creaking_wood.ogg')
#base.audio3d.attachSoundToObject(creak, tornado)
rain = ParticleLoader.loadParticleEffect('phase_14/etc/rain.ptf')
p = rain.getParticlesList()[0]
#p.setPoolSize(4096)
p.factory.setLifespanBase(0.5)
p.setBirthRate(0.01)
renNode = camera.attachNewNode('renNode')
renNode.setY(5)
renNode.setZ(10)
renPar = render.attachNewNode("renPar")
renPar.setLightOff()
renPar.setFogOff()
renPar.setP(-30)

rainSound = base.loadSfx('phase_14/audio/sfx/rain_ambient.ogg')

thunderSounds = [base.loadSfx('phase_14/audio/sfx/big_thunder_1.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_2.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_3.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_4.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_5.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_6.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_7.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_8.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_9.ogg'),
            base.loadSfx('phase_14/audio/sfx/big_thunder_10.ogg')]

lightningTrack = None

musicTrack = None

LightningRange = [15, 30]



def __lightningTask(task):
    global lightningTrack
    sound = random.choice(thunderSounds)
    sound.setVolume(0.5)
    sound.play()
    lightningTrack = Sequence()
    numStrikes = random.randint(1, 3)
    for _ in range(numStrikes):
        lightningTrack.append(Func(fog.setColor, 1.0, 1.0, 1.0))
        lightningTrack.append(Wait(0.1))
        lightningTrack.append(Func(fog.setColor, 0.3, 0.3, 0.3))
        lightningTrack.append(Wait(0.1))
    lightningTrack.start()
    waitTime = random.uniform(LightningRange[0], LightningRange[1])
    task.delayTime = waitTime
    return task.again

import math

#objects

lastShakeT = 0.4

shakeMod = 10.0
volumeMod = 100.0

def divVec3(vec, scalar):
    return Vec3(vec[0] / scalar, vec[1] / scalar, vec[2] / scalar)

def __monitorTornado(task):
    global lastShakeT

    torPos = tornado.getPos(render)
    campos = camera.getPos(render)
    offset = campos.getXy() - torPos.getXy()

    volume = volumeMod / offset.length()
    if volume > 3.0:
        volume = 3.0
    rumble.setVolume(volume)

    timeSinceLastShake = task.time - lastShakeT
    if timeSinceLastShake > 0.3:
        shake.intensity = (shakeMod / offset.length())
        lastShakeT = task.time
    
    if not ended:
        movingAnObject = False

        for node in geom.findAllMatches('**/*DNARoot'):
            dist = node.getDistance(tornado) * tor2scale[tor]
            if dist <= 60.0 and dist > 2.0:
                nodePos = node.getPos(render)
                nodePos = Vec3(nodePos[0], nodePos[1], nodePos[2])
                dirVec = Vec3(nodePos[0] - torPos[0], nodePos[1] - torPos[1], 0).normalized()
                newPos = nodePos.cross(divVec3(dirVec, (dist * 15)))
                newPos.setZ(0)
                node.setPos(node, newPos)
                movingAnObject = True
                
        if movingAnObject:
            if creak.status() == AudioSound.READY:
                base.playSfx(creak)
        else:
            creak.stop()
    else:
        creak.stop()

    return task.cont

def __startTornado(task):
    global musicTrack
    premusic.stop()
    musicTrack = Sequence(
        SoundInterval(appmusic, volume = 1.0, duration = appmusic.length() / 2.0),
        Func(__playInProg)
    )
    musicTrack.start()
    tornado.reparentTo(render)
    tornado.setTransparency(1)
    show = LerpColorScaleInterval(
        tornado,
        duration = 5.0,
        colorScale = VBase4(1, 1, 1, 0.8),
        startColorScale = VBase4(1, 1, 1, 0),
        blendType = 'easeInOut'
    ); show.start()
    path.play(tornado, duration = 250, rotate = False)
    base.playSfx(rumble, looping = 1)
    taskMgr.add(__monitorTornado, "monTor")

    shake.intensity = 0.0
    shake.start()

    return task.done

def __playInProg():
    base.playMusic(progmusic, volume = 1.0, looping = 1)

def __playBgm():
    base.playMusic(bgm, volume = 0.8, looping = 1)

def change_progmusic_vol(val):
    progmusic.setVolume(val)

def change_shake_mod(val):
    global shakeMod
    shakeMod = val

def change_volume_mod(val):
    global volumeMod
    volumeMod = val

def end():
    ended = True
    taskMgr.remove('CTPlayground.LightningTask')
    #shake.stop()
    premusic.stop()
    Sequence(
        LerpFunc(
            change_progmusic_vol,
            duration = 3.0,
            fromData = 1.0,
            toData = 0.0
        ),
        Func(progmusic.stop)
    ).start()
    path.stop()
    #rumble.stop()
    #taskMgr.remove("monTor")
    leave = Sequence(
        Wait(1.0),
        Parallel(
            Sequence(Wait(8.5), Func(dirt.softStop)),
            LerpFunc(
                change_shake_mod,
                duration = 11.0,
                fromData = 10.0,
                toData = 1.0
            ),
            LerpFunc(
                change_volume_mod,
                duration = 11.0,
                fromData = 100.0,
                toData = 1.0
            ),
            LerpColorScaleInterval(
                tornado,
                duration = 12.5,
                colorScale = (1, 1, 1, 0),
                startColorScale = (1, 1, 1, 1),
                blendType = 'easeInOut'
            ),
            LerpFunc(
                change_amb_light,
                duration = 16.5,
                fromData = 0.4,
                toData = 1,
                blendType = 'easeInOut'
            ),
            LerpFunc(
                change_fog,
                duration = 16.5,
                fromData = 0.0125,
                toData = 0.0,
                blendType = 'easeInOut'
            )
        ),
        Func(rain.softStop),
        Func(rainSound.stop),
        Func(taskMgr.remove, "monTor"),
        Func(rumble.stop),
        Func(shake.stop)
    ); leave.start()
    mus = Sequence(
        Wait(3.0),
        SoundInterval(endmusic, duration = endmusic.length() / 2.0),
        Func(__playBgm)
    ); mus.start()

def start():
    print 'start'
    bgm.stop()
    base.playSfx(rainSound, looping = 1)
    base.playMusic(premusic, volume = 1.0, looping = 1)
    rain.start(parent = renNode, renderParent = renPar)
    color = LerpFunc(
        change_amb_light,
        duration = 5.0,
        fromData = 1,
        toData = 0.4,
        blendType = 'easeInOut'
    ); color.start()
    fogcolor = LerpFunc(
        change_fog,
        duration = 10.0,
        fromData = 0.0,
        toData = 0.0125,
        blendType = 'easeInOut'
    ); fogcolor.start()
    waitTime = random.uniform(LightningRange[0], LightningRange[1])
    taskMgr.doMethodLater(waitTime, __lightningTask, 'CTPlayground.LightningTask')
    taskMgr.doMethodLater(waitTime, __startTornado, 'startIt')

    base.acceptOnce('e', end)

base.acceptOnce('b', start)

base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()
#base.localAvatar.hide()

mov.enableMovement()

#render.setAttrib(LightRampAttrib.makeHdr0())
#render.setShaderAuto()

base.disableMouse()
#base.enableMouse()
#base.startDirect()
#base.oobe()
base.run()
