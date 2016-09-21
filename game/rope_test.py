from lib.coginvasion.standalone.StandaloneToon import *
from direct.showutil.Rope import Rope
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.npc import NPCGlobals
from direct.showbase.Audio3DManager import Audio3DManager
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon import ParticleLoader
from lib.coginvasion.toon import Toon
from direct.interval.IntervalGlobal import *

sky = loader.loadModel('phase_3.5/models/props/BR_sky.bam')
sky.reparentTo(render)
sky.setZ(-40)
sky.setFogOff()

arena = loader.loadModel('phase_4/models/minigames/dodgeball_arena.egg')
arena.reparentTo(render)
arena.setScale(0.75)
arena.find('**/team_divider').setBin('ground', 18)
arena.find('**/floor').setBin('ground', 18)
arena.find('**/team_divider_coll').setCollideMask(CIGlobals.FloorBitmask)

tree_data = [['prop_snow_tree_small_ur', Point3(23.23, 66.52, 7.46)],
	['prop_snow_tree_small_ul', Point3(-34.03, 88.02, 24.17)],
	#['prop_snow_tree_small_ur', Point3(-54.80, 0, 4.19)],
	['prop_snow_tree_small_ul', Point3(54.80, -5, 4.19)],
	['prop_snow_tree_small_ur', Point3(62.71, 62.66, 16.80)],
	['prop_snow_tree_small_ul', Point3(-23.23, -66.52, 6)],
	['prop_snow_tree_small_ur', Point3(34.03, -88.02, 23)],
	['prop_snow_tree_small_ul', Point3(-62.71, -62.66, 16)]]
trees = []

def getSnowTree(path):
	trees = loader.loadModel('phase_8/models/props/snow_trees.bam')
	tree = trees.find('**/' + path)
	tree.find('**/*shadow*').removeNode()
	return tree

def getBigText(text, color, scale):
    font = base.loader.loadFont('phase_3/models/fonts/MinnieFont.bam')
    node = TextNode("signtext" + text)
    node.setText(text)
    node.setTextColor(color)
    node.setFont(font)
    node.setGlyphScale(25)
    np = render.attachNewNode(node)
    np.setScale(scale)
    return np

for data in tree_data:
	code = data[0]
	pos = data[1]
	tree = getSnowTree(code)
	tree.reparentTo(arena)
	tree.setPos(pos)
	trees.append(tree)

music = base.loadMusic('phase_4/audio/bgm/MG_Dodgeball.mp3')
base.playMusic(music, 1, volume = 0.8)

snow = ParticleLoader.loadParticleEffect('phase_8/etc/snowdisk.ptf')
snow.setPos(0, 0, 5)
snowRender = arena.attachNewNode('snowRender')
snowRender.setDepthWrite(0)
snowRender.setBin('fixed', 1)
snow.start(camera, snowRender)

fog = Fog('snowFog')
fog.setColor(0.486, 0.784, 1)
fog.setExpDensity(0.003)
render.setFog(fog)

#bSign = getBigText("B", (0, 0, 1, 1), 1)
#rSign = getBigText("R", (1, 0, 0, 1), 1)

#bSign.setPosHpr(-5.11, 66.98, 11.53, 0, 338.96, 0)
#rSign.setPosHpr(9.02, -63.09, 9.74, 180, 338.96, 0)
	
#trees[4].place()

base.enableMouse()
base.localAvatar.hide()
#base.localAvatar.startTrackAnimToSpeed()

smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
smiley.setScale(0.25)
smiley.setColor(0, 0, 0, 1)

base.localAvatar.pose('pie', 62)


BLUE = 0
RED = 1

spawnPointsByTeam = {
            BLUE: [
                [Point3(5, 15, 0), Vec3(180, 0, 0)],
                [Point3(15, 15, 0), Vec3(180, 0, 0)],
                [Point3(-5, 15, 0), Vec3(180, 0, 0)],
                [Point3(-15, 15, 0), Vec3(180, 0, 0)]],
            RED: [
                [Point3(5, -15, 0), Vec3(0, 0, 0)],
                [Point3(15, -15, 0), Vec3(0, 0, 0)],
                [Point3(-5, -15, 0), Vec3(0, 0, 0)],
                [Point3(-15, -15, 0), Vec3(0, 0, 0)]]}

start = NodePath('StartPath')
start.reparentTo(base.localAvatar)
start.setScale(render, 1)
start.setPos(0, 0, 0)
start.setP(0)

end = NodePath('ThrowPath')
end.reparentTo(start)
end.setScale(render, 1)
end.setPos(0, 160, -90)
end.setHpr(90, -90, 90)

duration = 2
grav = 0.9

def throw():
	smiley.setPos(base.localAvatar.find('**/def_joint_right_hold').getPos(render))
	
	ival = ProjectileInterval(
		 smiley, startPos = smiley.getPos(),
         endPos = end.getPos(render), gravityMult = grav, duration = duration
	)
	ival.setDoneEvent('ivalDone')
	base.acceptOnce('ivalDone', throw)
	ival.start()
	
throw()
end.place()

"""
toon1 = Toon.Toon(base.cr)
toon1.setDNAStrand("00/01/04/00/02/00/01/00/00/00/00/02/02/02/00")
toon1.reparentTo(render)
toon1.loop('neutral')
toon1.setName("BOB")
point = spawnPointsByTeam[BLUE][1]
toon1.setPos(point[0])
toon1.setHpr(point[1])
snowball1 = loader.loadModel('phase_5/models/props/snowball.bam')
snowball1.reparentTo(toon1.find('**/def_joint_right_hold'))

toon2 = Toon.Toon(base.cr)
toon2.setDNAStrand("00/01/04/00/02/00/01/00/00/00/00/18/18/18/00")
toon2.reparentTo(render)
toon2.loop('neutral')
toon2.setName("BOB2")
point = spawnPointsByTeam[BLUE][3]
toon2.setPos(point[0])
toon2.setHpr(point[1])
snowball2 = loader.loadModel('phase_5/models/props/snowball.bam')
snowball2.reparentTo(toon2.find('**/def_joint_right_hold'))

base.disableMouse()

BLUE_START_POS = Point3(-20, 0, 4)
BLUE_END_POS = Point3(20, 0, 4)
BLUE_HPR = Vec3(0, 0, 0)

RED_START_POS = Point3(20, 0, 4)
RED_END_POS = Point3(-20, 0, 4)
RED_HPR = Vec3(180, 0, 0)

def setToonsOver():
    point = spawnPointsByTeam[RED][3]
    toon2.setPos(point[0])
    toon2.setHpr(point[1])

    point = spawnPointsByTeam[RED][1]
    toon1.setPos(point[0])
    toon1.setHpr(point[1])

blueseq = Sequence(
    Func(camera.setHpr, BLUE_HPR),
    LerpPosInterval(
        camera, duration = 5.0, pos = BLUE_END_POS, startPos = BLUE_START_POS, blendType = 'easeOut'),
    Func(base.transitions.fadeOut, 0.4),
    Wait(0.45),
    Func(setToonsOver),
    Wait(0.05),
    Func(base.transitions.fadeIn, 0.4),
    Func(camera.setHpr, RED_HPR),
    LerpPosInterval(
        camera, duration = 5.0, pos = RED_END_POS, startPos = RED_START_POS, blendType = 'easeOut'))
blueseq.start()
"""
base.localAvatar.show()
base.localAvatar.stopSmooth()
base.localAvatar.setY(-25)
base.camLens.setMinFov(70.0 / (4./3.))
base.oobe()
base.run()

