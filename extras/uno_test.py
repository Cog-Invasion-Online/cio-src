from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
#loadPrcFileData('', 'notify-level debug')
loadPrcFileData('', 'audio-library-name p3fmod_audio')
loadPrcFileData('', 'egg-load-old-curves 0')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'win-size 256 256')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.particles.ParticleEffect import ParticleEffect
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog.Suit import Suit
from direct.interval.IntervalGlobal import *
from lib.coginvasion.cog.DistributedSuit import DistributedSuit
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.toon import NameTag, ToonDNA, ToonHead
from direct.directutil import Mopath
from direct.showbase.Audio3DManager import Audio3DManager
from direct.showutil.Rope import Rope
import glob

base.enableParticles()

base.cr = ClientRepository([])
base.cr.isShowingPlayerIds = False
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)

base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
base.lifter = CollisionHandlerGravity()
base.pusher = CollisionHandlerPusher()
from lib.coginvasion.nametag import NametagGlobals
from lib.coginvasion.margins.MarginManager import MarginManager
from lib.coginvasion.margins import MarginGlobals

NametagGlobals.setMe(base.cam)
NametagGlobals.setCardModel('phase_3/models/props/panel.bam')
NametagGlobals.setArrowModel('phase_3/models/props/arrow.bam')
NametagGlobals.setChatBalloon3dModel('phase_3/models/props/chatbox.bam')
NametagGlobals.setChatBalloon2dModel('phase_3/models/props/chatbox_noarrow.bam')
NametagGlobals.setThoughtBalloonModel('phase_3/models/props/chatbox_thought_cutout.bam')
chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui.bam')
NametagGlobals.setPageButton(chatButtonGui.find('**/Horiz_Arrow_UP'), chatButtonGui.find('**/Horiz_Arrow_DN'),
                             chatButtonGui.find('**/Horiz_Arrow_Rllvr'), chatButtonGui.find('**/Horiz_Arrow_UP'))
NametagGlobals.setQuitButton(chatButtonGui.find('**/CloseBtn_UP'), chatButtonGui.find('**/CloseBtn_DN'),
                             chatButtonGui.find('**/CloseBtn_Rllvr'), chatButtonGui.find('**/CloseBtn_UP'))
soundRlvr = DGG.getDefaultRolloverSound()
NametagGlobals.setRolloverSound(soundRlvr)
soundClick = DGG.getDefaultClickSound()
NametagGlobals.setClickSound(soundClick)

base.marginManager = MarginManager()
base.margins = aspect2d.attachNewNode(base.marginManager, DGG.MIDGROUND_SORT_INDEX + 1)
base.leftCells = [
    base.marginManager.addCell(0.1, -0.6, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.0, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.4, base.a2dTopLeft)
]
base.bottomCells = [
    base.marginManager.addCell(0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-1.0, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(1.0, 0.1, base.a2dBottomCenter)
]
base.rightCells = [
    base.marginManager.addCell(-0.1, -0.6, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.0, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.4, base.a2dTopRight)
]

# HACK: I don't feel like making a new file that inherits from ShowBase so I'm just going to do this...
def setCellsActive(cells, active):
    for cell in cells:
        cell.setActive(active)
    base.marginManager.reorganize()
base.setCellsActive = setCellsActive

def windowEvent(win):
    ShowBase.windowEvent(base, win)
    base.marginManager.updateMarginVisibles()
base.windowEvent = windowEvent

base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
base.mouseWatcherNode.setButtonUpPattern('button-up-%r')
"""
tunnel = loader.loadModel("safe_zone_entrance_tunnel_TT.bam")
tunnel.reparentTo(render)

toon = Toon(base.cr)
toon.setDNAStrand("00/00/00/00/00/00/00/00/00/00/00/00/00/00/00")
toon.generateToon()
toon.reparentTo(render)

smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
smiley.setX(45)
smiley.setY(5)
smiley.setZ(0)

toon.setPos(-15, -5, 0)
toon.setHpr(180, 0, 0)
toon.reparentTo(smiley)
toon.animFSM.request('run')

smiley.setHpr(-90, 0, 0)

ival = Sequence(LerpPosInterval(smiley, duration = 1.0, pos = (35, 5, 0), startPos = (45, 5, 0)), LerpHprInterval(smiley, duration = 2.0, hpr = (0, 0, 0), startHpr = (-90, 0, 0)))
Sequence(Wait(3.0), Func(ival.start)).start()
"""
"""
torsoType2flagY = {"dgs_shorts": -1.5, "dgs_skirt": -1.5, "dgm_shorts": -1.1, "dgm_skirt": -1.1, "dgl_shorts": -1.1, "dgl_skirt": -1.1}

flag = loader.loadModel('phase_4/models/minigames/flag.egg')
flag.find('**/flag').setTwoSided(1)
flag.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag.find('**/flag').setColor(1, 0, 0, 1.0)
flag.reparentTo(render)

anim = 'neutral'

from lib.coginvasion.npc import NPCGlobals

toon = Toon(base.cr)
toon.parseDNAStrand(NPCGlobals.NPC_DNA['Professor Prepostera'])
toon.setName('Professor Prepostera')
toon.generateToon()
toon.reparentTo(render)
toon.pose(anim, 0)
#toon.deleteShadow()
#toon.setX(-5)

flag.reparentTo(toon.find('**/def_joint_attachFlower'))
flag.setPos(0.2, torsoType2flagY[toon.torso], -1)

flag2 = loader.loadModel('phase_4/models/minigames/flag.egg')
flag2.find('**/flag').setTwoSided(1)
flag2.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag2.find('**/flag').setColor(0, 0, 1, 1.0)
flag2.reparentTo(render)

toon2 = Toon(base.cr)
toon2.parseDNAStrand("00/01/04/17/00/17/01/17/03/03/09/09/09/04/00")
toon2.generateToon()
toon2.reparentTo(render)
toon2.animFSM.request(anim)
toon2.setX(0)

flag2.reparentTo(toon2.find('**/def_joint_attachFlower'))
flag2.setPos(0.2, torsoType2flagY[toon2.torso], -1)

flag3 = loader.loadModel('phase_4/models/minigames/flag.egg')
flag3.find('**/flag').setTwoSided(1)
flag3.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag3.find('**/flag').setColor(0, 0, 1, 1.0)
flag3.reparentTo(render)

toon3 = Toon(base.cr)
toon3.parseDNAStrand("00/01/04/17/02/17/01/17/03/03/09/09/09/04/00")
toon3.generateToon()
toon3.reparentTo(render)
toon3.animFSM.request(anim)
toon3.setX(5)

flag3.reparentTo(toon3.find('**/def_joint_attachFlower'))
flag3.setPos(0.2, torsoType2flagY[toon3.torso], -1)
"""
"""
dna = ToonDNA.ToonDNA()
dna.parseDNAStrand(dna.dnaStrand)

head = ToonHead.ToonHead(base.cr)
head.generateHead(dna.gender, dna.animal, dna.head, 1)
head.getGeomNode().setDepthWrite(1)
head.getGeomNode().setDepthTest(1)
head.setH(180)
head.setScale(0.7)
#head.reparentTo(aspect2d)


from lib.coginvasion.base.SectionedSound import AudioClip

nextClip = None
testClip = None

def handlePartDone():
	global nextClip
	global testClip
	if nextClip:
		testClip.cleanup()
		testClip = AudioClip(1, nextClip)
		testClip.makeData()
		testClip.playAllParts()
	nextClip = None


testClip = AudioClip(1, "5050_orchestra")
testClip.makeData()
testClip.playAllParts()

def setNextClip(clip):
	global nextClip
	nextClip = clip

base.accept('AudioClip_partDone', handlePartDone)
base.accept('l', setNextClip, ['located_orchestra'])


toon = Toon(base.cr)
toon.setDNAStrand(toon.dnaStrand)
toon.reparentTo(render)
toon.setY(-20)
toon.setX(20)
toon.setZ(10)

from lib.coginvasion.cog import SuitBank

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit(SuitBank.MoverShaker, 0)
suit.reparentTo(render)
suit.setX(0)
suit.animFSM.request('die', [])
suit.show()
suit.pose('neutral', 20)

from lib.coginvasion.toon import ParticleLoader

smile = ParticleLoader.loadParticleEffect('phase_5/etc/smile.ptf')
smile.start(toon)
smiley = loader.loadModel('models/smiley'
)
smiley.reparentTo(smile)

camera.reparentTo(suit)
camera.setPos(0, 35, 10)
camera.setH(180)

#base.disableMouse()


############### TRUCK ###############
truck_node = render.attachNewNode('truck_node')
truck_node.setX(-22.73)
truck_node.setH(203.25)
truck_node.setScale(2.0)
kart = loader.loadModel('phase_6/models/karting/Kart3_Final.bam')
kart.find('**/decals').removeNode()
kart.reparentTo(truck_node)
pod = loader.loadModel('phase_4/models/minigames/pods_truck.egg')
pod.reparentTo(truck_node)
pod.setScale(0.2)
pod.setY(8.5)
pod.setH(180)
cord = Rope()
cord.ropeNode.setUseVertexColor(1)
cord.setup(3, ({'node': kart, 'point': (0, 1.5, 0.7), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': kart, 'point': (0, 1.5, 0.7), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': pod, 'point': (0, 31, 5), 'color': (0, 0, 0, 1), 'thickness': 1000}), [])
cord.setH(180)
cord.reparentTo(render)
sphere = CollisionSphere(0, 0, 0, 2)
sphere.setTangible(0)
node = CollisionNode('truck_trigger')
node.addSolid(sphere)
node.setCollideMask(CIGlobals.WallBitmask)
barrel1 = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
barrel1.reparentTo(toon.find('**/def_joint_right_hold'))
barrel1.find('**/gagTankColl').removeNode()
barrel1.setScale(0.2)
toon.loop('catchneutral')
barrel1.setP(90)
barrel1.setZ(0.25)
#####################################
barrelscale = 0.15
barrelpoints = [(1.05, 2.68, 0.84), (0, 2.68, 0.84), (-1.05, 2.68, 0.84),
				(1.05, 3.68, 0.84), (0, 3.68, 0.84), (-1.05, 3.68, 0.84),
				(1.05, 4.68, 0.84), (0, 4.68, 0.84), (-1.05, 4.68, 0.84),
				(1.05, 5.68, 0.84), (0, 5.68, 0.84), (-1.05, 5.68, 0.84),
				(1.05, 6.68, 0.84), (0, 6.68, 0.84), (-1.05, 6.68, 0.84),
				(1.05, 7.68, 0.84), (0, 7.68, 0.84), (-1.05, 7.68, 0.84)]
for point in barrelpoints:
	barrel = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
	barrel.setScale(barrelscale)
	barrel.setPos(point)
	barrel.setH(180)
	barrel.reparentTo(truck_node)
	if point == barrelpoints[0]:
		barrel.ls()

############### GAG SHOP ###############
shop = loader.loadModel('phase_4/models/modules/gagShop_TT.bam')
shop.reparentTo(render)
shop.setY(-70)
########################################

area = loader.loadModel('phase_4/models/minigames/delivery_area.egg')
area.setY(-5)
area.reparentTo(render)

sky = loader.loadModel('phase_3.5/models/props/TT_sky.bam')
sky.reparentTo(render)
sky.setZ(-20)


img = OnscreenImage(image = 'bg.tif', parent = render2d)
base.cam.node().getDisplayRegion(0).setSort(20)
"""
from lib.coginvasion.npc import NPCGlobals
from lib.coginvasion.toon.ToonHead import ToonHead

toon = Toon(base.cr)
toon.parseDNAStrand(NPCGlobals.NPC_DNA['Flippy'])
toon.setName('')
toon.generateToon()
toon.reparentTo(render)
toon.pose('neutral', 45)
toon.find('**/torso-top').setColor(1, 1, 1, 1)
toon.find('**/torso-top').setTexture(loader.loadTexture('/c/Users/Brian/Desktop/suit.jpg'), 1)
toon.deleteShadow()
toon.setPosHpr(3.55, 9.25, -3.58, 113.96, 12.53, 12.99)
"""
EyesAngry = loader.loadTexture('phase_3/maps/eyesAngry.jpg', 'phase_3/maps/eyesAngry_a.rgb')
EyesAngry.setMinfilter(Texture.FTLinear)
EyesAngry.setMagfilter(Texture.FTLinear)
toon.find('**/eyes').setTexture(EyesAngry, 1)
pie = loader.loadModel('phase_3.5/models/props/tart.bam')
pie.reparentTo(toon.find('**/joint_Rhold'))

from lib.coginvasion.cog import SuitBank

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.setMaxHealth(132)
suit.setHealth(132)
suit.setSuit(SuitBank.MrHollywood, 0)
suit.announceGenerate()
suit.reparentTo(render)
suit.setX(0)
suit.show()
suit.deleteShadow()
suit.setAnimState('off')
suit.pose('magic1', 20)
suit.cleanupPropeller()
suit.stopSmooth()
suit.setPosHpr(-5.13, 15.19, -7.08, 235.01, 15.26, 348.42)
suit.removeHealthBar()
toon.controlJoint(None, 'head', 'def_left_pupil')
toon.controlJoint(None, 'head', 'def_right_pupil')
toon.find('**/def_left_pupil').setPos(-0.10, 0.43, 0.41)
toon.find('**/def_right_pupil').setPos(0.17, 0.4, 0.4)

from lib.coginvasion.cog import SuitBank
suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.setMaxHealth(132)
suit.setHealth(132)
suit.setSuit(SuitBank.MrHollywood, 0)
suit.announceGenerate()
suit.reparentTo(render)
suit.setX(0)
suit.show()
suit.deleteShadow()
suit.setAnimState('off')
suit.pose('magic1', 20)
suit.cleanupPropeller()
suit.stopSmooth()
#suit.setPosHpr(-5.13, 15.19, -7.08, 235.01, 15.26, 348.42)
suit.removeHealthBar()
suit.hasSpawned = True
suit.startProjInterval(0, 0, 0, 10, 60, 0, 5.0, 0.25)
"""
base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
render.setAntialias(AntialiasAttrib.MMultisample)

for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(10)
			except:
				pass
	except:
		continue

#base.oobe()
#base.startDirect()
base.run()
