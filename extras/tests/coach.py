from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'default-model-extension .egg')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 64')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.distributed.ClientRepository import ClientRepository
from lib.toontown.globals import ToontownGlobals
from direct.interval.IntervalGlobal import *

import __builtin__
class game:
	process = "client"
__builtin__.game = game

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)

#base.setBackgroundColor(1, 1, 0)

base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()
base.cTrav.showCollisions(render)

AreaModels = ["phase_11/models/lawbotHQ/LB_Zone03a.bam",
				"phase_11/models/lawbotHQ/LB_Zone04a.bam",
				"phase_11/models/lawbotHQ/LB_Zone7av2.bam",
				"phase_11/models/lawbotHQ/LB_Zone08a.bam",
				"phase_11/models/lawbotHQ/LB_Zone13a.bam",
				"phase_10/models/cashbotHQ/ZONE17a.bam",
				"phase_10/models/cashbotHQ/ZONE18a.bam",
				"phase_11/models/lawbotHQ/LB_Zone22a.bam"]
AreaModelParents = [render, "EXIT", "EXIT", "EXIT",
					"ENTRANCE", "ENTRANCE", "ENTRANCE", "EXIT"]
AreaModelPos = [Point3(0.00, 0.00, 0.00),
					Point3(-1.02, 59.73, 0.00),
					Point3(0.00, 74.77, 0.00),
					Point3(0.00, 89.37, -13.50),
					Point3(16.33, -136.53, 0.00),
					Point3(-1.01, -104.40, 0.00),
					Point3(0.65, -23.86, 0.00),
					Point3(-55.66, -29.01, 0.00)]
AreaModelHpr = [Vec3(0.00, 0.00, 0.00),
				Vec3(0.00, 0.00, 0.00),
				Vec3(90.00, 0.00, 0.00),
				Vec3(180.00, 0.00, 0.00),
				Vec3(97.00, 0.00, 0.00),
				Vec3(359.95, 0.00, 0.00),
				Vec3(90.00, 0.00, 0.00),
				Vec3(270.00, 0.00, 0.00)]

areas = []
areaName2areaModel = {}

def attachArea(itemNum):
	name = 'SneakyArea-%s' % itemNum
	area = areaName2areaModel.get(name)
	parent = AreaModelParents[itemNum]
	if type(parent) == type(""):
		parent = areas[itemNum - 1].find('**/' + AreaModelParents[itemNum])
	pos = AreaModelPos[itemNum]
	hpr = AreaModelHpr[itemNum]
	area.reparentTo(parent)
	area.setPos(pos)
	area.setHpr(hpr)

_numItems = 0
name = None
for item in AreaModels:
	name = 'SneakyArea-%s' % _numItems
	area = loader.loadModel(item)
	areas.append(area)
	areaName2areaModel[name] = area
	attachArea(_numItems)
	_numItems += 1

render.setAntialias(AntialiasAttrib.MMultisample)

base.enableParticles()

base.camLens.setMinFov(ToontownGlobals.GunGameFOV / (4./3.))

base.disableMouse()
camera.setPos(0.0, -25.80, 7.59)
camera.setHpr(0.00, 0.00, 0.00)

ival = Sequence(
	Wait(10.157),
	LerpQuatInterval(camera, duration = 1.0, quat = (90, 0, 0), startHpr = Vec3(0, 0, 0), blendType = 'easeInOut'),
	LerpQuatInterval(camera, duration = 1.0, quat = (90, 15, 0), startHpr = Vec3(90, 0, 0), blendType = 'easeInOut'),
	LerpQuatInterval(camera, duration = 1.0, quat = (120, 0, 0), startHpr = Vec3(90, 15, 0), blendType = 'easeInOut'),
	Wait(0.3),
	LerpQuatInterval(camera, duration = 1.0, quat = (25, 0, 0), startHpr = Vec3(120, 0, 0), blendType = 'easeInOut'),
	Wait(1.35),
	LerpQuatInterval(camera, duration = 1.0, quat = (90, -15, 0), startHpr = Vec3(25, 0, 0), blendType = 'easeInOut'),
	Wait(0.3),
	LerpQuatInterval(camera, duration = 1.5, quat = (183, 0, 0), startHpr = Vec3(90, -15, 0), blendType = 'easeInOut'),
	Wait(6.0),
	LerpQuatInterval(camera, duration = 1.5, quat = (160, 0, 0), startHpr = Vec3(183, 0, 0), blendType = 'easeInOut'),
	Wait(1.5),
	LerpQuatInterval(camera, duration = 1.5, quat = (203, 0, 0), startHpr = Vec3(160, 0, 0), blendType = 'easeInOut'),
	Wait(3.85),
	LerpQuatInterval(camera, duration = 1.35, quat = (188, 0, 0), startHpr = Vec3(203, 0, 0), blendType = 'easeInOut'),
	Wait(7.0),
	LerpQuatInterval(camera, duration = 1.0, quat = (97, 0, 0), startHpr = Vec3(188, 0, 0), blendType = 'easeInOut'),
	Wait(0.35),
	LerpQuatInterval(camera, duration = 1.0, quat = (182, 0, 0), startHpr = Vec3(97, 0, 0), blendType = 'easeInOut'),
	Wait(1.0),
	Func(taskMgr.remove, "ft")
)
ival.start()

def forwardTask(task):
	camera.setY(camera, 25 * globalClock.getDt())
	return task.cont

taskMgr.add(forwardTask, "ft")

run()
