"""

  Filename: FirstPerson.py
  Created by: blach (28Apr15)

"""

from panda3d.core import WindowProperties
from direct.showbase.DirectObject import DirectObject

class FirstPerson(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)
        self.player_node = None
        self.min_camerap = -90.0
        self.max_camerap = 90.0

    def start(self):
        base.localAvatar.getGeomNode().hide()
        self.player_node = base.localAvatar.attachNewNode('PlayerNode')
        base.localAvatar.controlManager.disable()
        base.localAvatar.prepareToSwitchControlType()
        base.localAvatar.controlManager.wantWASD = 1
        base.localAvatar.controlManager.enable()
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        camera.reparentTo(self.player_node)
        camera.setZ(base.localAvatar.getHeight())

    def reallyStart(self):
        base.localAvatar.walkControls.enableAvatarControls()

    def disableMouse(self, startTask = True):
        if startTask:
            taskMgr.add(self.cameraMovement, "moveCamera")
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.acceptOnce("escape", self.enableMouse)

    def enableMouse(self):
        taskMgr.remove("moveCamera")
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        self.acceptOnce("escape", self.disableMouse)

    def end(self):
        self.ignore("escape")
        base.localAvatar.walkControls.disableAvatarControls()

    def reallyEnd(self):
        if self.player_node:
            self.player_node.removeNode()
            self.player_node = None
        camera.reparentTo(render)
        camera.setZ(0.0)
        base.localAvatar.getGeomNode().show()
        base.localAvatar.controlManager.disable()
        base.localAvatar.prepareToSwitchControlType()
        base.localAvatar.controlManager.wantWASD = 0
        base.localAvatar.controlManager.enable()

    def cleanup(self):
        if hasattr(self, 'min_camerap'):
            del self.min_camerap
            del self.max_camerap

    def cameraMovement(self, task):
        if hasattr(self, 'min_camerap') and hasattr(self, 'max_camerap'):
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                camera.setP(camera.getP() - (y - base.win.getYSize()/2)*0.1)
                base.localAvatar.setH(base.localAvatar.getH() - (x - base.win.getXSize()/2)*0.1)
                if camera.getP() < self.min_camerap:
                    camera.setP(self.min_camerap)
                elif camera.getP() > self.max_camerap:
                    camera.setP(self.max_camerap)
            return task.cont
        else:
            return task.done
