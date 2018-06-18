"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIBase.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import loadPrcFile, NodePath, PGTop, TextPropertiesManager, TextProperties, Vec3
from panda3d.core import CollisionHandlerFloor, CollisionHandlerQueue, CollisionHandlerPusher
from panda3d.bullet import BulletWorld, BulletDebugNode

from direct.showbase.ShowBase import ShowBase
from direct.showbase.Audio3DManager import Audio3DManager
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.filter.CommonFilters import CommonFilters

from src.coginvasion.manager.UserInputStorage import UserInputStorage
from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.ShadowCaster import ShadowCaster
from src.coginvasion.base import MusicCache
from ShakeCamera import ShakeCamera
from CubeMapManager import CubeMapManager
from WaterReflectionManager import WaterReflectionManager
from src.coginvasion.phys import PhysicsUtils

import __builtin__
import random

if game.usepipeline:
    from rpcore import RenderPipeline

class CIBase(ShowBase):
    notify = directNotify.newCategory("CIBase")

    def __init__(self):
        if game.usepipeline:
            self.pipeline = RenderPipeline()
            self.pipeline.create(self)
        else:
            ShowBase.__init__(self)

        #self.startTk()

        self.camLens.setNearFar(0.5, 10000)
        self.taskMgr.setupTaskChain('fpsIndependentStuff', numThreads = 1, frameSync = False)

        self.physicsWorld = BulletWorld()
        # Panda units are in feet, so the gravity is 32 feet per second,
        # not 9.8 meters per second.
        self.physicsWorld.setGravity(Vec3(0, 0, -32.1740))

        self.physicsWorld.setGroupCollisionFlag(7, 1, True)
        self.physicsWorld.setGroupCollisionFlag(7, 2, True)
        self.physicsWorld.setGroupCollisionFlag(7, 3, False)
        self.physicsWorld.setGroupCollisionFlag(7, 4, False)
        self.physicsWorld.setGroupCollisionFlag(7, 8, True)

        self.taskMgr.add(self.__physicsUpdate, "physicsUpdate", sort = 30)
        
        debugNode = BulletDebugNode('Debug')
        self.debugNP = render.attachNewNode(debugNode)
        self.physicsWorld.setDebugNode(self.debugNP.node())

        self.physicsDbgFlag = False
        self.setPhysicsDebug(self.config.GetBool('physics-debug', False))
            
        #self.shadowCaster = ShadowCaster(Vec3(163, -67, 0))
        #self.shadowCaster.enable()

        # Setup 3d audio                                 run before igLoop so 3d positioning doesn't lag behind
        base.audio3d = Audio3DManager(base.sfxManagerList[0], camera, taskPriority = 40)
        base.audio3d.setDropOffFactor(0.1)

        # Setup collision handlers
        base.lifter = CollisionHandlerFloor()
        base.pusher = CollisionHandlerPusher()
        base.queue = CollisionHandlerQueue()
        
        self.accept('/', self.projectShadows)

        uis = UserInputStorage()
        self.inputStore = uis
        self.userInputStorage = uis
        __builtin__.inputStore = uis
        __builtin__.userInputStorage = uis
        
        cbm = CubeMapManager()
        self.cubeMapMgr = cbm
        __builtin__.cubeMapMgr = cbm

        self.credits2d = self.render2d.attachNewNode(PGTop("credits2d"))
        self.credits2d.setScale(1.0 / self.getAspectRatio(), 1.0, 1.0)

        self.wakeWaterHeight = -30.0

        self.bloomToggle = False

        self.music = None
        self.currSongName = None

        """
        print 'TPM START'
        tpMgr = TextPropertiesManager.getGlobalPtr()
        print 'PROPERTIES GET'
        tpRed = TextProperties()
        tpRed.setTextColor(1, 0, 0, 1)
        tpSlant = TextProperties()
        tpSlant.setSlant(0.3)
        print 'RED AND SLANT GENERATED'
        tpMgr.setProperties('red', tpRed)
        print 'RED SET'
        try:
            tpMgr.setProperties('slant', tpSlant)
        except Exception:
            print 'AN EXCEPTION OCCURRED'
        print 'SLANT SET'
        print 'TPM END'
        """

    def doCamShake(self, intensity = 1.0, duration = 0.5, loop = False):
        shake = ShakeCamera(intensity, duration)
        shake.start(loop)
        return shake

    def renderFrames(self):
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()

    def prepareScene(self):
        render.prepareScene(self.win.getGsg())

    def setPhysicsDebug(self, flag):
        self.physicsDbgFlag = flag
        debugNode = self.debugNP.node()
        if flag:
            debugNode.showWireframe(True)
            debugNode.showConstraints(True)
            debugNode.showBoundingBoxes(True)
            debugNode.showNormals(False)
            self.debugNP.show()
        else:
            debugNode.showWireframe(False)
            debugNode.showConstraints(False)
            debugNode.showBoundingBoxes(False)
            debugNode.showNormals(False)
            self.debugNP.hide()

    def stopMusic(self):
        if self.music:
            self.music.stop()
            self.music = None
        self.currSongName = None

    def playMusic(self, songName, looping = True, volume = 1.0):
        if isinstance(songName, list):
            # A list of possible songs were passed in, pick a random one.
            songName = random.choice(songName)

        if songName == self.currSongName:
            # Don't replay the same song.
            return

        self.stopMusic()
        
        self.currSongName = songName

        song = MusicCache.findSong(songName)
        if not song:
            self.notify.warning("Song `{0}` not found in cache.".format(songName))
            return

        self.music = song
        self.music.setLoop(looping)
        self.music.setVolume(volume)
        self.music.play()

    def enablePhysicsNodes(self, rootNode):
        PhysicsUtils.attachBulletNodes(rootNode)

    def disablePhysicsNodes(self, rootNode):
        PhysicsUtils.detachBulletNodes(rootNode)

    def createPhysicsNodes(self, rootNode):
        PhysicsUtils.makeBulletCollFromPandaColl(rootNode)
        
    def createAndEnablePhysicsNodes(self, rootNode):
        self.createPhysicsNodes(rootNode)
        self.enablePhysicsNodes(rootNode)
        
    def removePhysicsNodes(self, rootNode):
        PhysicsUtils.removeBulletNodes(rootNode)
        
    def disableAndRemovePhysicsNodes(self, rootNode):
        PhysicsUtils.detachAndRemoveBulletNodes(rootNode)

    def __physicsUpdate(self, task):
        dt = globalClock.getDt()
        try: self.physicsWorld.doPhysics(dt, 0)
        except: pass
        return task.cont
     
    def projectShadows(self):
        #self.shadowCaster.projectShadows()
        pass

    def setBloom(self, flag):
        self.bloomToggle = flag

        if not hasattr(self, 'filters'):
            # Sanity check
            self.notify.warning("setBloom: CommonFilters not constructed")
            return

        if flag:
            self.filters.setBloom(desat = 1.0, intensity = 0.4)
        else:
            self.filters.delBloom()
        
    def initStuff(self):
        wrm = WaterReflectionManager()
        self.waterReflectionMgr = wrm
        __builtin__.waterReflectionMgr = wrm
        #self.shadowCaster.turnOnShadows()

        self.filters = CommonFilters(self.win, self.cam)
        self.setBloom(self.bloomToggle)
        
    def setCellsActive(self, cells, active):
        for cell in cells:
            cell.setActive(active)
        self.marginManager.reorganize()

    def saveCubeMap(self, namePrefix = 'cube_map_#.jpg', size = 1024):
        namePrefix = raw_input("Cube map file: ")

        base.localAvatar.stopSmooth()
        base.localAvatar.setHpr(0, 0, 0)

        # Hide all objects from our cubemap.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.hide()

        self.notify.info("Cube map position:", camera.getPos(render))

        ShowBase.saveCubeMap(self, namePrefix, size = size)

        # Reshow the objects.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.show()

        base.localAvatar.startSmooth()

    def setTimeOfDay(self, time):
        if game.usepipeline:
            self.pipeline.daytime_mgr.time = time

    def doOldToontownRatio(self):
        ShowBase.adjustWindowAspectRatio(self, 4. / 3.)
        self.credits2d.setScale(1.0 / (4. / 3.), 1.0, 1.0)

    def doRegularRatio(self):
        ShowBase.adjustWindowAspectRatio(self, self.getAspectRatio())

    def adjustWindowAspectRatio(self, aspectRatio):
        if (CIGlobals.getSettingsMgr() is None):
            ShowBase.adjustWindowAspectRatio(self, aspectRatio)
            self.credits2d.setScale(1.0 / aspectRatio, 1.0, 1.0)
            return

        if (CIGlobals.getSettingsMgr().getSetting("maspr") is True):
            # Go ahead and maintain the aspect ratio if the user wants us to.
            ShowBase.adjustWindowAspectRatio(self, aspectRatio)
            self.credits2d.setScale(1.0 / aspectRatio, 1.0, 1.0)
        else:
            # The user wants us to keep a 4:3 ratio no matter what (old toontown feels).
            self.doOldToontownRatio()

    def muteMusic(self):
        self.musicManager.setVolume(0.0)

    def unMuteMusic(self):
        self.musicManager.setVolume(CIGlobals.SettingsMgr.getSetting("musvol"))

    def muteSfx(self):
        self.sfxManagerList[0].setVolume(0.0)

    def unMuteSfx(self):
        self.sfxManagerList[0].setVolume(CIGlobals.SettingsMgr.getSetting("sfxvol"))
        
    def localAvatarReachable(self):
        # This verifies that the localAvatar hasn't been deleted and isn't none.
        return hasattr(self, 'localAvatar') and self.localAvatar
