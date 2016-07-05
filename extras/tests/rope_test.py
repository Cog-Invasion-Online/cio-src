from lib.coginvasion.standalone.StandaloneToon import *
from direct.showutil.Rope import Rope
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.npc import NPCGlobals
from direct.showbase.Audio3DManager import Audio3DManager
from direct.distributed.ClientRepository import ClientRepository

base.cr = ClientRepository([])
base.cr.isShowingPlayerIds = False
base.cTrav = CollisionTraverser('coll_trav')
base.audio3d = Audio3DManager(base.sfxManagerList[0], base.camera)

sky = loader.loadModel('phase_3.5/models/props/BR_sky.bam')
sky.reparentTo(render)
sky.setZ(-5)

arena = loader.loadModel('dodgeball_arena.egg')
arena.reparentTo(render)
arena.find('**/team_divider').setBin('ground', 18)
arena.find('**/floor').setBin('ground', 18)
arena.find('**/wall*_coll').setCollideMask(CIGlobals.WallBitmask)

tree_data = [['prop_snow_tree_small_ur', Point3(23.23, 66.52, 7.46)],
	['prop_snow_tree_small_ul', Point3(-34.03, 88.02, 24.17)],
	['prop_snow_tree_small_ur', Point3(-54.80, 0, 4.19)],
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

for data in tree_data:
	code = data[0]
	pos = data[1]
	tree = getSnowTree(code)
	tree.reparentTo(render)
	tree.setPos(pos)
	trees.append(tree)
	
#trees[4].place()

base.disableMouse()
base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.startTrackAnimToSpeed()

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

base.run()
