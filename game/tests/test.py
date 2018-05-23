from lib.coginvasion.standalone.StandaloneToon import *
from pandac.PandaModules import *

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
#for face in geom.findAllMatches('**/ground_sidewalk_front_*'):
	#face.setColorScale(0.8, 0.8, 0.8, 1.0)
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

base.localAvatar.hide()
"""

mdl = loader.loadModel('phase_7/models/modules/cog_bldg_confrence_flr.bam')
mdl.reparentTo(render)
#mdl.find('**/floor').setBin('ground', 18)

elev = loader.loadModel('phase_4/models/modules/elevator.bam')
#elev.reparentTo(render)
#elev.place()

base.setBackgroundColor(0.8, 0.5, 0.3)

base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()
#base.localAvatar.setBlend(frameBlend = True)


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
suit.place()

maxRun = 1.0
runEffect = 0.6
neutralEffect = maxRun - runEffect

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

base.localAvatar.walkControls.setCollisionsActive(0)
base.localAvatar.stopSmartCamera()
base.localAvatar.walkControls.displayDebugInfo()

def printPos():
	print base.localAvatar.getPos(render)
	print base.localAvatar.getHpr(render)

base.accept('p', printPos)

from lib.coginvasion.cthood.CogOfficePathDataAI import *
from direct.showutil.Rope import Rope

from panda3d.core import LineSegs

data = PathPolygons[CONFERENCE_FLOOR]
for section in data:
	linesegs = LineSegs()
	x, y = section[0]
	linesegs.moveTo(x, y, 1)
	for i in xrange(len(section)):
		if i > 0:
			x, y = section[i]
			linesegs.drawTo(x, y, 1)
		if i == len(section) - 1:
			linesegs.drawTo(section[0][0], section[0][1], 1)
	render.attachNewNode(linesegs.create())

from lib.coginvasion.cthood.DistributedCogOfficeBattle import *

def loadProps():
    dataList = DistributedCogOfficeBattle.ROOM_DATA[CONFERENCE_FLOOR]['props']
    for propData in dataList:
        name = propData[0]
        otherProps = []
        if isinstance(PROPS[name], list):
            for i in xrange(len(PROPS[name])):
                if i == 0:
                    continue
                path = PROPS[name][i]
                otherProps.append(path)
        x, y, z = propData[1], propData[2], propData[3]
        h, p, r = propData[4], propData[5], propData[6]
        scale = propData[7]
        if isinstance(PROPS[name], list):
            propMdl = loader.loadModel(PROPS[name][0])
        else:
            propMdl = loader.loadModel(PROPS[name])
        propMdl.reparentTo(render)
        propMdl.setPosHpr(x, y, z, h, p, r)
        propMdl.setScale(scale)
        #if name == 'photo_frame':
        #    propMdl.find('**/photo').setTexture(loader.loadTexture(self.DEPT_2_PAINTING[self.deptClass]), 1)
        for oPropPath in otherProps:
            oPropMdl = loader.loadModel(oPropPath)
            oPropMdl.reparentTo(propMdl)

dataList = DistributedCogOfficeBattle.ROOM_DATA[CONFERENCE_FLOOR]['elevators']
for elevatorData in dataList:
	elev = loader.loadModel('phase_4/models/modules/elevator.bam')
	elev.reparentTo(render)
	elev.setPosHpr(*elevatorData)

loadProps()

from lib.coginvasion.cthood.CogOfficePathDataAI import *
pathfinder = getPathFinder(CONFERENCE_FLOOR)
smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
smiley.setPos(-30, -5, 0)
smiley2 = loader.loadModel('models/smiley.egg.pz')
smiley2.reparentTo(render)
smiley2.setPos(0, 70, 0)
path = pathfinder.planPath((0, 70), (-30, -5))

linesegs = LineSegs()
linesegs.setColor(0, 0, 1, 1.0)
linesegs.moveTo(path[0][0], path[0][1], 1)

for i in xrange(len(path)):
	if i > 0:
		linesegs.drawTo(path[i][0], path[i][1], 1)

render.attachNewNode(linesegs.create())
"""
base.enableMouse()
#base.startDirect()
#base.oobe()
base.run()
