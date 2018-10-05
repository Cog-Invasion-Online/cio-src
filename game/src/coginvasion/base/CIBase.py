"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIBase.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import loadPrcFile, NodePath, PGTop, TextPropertiesManager, TextProperties, Vec3, MemoryUsage, MemoryUsagePointers, RescaleNormalAttrib
from panda3d.core import CollisionHandlerFloor, CollisionHandlerQueue, CollisionHandlerPusher, loadPrcFileData, TexturePool, ModelPool, RenderState, Vec4, Point3
from panda3d.core import CollisionTraverser, CullBinManager
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.bsp import BSPLoader, BSPRender

from p3recastnavigation import RNNavMeshManager

from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.filter.CommonFilters import CommonFilters
from direct.gui import DirectGuiGlobals

from src.coginvasion.manager.UserInputStorage import UserInputStorage
from src.coginvasion.margins.MarginManager import MarginManager
from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.CogInvasionLoader import CogInvasionLoader
from src.coginvasion.base.ShadowCaster import ShadowCaster
from src.coginvasion.base import ScreenshotHandler
from src.coginvasion.base import MusicCache

from CIAudio3DManager import CIAudio3DManager
from ShakeCamera import ShakeCamera
from CubeMapManager import CubeMapManager
from WaterReflectionManager import WaterReflectionManager
from src.coginvasion.phys import PhysicsUtils

import __builtin__
import random

class CIBase(ShowBase):
    notify = directNotify.newCategory("CIBase")

    def __init__(self):
        if metadata.USE_RENDER_PIPELINE:
            from rpcore import RenderPipeline
            self.pipeline = RenderPipeline()
            self.pipeline.create(self)
        else:
            ShowBase.__init__(self)
            self.loader.destroy()
            self.loader = CogInvasionLoader(self)
            __builtin__.loader = self.loader
            self.graphicsEngine.setDefaultLoader(self.loader.loader)

        #self.startTk()

        render.hide()

        self.camLens.setNearFar(0.5, 10000)
        #self.taskMgr.setupTaskChain('fpsIndependentStuff', numThreads = 1, frameSync = False)

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

        self.bspLoader = BSPLoader.getGlobalPtr()
        self.bspLoader.setGamma(2.2)
        self.bspLoader.setWin(self.win)
        self.bspLoader.setCamera(self.camera)
        self.bspLoader.setRender(self.render)
        self.bspLoader.setMaterialsFile("phase_14/etc/materials.txt")
        #self.bspLoader.setTextureContentsFile("phase_14/etc/texturecontents.txt")
        self.bspLoader.setWantVisibility(True)
        self.bspLoader.setVisualizeLeafs(False)
        self.bspLoader.setWantLightmaps(True)
        self.bspLoader.setShadowCamPos(Point3(-15, 5, 40))
        self.bspLoader.setShadowResolution(60 * 2, 1024 * 1)
        self.bspLevel = None
        self.materialData = {}
        
        self.nmMgr = RNNavMeshManager.get_global_ptr()
        self.nmMgr.set_root_node_path(self.render)
        self.nmMgr.get_reference_node_path().reparentTo(self.render)
        self.nmMgr.start_default_update()
        self.nmMgr.get_reference_node_path_debug().reparentTo(self.render)
        self.navMeshNp = None

        # Setup 3d audio                                 run before igLoop so 3d positioning doesn't lag behind
        base.audio3d = CIAudio3DManager(base.sfxManagerList[0], camera, taskPriority = 40)
        base.audio3d.setDropOffFactor(0.1)

        # Setup collision handlers
        base.cTrav = CollisionTraverser()
        base.lifter = CollisionHandlerFloor()
        base.pusher = CollisionHandlerPusher()
        base.queue = CollisionHandlerQueue()

        base.lightingCfg = None
        
        #self.accept('/', self.projectShadows)
        
        # Let's setup the user input storage system
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
        
        self.avatars = []
        
        # Let's setup our margins
        base.marginManager = MarginManager()
        base.margins = aspect2d.attachNewNode(base.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        base.leftCells = [
            base.marginManager.addCell(0.1, -0.6, base.a2dTopLeft),
            base.marginManager.addCell(0.1, -1.0, base.a2dTopLeft),
            base.marginManager.addCell(0.1, -1.4, base.a2dTopLeft)
        ]
        base.bottomCells = [
            base.marginManager.addCell(0.4, 0.1, base.a2dBottomCenter),
            base.marginManager.addCell(-0.4, 0.1, base.a2dBottomCenter),
            base.marginManager.addCell(-1.0, 0.1, base.a2dBottomCenter),
            base.marginManager.addCell(1.0, 0.1, base.a2dBottomCenter)
        ]
        base.rightCells = [
            base.marginManager.addCell(-0.1, -0.6, base.a2dTopRight),
            base.marginManager.addCell(-0.1, -1.0, base.a2dTopRight),
            base.marginManager.addCell(-0.1, -1.4, base.a2dTopRight)
        ]
        
        base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
        base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
        base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
        base.mouseWatcherNode.setButtonUpPattern('button-up-%r')
        
        cbm = CullBinManager.getGlobalPtr()
        cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
        if not metadata.USE_REAL_SHADOWS:
            cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
        cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
        cbm.addBin('gsg-popup', CullBinManager.BTFixed, 70)
        self.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        self.disableMouse()
        self.enableParticles()
        base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
        base.transitions.IrisModelName = "phase_3/models/misc/iris.bam"
        base.transitions.FadeModelName = "phase_3/models/misc/fade.bam"

        self.accept(self.inputStore.TakeScreenshot, ScreenshotHandler.takeScreenshot)

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
        
    def convertHammerAngles(self, angles):
        """
        (pitch, yaw + 90, roll) -> (yaw, pitch, roll)
        """
        temp = angles[0]
        angles[0] = angles[1] - 90
        angles[1] = temp
        return angles
        
    def planPath(self, startPos, endPos):
        """Uses recast/detour to find a path from the generated nav mesh from the BSP file."""

        if not self.navMeshNp:
            return [startPos, endPos]
        result = []
        valueList = self.navMeshNp.node().path_find_follow(startPos, endPos)
        for i in xrange(valueList.get_num_values()):
            result.append(valueList.get_value(i))
        return result
        
    def getBSPLevelLightEnvironmentData(self):
        #    [has data, angles, color]
        data = [0, Vec3(0), Vec4(0)]
        
        if not self.bspLoader.hasActiveLevel():
            return data
        
        for i in xrange(self.bspLoader.getNumEntities()):
            classname = self.bspLoader.getEntityValue(i, "classname")
            if classname == "light_environment":
                data[0] = 1
                data[1] = self.convertHammerAngles(
                    self.bspLoader.getEntityValueVector(i, "angles"))
                data[2] = self.bspLoader.getEntityValueColor(i, "_light")
                break
                
        return data
        
    def cleanupNavMesh(self):
        if self.navMeshNp:
            self.navMeshNp.removeNode()
            self.navMeshNp = None
        
    def setupNavMesh(self, node):
        self.cleanupNavMesh()
        
        nmMgr = RNNavMeshManager.get_global_ptr()
        self.navMeshNp = nmMgr.create_nav_mesh()
        self.navMeshNp.node().set_owner_node_path(node)
        self.navMeshNp.node().setup()
        
        if 0:
            self.navMeshNp.node().enable_debug_drawing(self.camera)
            self.navMeshNp.node().toggle_debug_drawing(True)
        
    def setupRender(self):
        """
        Creates the render scene graph, the primary scene graph for
        rendering 3-d geometry.
        """
        ## This is the root of the 3-D scene graph.
        ## Make it a BSPRender node to automatically cull
        ## nodes against the BSP leafs if there is a loaded
        ## BSP level.
        self.render = NodePath(BSPRender('render', BSPLoader.getGlobalPtr()))
        self.render.setAttrib(RescaleNormalAttrib.makeDefault())
        self.render.setTwoSided(0)
        self.backfaceCullingEnabled = 1
        self.textureEnabled = 1
        self.wireframeEnabled = 0

    def doNextFrame(self, func, extraArgs = []):
        taskMgr.add(self.__doNextFrameTask, "doNextFrame" + str(id(func)), extraArgs = [func, extraArgs], appendTask = True)

    def __doNextFrameTask(self, func, extraArgs, task):
        func(*extraArgs)
        return task.done

    def loadSfxOnNode(self, sndFile, node):
        """ Loads up a spatialized sound and attaches it to the specified node. """
        snd = self.audio3d.loadSfx(sndFile)
        self.audio3d.attachSoundToObject(snd, node)
        return snd

    def physicsReport(self):
        print "\nThere are {0} total rigid bodies:".format(base.physicsWorld.getNumRigidBodies())
        for rb in base.physicsWorld.getRigidBodies():
            print "\t", NodePath(rb)
        print "\n"

    def removeEverything(self):
        for task in self.taskMgr.getTasks():
            if task.getName() not in ['dataLoop', 'igLoop']:
                task.remove()
        camera.reparentTo(render)
        for tex in render.findAllTextures():
            tex.releaseAll()
        for tex in aspect2d.findAllTextures():
            tex.releaseAll()
        for tex in render2d.findAllTextures():
            tex.releaseAll()
        for tex in hidden.findAllTextures():
            tex.releaseAll()
        for node in render.findAllMatches("**;+s"):
            node.removeNode()
        for node in aspect2d.findAllMatches("**;+s"):
            node.removeNode()
        for node in render2d.findAllMatches("**;+s"):
            node.removeNode()
        for node in hidden.findAllMatches("**;+s"):
            node.removeNode()
        TexturePool.garbageCollect()
        ModelPool.garbageCollect()
        RenderState.garbageCollect()
        RenderState.clearCache()
        RenderState.clearMungerCache()

        self.win.getGsg().getPreparedObjects().releaseAll()
        self.graphicsEngine.renderFrame()
        
    def doMemReport(self):
        MemoryUsage.showCurrentTypes()
        MemoryUsage.showCurrentAges()
        print MemoryUsage.getCurrentCppSize()
        print MemoryUsage.getExternalSize()
        print MemoryUsage.getTotalSize()

    def doPointers(self):
        print "---------------------------------------------------------------------"
        data = {}
        mup = MemoryUsagePointers()
        MemoryUsage.getPointers(mup)
        for i in xrange(mup.getNumPointers()):
            ptr = mup.getPythonPointer(i)
            if ptr.__class__.__name__ in data.keys():
                data[ptr.__class__.__name__] += 1
            else:
                data[ptr.__class__.__name__] = 1
        
        print "NodeReferenceCount:", data["NodeReferenceCount"]
        print "CopyOnWriteObject:", data["CopyOnWriteObject"]
        
        print "---------------------------------------------------------------------"
        
        
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
        try: self.physicsWorld.doPhysics(dt, 1, 0.016)
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
        # Precache water bar shader, prevents crash from running out of GPU registers
        loader.loadShader("phase_14/models/shaders/progress_bar.sha")
    
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
        if self.metadata.USE_RENDER_PIPELINE:
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
