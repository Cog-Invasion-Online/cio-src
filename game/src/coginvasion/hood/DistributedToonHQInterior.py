"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedToonHQInterior.py
@author Brian Lach
@date July 29, 2015

"""

from panda3d.core import ModelNode, NodePath, Point3, CardMaker, \
    TransparencyAttrib, TextNode

from libpandadna import *

from src.coginvasion.globals import CIGlobals
import DistributedToonInterior
import ToonInteriorColors
import ZoneUtil

"""
from datetime import datetime
from pytz import timezone
import time"""
import random

class DistributedToonHQInterior(DistributedToonInterior.DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.ilc.lights = [[(-40, 30, 8.5), 0.3], [(24, 30, 8.5), 0.3],
                           [(-5.25, -5, 8.5), 0.3], [(-5.25, 65, 8.5), 0.3]]
        self.buildData = None
        self.ttTimePath = None
        self.clockTaskName = None
        self.lastFlickerMsTime = None
        self.inFlicker = False
        self.currentBuild = None
        self.buildDate = None
        self.crashedPiano = None
        self.logoNode = None
        self.logoImg = None

    def makeInterior(self):
        self.dnaStore = self.cr.playGame.dnaStore
        self.generator = random.Random()
        self.generator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_3.5/models/modules/HQ_interior.bam')
        self.interior.reparentTo(render)
        self.colors = ToonInteriorColors.colors[ZoneUtil.ToontownCentral]
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        color = self.generator.choice(self.colors['TI_door'])
        doorOrigins = render.findAllMatches('**/door_origin*')
        numDoorOrigins = doorOrigins.getNumPaths()

        for npIndex in xrange(numDoorOrigins):
            # Let's not generate the secondary door for the TTC playground interior.
            if npIndex == 0 or (npIndex == 1 and not self.zoneId == 2520):
                doorOrigin = doorOrigins[npIndex]
                doorOriginNPName = doorOrigin.getName()
                doorOriginIndexStr = doorOriginNPName[len('door_origin_'):]
                newNode = ModelNode('door_' + doorOriginIndexStr)
                newNodePath = NodePath(newNode)
                newNodePath.reparentTo(self.interior)
                doorNP = door.copyTo(newNodePath)
                doorOrigin.setScale(0.8, 0.8, 0.8)
                doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
                doorColor = self.generator.choice(self.colors['TI_door'])
                triggerId = str(self.block) + '0' + doorOriginIndexStr
                triggerId = int(triggerId)
                DNADoor.setupDoor(doorNP, newNodePath, doorOrigin, self.dnaStore, triggerId, doorColor)
                doorFrame = doorNP.find('door_*_flat')
                doorFrame.setColor(doorColor)
        del self.dnaStore
        del self.colors
        del self.generator
        
        if self.zoneId == 2520:
            # The interior of the TTC playground HQ needs to be populated with this so it doesn't
            # look so bland. 
            self.crashedPiano = loader.loadModel('phase_6/models/props/piano.bam')
            self.crashedPiano.reparentTo(self.interior)
            self.crashedPiano.setPosHpr(1.62019231, 66.6371124268, 0.0250000003725, -46.400062561, 0.0, 0.0)
            
            # This is the ceiling crack above the crashed piano.
            crack = self.crashedPiano.find('**/shadow_crack').copyTo(self.crashedPiano)
            crack.setZ(21.425)
            crack.setTwoSided(1)
        
        self.generateBuildDataBoard(self.interior.find('**/empty_board').getChild(0))
        self.interior.flattenMedium()
        
    def generateBuildDataBoard(self, parent):
        self.buildData = hidden.attachNewNode('buildData')
        self.buildData.setPosHprScale(0.0, 0, 4.5, 90, 0, 0, 0.9, 0.9, 0.9)
        self.buildData.setDepthOffset(1)
        
        self.logoNode, self.logoImg = CIGlobals.getLogoImage(self.buildData, 12, (0, 0, -3.15))
        
        # Let's generate the Toontown Time textnode.
        _, self.ttTimePath = self.__generateTextNodeAndNodePath('toontownTimeText', 
            'Toontown Time: Disabled')
        self.ttTimePath.reparentTo(self.buildData)
        self.ttTimePath.setScale(0.85)
        self.ttTimePath.setZ(-8.0)
        
        # Let's generate the Build Version text node.
        _, self.currentBuild = self.__generateTextNodeAndNodePath('currentBuildVersion', 'Current Build: {0} v{1}'
            .format(game.build, game.version))
        self.currentBuild.reparentTo(self.buildData)
        self.currentBuild.setScale(0.75)
        self.currentBuild.setZ(-9.25)
        
        # Let's generate the Build Date text node
        _, self.buildDate = self.__generateTextNodeAndNodePath('currentBuildDate', 'Build Date: {0}'.format(game.builddate))
        self.buildDate.reparentTo(self.buildData)
        self.buildDate.setScale(0.75)
        self.buildDate.setZ(-10.25)
        
        self.buildData.reparentTo(parent)
        
        # Let's begin our clock task.
        """
        self.clockTaskName = self.uniqueName('ESTClock')
        self.lastFlickerMsTime = int(round(time.time() * 1000))
        base.taskMgr.doMethodLater(0.25, self.__updateTime, self.clockTaskName)
        """
        
    def __generateTextNodeAndNodePath(self, nodeName, text):
        """ Constructs a TextNode and a NodePath pair """
        node = TextNode(nodeName)
        node.setFont(CIGlobals.getToonFont())
        node.setAlign(TextNode.ACenter)
        node.setTextColor(1, 1, 1, 0.7)
        node.setText(text)
        
        nodepath = hidden.attachNewNode(node)
        return node, nodepath
    
    """
    def __updateTime(self, task):
        curTime = self.getToontownTime()
        now = int(round(time.time() * 1000))

        if self.inFlicker:
            curTime = curTime[:curTime.index(':')] + ' ' + curTime[curTime.index(':')+1:]
            self.ttTimePath.node().setText('Toontown Time: ' + curTime)
        else:
            self.ttTimePath.node().setText('Toontown Time: ' + curTime)

        if (now - self.lastFlickerMsTime) >= 1000:
            self.lastFlickerMsTime = now
            self.inFlicker = (not self.inFlicker)
        return task.cont
        
    def getToontownTime(self):
        eastern = timezone('US/Eastern')
        return datetime.now(eastern).strftime('%I:%M %p')
    """
    
    def disable(self):
        DistributedToonInterior.DistributedToonInterior.disable(self)
        
        if self.logoImg:
            self.logoImg.destroy()
        self.logoImg = None
        if self.logoNode:
            self.logoNode.removeNode()
        self.logoNode = None
        
        if self.clockTaskName:
            base.taskMgr.remove(self.clockTaskName)
            
        if self.ttTimePath:
            self.ttTimePath.removeNode()
            
        if self.currentBuild:
            self.currentBuild.removeNode()
            
        if self.buildDate:
            self.buildDate.removeNode()
        
        if self.buildData:
            self.buildData.removeNode()
            
        if self.crashedPiano:
            self.crashedPiano.removeNode()
            
        del self.clockTaskName
        del self.ttTimePath
        del self.lastFlickerMsTime
        del self.inFlicker
        del self.currentBuild
        del self.buildDate
        del self.buildData
        del self.crashedPiano
        