"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TPMouseMovement.py
@author Brian Lach
@date March 19, 2017

"""

from pandac.PandaModules import WindowProperties, Point3
from direct.showbase.DirectObject import DirectObject

from src.coginvasion.globals import CIGlobals

from ccoginvasion import Lerper

class TPMouseMovement(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)
        self.player_node = None
        self.min_camerap = -45.0
        self.max_camerap = 45.0

        self.pnLerp = Lerper(Point3(0), 0.5)
        self.camPLerp = Lerper(0.0, 0.5)
        self.laHLerp = Lerper(0.0, 0.5)

    def initialize(self):
        if self.player_node:
            camera.wrtReparentTo(base.localAvatar)
            self.player_node.removeNode()
            self.player_node = None

        self.player_node = render.attachNewNode('PlayerNode')

    def enableMovement(self, startTask = True):
        if self.player_node is None:
            return
            
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.MConfined)
        base.win.requestProperties(props)
        self.acceptOnce(base.inputStore.ToggleGTAControls, self.disableMovement)
        
        self.player_node.setHpr(base.localAvatar, 0, 0, 0)

        # Re-center the mouse.
        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
            
        camera.wrtReparentTo(self.player_node)
        if startTask:
            self.camPLerp.setLastFloat(camera.getP())
            self.laHLerp.setLastFloat(base.localAvatar.getH())

            self.pnLerp.setLastP3(base.localAvatar.getPos(render))
            self.player_node.setPos(self.pnLerp.getLastP3())

            taskMgr.add(self.cameraMovement, "TPMM.enableMovement")
        

    def disableMovement(self):
        taskMgr.remove("TPMM.enableMovement")
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)
        camera.wrtReparentTo(base.localAvatar)
        self.acceptOnce(base.inputStore.ToggleGTAControls, self.enableMovement)

    def cleanup(self):
        self.disableMovement()

        if self.player_node:
            camera.wrtReparentTo(base.localAvatar)
            self.player_node.removeNode()
            self.player_node = None

        if hasattr(self, 'max_camerap'):
            del self.max_camerap
            del self.min_camerap
            del self.laHLerp
            del self.pnLerp
            del self.camPLerp

    def cameraMovement(self, task):
        if hasattr(self, 'min_camerap') and hasattr(self, 'max_camerap') and base.mouseWatcherNode.hasMouse():
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            centerX = base.win.getXSize() / 2
            centerY = base.win.getYSize() / 2

            if abs(x - centerX) > 0 or abs(y - centerY) > 0:
                base.win.movePointer(0, centerX, centerY)

            # Get the mouse sensitivity
            sens = CIGlobals.getSettingsMgr().getSetting("fpmgms")

            dt = globalClock.getDt()

            # Do some mouse movement smoothing / lerping
            goalPos = base.localAvatar.getPos(render)
            goalH = self.player_node.getH() - (x - centerX) * sens
            goalP = self.player_node.getP() - (y - centerY) * sens

            #lastPNPos = self.pnLerp.lerpToP3(goalPos)
            
            #self.player_node.setPos(lastPNPos)
            self.player_node.setPos(goalPos)
            self.player_node.setH(goalH)
            #self.player_node.setP(goalP)

            if base.localAvatar.isMoving():
                # We can turn our character with the mouse while moving.
                base.localAvatar.setH(render, self.player_node.getH(render))

            if camera.getP() < self.min_camerap:
                camera.setP(self.min_camerap)
            elif camera.getP() > self.max_camerap:
                camera.setP(self.max_camerap)
                
        return task.cont
