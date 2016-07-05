from lib.coginvasion.standalone.StandaloneToon import *
from pandac.PandaModules import *

loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'load-display pandadx9')

from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from direct.controls.GravityWalker import GravityWalker
from lib.coginvasion.toon.Toon import Toon
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.SmartCamera import SmartCamera
from direct.showbase.Audio3DManager import Audio3DManager
from direct.gui import DirectGuiGlobals
from lib.coginvasion.cog.Suit import Suit
from lib.coginvasion.cog import SuitBank
#from lib.toontown.base.ShadowCreator import ShadowCreator

#caster = ShadowCreator()

#from rp.Code.RenderingPipeline import RenderingPipeline

render.setAntialias(AntialiasAttrib.MMultisample)

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
"""
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
geom.find('**/toontown_central_beta_DNARoot').setTwoSided(1)
geom.find('**/ground_center').setBin('ground', 18)
geom.find('**/ground_sidewalk').setBin('ground', 18)
geom.find('**/ground').setBin('ground', 18)
geom.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
geom.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)
for face in geom.findAllMatches('**/ground_sidewalk_front_*'):
	face.setColorScale(0.8, 0.8, 0.8, 1.0)
for tunnel in geom.findAllMatches('**/linktunnel_tt*'):
	tunnel.find('**/tunnel_floor_1').setTexture(loader.loadTexture('phase_4/models/neighborhoods/tex/sidewalkbrown.jpg'), 1)
for tree in geom.findAllMatches('**/prop_green_tree_*_DNARoot'):
	newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
	newShadow.reparentTo(tree)
	newShadow.setScale(1.5)
	newShadow.setColor(0, 0, 0, 0.5, 1)
sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
sky.reparentTo(render)
sky.setScale(5)
sky.find('**/cloud1').setSz(0.65)
sky.find('**/cloud2').removeNode()
"""

mdl = loader.loadModel('cog-bldg-modles/cog_bldg_reception_flr.egg')
mdl.reparentTo(render)
mdl.find('**/floor').setBin('ground', 18)

painting = loader.loadModel('cog-bldg-modles/photo_frame.egg')
painting.reparentTo(render)
painting.setPos(-42.86, 0.72, 8.0)
painting.setR(90)

rug = loader.loadModel('phase_3.5/models/modules/rug.bam')
rug.reparentTo(render)
rug.setH(90)

couch = loader.loadModel('phase_3.5/models/modules/couch_2person.bam')
couch.reparentTo(render)
couch.setPos(-23.68, 26.89, 0)
couch.setScale(1.25)

couch2 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
couch2.reparentTo(render)
couch2.setPos(-19.7, -6.5, 0)
couch2.setH(180)

couch3 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
couch3.reparentTo(render)
couch3.setPos(-24, -6.5, 0)
couch3.setH(180)

chair = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
chair.reparentTo(render)
chair.setPos(2.73, 19.46, 0)
chair.setH(330.95)

computer = loader.loadModel('cog-bldg-modles/computer_monitor.egg')
computer.reparentTo(render)
computer.setPos(0.19, 14.21, 3.01)
computer.setH(335.06)

coffee = loader.loadModel('cog-bldg-modles/coffee_cup.egg')
coffee.reparentTo(render)
coffee.setPos(-1.66, 15.88, 3.01)

phone = loader.loadModel('phase_3.5/models/props/phone.bam')
receiver = loader.loadModel('phase_3.5/models/props/receiver.bam')
receiver.reparentTo(phone)
phone.reparentTo(render)
phone.setPosHpr(3.17, 13.35, 2.97, 171.47, 0, 0)

paper1 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper1.reparentTo(render)
paper1.setPosHpr(-3.32, 17.81, 3.01, 127.2, 0, 0)

paper2 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper2.reparentTo(render)
paper2.setPosHpr(-3.32, 17.81, 3.005, 147.53, 0, 0)

elevator1 = loader.loadModel('phase_4/models/modules/elevator.bam')
elevator1.reparentTo(render)
elevator1.setPos(0.74202, -9.50081, 0)
elevator1.setH(180)

elevator2 = loader.loadModel('phase_4/models/modules/elevator.bam')
elevator2.reparentTo(render)
elevator2.setPos(-39.49848, 20.74907, 0)
elevator2.setH(90)

base.setBackgroundColor(0.8, 0.5, 0.3)

base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()

"""
#base.disableMouse()

from lib.coginvasion.cthood.ElevatorConstants import *

base.localAvatar.walkControls.setCollisionsActive(0)
base.localAvatar.disableAvatarControls()

base.localAvatar.reparentTo(elevator1)
print ElevatorPoints[0]
base.localAvatar.stopSmooth()
base.localAvatar.setPos(ElevatorPoints[0])
base.localAvatar.setHpr(180, 0, 0)

currentParent = elevator1

def toggleParent():
	global currentParent
	if currentParent == elevator1:
		currentParent = elevator2
	else:
		currentParent = elevator1
	base.localAvatar.reparentTo(currentParent)
	
base.accept('p', toggleParent)

camera.reparentTo(elevator1)
camera.setH(180)


#base.localAvatar.attachCamera()
#base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()
base.localAvatar.stopLookAround()

base.camLens.setFov(CIGlobals.DefaultCameraFov)

music = base.loadMusic("phase_7/audio/bgm/tt_elevator.ogg")
base.playMusic(music, volume = 0.8, looping = 1, interrupt = 1)

from lib.coginvasion.cthood.ElevatorUtils import *

leftDoor = elevator1.find('**/left-door')
rightDoor = elevator1.find('**/right-door')
closeDoors(leftDoor, rightDoor)

ival = getRideElevatorInterval()
ival.append(getOpenInterval(base.localAvatar, leftDoor, rightDoor, base.loadSfx('phase_5/audio/sfx/elevator_door_open.mp3'), None))
#ival.start()
"""
from lib.coginvasion.cog import Variant

receptionistPosHpr = (0.91, 16.92, 0, 149.53, 0, 0)

base.disableMouse()
suit = Suit()
suit.level = 12
suit.generate(SuitBank.ColdCaller, Variant.NORMAL, hideFirst = False)
suit.setName('Cold Caller', 'Cold Caller')
suit.reparentTo(render)
suit.loop('sit')
suit.cleanupPropeller()
suit.setPosHpr(*receptionistPosHpr)

def printPosHpr():
	print 'Pos: {0}'.format(base.localAvatar.getPos(render))
	print 'Hpr: {0}'.format(base.localAvatar.getHpr(render))

base.accept('p', printPosHpr)

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
base.run()
