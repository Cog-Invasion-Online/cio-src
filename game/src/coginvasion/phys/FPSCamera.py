from panda3d.core import ModelRoot, Point2, WindowProperties, ConfigVariableDouble, Point3, NodePath, CharacterJointEffect, BitMask32, PerspectiveLens, Quat, Vec3
from panda3d.bsp import BSPRender, BSPLoader

from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.gui.DirectGui import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Wait, LerpColorScaleInterval
from direct.interval.IntervalGlobal import Parallel, LerpHprInterval, LerpPosInterval
from direct.showutil import Effects

from src.coginvasion.attack.Attacks import ATTACK_HOLD_LEFT, ATTACK_HOLD_RIGHT
from src.coginvasion.base.Precache import precacheActor
from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.ToonDNA import ToonDNA
from src.coginvasion.gags.BCakeEntity import BCakeEntity

import math, random

class FPSCamera(DirectObject):
    
    MaxP = 90.0
    MinP = -90.0
    PitchUpdateEpsilon = 0.1
    ViewModelFOV = 70.0
    
    BobCycleMin = 1.0
    BobCycleMax = 0.45
    Bob = 0.002
    BobUp = 0.5
    
    PunchDamping = 9.0
    PunchSpring = 65.0
    
    PrintAnimLengths = False

    def __init__(self):
        DirectObject.__init__(self)
        
        self.mouseEnabled = False
        
        self.lastCamRoot2Quat = Quat(Quat.identQuat())
        
        self.punchAngleVel = Vec3(0)
        self.punchAngle = Vec3(0)

        self.lastFacing = Vec3(0)
        
        self.lastMousePos = Point2(0)
        self.currMousePos = Point2(0)
        
        self.bobTime = 0
        self.lastBobTime = 0

        self.lastVMPos = Point3(0)
        
        self.camRoot = NodePath("camRoot")
        self.camRoot2 = self.camRoot.attachNewNode("camRoot2")
        self.lastPitch = 0

        self.lastEyeHeight = 0.0

        # Updates to the transform of camRoot
        self.vmRender = NodePath(BSPRender('vmRender', BSPLoader.getGlobalPtr()))
        self.vmRender.setShaderAuto()
        self.vmRoot = self.vmRender.attachNewNode('vmRoot')
        self.vmRoot2 = self.vmRoot.attachNewNode(ModelRoot('vmRoot2'))
        self.viewModel = Actor("phase_14/models/char/v_toon_arms.bam",

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

                                "gumball_draw": "phase_14/models/char/v_toon_arms-gumball_draw.egg",
				                "gumball_idle": "phase_14/models/char/v_toon_arms-gumball_idle.egg",
				                "gumball_fire": "phase_14/models/char/v_toon_arms-gumball_fire.egg",
                                
                                "hose_draw": "phase_14/models/char/v_toon_arms-hose_draw.egg",
                                "hose_idle": "phase_14/models/char/v_toon_arms-hose_idle.egg",
                                "hose_shoot_begin": "phase_14/models/char/v_toon_arms-hose_shoot_begin.egg",
                                "hose_shoot_loop": "phase_14/models/char/v_toon_arms-hose_shoot_loop.egg",
                                "hose_shoot_end": "phase_14/models/char/v_toon_arms-hose_shoot_end.egg",
                                
                                "tnt_draw": "phase_14/models/char/v_toon_arms-tnt_draw.egg",
                                "tnt_idle": "phase_14/models/char/v_toon_arms-tnt_idle.egg",
                                "tnt_throw": "phase_14/models/char/v_toon_arms-tnt_throw.egg",
                                
                                "slap_idle": "phase_14/models/char/v_toon_arms-slap_idle.egg",
                                "slap_hit": "phase_14/models/char/v_toon_arms-slap_hit.egg",
                                
                                "sound": "phase_14/models/char/v_toon_arms-sound.egg"})
        self.viewModel.setBlend(frameBlend = base.config.GetBool("interpolate-frames", False))
        self.viewModel.reparentTo(self.vmRoot2)
        self.viewModel.find("**/hands").setTwoSided(True)
        self.viewModel.hide()
        
        self.defaultViewModel = self.viewModel
        self.idealFov = self.ViewModelFOV
        
        precacheActor(self.viewModel)
        #self.viewModel.clearMaterial()
        #self.viewModel.setMaterial(CIGlobals.getCharacterMaterial(specular = (0, 0, 0, 1)), 1)
        self.viewportLens = PerspectiveLens()
        self.viewportLens.setMinFov(self.ViewModelFOV / (4. / 3.))
        self.viewportLens.setNear(0.3)
        # Updates to the transform of base.camera
        self.viewportCam = base.makeCamera(base.win, clearDepth = True, camName = 'fpsViewport',
                                           mask = CIGlobals.ViewModelCamMask, lens = self.viewportLens)
        # Pretend to be the main camera so the viewmodel gets ambient probes updated
        self.viewportCam.node().setTag("__mainpass__", "1")
        self.viewportCam.reparentTo(self.vmRoot)

        self.vmGag = None
        self.vmAnimTrack = None
        self.dmgFade = OnscreenImage(image = "phase_14/maps/damage_effect.png", parent = render2d)
        self.dmgFade.setBin('gui-popup', 100)
        self.dmgFade.setTransparency(1)
        self.dmgFade.setColorScale(1, 1, 1, 0)
        self.dmgFadeIval = None
        
        #self.accept('v', self.vmRender.ls)

        #base.bspLoader.addDynamicNode(self.vmRoot)
        
        if self.PrintAnimLengths:
            print "v_toon_arms animation lengths:"
            for anim in self.viewModel.getAnimNames():
                print "\t{0}\t:\t{1}".format(anim, self.viewModel.getDuration(anim))

        taskMgr.add(self.__vpDebugTask, "vpdebutask", sort = -100)

    def setViewModelFOV(self, fov):
        self.idealFov = fov

    def restoreViewModelFOV(self):
        self.idealFov = self.ViewModelFOV
        
    def swapViewModel(self, newViewModel, fov = 70.0):
        if newViewModel.isEmpty():
            return
            
        isHidden = False
        if not self.viewModel.isEmpty():
            self.viewModel.reparentTo(hidden)
            isHidden = self.viewModel.isHidden()
            
        self.viewModel = newViewModel
        self.viewModel.reparentTo(self.vmRoot2)
        if isHidden:
            self.viewModel.hide()
        else:
            self.viewModel.show()
            
        self.setViewModelFOV(fov)
        
    def restoreViewModel(self):
        isHidden = False
        if not self.viewModel.isEmpty():
            self.viewModel.reparentTo(hidden)
            isHidden = self.viewModel.isHidden()
            
        self.viewModel = self.defaultViewModel
        self.viewModel.reparentTo(self.vmRoot2)
        if isHidden:
            self.viewModel.hide()
        else:
            self.viewModel.show()
            
        self.restoreViewModelFOV()
        
    def addViewPunch(self, punch):
        self.punchAngleVel += punch * 20
        
    def resetViewPunch(self, tolerance = 0.0):
        if tolerance != 0.0:
            tolerance *= tolerance
            check = self.punchAngleVel.lengthSquared() + self.punchAngle.lengthSquared()
            if check > tolerance:
                return
                
        self.punchAngle = Vec3(0)
        self.punchAngleVel = Vec3(0)
        
    def decayPunchAngle(self):
        if self.punchAngle.lengthSquared() > 0.001 or self.punchAngleVel.lengthSquared() > 0.001:
            dt = globalClock.getDt()
            self.punchAngle += self.punchAngleVel * dt
            damping = 1 - (self.PunchDamping * dt)
            
            if damping < 0:
                damping = 0
            self.punchAngleVel *= damping
            
            # Torsional spring
            springForceMag = self.PunchSpring * dt
            springForceMag = CIGlobals.clamp(springForceMag, 0.0, 2.0)
            self.punchAngleVel -= self.punchAngle * springForceMag
            
            # Don't wrap around
            self.punchAngle.set(CIGlobals.clamp(self.punchAngle[0], -179, 179),
                                CIGlobals.clamp(self.punchAngle[1], -89, 89),
                                CIGlobals.clamp(self.punchAngle[2], -89, 89))
        else:
            self.punchAngle = Vec3(0)
            self.punchAngleVel = Vec3(0)

    def hideViewModel(self):
        self.viewModel.hide(BitMask32.allOn())

    def showViewModel(self):
        if not base.localAvatar.isFirstPerson():
            return

        self.viewModel.showThrough(CIGlobals.ViewModelCamMask)

    def __vpDebugTask(self, task):
        if self.vmRender.getState() != render.getState():
            # pretend like the view model is part of the main scene
            self.vmRender.setState(render.getState())
            
        self.viewportLens.setAspectRatio(base.getAspectRatio())
        self.viewportLens.setMinFov(self.idealFov / (4. / 3.))
        self.vmRoot.setTransform(render, self.camRoot.getTransform(render))
        self.viewportCam.setTransform(render, base.camera.getTransform(render))

        # Since the viewmodel is not underneath BSPRender, it's not going to be automatically
        # influenced by the ambient probes. We need to do this explicitly.
        #base.bspLoader.updateDynamicNode(self.vmRoot)

        #self.viewportDebug.setImage(self.viewportCam.node().getDisplayRegion(0).getScreenshot())

        return task.cont

    def handleSuitAttack(self, attack):
        print "FPSCamera handleSuitAttack:", attack

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

        handNode = NodePath()
        if hand == ATTACK_HOLD_RIGHT:
            handNode = self.getViewModelRightHand()
        elif hand == ATTACK_HOLD_LEFT:
            handNode = self.getViewModelLeftHand()

        if isinstance(gag, Actor) and animate:
            self.vmGag = Actor(other = gag)
            self.vmGag.reparentTo(handNode)
            self.vmGag.loop('chan')
        else:
            self.vmGag = gag.copyTo(handNode)
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
        try:
            # Match the arm color with the torso color of local avatar
            self.viewModel.find("**/arms").setColorScale(base.localAvatar.getTorsoColor(), 1)
            # Same with glove cover
            self.viewModel.find("**/hands").setColorScale(base.localAvatar.getGloveColor(), 1)
        except:
            pass

        self.attachCamera()

    def attachCamera(self, reset = True):
        if reset:
            self.camRoot.reparentTo(base.localAvatar)
            if base.localAvatar.isFirstPerson():
                self.camRoot.setPos(base.localAvatar.getEyePoint())
            else:
                self.camRoot.setPos(0, 0, max(base.localAvatar.getHeight(), 3.0))
            self.camRoot.setHpr(0, 0, 0)
            self.camRoot2.setPosHpr(0, 0, 0, 0, 0, 0)
            
        base.camera.reparentTo(self.camRoot2)

        if base.localAvatar.isFirstPerson():
            base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        elif base.localAvatar.isThirdPerson():            
            pos, lookAt = self.getThirdPersonBattleCam()
            base.localAvatar.smartCamera.setIdealCameraPos(pos)
            base.localAvatar.smartCamera.setLookAtPoint(lookAt)
            
    def getThirdPersonBattleCam(self):
        camHeight = max(base.localAvatar.getHeight(), 3.0)
        heightScaleFactor = camHeight * 0.3333333333
        
        return ((1, -5 * heightScaleFactor, 0), (1, 10, 0))

    def getViewModelLeftHand(self):
        return self.viewModel.find("**/def_left_hold")

    def getViewModelRightHand(self):
        return self.viewModel.find("**/def_right_hold")

    def getViewModel(self):
        return self.viewModel

    def acceptEngageKeys(self):
        self.acceptOnce("escape", self.__handleEscapeKey)

    def ignoreEngageKeys(self):
        self.ignore("escape")
        
    def enableMouseMovement(self):
        props = WindowProperties()
        props.setMouseMode(WindowProperties.MConfined)
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.attachCamera(False)
        if base.localAvatar.isFirstPerson():
            base.localAvatar.getGeomNode().hide()
        
        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
        
        base.taskMgr.add(self.__updateTask, "mouseUpdateFPSCamera", sort = -40)
        self.acceptEngageKeys()
        
        self.mouseEnabled = True
        
        base.localAvatar.enableGagKeys()
        
    def disableMouseMovement(self, allowEnable = False, showAvatar = True):
        props = WindowProperties()
        props.setMouseMode(WindowProperties.MAbsolute)
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        
        base.taskMgr.remove("mouseUpdateFPSCamera")
        
        base.localAvatar.disableGagKeys()
        
        if allowEnable:
            self.acceptEngageKeys()
        else:
            self.ignoreEngageKeys()
            if showAvatar or base.localAvatar.isThirdPerson():
                base.localAvatar.getGeomNode().show()
            else:
                base.localAvatar.getGeomNode().hide()
            
        self.mouseEnabled = False
            
    def __handleEscapeKey(self):
        if self.mouseEnabled:
            self.disableMouseMovement(True)
        else:
            self.enableMouseMovement()
            
    #def doCameraJolt(self, amplitude, horizRange = [-1, 1], vertRange = [1]):
        #h = random.choice(horizRange) * amplitude
        #p = random.choice(vertRange) * amplitude
        #nquat = Quat(Quat.identQuat())
        #nquat.setHpr((h, p, 0))
        #self.lastCamRoot2Quat = self.lastCamRoot2Quat + nquat
        
        #Effects.createPBounce(self.camRoot2, 3, self.camRoot2.getHpr(), 1, amplitude).start()
        #Effects.createHBounce(self.camRoot2, 3, self.camRoot2.getHpr(), 1, amplitude).start()

    def handleJumpHardLand(self):
        down = Parallel(LerpPosInterval(base.cam, 0.1, (-0.1, 0, -0.2), (0, 0, 0), blendType = 'easeOut'),
                        LerpHprInterval(base.cam, 0.1, (0, 0, -2.5), (0, 0, 0), blendType = 'easeOut'))
        up = Parallel(LerpPosInterval(base.cam, 0.7, (0, 0, 0), (-0.1, 0, -0.2), blendType = 'easeInOut'),
                      LerpHprInterval(base.cam, 0.7, (0, 0, 0), (0, 0, -2.5), blendType = 'easeInOut'))
        Sequence(down, up).start()
            
    def __updateTask(self, task):
        # TODO -- This function does a lot of math, I measured it to take .5 ms on my laptop
        #         That's a lot of time for something miniscule like sway and bob.
        
        dt = globalClock.getDt()
        time = globalClock.getFrameTime()

        if base.localAvatar.isFirstPerson():
            eyePoint = base.localAvatar.getEyePoint()
            if base.localAvatar.walkControls.crouching:
                eyePoint[2] = eyePoint[2] / 2.0
            eyePoint[2] = CIGlobals.lerpWithRatio(eyePoint[2], self.lastEyeHeight, 0.4)
            self.lastEyeHeight = eyePoint[2]
            
        camRootAngles = Vec3(0)
        
        # Mouse look around
        mw = base.mouseWatcherNode
        if mw.hasMouse():
            md = base.win.getPointer(0)
            center = Point2(base.win.getXSize() / 2, base.win.getYSize() / 2)

            xDist = md.getX() - center.getX()
            yDist = md.getY() - center.getY()

            sens = self.__getMouseSensitivity()
            
            angular = -(xDist * sens) / dt
            base.localAvatar.walkControls.controller.setAngularMovement(angular)
            camRootAngles.setY(self.lastPitch - yDist * sens)
            
            if camRootAngles.getY() > FPSCamera.MaxP:
                camRootAngles.setY(FPSCamera.MaxP)
                yDist = 0
            elif camRootAngles.getY() < FPSCamera.MinP:
                yDist = 0
                camRootAngles.setY(FPSCamera.MinP)
                
            base.win.movePointer(0, int(center.getX()), int(center.getY()))
        
        if base.localAvatar.isFirstPerson():
            # Camera / viewmodel bobbing
            vmBob = Point3(0)
            vmAngles = Vec3(0)
            vmRaise = Point3(0)
            camBob = Point3(0)
            
            maxSpeed = base.localAvatar.walkControls.BattleRunSpeed * 16.0
            
            speed = base.localAvatar.walkControls.speeds.length() * 16.0
            speed = max(-maxSpeed, min(maxSpeed, speed))
            
            bobOffset = CIGlobals.remapVal(speed, 0, maxSpeed, 0.0, 1.0)
            
            self.bobTime += (time - self.lastBobTime) * bobOffset
            self.lastBobTime = time
            
            # Calculate the vertical bob
            cycle = self.bobTime - int(self.bobTime / self.BobCycleMax)*self.BobCycleMax
            cycle /= self.BobCycleMax
            if cycle < self.BobUp:
                cycle = math.pi * cycle / self.BobUp
            else:
                cycle = math.pi + math.pi*(cycle-self.BobUp)/(1.0 - self.BobUp)
                
            verticalBob = speed * 0.005
            verticalBob = verticalBob*0.3 + verticalBob*0.7*math.sin(cycle)
            verticalBob = max(-7.0, min(4.0, verticalBob))
            verticalBob /= 16.0
            
            # Calculate the lateral bob
            cycle = self.bobTime - int(self.bobTime / self.BobCycleMax*2)*self.BobCycleMax*2
            cycle /= self.BobCycleMax*2
            if cycle < self.BobUp:
                cycle = math.pi * cycle / self.BobUp
            else:
                cycle = math.pi + math.pi*(cycle-self.BobUp)/(1.0 - self.BobUp)
                
            lateralBob = speed * 0.005
            lateralBob = lateralBob*0.3 + lateralBob*0.7*math.sin(cycle)
            lateralBob = max(-7.0, min(4.0, lateralBob))
            lateralBob /= 16.0

            # Apply bob, but scaled down a bit
            vmBob.set(lateralBob * 0.8, 0, verticalBob * 0.1)
            # Z bob a bit more
            vmBob[2] += verticalBob * 0.1
            # Bob the angles
            vmAngles[2] += verticalBob * 0.5
            vmAngles[1] -= verticalBob * 0.4
            vmAngles[0] -= lateralBob * 0.3

            # ================================================================
            # Viewmodel lag/sway
            
            angles = self.camRoot.getHpr(render)
            quat = Quat()
            quat.setHpr(angles)
            invQuat = Quat()
            invQuat.invertFrom(quat)

            maxVMLag = 1.5
            lagforward = quat.getForward()
            if dt != 0.0:
                lagdifference = lagforward - self.lastFacing
                lagspeed = 5.0
                lagdiff = lagdifference.length()
                if (lagdiff > maxVMLag) and (maxVMLag > 0.0):
                    lagscale = lagdiff / maxVMLag
                    lagspeed *= lagscale

                self.lastFacing = CIGlobals.extrude(self.lastFacing, lagspeed * dt, lagdifference)
                self.lastFacing.normalize()
                lfLocal = invQuat.xform(lagdifference)
                vmBob = CIGlobals.extrude(vmBob, 5.0 / 16.0, lfLocal * -1.0)

            pitch = angles[1]
            if pitch > 180:
                pitch -= 360
            elif pitch < -180:
                pitch += 360

            vmBob = CIGlobals.extrude(vmBob, pitch * (0.035 / 16), Vec3.forward())
            vmBob = CIGlobals.extrude(vmBob, pitch * (0.03 / 16), Vec3.right())
            vmBob = CIGlobals.extrude(vmBob, pitch * (0.02 / 16), Vec3.up())

            # ================================================================
            
            vmRaise.set(0, 0, 0)#(0, abs(camRootAngles.getY()) * -0.002, camRootAngles.getY() * 0.002)
            camBob.set(0, 0, 0)

            # Apply bob, raise, and sway to the viewmodel.
            self.viewModel.setPos(vmBob + vmRaise + self.lastVMPos)
            self.vmRoot2.setHpr(vmAngles)
            self.camRoot.setPos(eyePoint + camBob)

        newPitch = camRootAngles.getY()

        if abs(newPitch - self.lastPitch) > self.PitchUpdateEpsilon:
            # Broadcast where our head is looking
            head = base.localAvatar.getPart("head")
            if head and not head.isEmpty():
                # Constrain the head pitch a little bit so it doesn't look like their head snapped
                headPitch = max(-47, newPitch)
                headPitch = min(75, headPitch)
                base.localAvatar.b_setLookPitch(headPitch)

        self.lastPitch = newPitch
        
        if base.localAvatar.isFirstPerson():
            # Apply punch angle
            self.decayPunchAngle()
            camRootAngles += self.punchAngle
            
        self.camRoot.setHpr(camRootAngles)
            
        return task.cont
    
    def __getMouseSensitivity(self):
        return CIGlobals.getSettingsMgr().getSetting('fpmgms').getValue()
        
    def cleanup(self):
        taskMgr.remove("vpdebutask")
        self.disableMouseMovement(False, False)
        self.clearVMAnimTrack()
        self.clearVMGag()
        if self.viewModel:
            self.viewModel.cleanup()
            self.viewModel.removeNode()
        self.viewModel = None
        if self.vmRender:
            self.vmRender.removeNode()
        self.vmRender = None
        self.vmRoot = None
        self.vmRoot2 = None
        self.viewportLens = None
        if self.viewportCam:
            self.viewportCam.removeNode()
        self.viewportCam = None
        if self.camRoot:
            self.camRoot.removeNode()
        self.camRoot = None
        self.camRoot2 = None
        self.lastEyeHeight = None
        self.lastPitch = None
        self.bobTime = None
        self.lastBobTime = None
        self.mouseEnabled = None
        self.lastCamRoot2Quat = None
        self.punchAngleVel = None
        self.punchAngle = None
        self.lastFacing = None
        self.lastMousePos = None
        self.currMousePos = None
        self.lastVMPos = None
        self.defaultViewModel = None
        self.idealFov = None
        self.vmGag = None
        self.vmAnimTrack = None
        self.dmgFade = None
        self.dmgFadeIval = None
        self.ignoreAll()
