"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TPMouseMovement.py
@author Brian Lach
@date March 19, 2017

"""

from panda3d.core import WindowProperties, Point3
from direct.showbase.DirectObject import DirectObject

from src.coginvasion.globals import CIGlobals

class TPMouseMovement(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)
        self.player_node = None
        self.min_camerap = -45.0
        self.max_camerap = 45.0
        self.enabled = False
        self.disabledByFocusLoss = False
        self.disabledByChat = False
        self.enableOnChatExit = False

    def initialize(self):
        if self.player_node:
            camera.reparentTo(base.localAvatar)
            self.player_node.removeNode()
            self.player_node = None

        self.player_node = base.localAvatar.attachNewNode('PlayerNode')
        
    def __handleWindowEvent(self, window = None):
        if window is not None:
            wp = window.getProperties()
            isInForeground = wp.getForeground()
            
            if not isInForeground and self.enabled:
                self.disableMovement(allowReEnable = True, byChatInput = False)
                self.disabledByFocusLoss = True
            elif not self.enabled and self.disabledByFocusLoss:
                self.enableMovement()
                self.disabledByFocusLoss = False

    def enableMovement(self, startTask = True):
        if self.disabledByChat:
            self.enableOnChatExit = True
            return
    
        if self.player_node is None or self.enabled:
            return
            
        self.enableOnChatExit = False
            
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.MConfined)
        base.win.requestProperties(props)
        self.acceptOnce(base.inputStore.ToggleGTAControls, self.disableMovement)
        self.accept(base.win.getWindowEvent(), self.__handleWindowEvent)
        
        self.player_node.setHpr(0, 0, 0)

        # Re-center the mouse.
        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
            
        camera.reparentTo(self.player_node)
        
        if startTask:
            taskMgr.add(self.cameraMovement, "TPMM.enableMovement")
        
        self.enabled = True

    def disableMovement(self, allowReEnable = True, byChatInput = False):
        self.disabledByChat = byChatInput
        self.enableOnChatExit = byChatInput
        
        if not self.enabled:
            return
        
        taskMgr.remove("TPMM.enableMovement")
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)
        camera.wrtReparentTo(base.localAvatar)
        if allowReEnable:
            self.allowReEnable()
        self.enabled = False
        
    def allowReEnable(self):
        self.acceptOnce(base.inputStore.ToggleGTAControls, self.enableMovement)

    def cleanup(self):
        self.disableMovement(False)

        if self.player_node:
            camera.wrtReparentTo(base.localAvatar)
            self.player_node.removeNode()
            self.player_node = None

        if hasattr(self, 'max_camerap'):
            del self.max_camerap
            del self.min_camerap
            del self.enabled
            del self.disabledByChat

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

            # Do some mouse movement
            goalH = self.player_node.getH() - (x - centerX) * sens
            self.player_node.setH(goalH)

            if base.localAvatar.isMoving():
                # We can turn our character with the mouse while moving.
                base.localAvatar.setH(render, self.player_node.getH(render))
                self.player_node.setH(0)
                
        return task.cont
