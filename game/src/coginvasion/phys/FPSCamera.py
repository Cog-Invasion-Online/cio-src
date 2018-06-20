from panda3d.core import Point2, WindowProperties, ConfigVariableDouble, Point3, NodePath, CharacterJointEffect

from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.gui.DirectGui import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Wait, LerpColorScaleInterval
from direct.interval.IntervalGlobal import Parallel, LerpHprInterval, LerpPosInterval

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.ToonDNA import ToonDNA
from src.coginvasion.gags.BCakeEntity import BCakeEntity

import math

class FPSCamera(DirectObject):
    
    MaxP = 90.0
    MinP = -90.0
    PitchUpdateEpsilon = 0.1

    def __init__(self):
        DirectObject.__init__(self)
        
        self.mouseEnabled = False
        
        self.lastMousePos = Point2(0)
        self.currMousePos = Point2(0)

        self.lastVMPos = Point3(0)
        
        self.camRoot = NodePath("camRoot")
        self.lastPitch = 0

        self.lastEyeHeight = 0.0

        self.viewModel = Actor("phase_14/models/char/v_toon_arms.egg",

                               {"zero": "phase_14/models/char/v_toon_arms.egg",

                                # Squirt gun viewmodel animations
                                "sg_draw": "phase_14/models/char/v_toon_arms-draw.egg",
                                "sg_idle": "phase_14/models/char/v_toon_arms-idle.egg",
                                "sg_inspect": "phase_14/models/char/v_toon_arms-inspect.egg",
                                "sg_shoot_begin": "phase_14/models/char/v_toon_arms-shoot_begin.egg",
                                "sg_shoot_loop": "phase_14/models/char/v_toon_arms-shoot_loop.egg",
                                "sg_shoot_end": "phase_14/models/char/v_toon_arms-shoot_end.egg",
                                
                                "pie_draw": "phase_14/models/char/v_toon_arms-pie_draw.egg",
                                "pie_idle": "phase_14/models/char/v_toon_arms-pie_idle.egg",
                                
                                "button_draw": "phase_14/models/char/v_toon_arms-button_draw.egg",
                                "button_idle": "phase_14/models/char/v_toon_arms-button_idle.egg",
                                "button_press": "phase_14/models/char/v_toon_arms-button_press.egg",
                                
                                "hose_draw": "phase_14/models/char/v_toon_arms-hose_draw.egg",
                                "hose_idle": "phase_14/models/char/v_toon_arms-hose_idle.egg",
                                "hose_shoot_begin": "phase_14/models/char/v_toon_arms-hose_shoot_begin.egg",
                                "hose_shoot_loop": "phase_14/models/char/v_toon_arms-hose_shoot_loop.egg",
                                "hose_shoot_end": "phase_14/models/char/v_toon_arms-hose_shoot_end.egg"})
        self.viewModel.reparentTo(self.camRoot)
        self.viewModel.find("**/hands").setTwoSided(True)
        self.viewModel.hide()

        self.dmgFade = OnscreenImage(image = "phase_14/maps/damage_effect.png", parent = render2d)
        self.dmgFade.setBin('gui-popup', 100)
        self.dmgFade.setTransparency(1)
        self.dmgFade.setColorScale(1, 1, 1, 0)
        self.dmgFadeIval = None

        self.vmGag = None
        self.vmAnimTrack = None

    def doDamageFade(self, r, g, b, severity = 1.0):
        if self.dmgFadeIval:
            self.dmgFadeIval.finish()
            self.dmgFadeIval = None
        severity = min(1.0, severity)
        self.dmgFadeIval = Sequence(LerpColorScaleInterval(self.dmgFade, 0.25, (r, g, b, severity), (r, g, b, 0), blendType = 'easeOut'),
                                    Wait(1.0),
                                    LerpColorScaleInterval(self.dmgFade, 2.0, (r, g, b, 0), (r, g, b, severity), blendType = 'easeInOut'))
        self.dmgFadeIval.start()

    def setVMAnimTrack(self, track, loop = False):
        self.clearVMAnimTrack()

        self.vmAnimTrack = track
        if loop:
            self.vmAnimTrack.loop()
        else:
            self.vmAnimTrack.start()

    def clearVMAnimTrack(self):
        if self.vmAnimTrack:
            self.vmAnimTrack.pause()
            self.vmAnimTrack = None

    def setVMGag(self, gag, pos = (0, 0, 0), hpr = (0, 0, 0), scale = (1, 1, 1), hand = 0, animate = True):
        self.clearVMGag()

        hand = self.getViewModelRightHand() if hand == 0 else self.getViewModelLeftHand()

        if isinstance(gag, Actor) and animate:
            self.vmGag = Actor(other = gag)
            self.vmGag.reparentTo(hand)
            self.vmGag.loop('chan')
        else:
            self.vmGag = gag.copyTo(hand)
        self.vmGag.setPos(pos)
        self.vmGag.setHpr(hpr)
        self.vmGag.setScale(scale)

    def clearVMGag(self):
        if self.vmGag:
            if isinstance(self.vmGag, Actor):
                self.vmGag.cleanup()
            self.vmGag.removeNode()
            self.vmGag = None
        
    def setup(self):
        self.camRoot.reparentTo(base.localAvatar)
        self.camRoot.setPos(base.localAvatar.getEyePoint())
        self.camRoot.setHpr(0, 0, 0)

        # Match the arm color with the torso color of local avatar
        self.viewModel.find("**/arms").setColorScale(base.localAvatar.getTorsoColor(), 1)
        # Same with glove cover
        self.viewModel.find("**/hands").setColorScale(base.localAvatar.getGloveColor(), 1)

        self.attachCamera()

    def attachCamera(self):
        base.camera.reparentTo(self.camRoot)
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)

    def getViewModelLeftHand(self):
        return self.viewModel.find("**/def_left_hold")

    def getViewModelRightHand(self):
        return self.viewModel.find("**/def_right_hold")

    def getViewModel(self):
        return self.viewModel
        
    def enableMouseMovement(self):
        props = WindowProperties()
        props.setMouseMode(WindowProperties.MConfined)
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.attachCamera()
        base.localAvatar.getGeomNode().hide()
        
        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
        
        base.taskMgr.add(self.__updateTask, "mouseUpdateFPSCamera", sort = -40)
        self.acceptOnce("escape", self.__handleEscapeKey)
        
        self.mouseEnabled = True
        
    def disableMouseMovement(self, allowEnable = False):
        props = WindowProperties()
        props.setMouseMode(WindowProperties.MAbsolute)
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        
        base.taskMgr.remove("mouseUpdateFPSCamera")
        
        if allowEnable:
            self.acceptOnce("escape", self.__handleEscapeKey)
        else:
            self.ignore("escape")
            base.localAvatar.getGeomNode().show()
            
        self.mouseEnabled = False
            
    def __handleEscapeKey(self):
        if self.mouseEnabled:
            self.disableMouseMovement(True)
        else:
            self.enableMouseMovement()

    def handleJumpHardLand(self):
        down = Parallel(LerpPosInterval(base.cam, 0.1, (-0.1, 0, -0.2), (0, 0, 0), blendType = 'easeOut'),
                        LerpHprInterval(base.cam, 0.1, (0, 0, -2.5), (0, 0, 0), blendType = 'easeOut'))
        up = Parallel(LerpPosInterval(base.cam, 0.7, (0, 0, 0), (-0.1, 0, -0.2), blendType = 'easeInOut'),
                      LerpHprInterval(base.cam, 0.7, (0, 0, 0), (0, 0, -2.5), blendType = 'easeInOut'))
        Sequence(down, up).start()
            
    def __updateTask(self, task):
        dt = globalClock.getDt()
        time = globalClock.getFrameTime()

        eyePoint = base.localAvatar.getEyePoint()
        if base.localAvatar.walkControls.crouching:
            eyePoint[2] = eyePoint[2] / 2.0
        eyePoint[2] = CIGlobals.lerpWithRatio(eyePoint[2], self.lastEyeHeight, 0.4)
        self.lastEyeHeight = eyePoint[2]
        
        # Mouse look around
        mw = base.mouseWatcherNode
        if mw.hasMouse():
            md = base.win.getPointer(0)
            center = Point2(base.win.getXSize() / 2, base.win.getYSize() / 2)

            xDist = md.getX() - center.getX()
            yDist = md.getY() - center.getY()
            
            angular = -(xDist * self.__getMouseSensitivity()) / dt
            base.localAvatar.walkControls.controller.setAngularMovement(angular)
            self.camRoot.setP(self.camRoot.getP() - yDist * self.__getMouseSensitivity())
            
            if self.camRoot.getP() > FPSCamera.MaxP:
                self.camRoot.setP(FPSCamera.MaxP)
                yDist = 0
            elif self.camRoot.getP() < FPSCamera.MinP:
                yDist = 0
                self.camRoot.setP(FPSCamera.MinP)

            maxSway = 0.6
            minSway = 0.1
            swayXFactor = 0.1 * 0.7
            swayYFactor = 0.05 * 0.7
            swayRatio = 0.2
            swayX = (xDist * swayXFactor)
            swayY = (yDist * swayYFactor)
            
            if abs(swayX) < minSway:
                swayX = 0.0
            elif swayX < 0:
                swayX = swayX + minSway
            elif swayX > 0:
                swayX = swayX - minSway
            if swayX < -maxSway:
                swayX = -maxSway
            elif swayX > maxSway:
                swayX = maxSway

            if abs(swayY) < minSway:
                swayY = 0.0
            elif swayY < 0:
                swayY = swayY + minSway
            elif swayX > 0:
                swayY = swayY - minSway
            if swayY < -maxSway:
                swayY = -maxSway
            elif swayY > maxSway:
                swayY = maxSway

            vmGoal = Point3(-swayX, 0, swayY)
            self.lastVMPos = CIGlobals.lerpWithRatio(vmGoal, self.lastVMPos, swayRatio)
                
            base.win.movePointer(0, int(center.getX()), int(center.getY()))
        
        # Camera / viewmodel bobbing
        vmBob = Point3(0)
        vmRaise = Point3(0)
        camBob = Point3(0)
        if base.localAvatar.walkControls.controller.isOnGround():
            amplitude = base.localAvatar.walkControls.speeds.length() * 0.005
            bob = math.cos(time * 10) * (amplitude * 0.4)
            cBob = math.cos(time * 10) * (amplitude)
            xBob = math.sin(time * 5) * (amplitude * 1.3)

            vmBob.set(xBob, -bob * 2, -bob)
            vmRaise.set(0, abs(self.camRoot.getP()) * -0.002, self.camRoot.getP() * 0.002)
            camBob.set(0, 0, cBob)

        # Apply bob, raise, and sway to the viewmodel.
        self.viewModel.setPos(vmBob + vmRaise + self.lastVMPos)
        self.camRoot.setPos(eyePoint + camBob)

        newPitch = self.camRoot.getP()

        if abs(newPitch - self.lastPitch) > self.PitchUpdateEpsilon:
            # Broadcast where our head is looking
            head = base.localAvatar.getPart("head")
            if head and not head.isEmpty():
                # Constrain the head pitch a little bit so it doesn't look like their head snapped
                headPitch = max(-47, newPitch)
                headPitch = min(75, headPitch)
                base.localAvatar.b_setLookPitch(headPitch)

        self.lastPitch = newPitch
            
        return task.cont
    
    def __getMouseSensitivity(self):
        return CIGlobals.getSettingsMgr().getSetting('fpmgms')
