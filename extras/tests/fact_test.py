from panda3d.core import *
cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 16')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.controls.ControlManager import CollisionHandlerRayStart
from Tkinter import *
from direct.gui.OnscreenText import OnscreenText
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.Suit import Suit
from direct.distributed.ClientRepository import ClientRepository
from collections import deque
from libpandadna import *
from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
#base.startTk()
import random

base.cTrav = CollisionTraverser()
base.cr = ClientRepository([])
base.shadowTrav = CollisionTraverser()
base.lifter = CollisionHandlerFloor()
base.pusher = CollisionHandlerPusher()

class Points:

    def __init__(self):
        self.points = []
        self.lastPoint = None

    def createPoint(self):
        tn = TextNode('tn')
        tn.setText("Point " + str(len(self.points) + 1))
        tn.setAlign(TextNode.ACenter)
        tnp = render.attachNewNode(tn)
        tnp.reparentTo(render)
        if self.lastPoint:
            tnp.setPos(self.lastPoint.getPos(render))
        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        cRayNode = CollisionNode('pointray')
        cRayNode.addSolid(cRay)
        cRayNodePath = tnp.attachNewNode(cRayNode)
        cRayBitMask = CIGlobals.FloorBitmask
        cRayNode.setFromCollideMask(cRayBitMask)
        cRayNode.setIntoCollideMask(BitMask32.allOff())
        lifter = CollisionHandlerFloor()
        lifter.addCollider(cRayNodePath, tnp)
        base.cTrav.addCollider(cRayNodePath, lifter)

        cSphere = CollisionSphere(0.0, 0.0, 1, 0.01)
        cSphereNode = CollisionNode('pointfc')
        cSphereNode.addSolid(cSphere)
        cSphereNodePath = tnp.attachNewNode(cSphereNode)

        cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
        cSphereNode.setIntoCollideMask(BitMask32.allOff())

        pusher = CollisionHandlerPusher()
        pusher.addCollider(cSphereNodePath, tnp)
        floorCollNodePath = cSphereNodePath
        base.cTrav.addCollider(cSphereNodePath, pusher)
        #if self.lastPoint:
        #   self.lastPoint.place()
        self.lastPoint = tnp

    def placeLastPoint(self):
        self.lastPoint.place()

class WalkPoints(Points):

    def __init__(self):
        Points.__init__(self)

    def createPoint(self):
        Points.createPoint(self)
        self.lastPoint.node().setText("Walk Point " + str(len(self.points) + 1))
        self.lastPoint.node().setText("")
        self.lastPoint.setBillboardAxis()
        self.points.append(self.lastPoint)

class GuardPoints(Points):

    def __init__(self):
        Points.__init__(self)

    def createPoint(self):
        Points.createPoint(self)
        self.lastPoint.node().setText("Guard Point " + str(len(self.points) + 1))
        self.lastPoint.node().setText("")
        self.lastPoint.node().setTextColor(VBase4(0.5, 0.5, 1, 1.0))
        self.lastPoint.setTwoSided(1)
        self.points.append(self.lastPoint)

class BarrelPoints(Points):

    def createPoint(self):
        Points.createPoint(self)
        self.lastPoint.node().setText("Barrel Point " + str(len(self.points) + 1))
        self.lastPoint.node().setText("")
        self.lastPoint.node().setTextColor(VBase4(1, 0.5, 0.5, 1.0))
        self.lastPoint.setTwoSided(1)
        self.points.append(self.lastPoint)

"""
ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.pdna")
loadDNAFile(ds, "phase_6/dna/storage_OZ.pdna")
loadDNAFile(ds, "phase_6/dna/storage_OZ_sz.pdna")
node = loadDNAFile(ds, "phase_6/dna/outdoor_zone_sz.pdna")

if node.getNumParents() == 1:
    geom = NodePath(node.getParent(0))
    geom.reparentTo(hidden)
else:
    geom = hidden.attachNewNode(node)
gsg = base.win.getGsg()
if gsg:
    geom.prepareScene(gsg)

partyGate = geom.find('**/prop_party_gate_DNARoot')
if not partyGate.isEmpty():
    partyGate.removeNode()
del partyGate

geom.reparentTo(render)

sky = loader.loadModel('phase_3.5/models/props/TT_sky.bam')
sky.reparentTo(render)
sky.setScale(5)


walks = WalkPoints()
guards = GuardPoints()
barrels = BarrelPoints()

def writeWPoint():
    pointfile = open("factory_sneak_guard_walk_points.py", "a")
    pointfile.write("\n" + str(walks.lastPoint.getX()) + " " + str(walks.lastPoint.getY()) + " " + str(walks.lastPoint.getZ()))
    pointfile.flush()
    pointfile.close()
    del pointfile

def createWPoint():
    walks.createPoint()
    walks.placeLastPoint()

def writeGPoint():
    pointfile = open("factory_sneak_guard_guard_points.py", "a")
    pointfile.write("\n" + str(guards.lastPoint.getX()) + " " + str(guards.lastPoint.getY()) + " " + str(guards.lastPoint.getZ()) + "|" + str(guards.lastPoint.getH()) + " " + str(guards.lastPoint.getP()) + " " + str(guards.lastPoint.getR()))
    pointfile.flush()
    pointfile.close()
    del pointfile

def createGPoint():
    guards.createPoint()
    guards.placeLastPoint()

def writeJBSPoint():
    pointfile = open("factory_sneak_barrel_points.py", "a")
    pointfile.write("\n" + str(barrels.lastPoint.getX()) + " " + str(barrels.lastPoint.getY()) + " " + str(barrels.lastPoint.getZ()) + "|" + str(barrels.lastPoint.getH()) + " " + str(barrels.lastPoint.getP()) + " " + str(barrels.lastPoint.getR()))
    pointfile.flush()
    pointfile.close()
    del pointfile

def createJBSPoint():
    barrels.createPoint()
    barrels.placeLastPoint()

newWalkBtn = Button(base.tkRoot, text = "Walk Point", command = createWPoint)
newWalkBtn.pack()
walkPointDoneBtn = Button(base.tkRoot, text = "WP Done", command = writeWPoint)
walkPointDoneBtn.pack()
newGuardBtn = Button(base.tkRoot, text = "Guard Point", command = createGPoint)
newGuardBtn.pack()
gPointDoneBtn = Button(base.tkRoot, text = "GP Done", command = writeGPoint)
gPointDoneBtn.pack()
newJbsBtn = Button(base.tkRoot, text = "JBS Point", command = createJBSPoint)
newJbsBtn.pack()
jbsPointDoneBtn = Button(base.tkRoot, text = "JBS Done", command = writeJBSPoint)
jbsPointDoneBtn.pack()

pointfile = open("factory_sneak_guard_walk_points.py", "r")
for line in pointfile.readlines():
    print line
    x, y, z = line.split(' ')
    x = float(x)
    y = float(y)
    z = float(z)
    walks.createPoint()
    walks.lastPoint.setPos(Point3(x, y, z))
pointfile.close()
del pointfile

pointfile = open("factory_sneak_guard_guard_points.py", "r")
for line in pointfile.readlines():
    pos, hpr = line.split('|')
    x, y, z = pos.split(' ')
    h, p, r = hpr.split(' ')
    x = float(x)
    y = float(y)
    z = float(z)
    h = float(h)
    p = float(p)
    r = float(r)
    guards.createPoint()
    guards.lastPoint.setPos(Point3(x, y, z))
    guards.lastPoint.setHpr(Vec3(h, p, r))
pointfile.close()
del pointfile

pointfile = open("factory_sneak_barrel_points.py", "r")
for line in pointfile.readlines():
    pos, hpr = line.split('|')
    x, y, z = pos.split(' ')
    h, p, r = hpr.split(' ')
    x = float(x)
    y = float(y)
    z = float(z)
    h = float(h)
    p = float(p)
    r = float(r)
    string = "    [Point3({0}, {1}, {2}), Vec3({3}, {4}, {5})],\n".format(x, y, z, h, p, r)
    #output.write(string)
#output.write("]")
#output.flush()
#output.close()
#del output
pointfile.close()
del pointfile

"""
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.interval.IntervalGlobal import *

factory = loader.loadModel("phase_9/models/cogHQ/SelbotLegFactory.bam")
factory.reparentTo(render)
"""
#base.disableMouse()

node = NodePath('baseNode')
node.reparentTo(render)

collisionSphere = CollisionSphere(0, 0, 0, 2)
sensorNode = CollisionNode("sensors")
sensorNode.addSolid(collisionSphere)
sensorNodePath = node.attachNewNode(sensorNode)
sensorNodePath.setZ(2.5)
sensorNodePath.setSz(2)
sensorNodePath.setCollideMask(BitMask32(0))
sensorNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)
sensorNodePath.show()
event = CollisionHandlerEvent()
event.setInPattern("%fn-into")
event.setOutPattern("%fn-out")
base.cTrav.addCollider(sensorNodePath, event)

cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
cRayNode = CollisionNode('ray' + 'r')
cRayNode.addSolid(cRay)
cRayNodePath = node.attachNewNode(cRayNode)
cRayBitMask = CIGlobals.FloorBitmask
cRayNode.setFromCollideMask(cRayBitMask)
cRayNode.setIntoCollideMask(BitMask32.allOff())
lifter = CollisionHandlerFloor()
lifter.addCollider(cRayNodePath, node)
base.cTrav.addCollider(cRayNodePath, lifter)

cSphere = CollisionSphere(0.0, 0.0, 2, 0.01)
cSphereNode = CollisionNode('sphere' + 'fc')
cSphereNode.addSolid(cSphere)
cSphereNodePath = node.attachNewNode(cSphereNode)

cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
cSphereNode.setIntoCollideMask(BitMask32.allOff())

pusher = CollisionHandlerPusher()
pusher.addCollider(cSphereNodePath, node)
floorCollNodePath = cSphereNodePath
base.cTrav.addCollider(cSphereNodePath, pusher)

#base.disableMouse()

#camera.reparentTo(node)
#camera.setY(-10)
#camera.setZ(2)

sphere = CollisionSphere(0, 0, 0, 1)
cnode = CollisionNode('collNode')
cnode.addSolid(sphere)
cnode.setCollideMask(CIGlobals.WallBitmask)
np = render.attachNewNode(cnode)
np.setScale(75)
np.setPos(-26.8, 5.18, 0.0)
np.show()

sphere = CollisionSphere(0, 0, 0, 1)
cnode = CollisionNode('collNode')
cnode.addSolid(sphere)
cnode.setCollideMask(CIGlobals.WallBitmask)
np = render.attachNewNode(cnode)
np.show()
np.setPos(-14.39, 127.12, 0)
np.setScale(20)

sphere = CollisionSphere(0, 0, 0, 1)
cnode = CollisionNode('collNode')
cnode.addSolid(sphere)
cnode.setCollideMask(CIGlobals.WallBitmask)
np = render.attachNewNode(cnode)
np.show()
np.setPos(-14.39, 92.18, 0)
np.setScale(20)

sphere = CollisionSphere(0, 0, 0, 1)
cnode = CollisionNode('collNode')
cnode.addSolid(sphere)
cnode.setCollideMask(CIGlobals.WallBitmask)
np = render.attachNewNode(cnode)
np.show()
np.setPos(31.02, -51.43, 0.0)
np.setScale(20)

class WayPointTest:

    def __init__(self, point, number):
        self.point = point
        self.number = number
        self.wayPointsToTest = dict(CIGlobals.SuitSpawnPoints[CIGlobals.DonaldsDock])
        del self.wayPointsToTest[number]
        self.finalList = []
        self.currentWayPointTestKey = None
        self.numberOfTests = -1
        self.movementIval = None
        self.allTestsDone = False
        print "Testing waypoint: " + str(number)
        self.testNextWayPoint()

    def allTestsCompleted(self):
        print "Done testing waypoint: " + str(self.number)
        self.allTestsDone = True

    def testNextWayPoint(self):
        self.numberOfTests += 1
        if self.movementIval:
            self.movementIval.pause()
            self.movementIval = None
        if self.numberOfTests > len(self.wayPointsToTest.keys()) - 1:
            self.allTestsCompleted()
            return
        print "Test number " + str(self.numberOfTests) + " on waypoint " + str(self.number)
        self.currentWayPointTestKey = self.wayPointsToTest.keys()[self.numberOfTests]
        self.movementIval = NPCWalkInterval(node, self.wayPointsToTest[self.currentWayPointTestKey],
            0.01, startPos = self.point, fluid = 1)
        self.movementIval.setDoneEvent('testWayPointDone')
        base.acceptOnce(self.movementIval.getDoneEvent(), self.currentTestSucceeded)
        base.acceptOnce("sensors-into", self.handleBadTest)
        self.movementIval.start()

    def handleBadTest(self, entry):
        print "Failed"
        base.ignore("sensors-into")
        base.ignore("sensors-out")
        base.ignore(self.movementIval.getDoneEvent())
        self.movementIval.pause()
        self.movementIval = None
        self.testNextWayPoint()

    def currentTestSucceeded(self):
        print "Passed"
        base.ignore("sensors-into")
        base.ignore("sensors-out")
        base.ignore(self.movementIval.getDoneEvent())
        self.finalList.append(self.currentWayPointTestKey)
        self.testNextWayPoint()

class WayPointTests:

    def __init__(self):
        self.finalDict = {}
        self.wayPointsToTest = dict(CIGlobals.SuitSpawnPoints[CIGlobals.DonaldsDock])
        self.numberOfTests = -1
        self.currentWayPointTestKey = None
        self.currentTest = None
        print "Starting waypoint tests..."
        self.testNextWayPoint()

    def testNextWayPoint(self):
        self.numberOfTests += 1
        if self.numberOfTests > len(self.wayPointsToTest.keys()) - 1:
            self.done()
            return
        print "Test number: " + str(self.numberOfTests)
        self.currentWayPointTestKey = self.wayPointsToTest.keys()[self.numberOfTests]
        point = self.wayPointsToTest[self.currentWayPointTestKey]
        self.currentTest = WayPointTest(point, self.currentWayPointTestKey)
        taskMgr.add(self.watchTestStatus, "watchCurrentTestStatus")

    def watchTestStatus(self, task):
        if self.currentTest.allTestsDone == True:
            self.finalDict[self.currentWayPointTestKey] = self.currentTest.finalList
            self.currentTest = None
            self.testNextWayPoint()
            return task.done
        return task.cont

    def done(self):
        open("dd_suit_accessible_waypoints.py", "w").write(str(self.finalDict))
        print "Completed!"
        sys.exit()

WayPointTests()



from lib.coginvasion.minigame import CogGuardGlobals as CGG
from lib.coginvasion.npc.NPCWalker import *
import random

cog = Suit()
cog.generateSuit("A", "mrhollywood", "s", 132, 0, False)
#cog.setName("Mr. Hollywood", "mrhollywood")
#cog.setupNameTag()
cog.loop('neutral')
cog.reparentTo(render)

def findClosestWayPoint(pos, returnId = False):
    distances = {}
    shortestDistance = 999
    closestPoint = None
    for waypoint in CGG.FactoryWalkPoints:
        id = waypoint
        waypoint = CGG.FactoryWalkPoints[waypoint]
        distance = (pos - waypoint).length()
        distances.update({id : [id, distance]})
    for distance in distances:
        distance = distances[distance]
        if distance[1] < shortestDistance:
            shortestDistance = distance[1]
            closestPoint = distance[0]
    if shortestDistance != 999 and closestPoint:
        print "Closest Waypoint: %s. Shortest distance: %s." % (closestPoint, shortestDistance)
        if not returnId:
            return CGG.FactoryWalkPoints[closestPoint]
        else:
            return [closestPoint, CGG.FactoryWalkPoints[closestPoint]]
    else:
        return None
def findPath(graph, start, end):
    Method to determine if a pair of vertices are connected using BFS

   Args:
     start, end: vertices for the traversal.

   Returns:
     [start, v1, v2, ... end]

        doesnt check for distance
    path = []
    q = deque()
    q.append(start)
    while len(q):
      tmp_vertex = q.popleft()
      if tmp_vertex not in path:
        path.append(tmp_vertex)

      if tmp_vertex == end:
        return path

      for vertex in graph[tmp_vertex]:
        if vertex not in path:
          q.append(vertex)
    return path

closestWalkPoint = findClosestWayPoint(cog.getPos(render), returnId = True)
destination = CGG.FactoryGuardPoints['1'][0]
farthestWalkPoint = findClosestWayPoint(destination, returnId = True)

path = findPath(CGG.FactoryWayPointData, closestWalkPoint[0], farthestWalkPoint[0])
print path


class CogFactoryWander:

    def __init__(self, cog, currentWayPoint = None, lastWayPoint = None, path = None):
        self.cog = cog
        self.walkIval = None
        self.currentWayPoint = currentWayPoint
        self.lastWayPoint = lastWayPoint
        self.path = path

    def startWandering(self):
        if not self.currentWayPoint:
            self.currentWayPoint = self.path[0]
        else:
            self.lastWayPoint = self.currentWayPoint
            self.currentWayPoint = self.path[self.path.index(self.currentWayPoint) + 1]
        self.walkIval = NPCWalkInterval(self.cog, CGG.FactoryWalkPoints[self.currentWayPoint], 0.1, startPos = self.cog.getPos(render))
        self.walkIval.setDoneEvent('wanderIvalDone')
        self.walkIval.start()
        self.cog.animFSM.request('walk')
        base.acceptOnce(self.walkIval.getDoneEvent(), self.wanderFinished)

    def wanderFinished(self):
        self.cog.animFSM.request('neutral')
        self.wanderAgain()

    def wanderAgain(self):
        if self.walkIval:
            self.walkIval.pause()
            self.walkIval = None
        newWayPoint = self.path[self.path.index(self.currentWayPoint) + 1]
        print "Old way point: " + str(self.currentWayPoint)
        print "New way point: " + newWayPoint
        self.walkIval = NPCWalkInterval(self.cog, CGG.FactoryWalkPoints[newWayPoint], 0.1, startPos = self.cog.getPos(render))
        self.walkIval.setDoneEvent('wanderIvalDone')
        self.walkIval.start()
        self.lastWayPoint = self.currentWayPoint
        self.currentWayPoint = newWayPoint
        self.cog.animFSM.request('walk')
        base.acceptOnce(self.walkIval.getDoneEvent(), self.wanderFinished)
#wander = CogFactoryWander(cog, path = path)
#wander.startWandering()

class CogPathFinder:

    def __init__(self, cog, destinationHpr = None):
        self.cog = cog
        self.destinationHpr = destinationHpr
        self.closestPointToDest = None
        self.walkIval = None
        self.pathsVisited = []
        self.pathIndex = 0
        self.walk()

    def findPath(self):
        endPoint = base.the_path[self.pathIndex]
        startPoint = base.the_path[self.pathIndex - 1]

        return [endPoint, startPoint]

    def walk(self):
        self.pathIndex += 1
        if len(base.the_path) <= self.pathIndex:
            print "You have arrived!"
            self.cog.setHpr(self.destinationHpr)
            self.cog.loop("neutral")
            return None
        endPoint, startPoint = self.findPath()
        #if not self.isValidPath(point):
        #	del distanceDict[point]
        #	point = random.choice(distanceDict.keys())
        self.walkIval = NPCWalkInterval(self.cog, endPoint, 0.15, startPos = startPoint)
        self.walkIval.setDoneEvent('walkDone')
        base.acceptOnce("walkDone", self.walk)
        self.walkIval.start()
        self.cog.loop('walk')
        self.currentPoint = endPoint

    def walkToDestination(self):
        self.walkIval = NPCWalkInterval(self.cog, self.destination, 0.04, startPos = self.cog.getPos(render))
        self.walkIval.setDoneEvent("walkToDestDone")
        base.acceptOnce("walkToDestDone", self.handleWalkToDestDone)
        self.walkIval.start()
        self.cog.animFSM.request('walk')

    def handleWalkToDestDone(self):
        self.cog.animFSM.request('neutral')
        if self.destinationHpr:
            self.cog.setHpr(self.destinationHpr)

    def handleWalkDone(self):
        self.pathsVisited.append(self.currentPoint)
        if self.currentPoint == self.closestPointToDest:
            print "You, have arrived!"
            self.walkToDestination()
        else:
            print "Turn to your next waypoint, in 0 feet."
            self.walk()


#render.setTwoSided(True)

class Node:

    def __init__(self, g_cost, h_cost, key, point):
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.key = key
        self.point = point
        self.parent = None

def get_distance(point1, point2):
    return (point1 - point2).length()

import time

def get_path(start_key, target_key):
    path = []

    for node in nodes:
        if node.key == start_key:
            start_node = node
        elif node.key == target_key:
            target_node = node

    current_node = target_node
    while (current_node != start_node)::
        print current_node.key
        path.append(current_node.point)
        current_node = current_node.parent
    path.append(start_point)
    return list(reversed(path))

start_key = '1'
start_point = CGG.FactoryWalkPoints[start_key]
target_key = '24'
target_point = CGG.FactoryWalkPoints[target_key]

nodes = []
open_nodes = []
closed_nodes = []

for key, point in CGG.FactoryWalkPoints.items():
    g_cost = get_distance(point, start_point)
    h_cost = get_distance(point, target_point)
    node = Node(g_cost, h_cost, key, point)
    nodes.append(node)

for node in nodes:
    if node.key == start_key:
        open_nodes.append(node)

while len(open_nodes):
    f_cost_list = []
    for node in open_nodes:
        f_cost_list.append(node.f_cost)

    lowest_f_cost = min(f_cost_list)

    current = None
    for node in open_nodes:
        if lowest_f_cost == node.f_cost:
            current = node

    open_nodes.remove(current)
    closed_nodes.append(current)

    print current.key

    if current.key == target_key:
        #print current.parent
        print "Path found from checkpoint {0} to checkpoint {1}".format(start_key, target_key)
        base.the_path = get_path(start_key, target_key)
        print base.the_path
        #print "-------------------------------------------"
        #for node in open_nodes:
        #    print node.key
        break

    neighbor_keys = CGG.FactoryWayPointData[current.key]
    for neighbor_key in neighbor_keys:
        neighbor = None
        isClosed = False
        for node in closed_nodes:
            if node.key == neighbor_key:
                isClosed = True
                break
        if isClosed:
            continue
        for node in nodes:
            if node.key == neighbor_key:
                neighbor = node
                break
        nm_cost_2_neighbor = current.g_cost + get_distance(current.point, neighbor.point)
        if (not neighbor in open_nodes) or \
        (nm_cost_2_neighbor < neighbor.g_cost):
            neighbor.g_cost = nm_cost_2_neighbor
            neighbor.h_cost = get_distance(neighbor.point, target_point)
            neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
            print "setting parent of %s to %s" % (neighbor.key, current.key)
            neighbor.parent = current
            if not neighbor in open_nodes:
                open_nodes.append(neighbor)

path = CogPathFinder(cog, CGG.FactoryGuardPoints['1'][1])

base.disableMouse()

def watchCog(task):
    camera.setPos(cog.getPos(render) + (0, -20, 10))
    return task.again

taskMgr.add(watchCog, "watchCog")
"""

b = Suit()
b.generateSuit("B", "bloodsucker", "l", 132, 0, False)
#cog.setName("Mr. Hollywood", "mrhollywood")
#cog.setupNameTag()
b.pose('win', 15)
b.reparentTo(render)
b.place()
"""
r = Suit()
r.generateSuit("A", "robberbaron", "m", 132, 0, False)
#cog.setName("Mr. Hollywood", "mrhollywood")
#cog.setupNameTag()
r.pose('glower', 20)
r.reparentTo(render)
r.setPosHpr(0, 106.78, -25.10, 206.57, 0, 0)

world = loader.loadModel('phase_9/models/cogHQ/SellbotHQExterior.bam')
world.reparentTo(base.render)
world.setPos(0, 227.09, -25.36)
sky = loader.loadModel('phase_9/models/cogHQ/cog_sky.bam')
sky.setScale(1)
sky.reparentTo(base.render)
sky.find('**/InnerGroup').removeNode()
fog = Fog('charSelectFog')
fog.setColor(0.2, 0.2, 0.2)
fog.setExpDensity(0.003)
"""
#base.disableMouse()
render.setAntialias(AntialiasAttrib.MMultisample)

for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(16)
			except:
				pass
	except:
		continue

base.camLens.setMinFov(70.0 / (4./3.))
#base.startDirect()
base.oobe()
base.run()
