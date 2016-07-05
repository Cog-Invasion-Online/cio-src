"""
  
  Filename: TTCHood.py
  Created by: blach (19June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.SkyUtil import SkyUtil
from lib.coginvasion.dna.DNAParser import *
from direct.actor.Actor import *

from panda3d.core import TransparencyAttrib, BitMask32, AmbientLight, VBase4
from panda3d.core import Fog, NodePath

from direct.interval.IntervalGlobal import LerpColorInterval, LerpFunc, Sequence
from direct.interval.IntervalGlobal import Wait, Func

import random

class TTCHood:
    
    def __init__(self, cr):
        self.cr = cr
        self.dnaStore = DNAStorage()
        self.isLoaded = 0
        self.suitEffectEnabled = False
        self.amblight = None
        self.ambNode = None
        self.sky = None
        self.skyTrack = None
        self.skySeq = None
        self.lightTrack = None
        self.skyUtil = SkyUtil()
        
    def createHood(self, loadStorage = 1, AI = 0):
        if loadStorage:
            loadDNAFile(self.dnaStore, "phase_4/dna/storage.dna")
            loadDNAFile(self.dnaStore, "phase_4/dna/storage_TT.dna")
            loadDNAFile(self.dnaStore, "phase_4/dna/storage_TT_sz.dna")
            loadDNAFile(self.dnaStore, "phase_5/dna/storage_town.dna")
            loadDNAFile(self.dnaStore, "phase_5/dna/storage_TT_town.dna")
        self.node = loadDNAFile(self.dnaStore, "phase_4/dna/toontown_central_sz.dna")
        if self.node.getNumParents() == 1:
            self.geom = NodePath(self.node.getParent(0))
            self.geom.reparentTo(hidden)
        else:
            self.geom = hidden.attachNewNode(self.node)
        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)
        self.geom.setName('toontown_central')
        
        self.geom.find('**/hill').setTransparency(TransparencyAttrib.MBinary, 1)
        self.createSky("tt")
        base.hoodBGM = base.loadMusic("phase_4/audio/bgm/TC_nbrhood.ogg")
        base.hoodBGM.setVolume(0.25)
        base.hoodBGM.setLoop(True)
        base.hoodBGM.play()
        
        self.clerk_node = render.attach_new_node('clerk_node')
        self.clerk_node.set_pos(-80, -85.57, 0.5)
        self.clerk_node.set_h(165.07)
        
        self.geom.find('**/toontown_central').setCollideMask(BitMask32.allOff())
        self.geom.find('**/coll_sidewalk').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/collision_1').node().setIntoCollideMask(CIGlobals.WallBitmask)
        self.geom.find('**/coll_mainFoolr').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/left_ear').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/right_ear').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_bridge_floor').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_bridge').node().setIntoCollideMask(CIGlobals.WallBitmask)
        self.geom.find('**/coll_r_stair').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_l_stair_2').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_l_stairend_1').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_r_satirend_1').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_plaza').node().setIntoCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/coll_hedges').node().setIntoCollideMask(CIGlobals.WallBitmask)
        
        self.coll_list = ['coll_sidewalk', 'collision_1', 'coll_mainFoolr', 'left_ear', 'right_ear', 'coll_bridge_floor', 'coll_bridge', 'coll_r_stair',
                        'coll_l_stair_2', 'coll_l_stairend_1', 'coll_r_stairend_1', 'coll_plaza', 'coll_hedges']
        self.geom.reparentTo(render)
        
        self.telescope = Actor(self.geom.find('**/*animated_prop_HQTelescopeAnimatedProp*'),
                            {"chan": "phase_3.5/models/props/HQ_telescope-chan.bam"}, copy=0)
        self.telescope.reparentTo(self.geom.find('**/*toon_landmark_hqTT*'))
        self.createLights(1, 1, 1)
        
        #if AI:
        #    self.createTrolley()
        
        taskMgr.add(self.telescopeTask, "telescopeTask")
        self.isLoaded = 1
        messenger.send("loadedHood")
        
    def createLights(self, r, g, b, startColor=1, fade=0):
        self.deleteLights()
        self.amblight = AmbientLight("amblight")
        self.amblight.setColor(VBase4(r, g, b, 1))
        self.ambNode = render.attachNewNode(self.amblight)
        render.setLight(self.ambNode)
        if fade:
            self.lightTrack = LerpFunc(self.setLightColor,
                                fromData=startColor,
                                toData=r,
                                duration=2.5,
                                blendType="easeInOut")
            self.lightTrack.start()
            self.skyTrack = LerpColorInterval(self.sky,
                                        color=VBase4(r + 0.4, g + 0.4, b + 0.4, 1.0),
                                        startColor=VBase4(startColor, startColor, startColor, 1.0),
                                        duration=1.5)
            self.skyTrack.start()
            sky = "tt"
            if r < 0.6:
                sky = "br"
            self.skySeq = Sequence(Wait(1.5), Func(self.createSky, sky))
            self.skySeq.start()
            
    def createSky(self, sky):
        self.deleteSky()
        skyPath = "phase_3.5/models/props/" + sky.upper() + "_sky.bam"
        self.sky = loader.loadModel(skyPath)
        self.sky.reparentTo(self.geom)
        self.sky.setPos(9.15527e-005, -1.90735e-006, 2.6226e-006)
        self.sky.setH(-90)
        if sky == "tt":
            self.skyUtil.startSky(self.sky)
            
    def deleteSky(self):
        self.skyUtil.stopSky()
        if self.sky:
            self.sky.removeNode()
            self.sky = None
        if self.lightTrack:
            self.lightTrack.pause()
            self.lightTrack = None
        if self.skyTrack:
            self.skyTrack.pause()
            self.skyTrack = None
        if self.skySeq:
            self.skySeq.pause()
            self.skySeq = None
            
    def setLightColor(self, color):
        self.amblight.setColor(VBase4(color, color, color, 1))
        
    def deleteLights(self):
        if self.ambNode:
            render.clearLight(self.ambNode)
            self.ambNode.removeNode()
            self.ambNode = None
        
    def telescopeTask(self, task):
        if not self.isLoaded:
            return task.done
        self.telescope.play("chan")
        task.delayTime = 12
        return task.again
        
    def enableSuitEffect(self, size):
        self.createLights(0.4, 0.4, 0.4, startColor=1, fade=1)
        
        self.fogNode = Fog("fog")
        self.fogNode.setColor(0.3, 0.3, 0.3)
        self.fogNode.setExpDensity(0.0025)
        render.setFog(self.fogNode)
        
        base.hoodBGM.stop()
        song = random.randint(1, 4)
        base.hoodBGM = base.loadMusic("phase_3.5/audio/bgm/encntr_general_bg.ogg")
        base.hoodBGM.setVolume(0.7)
        base.hoodBGM.setLoop(True)
        base.hoodBGM.play()
        
        self.suitEffectEnabled = True
        
    def bossSpawned(self):
        base.hoodBGM.stop()
        base.hoodBGM = base.loadMusic("phase_7/audio/bgm/encntr_suit_winning_indoor.ogg")
        base.hoodBGM.setVolume(0.7)
        base.hoodBGM.setLoop(True)
        Sequence(Wait(0.5), Func(base.hoodBGM.play)).start()
        
    def disableSuitEffect(self):
        self.createLights(1, 1, 1)
        self.createSky("tt")
        #render.clearFog()
        
        base.hoodBGM.stop()
        base.hoodBGM = base.loadMusic("phase_4/audio/bgm/TC_nbrhood.ogg")
        base.hoodBGM.setVolume(0.25)
        base.hoodBGM.setLoop(True)
        base.hoodBGM.play()
        
        self.suitEffectEnabled = False
        
    def unloadHood(self):
        self.isLoaded = 0
        if self.suitEffectEnabled:
            self.disableSuitEffect()
        self.deleteSky()
        self.deleteLights()
        self.geom.remove()
        self.clerk_node.remove_node()
        base.hoodBGM.stop()