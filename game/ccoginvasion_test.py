from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'ctmusic-numsongs 4')

from src.coginvasion.standalone.StandaloneToon import *

import ccoginvasion

print dir(ccoginvasion)
"""
ccoginvasion.CTMusicData.initialize_chunk_data()
ccoginvasion.CTMusicManager.spawn_load_tournament_music_task()

mgr = None

def poll_loaded(task):
    global mgr
    if ccoginvasion.CTMusicManager.is_loaded():
        mgr = ccoginvasion.CTMusicManager()
        mgr.set_song_name("encntr_nfsmw_bg_4")
        mgr.start_music("_base")
        
        base.accept('control-5', mgr.set_clip_request, ["5050_orchestra"])
        base.accept('5', mgr.set_clip_request, ["5050_base"])
        base.accept('control-l', mgr.set_clip_request, ["located_orchestra"])
        base.accept('l', mgr.set_clip_request, ["located_base"])
        base.accept('control-r', mgr.set_clip_request, ["running_away_orchestra"])
        base.accept('r', mgr.set_clip_request, ["running_away_base"])
        base.accept('control-g', mgr.set_clip_request, ["getting_worse_orchestra"])
        base.accept('g', mgr.set_clip_request, ["getting_worse_base"])
        base.accept('control-i', mgr.set_clip_request, ["intro_orchestra"])
        base.accept('i', mgr.set_clip_request, ["intro_base"])
        base.accept('shift-s', mgr.set_clip_request, ['static_cooldown'])
        base.accept('a', mgr.set_clip_request, ["arresting_you"])
        base.accept('h', mgr.set_clip_request, ["high_speed_cooldown_base"])
        base.accept('control-h', mgr.set_clip_request, ["high_speed_cooldown_orchestra"])
        base.accept('v', mgr.set_clip_request, ["very_low_speed_cooldown"])
        base.accept('c', mgr.set_clip_request, ["low_speed_cooldown_1"])
        base.accept('control-c', mgr.set_clip_request, ["low_speed_cooldown_2"])
        base.accept('shift-a', mgr.set_clip_request, ["approaching_base"])
        base.accept('shift-control-a', mgr.set_clip_request, ["approaching_orchestra"])
        base.accept('control-a', mgr.set_clip_request, ["arrested_1"])
        base.accept('e', mgr.set_clip_request, ["evaded_1"])
        base.accept('f', mgr.set_clip_request, ["intro_orchestra_from_located"])
        
        return task.done
    return task.cont

base.taskMgr.add(poll_loaded, "poll_loaded")


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

from panda3d.core import *

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
	"""
from src.coginvasion.cog import SuitPathDataAI
from src.coginvasion.globals import CIGlobals

office = loader.loadModel("phase_7/models/modules/cog_bldg_reception_flr.bam")
office.reparentTo(render)

smiley1 = loader.loadModel("models/smiley.egg.pz")
smiley1.reparentTo(render)
smiley1.setPos(0, 80, 0)

smiley2 = loader.loadModel("models/smiley.egg.pz")
smiley2.reparentTo(render)
smiley2.setPos(0, 0, 0)

finder = SuitPathDataAI.getPathFinder(CIGlobals.BattleTTC)


import time
st = time.time()
path = finder.planPath((120, 80), (0, 0))
print "took:", time.time() - st



linesegs = LineSegs('visual')
linesegs.setColor(0, 0, 0, 1)

for point in path:
	linesegs.drawTo(point[0], point[1], 0)

node = linesegs.create(False)
np = render.attachNewNode(node)

print path

#PStatClient.connect()

base.run()
