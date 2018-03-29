"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Viewfinder.py
@author Brian Lach
@date March 8, 2018

@desc A visible camera viewfinder onscreen, with the ability to see what's in view,
      and even take pictures from the view.

"""

from panda3d.core import TransparencyAttrib, Camera, NodePath, PerspectiveLens
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, BitMask32
from panda3d.core import CollisionHandlerQueue, PNMImage, StringStream, Filename

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame

from src.coginvasion.globals import CIGlobals

class Viewfinder(DirectFrame):
    notify = directNotify.newCategory("Viewfinder")

    Ratio = 0.91
    GoodRows = 13
    BadRows = 4
    RaySpreadX = 0.08
    RaySpreadY = 0.06
    ViewSizeX = (GoodRows - BadRows) * RaySpreadX
    ViewSizeY = (GoodRows - BadRows) * RaySpreadY

    def __init__(self, size):
        DirectFrame.__init__(self, parent = aspect2d, pos = (0, -1.0, 0), relief = None)
        image = loader.loadModel("phase_4/models/minigames/photo_game_viewfinder.bam")
        self['image'] = image
        self['image_scale'] = (size, 1.0, size)

        self.screenSizeMult = size * Viewfinder.Ratio

        self.setTransparency(True)
        self.setDepthWrite(1)
        self.setDepthTest(1)

        self.initialiseoptions(Viewfinder)

        self.captureCam = NodePath(Camera("CaptureCamera"))
        self.captureCam.reparentTo(base.camera)
        self.captureLens = PerspectiveLens()
        self.captureCam.node().setLens(self.captureLens)

        self.focusTrav = CollisionTraverser('focusTrav')
        ray = CollisionRay()
        rayNode = CollisionNode('rayNode')
        rayNode.addSolid(ray)
        rayNode.setCollideMask(BitMask32(0))
        rayNode.setFromCollideMask(CIGlobals.WallBitmask)
        self.focusRay = ray
        self.focusRayNode = self.captureCam.attachNewNode(rayNode)
        self.focusHandler = CollisionHandlerQueue()
        self.focusTrav.addCollider(self.focusRayNode, self.focusHandler)

        self.textureBuffer = base.win.makeTextureBuffer("ViewFinderCapture", int(128 * 1.33), 128)
        self.displayRegion = self.textureBuffer.makeDisplayRegion()
        self.displayRegion.setCamera(self.captureCam)

        self.__updateRegions()
        
        taskMgr.add(self.__update, "viewfinderUpdate")

    def takePicture(self):
        return self.displayRegion.getScreenshot()

    def takePictureRaw(self):
        img = PNMImage()
        tex = self.takePicture()
        tex.store(img)

        ss = StringStream()
        img.write(ss, 'jpg')

        if 1:
            # Test it
            img2 = PNMImage()
            img2.read(ss)
            img2.write(Filename("test_viewfinder.jpg"))

        return ss.getData()

    def isInView(self, nodePath):
        """
        Returns True if the `nodePath` is both in the bounds of the
        camera lens and not occluded by anything.
        """

        lensBounds = self.captureCam.node().getLens().makeBounds()
        bounds = nodePath.getBounds()
        bounds.xform(nodePath.getParent().getMat(self.captureCam))
        inView = lensBounds.contains(bounds)

        if inView:
            # We have another step, make sure they're not occluded by another object.
            self.focusRayNode.lookAt(av)
            self.focusTrav.traverse(render)
            if self.focusHandler.getNumEntries() > 0:

                self.focusHandler.sortEntries()

                collNP = self.focusHandler.getEntry(0).getIntoNodePath()
                parentNP = collNP.getParent().getPythonTag('player')
                # Make sure this is the same NodePath that was passed in.
                if parentNP == nodePath:
                    return True

        return False

    def __updateRegions(self):
        self.screenSizeX = (base.a2dRight - base.a2dLeft) * self.screenSizeMult
        self.screenSizeY = (base.a2dTop - base.a2dBottom) * self.screenSizeMult
        self.captureFOV = (Viewfinder.ViewSizeX / self.screenSizeX *
                           CIGlobals.getSettingsMgr().getSetting("fpmgfov") *
                           0.5)
        self.captureLens.setFov(self.captureFOV)
        self.captureLens.setAspectRatio(1.33)

    def __update(self, task):
        self.__updateRegions()
        return task.cont

    def cleanup(self):
        taskMgr.remove("viewfinderUpdate")
        self.captureCam.removeNode()
        del self.captureCam
        del self.screenSizeX
        del self.screenSizeY
        del self.captureLens
        del self.captureFOV
        del self.screenSizeMult
        self.focusRayNode.removeNode()
        del self.focusRayNode
        del self.focusRay
        del self.focusTrav
        del self.focusHandler
        self.destroy()