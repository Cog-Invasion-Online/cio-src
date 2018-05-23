from lib.coginvasion.standalone.StandaloneToon import *
from pandac.PandaModules import *

#loadPrcFile('config/config_client.prc')
#loadPrcFileData('', 'load-display pandadx9')

from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from direct.controls.GravityWalker import GravityWalker
from lib.coginvasion.toon.Toon import Toon
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.SmartCamera import SmartCamera
from direct.showbase.Audio3DManager import Audio3DManager
from direct.gui import DirectGuiGlobals
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from lib.coginvasion.cog.Suit import Suit
from lib.coginvasion.cog.SuitPathFinderAI import SuitPathFinderAI
from direct.gui.DirectGui import *
from panda3d.core import *
from lib.coginvasion.npc.DisneyCharGlobals import *
#base.setSleep(0.04)

base.minigame = None
#from lib.toontown.base.ShadowCreator import ShadowCreator

#caster = ShadowCreator()

#from rp.Code.RenderingPipeline import RenderingPipeline

#render.setAntialias(AntialiasAttrib.MMultisample)

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
#geom.writeBamFile('ttc_b_f.bam')
#base.localAvatar.attachCamera()
#base.localAvatar.startSmartCamera()
#base.localAvatar.startTrackAnimToSpeed()
#base.localAvatar.reparentTo(render)
#base.disableMouse()
"""
def printPos():
    print base.localAvatar.getPos(render)
    
base.accept('p', printPos)

texts = []

for data in WALK_POINTS[MICKEY]:
    name = data[0]
    point = data[1]
    tn = TextNode('tn')
    tn.setText(name)
    tnnp = render.attachNewNode(tn)
    tnnp.setScale(5)
    tnnp.setPos(point)
    texts.append(tnnp)
"""
"""

mdl = loader.loadModel('cog-bldg-modles/cog_bldg_executive_flr.egg')
mdl.reparentTo(render)
mdl.find('**/floor').setBin('ground', 18)

sky = loader.loadModel('phase_3.5/models/props/BR_sky.bam')
sky.reparentTo(render)
sky.setZ(-100)

painting = loader.loadModel('cog-bldg-modles/photo_frame.egg')
painting.reparentTo(render)
painting.setPosHpr(16.26, 63.84, 8.34, 270.0, 0, 90.0)

bookshelf1 = loader.loadModel('phase_11/models/lawbotHQ/LB_bookshelfA.bam')
bookshelf1.reparentTo(render)
bookshelf1.setScale(1.5)
bookshelf1.setPosHpr(-22.11, 49.88, 0.01, 90.0, 0, 0)

bookshelf2 = loader.loadModel('phase_11/models/lawbotHQ/LB_bookshelfB.bam')
bookshelf2.reparentTo(render)
bookshelf2.setScale(1.5)
bookshelf2.setPosHpr(-22.11, 35, 0.01, 90, 0, 0)

plant = loader.loadModel('phase_11/models/lawbotHQ/LB_pottedplantA.bam')
plant.setScale(12)
plant.reparentTo(render)
plant.setPos(20.51, -5.13, 0)

rug1 = loader.loadModel('phase_3.5/models/modules/rug.bam')
rug1.reparentTo(render)

rug2 = loader.loadModel('phase_3.5/models/modules/rug.bam')
rug2.reparentTo(render)
rug2.setPos(0, 52, 0)

clock = loader.loadModel('cog-bldg-modles/clock.egg')
clock.reparentTo(render)
clock.setPosHpr(23.68, 20.95, 9.67, 0, 0, 90)

recepC = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
recepC.reparentTo(render)
recepC.setPosHpr(20.7, 8.14, 0, 270, 0, 0)

recepM = loader.loadModel('cog-bldg-modles/computer_monitor.egg')
recepM.reparentTo(render)
recepM.setPosHpr(13.73, 8.17, 3.99, 270, 0, 0)

recepCC = loader.loadModel('cog-bldg-modles/coffee_cup.egg')
recepCC.reparentTo(render)
recepCC.setPosHpr(14.25, 10.65, 3.99, 78.69, 0, 0)

phone = loader.loadModel('phase_3.5/models/props/phone.bam')
receiver = loader.loadModel('phase_3.5/models/props/receiver.bam')
receiver.reparentTo(phone)
phone.reparentTo(render)
phone.setScale(1.2)
phone.setPosHpr(14.20, 5.29, 3.99, 95.96, 0, 0)

paper1 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper1.reparentTo(render)
paper1.setPosHpr(14.54, 13.34, 4.01, 63.43, 0, 0)

paper2 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper2.reparentTo(render)
paper2.setPosHpr(14.43, 0.72, 4.01, 270, 0, 0)

paper3 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper3.reparentTo(render)
paper3.setPosHpr(16.8, 1.14, 4.01, 118.61, 0, 0)

table = loader.loadModel('cog-bldg-modles/meeting_table.egg')
table.reparentTo(render)
table.setPos(-12.7, 5.94, 0)

tableC1 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC1.reparentTo(render)
tableC1.setPosHpr(-22.02, 1.57, 0, 90.0, 0, 0)

tableC2 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC2.reparentTo(render)
tableC2.setPosHpr(-22.02, 10.23, 0, 90.0, 0, 0)

tableC3 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC3.reparentTo(render)
tableC3.setPosHpr(-13.13, 19.73, 0, 0, 0, 0)

tableS = loader.loadModel('phase_3/models/props/square_drop_shadow.bam')
tableS.reparentTo(render)
tableS.setPos(-12.7, 5.94, 0.01)
tableS.setScale(2, 3.5, 1)

elev2 = loader.loadModel('phase_4/models/modules/elevator.bam')
elev2.reparentTo(render)
elev2.setPos(0.23007, 60.47556, 0)

elev1 = loader.loadModel('phase_4/models/modules/elevator.bam')
elev1.reparentTo(render)
elev1.setPos(0.74202, -9.50081, 0)
elev1.setH(180)
elev1.ls()

tableP1 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP1.reparentTo(render)
tableP1.setPosHpr(-16.71, 1.57, 3.4, 270, 0, 0)

tableP2 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP2.reparentTo(render)
tableP2.setPosHpr(-16.71, 10.23, 3.4, 270, 0, 0)

tableP3 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP3.reparentTo(render)
tableP3.setPosHpr(-13.44, 14.8, 3.41, 180, 0, 0)

tableP4 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP4.reparentTo(render)
tableP4.setPosHpr(-13.44, 14.8, 3.4, 150, 0, 0)

base.disableMouse()

#base.localAvatar.enableAvatarControls()
#base.localAvatar.startTrackAnimToSpeed()
#base.localAvatar.attachCamera()
#base.localAvatar.startSmartCamera()
base.localAvatar.reparentTo(hidden)

def printPosHpr():
	print 'Pos: {0}'.format(base.localAvatar.getPos())
	print 'Hpr: {0}'.format(base.localAvatar.getHpr())

base.accept('p', printPosHpr)
"""
#tex = loader.loadTexture("bg.tif")
#tex.setMinfilter(Texture.FTNearest)
#tex.setMagfilter(Texture.FTNearest)

#bg = OnscreenImage(image = tex, parent = render2d)

#base.cam.node().getDisplayRegion(0).setSort(20)

#from lib.coginvasion.cog import SuitBank
#from lib.coginvasion.cog import Variant
#from lib.coginvasion.cog.DistributedSuit import DistributedSuit

#camera.setH(90)
#camera.setZ(5)
#camera.setY(20)
"""
refNode = NodePath('refNode')
refNode.reparentTo(render)
refNode.setPosHpr(-4.88, 14.68, -6.91, 240.42, 7.77, 353.29)

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit(SuitBank.MrHollywood)
suit.setName("")
suit.reparentTo(refNode)
suit.stopSmooth()
suit.show()
suit.cleanupPropeller()
suit.removeHealthBar()
suit.pose('magic1', 15)

from lib.coginvasion.npc import NPCGlobals

refNodeT = NodePath('ref2Node')
refNodeT.reparentTo(render)

toon = Toon(base.cr)
toon.parseDNAStrand(NPCGlobals.NPC_DNA['Flippy'])
toon.generateToon()
toon.deleteShadow()
toon.setName("")
toon.reparentTo(refNodeT)
pie = loader.loadModel('phase_3.5/models/props/tart.bam')
pie.reparentTo(toon.find('**/joint_Rhold'))
toon.pose('pie', 45)
refNodeT.setPosHpr(3.22, 9, -3.56, 104.04, 9.73, 9.16)
pupilL = toon.controlJoint(None, 'head', 'joint_pupilL')
pupilL.setPosHpr(0.02, 0.08, -3.95, 15.01, 0, 0)
pupilR = toon.controlJoint(None, 'head', 'joint_pupilR')
pupilR.setPosHpr(0.03, 0.07, -3.96, 344.99, 0, 0)
angryEyes = loader.loadTexture('phase_3/maps/eyesAngry.jpg', 'phase_3/maps/eyesAngry_a.rgb')
toon.find('**/eyes').setTexture(angryEyes, 1)
#refNodeT.place()


ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT_sz.pdna")
node = loadDNAFile(ds, "phase_4/dna/toontown_central_sz.pdna")

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


bar = DirectWaitBar(value = 68)
bar.setBillboardAxis()
suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit(SuitBank.MrHollywood)
suit.setName("")
suit.reparentTo(render)
suit.stopSmooth()
suit.show()
suit.cleanupPropeller()
suit.removeHealthBar()

bar.reparentTo(suit)
bar.setZ(10)
StartPosFromDoor = Point3(1.6, -10, 0)
AtDoorPos = Point3(1.6, -1, 0)
takeOverTrack = Parallel(
    Sequence(
        Func(suit.animFSM.request, 'flyDown', [0]),
        Wait(6.834),
        Func(suit.loop, 'neutral'),
        Wait(0.5),
        Func(suit.loop, 'walk'),
        LerpPosInterval(suit, duration = 2.0, pos = AtDoorPos,
                        startPos = StartPosFromDoor),
        Func(suit.loop, 'neutral'),
        Wait(0.3),
        Func(suit.loop, 'walk'),
        LerpPosInterval(suit, duration = 0.5, pos = Point3(1.6, -5.5, 0.0),
                        startPos = AtDoorPos),
        Func(suit.loop, 'neutral'),
        Wait(0.3),
        Func(suit.loop, 'walk'),
        LerpPosInterval(suit, duration = 1.0, pos = Point3(1.6, 3.0, 0.0),
                        startPos = Point3(1.6, -5.5, 0.0))),
    LerpPosInterval(suit,
                    duration = 4.375,
                    pos = StartPosFromDoor,
                    startPos = StartPosFromDoor + (0, 0, 6.5 * 4.8))
)

takeOverTrack.start()

pieSpeed = 0.2
pieExponent = 0.75

import math

powerBar = DirectWaitBar(range = 150, frameColor = (1, 1, 1, 1),
                         barColor = (0.286, 0.901, 1, 1), relief = DGG.RAISED,
                         borderWidth = (0.04, 0.04), pos = (0, 0, 0.85), scale = 0.2,
                         hpr = (0, 0, 0), parent = aspect2d, frameSize = (-0.85, 0.85, -0.12, 0.12))
                         
def scaleTask(task):
	powerBar['value'] = __getPiePower(globalClock.getFrameTime())
	return task.cont

def startMoving():
	print 'hi'
	global tossPieStart
	tossPieStart = globalClock.getFrameTime()
	taskMgr.add(scaleTask, "scaleTask")
	
def stopMoving():
	taskMgr.remove("scaleTask")
	print powerBar['value'] + 50

#base.accept('mouse1', startMoving)
#base.accept('mouse1-up', stopMoving)

frame = DirectScrolledFrame(canvasSize = (-1, 1, -3.5, 1), frameSize = (-0.8, 2, -0.6, 0.9), parent = base.a2dBottomLeft)
frame.setPos(0, 0, 0)
frame.setScale(0.3)
#frame.place()
"""
from lib.coginvasion.cog.SuitPathDataAI import *

#from lib.coginvasion.cog import SuitPathFinder

from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
import time
startTime = time.time()
#path = pathfinder.planPath((-30.0, 27.0), (-50, -20))
print time.time() - startTime
#linesegs = LineSegs('visual')
#linesegs.setColor(0, 0, 0, 1)

#for vertex in pathfinder.vertices:
#	#linesegs.drawTo(vertex.prevPolyNeighbor.pos.getX(), vertex.prevPolyNeighbor.pos.getY(), 20)
#	linesegs.drawTo(vertex.nextPolyNeighbor.pos.getX(), vertex.nextPolyNeighbor.pos.getY(), 20)
#node = linesegs.create(False)
#np = render.attachNewNode(node)

from panda3d.core import LineSegs

linesegs = LineSegs('visual')
linesegs.setColor(0, 0, 0, 1)

for point in path:
	linesegs.drawTo(point.getX(), point.getY(), 0)

node = linesegs.create(False)
np = render.attachNewNode(node)

def doPath():
	global path
	if not len(path):
		suit.loop('neutral')
		return
	endX, endY = path[0]
	endPoint = Point3(endX, endY, 0)
	startPoint = suit.getPos(render)
	path.remove(path[0])
	ival = NPCWalkInterval(suit, endPoint, 0.2, startPoint)
	ival.setDoneEvent(suit.uniqueName('guardWalkDone'))
	base.acceptOnce(suit.uniqueName('guardWalkDone'), doPath)
	ival.start()
	suit.loop('walk')


smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
#smiley.place()

def makePathandgo():
	point = (smiley.getX(), smiley.getY())
	startPoint = (suit.getX(), suit.getY())
	global path
	path = pathfinder.planPath(startPoint, point)
	if len(path) > 1:
		path.remove(path[0])
	print path
	doPath()

#base.accept('p', makePathandgo)

from datetime import datetime

def update(task):
	if base.mouseWatcherNode.hasMouse():
		md = base.win.getPointer(0)
		x = (base.win.getXSize() - md.getX()) * 0.1
		y = (md.getY() - base.win.getYSize()/2.0) * 0.1
		#print "X: " + str(x) + " Y: " + str(y)
		print 500.0 / (base.win.getXSize()*0.07)
		if (x <= 500.0 / (base.win.getXSize()*0.07) and y <= 500.0 / (base.win.getXSize()*0.07)) and (x <= 500.0 / (base.win.getXSize()*0.07) and y >= -500.0 / (base.win.getXSize()*0.07)):
			print "entered!"
		else:
			print "Exited!"
	return task.cont

def handleEnter(foo):
	print "entered"
	
def handleExit(foo):
	print "exited"

button = DirectButton(text = "", relief = None, text_bg = (1, 1, 1, 0), parent = base.a2dRightCenter,
					  pos = (-0.1725, 0, 0), frameSize = (-0.2, 0.2, -0.8, 0.8))
button.bind(DGG.ENTER, handleEnter)
button.bind(DGG.EXIT, handleExit)
button.guiItem.setActive(True)

#base.taskMgr.add(update, "update")


startTime = time.time()



base.setFrameRateMeter(True)











def findPath(task):
	for i in range(101):
		SuitPathFinder.find_path(CIGlobals.DonaldsDreamland, '1', '36')
	print task.time
	return task.again


def start():
	taskMgr.add(findPath, 'findPath')
	
def pause():
	taskMgr.remove('findPath')

base.accept('s', start)
base.accept('p', pause)
print 'start'
print time.time() - startTime
#print datetime.now() - startTime


#render.setAntialias(AntialiasAttrib.MMultisample)

#base.disableMouse()

#refNode.place()

#base.startDirect()

#toon = loader.loadModel('models/smiley')
#toon.reparentTo(elevator1)
#toon.place()

#music = base.loadMusic("phase_7/audio/bgm/encntr_general_bg_indoor.ogg")
#base.playMusic(music, volume = 0.25, looping = 1, interrupt = 1)

#spin = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.mp3')
#deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.mp3')

#track = Sequence(Wait(0.8), SoundInterval(spin, duration = 1.2, startTime = 1.5, volume = 0.2), SoundInterval(spin, duration = 3.0, startTime = 0.6, volume = 0.9), SoundInterval(deathSound, volume = 0.4))
#track.start()

#sound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_Full.mp3')
#base.playSfx(sound, volume = 10)

#base.disableMouse()
base.localAvatar.reparentTo(render)

#base.localAvatar.attachCamera()
#base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()

base.enableMouse()

def compute2dPosition(nodePath, point = Point3(0, 0, 0)):
    """ Computes a 3-d point, relative to the indicated node, into a
    2-d point as seen by the camera.  The range of the returned value
    is based on the len's current film size and film offset, which is
    (-1 .. 1) by default. """

    # Convert the point into the camera's coordinate space
    p3d = base.cam.getRelativePoint(nodePath, point)

    # Ask the lens to project the 3-d point to 2-d.
    p2d = Point2()
    if base.camLens.project(p3d, p2d):
        # Got it!
        return p2d
	
    # If project() returns false, it means the point was behind the
    # lens.
    return None
    
#button = DirectButton(text = "")

def __updateFrameTask(task):
    twodpos = compute2dPosition(base.localAvatar)
    print twodpos
    
    if twodpos is None:
	return task.cont
    #point3 = Point3(twodpos.getX(), 0, twodpos.getY())
    #button.setPos(point3)
    
    centerX = twodpos.getX() / 2.0
    centerY = twodpos.getY() / 2.0
    bounds = base.localAvatar.getGeomNode().getTightBounds()
    bound1 = Point2()
    bound2 = Point2()
    base.camLens.project(bounds[0], bound1)
    base.camLens.project(bounds[1], bound2)
    left = centerX - (bound1.getX() / 2.0)
    right = centerX + (bound2.getX() / 2.0)
    bottom = centerY - (bound1.getY() / 2.0)
    top = centerY + (bound2.getY() / 2.0)
    
    
    transform = base.localAvatar.getGeomNode().getNetTransform()

    # We use the inverse of the cam transform so that it will not be
    # applied to the frame points twice:
    camTransform = base.cam.getNetTransform().getInverse()

    # Compose the inverse of the cam transform and our node's transform:
    transform = camTransform.compose(transform)

    # Discard its rotational components:
    #transform.setQuat(Quat())

    # Transform the frame points into cam space:
    mat = transform.getMat()
    camSpaceTopLeft = mat.xformPoint(Point3(left, 0, top))
    camSpaceBottomRight = mat.xformPoint(Point3(right, 0, bottom))
        
    # Project into screen space:
    screenSpaceTopLeft = Point2()
    screenSpaceBottomRight = Point2()
    base.camLens.project(Point3(camSpaceTopLeft), screenSpaceTopLeft)
    base.camLens.project(Point3(camSpaceBottomRight), screenSpaceBottomRight)

    left, top = screenSpaceTopLeft
    right, bottom = screenSpaceBottomRight
    
    #button['frameSize'] = (left, right, bottom, top)
    return task.cont

#taskMgr.add(__updateFrameTask, "updateFrame")


#bounds = base.localAvatar.getTightBounds()
#smiley  = loader.loadModel('models/smiley.egg.pz')
#smiley.reparentTo(base.localAvatar.getGeomNode())
#smiley.setPos(bounds[0])
#smiley2 = loader.loadModel('models/smiley.egg.pz')
#smiley2.reparentTo(base.localAvatar.getGeomNode())
#smiley2.setPos(bounds[1])

from direct.showbase.ShadowDemo import arbitraryShadow

base.localAvatar.stopTrackAnimToSpeed()
base.localAvatar.deleteShadow()
arbitraryShadow(base.localAvatar)

dance = base.loadSfx('/c/Users/Brian/Desktop/ENC_Win.wav')

def win():
    base.playSfx(dance, looping = 1)
    base.localAvatar.loop('win')
    
base.accept('w', win)

print base.localAvatar.getDuration('win')
#base.localAvatar.getGeomNode().getChild(0).node().forceSwitch(0)

from panda3d.core import *

light = PointLight('slight')
light.setColor(VBase4(1, 1, 1, 1))
lnp = render.attachNewNode(light)
render.setLight(lnp)

amb = AmbientLight('alight')
amb.setColor(VBase4(0.5, 0.5, 0.5, 1))
anp = render.attachNewNode(amb)
render.setLight(anp)

render.setShaderAuto()

"""
for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(10)
			except:
				pass
	except:
		continue

#base.useDrive()
#base.oobe()
base.run()
