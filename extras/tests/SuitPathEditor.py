# Filename: SuitPathEditor.py
# Created by:  blach (27Dec15)

from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'window-title Suit Path Editor')
loadPrcFileData('', 'cursor-filename none')
loadPrcFileData('', 'framebuffer-multisample 0')

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()

from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.controls.ControlManager import CollisionHandlerRayStart
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval

import yaml, os

base.cTrav = CollisionTraverser()

defaultDNA = ['phase_4/dna/storage.pdna', 'phase_5/dna/storage_town.pdna']

areas = {
    CIGlobals.ToontownCentral: ['phase_4/dna/storage_TT.pdna', 'phase_4/dna/storage_TT_sz.pdna', 'phase_4/dna/cog_toontown_central_sz.pdna'],
    CIGlobals.DonaldsDock: ['phase_6/dna/storage_DD.pdna', 'phase_6/dna/storage_DD_sz.pdna', 'phase_6/dna/donalds_dock_dz.pdna'],
    CIGlobals.DonaldsDreamland: ['phase_8/dna/storage_DL.pdna', 'phase_8/dna/storage_DL_sz.pdna', 'phase_8/dna/donalds_dreamland_sz.pdna'],
    CIGlobals.TheBrrrgh: ['phase_8/dna/storage_BR.pdna', 'phase_8/dna/storage_BR_sz.pdna', 'phase_8/dna/the_burrrgh_sz.pdna']
}

allocator = UniqueIdAllocator(1, 5000)

class Waypoint(NodePath):
    
    def __init__(self):
        NodePath.__init__(self, 'waypoint')
        self.id = allocator.allocate()
        self.neighbors = []
        self.visual = loader.loadModel('models/smiley')
        self.visual.reparentTo(self)
        sphere = CollisionSphere(0, 0, 0, 1.5)
        sphere.setTangible(0)
        node = CollisionNode('collnode')
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.collNP = self.attachNewNode(node)
        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        cRayNode = CollisionNode('pointray')
        cRayNode.addSolid(cRay)
        cRayNodePath = self.attachNewNode(cRayNode)
        cRayBitMask = CIGlobals.FloorBitmask
        cRayNode.setFromCollideMask(cRayBitMask)
        cRayNode.setIntoCollideMask(BitMask32.allOff())
        lifter = CollisionHandlerFloor()
        lifter.addCollider(cRayNodePath, self)
        base.cTrav.addCollider(cRayNodePath, lifter)
        self.reparentTo(render)
        self.setPythonTag('waypoint', self)
        
    def addNeighbor(self, waypoint):
        self.neighbors.append(waypoint)
        
    def removeNeighbor(self, waypoint):
        self.neighbors.remove(waypoint)

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
        
class WayPointTest:

    def __init__(self, point, number, wayPointsToTest):
        self.point = point
        self.number = number
        self.wayPointsToTest = wayPointsToTest
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
        self.movementIval = NPCWalkInterval(node, Point3(*self.wayPointsToTest[self.currentWayPointTestKey]['pos']),
            0.005, startPos = self.point, fluid = 1)
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
        print self.finalList
        self.testNextWayPoint()

class WayPointTests:

    def __init__(self, wayPointsToTest):
        self.finalDict = {}
        self.wayPointsToTest = wayPointsToTest
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
        point = Point3(*self.wayPointsToTest[self.currentWayPointTestKey]['pos'])
        self.currentTest = WayPointTest(point, self.currentWayPointTestKey, self.wayPointsToTest)
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

class SuitPathEditor(FSM):
    
    def __init__(self):
        FSM.__init__(self, 'SuitPathEditor')
        self.dnaStore = DNAStorage()
        self.waypoints = []
        self.lineSeg2Neighbors = {}
        self.selectedWaypoint = None
        self.geom = None
        self.area = None
        self.mode = None
        self.smileysHidden = False
        self.yamlData = None
    
    def enterChooseArea(self):
        self.title = OnscreenText(text = 'Choose Area To Edit', pos = (0, 0.9), fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1))
        self.scrolledList = DirectScrolledList(decButton_pos = (0.35, 0, 0.53),
            decButton_text = "Up",
            decButton_text_scale = 0.04,
            decButton_borderWidth = (0.005, 0.005),
            
            incButton_pos = (0.35, 0, -0.02),
            incButton_text = "Down",
            incButton_text_scale = 0.04,
            incButton_borderWidth = (0.005, 0.005),
            
            frameSize = (0.0, 0.7, -0.05, 0.59),
            frameColor = (1, 0, 0, 0.5),
            pos = (-0.5, 0, -0.4),
            numItemsVisible = 6,
            forceHeight = 0.05,
            itemFrame_frameSize = (-0.2, 0.2, -0.37, 0.11),
            itemFrame_pos = (0.35, 0, 0.4),
            scale = 1.5
        )
        for areaName in areas.keys():
            btn = DirectButton(text = areaName, scale = 0.04, command = self.request, extraArgs = ['ChooseMode', areaName])
            self.scrolledList.addItem(btn)
        
    def exitChooseArea(self):
        self.title.destroy()
        del self.title
        self.scrolledList.destroy()
        del self.scrolledList
        
    def enterChooseMode(self, areaName):
        self.area = areaName
        self.title = OnscreenText(text = "Test or Edit?", pos = (0, 0.9), fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1))
        self.test = DirectButton(text = "Test", scale = 0.08, pos = (-0.1, 0, 0), command = self.request, extraArgs = ['LoadArea', 0])
        self.edit = DirectButton(text = "Edit", scale = 0.08, pos = (0.1, 0, 0), command = self.request, extraArgs = ['LoadArea', 1])
        
    def exitChooseMode(self):
        self.title.destroy()
        del self.title
        self.test.destroy()
        del self.test
        self.edit.destroy()
        del self.edit
        
    def enterLoadArea(self, mode):
        self.mode = mode
        print 'Loading area: {0}'.format(self.area)
        self.title = OnscreenText(text = "Loading {0}...".format(self.area), pos = (0, 0), fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1))
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        for dnaFile in defaultDNA:
            loadDNAFile(self.dnaStore, dnaFile)
        for i in xrange(len(areas[self.area])):
            dnaFile = areas[self.area][i]
            if i == len(areas[self.area]) - 1:
                node = loadDNAFile(self.dnaStore, dnaFile)
                if node.getNumParents() == 1:
                    geom = NodePath(node.getParent(0))
                    geom.reparentTo(hidden)
                else:
                    geom = hidden.attachNewNode(node)
                gsg = base.win.getGsg()
                if gsg:
                    geom.prepareScene(gsg)
                geom.setName('area_top_level')
                self.geom = geom
            else:
                loadDNAFile(self.dnaStore, dnaFile)
        if os.path.exists(self.getFileName()):
            with open(self.getFileName(), 'r') as stream:
                data = yaml.load(stream)
                self.yamlData = data
                for waypointId, waypointData in data.items():
                    waypoint = Waypoint()
                    x, y, z = data[waypointId]['pos']
                    pos = Point3(x, y, z)
                    waypoint.setPos(pos)
                    self.waypoints.append(waypoint)
                stream.close()
        if self.mode == 0:
            self.demand('Test')
        elif self.mode == 1:
            self.demand('Edit')
        
    def exitLoadArea(self):
        self.title.destroy()
        del self.title
        
    def enterTest(self):
        self.toggleSmileys()
        for waypoint in self.waypoints:
            waypoint.removeNode()
        self.geom.reparentTo(render)
        WayPointTests(self.yamlData)
        
    def exitTest(self):
        pass
        
    def getFileName(self):
        fileName = self.area.lower()
        fileName = fileName.replace(' ', '_')
        fileName = fileName.replace("'", '')
        fileName += '.yaml'
        return fileName
        
    def enterEdit(self):
        self.geom.reparentTo(render)
        self.shooterTrav = CollisionTraverser('SuitPathEditor.shooterTrav')
        ray = CollisionRay()
        rayNode = CollisionNode('SuitPathEditor.rayNode')
        rayNode.addSolid(ray)
        rayNode.setCollideMask(BitMask32(0))
        rayNode.setFromCollideMask(CIGlobals.WallBitmask)
        self.shooterRay = ray
        self.shooterRayNode = base.camera.attachNewNode(rayNode)
        self.shooterHandler = CollisionHandlerQueue()
        self.shooterTrav.addCollider(self.shooterRayNode, self.shooterHandler)
        base.accept('mouse1-up', self.maybeSelect)
        base.accept('mouse3-up', self.maybeMakeNeighbor)
        base.accept('p', self.makeWaypoint)
        base.accept('arrow_up', self.moveSelectedPoint, [0])
        base.accept('arrow_down', self.moveSelectedPoint, [1])
        base.accept('arrow_left', self.moveSelectedPoint, [2])
        base.accept('arrow_right', self.moveSelectedPoint, [3])
        base.accept('control-s', self.save)
        base.accept('h', self.toggleSmileys)
        
    def toggleSmileys(self):
        for waypoint in self.waypoints:
            if self.smileysHidden:
                waypoint.show()
            else:
                waypoint.hide()
        self.smileysHidden = not self.smileysHidden
        
    def save(self):
        fileName = self.getFileName()
        print "Saving to: " + fileName
        data = {}
        for waypoint in self.waypoints:
            data.update({waypoint.id: {'pos': 0, 'neighbors': []}})
            x, y, z = waypoint.getPos(render)
            data[waypoint.id]['pos'] = [x, y, z]
            data[waypoint.id]['neighbors'] = []
            for neighbor in waypoint.neighbors:
                data[waypoint.id]['neighbors'].append(neighbor.id)
        with open(fileName, 'w') as stream:
            stream.write(yaml.dump(data))
            stream.flush()
            stream.close()
        
    def moveSelectedPoint(self, direction):
        if self.selectedWaypoint is not None:
            if direction == 0:
                self.selectedWaypoint.setY(self.selectedWaypoint, 5)
            elif direction == 1:
                self.selectedWaypoint.setY(self.selectedWaypoint, -5)
            elif direction == 2:
                self.selectedWaypoint.setX(self.selectedWaypoint, -5)
            elif direction == 3:
                self.selectedWaypoint.setX(self.selectedWaypoint, 5)
        
    def makeWaypoint(self):
        waypoint = Waypoint()
        if self.selectedWaypoint is not None:
            waypoint.setPos(self.selectedWaypoint.getPos(render))
        else:
            waypoint.setPos(0, 0, 0)
        self.waypoints.append(waypoint)
        self.selectWaypoint(waypoint)
        
    def makeNeighbor(self, waypoint):
        if self.selectedWaypoint is None:
            return
        if waypoint not in self.selectedWaypoint.neighbors:
            # Make them neighbors and make the visualization.
            waypoint.addNeighbor(self.selectedWaypoint)
            waypoint.setColorScale(1, 0, 0, 1)
            self.selectedWaypoint.addNeighbor(waypoint)
            lineseg = LineSegs('visualization')
            lineseg.setColor(0, 0, 1, 1)
            lineseg.setThickness(5)
            lineseg.drawTo(waypoint.getPos(render))
            lineseg.drawTo(self.selectedWaypoint.getPos(render))
            node = lineseg.create(False)
            nodePath = render.attachNewNode(node)
            self.lineSeg2Neighbors[nodePath] = [waypoint, self.selectedWaypoint]
        else:
            # Make them no longer neighbors and remove the visualization.
            waypoint.removeNeighbor(self.selectedWaypoint)
            waypoint.setColorScale(0.5, 0.5, 0.5, 1.0)
            self.selectedWaypoint.removeNeighbor(waypoint)
            for lineSeg, neighbors in self.lineSeg2Neighbors.items():
                if waypoint in neighbors and self.selectedWaypoint in neighbors:
                    lineSeg.removeNode()
                    del self.lineSeg2Neighbors[lineSeg]
                    break
        
    def selectWaypoint(self, waypoint):
        for otherWaypoint in self.waypoints:
            otherWaypoint.setColorScale(0.5, 0.5, 0.5, 1)
        for neighbor in waypoint.neighbors:
            neighbor.setColorScale(1, 0, 0, 1)
        waypoint.setColorScale(0, 0, 1, 1)
        self.selectedWaypoint = waypoint
        
    def maybeMakeNeighbor(self):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.shooterRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.shooterTrav.traverse(render)
            if self.shooterHandler.getNumEntries() > 0:
                self.shooterHandler.sortEntries()
                pickedObj = self.shooterHandler.getEntry(0).getIntoNodePath()
                pickedObj = pickedObj.getParent().getPythonTag('waypoint')
                if pickedObj:
                    if pickedObj != self.selectedWaypoint:
                        self.makeNeighbor(pickedObj)
        
    def maybeSelect(self):
        mpos = base.mouseWatcherNode.getMouse()
        self.shooterRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.shooterTrav.traverse(render)
        if self.shooterHandler.getNumEntries() > 0:
            self.shooterHandler.sortEntries()
            pickedObj = self.shooterHandler.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.getParent().getPythonTag('waypoint')
            if pickedObj:
                self.selectWaypoint(pickedObj)
        
    def exitEdit(self):
        pass
        
editor = SuitPathEditor()
editor.request('ChooseArea')

base.run()
