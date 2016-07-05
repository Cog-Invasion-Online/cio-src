from pandac.PandaModules import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'multisamples 1000')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'default-model-extension .egg')
#loadPrcFileData('', 'window-title Grand Theft Toontown')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.distributed.ClientRepository import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *

base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()
aspect2d.setAntialias(AntialiasAttrib.MMultisample)

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

import __builtin__
class game:
	process = 'client'
__builtin__.game = game

bgm = base.loadMusic("LOADING_TUNE.wav")

base.playMusic(bgm, looping = 1)
base.transitions.fadeOut(0)
"""
from lib.toontown.hood.SkyUtil import SkyUtil
util = SkyUtil()
track = loader.loadModel("phase_4/models/minigames/sprint_track.egg")
track.reparentTo(render)
sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
sky.reparentTo(track)
util.startSky(sky)
"""
"""
light = render.attachNewNode(Spotlight('light'))
light.node().setColor(Vec4(1, 1, 1, 1))
light.node().setShadowCaster(True, 2048, 2048)
light.setPos(-22.00, -115, 20)
light.setH(180)
render.setLight(light)
amb = render.attachNewNode(AmbientLight('amblight'))
amb.node().setColor(Vec4(1.0, 1.0, 1.0, 1))
render.setLight(amb)
render.setAttrib(LightRampAttrib.makeDefault())
render.setShaderAuto()
render.flattenStrong()
render.setTwoSided(True)


for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(10)
			except:
				pass
	except:
		continue
"""
"""
from lib.toontown.toon import Toon
model = Toon.Toon(base.cr)
model.setDNAStrand("00/08/00/17/01/17/01/17/19/19/03/07/07/07/00")
model.generateToon()
model.reparentTo(render)
model.setName("toon")
#model.setPos(-22.00, -205.00, 0.00)
#light.lookAt(model)
#model.animFSM.request('neutral')
#model.pose("neutral", 1)
for leg_joint in model.getJoints(partName = "legs"):
	model.controlJoint(None, "legs", leg_joint.getName())
for torso_joint in model.getJoints(partName = "torso"):
	model.controlJoint(None, "torso", torso_joint.getName())
hat = loader.loadModel("phase_4/models/accessories/tt_m_chr_avt_acc_hat_fedora.bam")
hat.reparentTo(model.find('**/def_neck'))
hat.setPos(0.00, 2.09, 2.21)
hat.setH(180.00)
hat.setScale(0.28)
model.place()

model.listJoints("torso")


base.camLens.setMinFov(30.0/(4./3.))

#base.setBackgroundColor(0, 0, 1)

def eyesLookAt(task):
	for node in model.findAllMatches('**/joint_pupil*'):
		node.headsUp(camera)
		if node.getH() > 0:
			if node.getH() > 5.7:
				node.setH(5.7)
		else:
			if node.getH() < -5.7:
				node.setH(-5.7)
	return task.again

taskMgr.add(eyesLookAt, "eyesLookAt")


render.setTwoSided(True)
render.setAntialias(AntialiasAttrib.MMultisample)

"""
model = None

def __loadingScreen():
	Sequence(Func(__model_2), Func(base.transitions.fadeIn, 0.4), Wait(8), Func(base.transitions.fadeOut, 0.4), Wait(0.41), Func(removeModel), Func(__model_1), Func(base.transitions.fadeIn, 0.4), Wait(8), Func(base.transitions.fadeOut, 0.4), Wait(0.41), Func(removeModel)).loop()

def removeModel():
	global model
	if model != None:
		if not model.isEmpty():
			model.destroy()
			model = None
			
def __model_2():
	global model
	model = OnscreenImage(image = "/c/Users/Brian/Pictures/ciloading/model_2_regular.png", scale = (0.5, 0.8, 0.8), pos = (-0.85, 0, -0.2))
	model.setTransparency(True)
	ival = model.scaleInterval(200.0, (3.7, 4.4, 4.4), startScale = model.getScale())
	ival.start()
	ival2 = model.posInterval(140.0, (1, 0, -0.5), startPos = model.getPos())
	ival2.start()
	
def __model_1():
	global model
	model = OnscreenImage(image = "/c/Users/Brian/Pictures/ciloading/model_1_regular.png", scale = (0.5, 0.8, 0.8), pos = (0.85, 0, -0.35))
	model.setTransparency(True)
	ival = model.scaleInterval(200.0, (3.7, 4.4, 4.4), startScale = model.getScale())
	ival.start()
	ival2 = model.posInterval(140.0, (-1, 0, -0.5), startPos = model.getPos())
	ival2.start()

Sequence(Wait(0.4), Func(__loadingScreen)).start()


base.oobe()
camera.hide()
run()
