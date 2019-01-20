from panda3d.core import Vec3, VirtualFileSystem, BitMask32
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from src.coginvasion.phys.BulletCharacterController import BulletCharacterController
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.TestBananaPeel import TestBananaPeel, TestCan, TestSafe
from src.coginvasion.phys.FPSCamera import FPSCamera
from src.coginvasion.phys import PhysicsUtils

import math
import random
import sys

class LocalControls(DirectObject):
    SlideFactor = 0.75
    DiagonalFactor = math.sqrt(2.0) / 2.0
    CrouchSpeedFactor = 0.3
    FootstepIval = 0.6
    FootstepVolumeMod = 1.0
    
    BattleNormalSpeed = 320 / 16.0
    BattleRunSpeed = 416 / 16.0
    BattleWalkSpeed = 190 / 16.0

    SwimGravityMod = 0.5

    # Mode
    MThirdPerson = 0
    MFirstPerson = 1

    # Scheme
    SDefault = 0
    SSwim = 1

    def __init__(self):
        DirectObject.__init__(self)

        self.fsm = ClassicFSM('ControlMode',
                              [State('off', self.enterOff, self.exitOff),
                               State('firstperson', self.enterFirstPerson, self.exitFirstPerson),
                               State('thirdperson', self.enterThirdPerson, self.exitThirdPerson)],
                              'off', 'off')
        self.fsm.enterInitialState()

        self.controller = None
        self.staticFriction = 0.8
        self.dynamicFriction = 0.3
        self.speeds = Vec3(0)
        self.lastSpeeds = Vec3(0)

        self.idealFwd = 0
        self.idealRev = 0
        self.idealRot = 0
        self.idealJump = 0

        self.fwdSpeed = CIGlobals.ToonForwardSpeed
        self.revSpeed = CIGlobals.ToonReverseSpeed
        self.turnSpeed = CIGlobals.ToonRotateSpeed
        
        self.controlsEnabled = False
        self.airborne = False
        self.crouching = False

        self.standingUp = True
        self.footstepIval = LocalControls.FootstepIval
        self.lastFootstepTime = 0
        self.currentSurface = None
        self.footstepSounds = {}
        self.currFootstepSound = None
        self.lastFoot = True
        self.setCurrentSurface('default')
        
        self.currentObjectUsing = None
        self.lastUseObjectTime = 0.0
		
        self.defaultSounds = [base.loadSfx("phase_14/audio/sfx/footsteps/default1.ogg"),
                              base.loadSfx("phase_14/audio/sfx/footsteps/default2.ogg")]

        self.mode = LocalControls.MFirstPerson
        self.scheme = LocalControls.SDefault
        self.fpsCam = FPSCamera()

        self.movementTokens = []

        self.active = False

        self.charUpdateTaskName = "controllerUpdateTask-" + str(id(self))
        
        self.useInvalidSound = base.loadSfx("phase_4/audio/sfx/ring_miss.ogg")

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def setControlScheme(self, scheme):
        self.scheme = scheme
        if scheme == LocalControls.SSwim:
            self.controller.movementState = "swimming"
            self.controller.gravity = base.physicsWorld.getGravity()[2] * LocalControls.SwimGravityMod
            self.staticFriction = 0.15
            self.dynamicFriction = 0.08
            self.allowCrouch = False
            self.allowJump = False
        else:
            if self.controller.movementState == "swimming":
                self.controller.movementState = "ground"
            self.controller.gravity = base.physicsWorld.getGravity()[2]
            self.staticFriction = 0.8
            self.dynamicFriction = 0.3
            self.allowCrouch = True
            self.allowJump = True
        
    def attachCamera(self):
        self.fpsCam.attachCamera()

    def enterFirstPerson(self):
        self.fpsCam.setup()

        if self.controlsEnabled:
            self.fp_enable()
            
        self.revSpeed = CIGlobals.ToonForwardSpeed

    def fp_enable(self, wantMouse = 0):
        if wantMouse:
            self.fpsCam.enableMouseMovement()
        else:
            # At least allow them to engage the mouse.
            self.fpsCam.acceptEngageKeys()

        base.localAvatar.resetHeadHpr(True)

        bp = base.localAvatar.getBackpack()
        if bp and bp.getCurrentGag():
            base.localAvatar.showCrosshair()
            if base.localAvatar.isFirstPerson():
                self.fpsCam.getViewModel().show()
            base.localAvatar.b_setLookMode(base.localAvatar.LMCage)
        else:
            base.localAvatar.b_setLookMode(base.localAvatar.LMHead)

        base.camLens.setMinFov(70.0 / (4. / 3.))
            
        base.localAvatar.enableGagKeys()

    def exitFirstPerson(self):
        self.fpsCam.disableMouseMovement()
        base.localAvatar.hideCrosshair()

    def enterThirdPerson(self):
        #base.localAvatar.b_setLookMode(base.localAvatar.LMOff)
        #base.localAvatar.getGeomNode().show()
        #self.tp_attachCamera()
        #base.localAvatar.hideCrosshair()
        #self.fpsCam.getViewModel().hide()
        #self.revSpeed = CIGlobals.ToonReverseSpeed\

        self.fpsCam.setup()
        
        if self.controlsEnabled:
            self.fp_enable()
            base.localAvatar.startSmartCamera()

        self.revSpeed = CIGlobals.ToonForwardSpeed

    def tp_attachCamera(self):
        camera.reparentTo(base.localAvatar)
        base.localAvatar.smartCamera.setCameraPositionByIndex(base.localAvatar.smartCamera.cameraIndex)
        #camera.setPos(base.localAvatar.smartCamera.getIdealCameraPos())
        #camera.lookAt(base.localAvatar.smartCamera.getLookAtPoint())
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4. / 3.))

    def exitThirdPerson(self):
        base.localAvatar.stopSmartCamera()

    def setMode(self, mode):
        self.mode = mode
        
        if mode == LocalControls.MFirstPerson:
            self.fsm.request('firstperson')
        elif mode == LocalControls.MThirdPerson:
            self.fsm.request('thirdperson')
        else:
            self.notify.warning("unknown control mode {0}".format(mode))
            return

        self.watchMovementInputs()

    def switchMode(self):
        if self.mode == LocalControls.MFirstPerson:
            self.setMode(LocalControls.MThirdPerson)
        elif self.mode == LocalControls.MThirdPerson:
            self.setMode(LocalControls.MFirstPerson)

    def getCollisionsActive(self):
        return self.active

    def setWalkSpeed(self, fwd, jump, rev, rot):
        self.idealFwd = fwd
        self.idealJump = jump
        self.idealRev = rev
        self.idealRot = rot

        self.fwdSpeed = fwd
        self.revSpeed = rev
        self.turnSpeed = rot

    def setCollisionsActive(self, flag, andPlaceOnGround=0):
        if not flag:
            
            # There may be times when we need to return the avatar to the
            # ground so they don't break the laws of physics. Such as
            # when we disable collisions when moving a player through
            # a tunnel.
            if andPlaceOnGround:
                self.exitControlsWhenGrounded = True
            else:
                self.stopControllerUpdate()
        else:
            self.startControllerUpdate()

    def getSpeeds(self):
        return self.speeds

    def isMoving(self):
        return self.speeds.length() != 0

    def isCrouching(self):
        return self.crouching

    def setCurrentSurface(self, surface):
        if self.currentSurface == surface:
            return
            
        self.currentSurface = surface
        
        if not surface in self.footstepSounds:
            self.footstepSounds[surface] = []
            vfs = VirtualFileSystem.getGlobalPtr()
            for vFile in vfs.scanDirectory("phase_14/audio/sfx/footsteps/"):
                fullPath = vFile.getFilename().getFullpath()
                if surface == vFile.getFilename().getBasenameWoExtension()[:len(surface)]:
                    sound = base.loadSfx(fullPath)
                    self.footstepSounds[surface].append(sound)

    def getCurrentSurface(self):
        return self.currentSurface

    def enableControls(self, wantMouse = 0):
        if self.controlsEnabled:
            return
        
        base.taskMgr.add(self.__handlePlayerControls, "LocalControls.handlePlayerControls")
        base.taskMgr.add(self.__handleFootsteps, "LocalControls.handleFootsteps", taskChain = "fpsIndependentStuff")

        self.watchMovementInputs()

        if base.localAvatar.battleControls:
            base.taskMgr.add(self.__handleUse, "LocalControls.handleUse", taskChain = "fpsIndependentStuff")
            #self.accept(base.inputStore.NextCameraPosition, self.switchMode)

            if self.mode == LocalControls.MFirstPerson:
                self.fp_enable(wantMouse)
            elif self.mode == LocalControls.MThirdPerson:
                self.fp_enable(wantMouse)
                base.localAvatar.startSmartCamera()
                
            base.localAvatar.setWalkSpeedNormal()
            self.idealFwd = self.BattleNormalSpeed
            self.idealRev = self.BattleNormalSpeed
            self.fwdSpeed = self.idealFwd
            self.revSpeed = self.idealRev
        else:
            self.tp_attachCamera()
            base.localAvatar.startSmartCamera()
            self.accept(base.inputStore.NextCameraPosition, base.localAvatar.smartCamera.nextCameraPos, [1])
            self.accept(base.inputStore.PreviousCameraPosition, base.localAvatar.smartCamera.nextCameraPos, [0])
            self.accept(base.inputStore.LookUp, base.localAvatar.smartCamera.pageUp)
            self.accept(base.inputStore.LookDown, base.localAvatar.smartCamera.pageDown)
            if base.localAvatar.getHealth() > 0: 
                base.localAvatar.setWalkSpeedNormal()
            else:
                base.localAvatar.setWalkSpeedSlow()

        self.controlsEnabled = True
        self.exitControlsWhenGrounded = False

    def __throwTestBPeel(self):
        cls = random.choice([TestBananaPeel, TestCan, TestSafe])
        cls()

    def isOnGround(self):
        if self.controller:
            return self.controller.isOnGround()
        return False

    def __controllerUpdate(self, task):
        if self.controller:
            self.controller.update()

        return task.cont
        
    def startControllerUpdate(self):
        self.stopControllerUpdate()
    
        self.active = True
        self.controller.placeOnGround()
        taskMgr.add(self.__controllerUpdate, self.charUpdateTaskName, sort = 50)
        
    def stopControllerUpdate(self):
        taskMgr.remove(self.charUpdateTaskName)
        self.active = False

    def setupControls(self):
        self.controller = BulletCharacterController(base.physicsWorld, render, base.localAvatar.getHeight(),
                                                    base.localAvatar.getHeight() / 2.0, 0.3, 1.0)
        self.controller.setMaxSlope(75.0, False)
        self.controller.shapeGroup = CIGlobals.LocalAvGroup
        self.controller.setCollideMask(CIGlobals.LocalAvGroup)
        self.controller.setPythonTag("localAvatar", base.localAvatar)
        self.controller.setStandUpCallback(self.__handleStandUp)
        self.controller.setFallCallback(self.__handleLand)
        self.controller.enableSpam()
        base.localAvatar.reparentTo(self.controller.movementParent)
        base.localAvatar.assign(self.controller.movementParent)
        base.cr.doId2do[base.localAvatar.doId] = base.localAvatar

        self.setControlScheme(LocalControls.SDefault)

    def releaseMovementInputs(self):
        for tok in self.movementTokens:
            tok.release()
        self.movementTokens = []

    def watchMovementInputs(self):
        self.releaseMovementInputs()
        
        if base.localAvatar.battleControls:
            self.movementTokens.append(inputState.watchWithModifiers('forward', 'w', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('reverse', 's', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('slideLeft', 'a', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('slideRight', 'd', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('jump', 'space', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('crouch', 'control', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('sprint', 'shift', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('walk', 'alt', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('use', 'e', inputSource = inputState.WASD))
        else:
            self.movementTokens.append(inputState.watchWithModifiers('forward', 'arrow_up', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('reverse', 'arrow_down', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('turnLeft', 'arrow_left', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('turnRight', 'arrow_right', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('jump', 'control', inputSource = inputState.WASD))

    def disableControls(self, chat = False):
        if not self.controlsEnabled:
            return

        if base.localAvatar.battleControls:
            self.fpsCam.disableMouseMovement(False, not chat)

        self.ignore('alt')
        self.ignore(base.inputStore.NextCameraPosition)
        self.ignore(base.inputStore.PreviousCameraPosition)
        
        if base.localAvatar.isThirdPerson() or not base.localAvatar.battleControls:
            base.localAvatar.stopSmartCamera()
        
        inputState.set('forward', False, inputSource = inputState.WASD)
        inputState.set('reverse', False, inputSource = inputState.WASD)
        inputState.set('slideLeft', False, inputSource = inputState.WASD)
        inputState.set('slideRight', False, inputSource = inputState.WASD)
        inputState.set('jump', False, inputSource = inputState.WASD)
        inputState.set('crouch', False, inputSource = inputState.WASD)
        inputState.set('walk', False, inputSource = inputState.WASD)
        inputState.set('sprint', False, inputSource = inputState.WASD)
        inputState.set('use', False, inputSource = inputState.WASD)
        base.taskMgr.remove("LocalControls.handlePlayerControls")
        base.taskMgr.remove("LocalControls.handleFootsteps")
        base.taskMgr.remove("LocalControls.handleUse")
        self.controller.setLinearMovement(Vec3(0))
        self.controller.setAngularMovement(0)
        self.controlsEnabled = False

    def __handleStandUp(self):
        self.standingUp = True

    def __handleLand(self, fallDistance):
        
        
        if self.controlsEnabled:
            self.playFootstep(1.5)
            
            if fallDistance > 8:
                base.localAvatar.handleJumpHardLand()
                #if self.mode == LocalControls.MFirstPerson:
                #    self.fpsCam.handleJumpHardLand()
            else:
                base.localAvatar.handleJumpLand()
            
        if self.exitControlsWhenGrounded:
            self.stopControllerUpdate()
            self.exitControlsWhenGrounded = False
            
    def getDefaultSurface(self):
        return "default"

    def playFootstep(self, volume = 1.0):
        surfSounds = self.footstepSounds[self.currentSurface]
        numSounds = len(surfSounds)
        if numSounds > 0:
            self.lastFoot = not self.lastFoot
            mid = int(numSounds / 2)
            if self.lastFoot:
                choices = surfSounds[:mid]
            else:
                choices = surfSounds[mid:]
            if self.currFootstepSound:
                self.currFootstepSound.stop()
            sound = random.choice(choices)
            sound.setVolume(volume * LocalControls.FootstepVolumeMod)
            sound.play()
            if self.currentSurface != self.getDefaultSurface():
                # if it's not the default footstep sound, put the default toon step sound behind it
                # to sound more like feet running
                default = self.defaultSounds[int(self.lastFoot)]
                default.setVolume(volume * LocalControls.FootstepVolumeMod)
                default.play()
            self.currFootstepSound = sound
        self.lastFootstepTime = globalClock.getFrameTime()
        
    def __handleFootsteps(self, task):
        time = globalClock.getFrameTime()
        speeds = self.speeds.length()
        if speeds > 0.1 and (self.isOnGround() or self.scheme == LocalControls.SSwim):
            # 8 frames in between footsteps in run animation
            if base.localAvatar.playingAnim == 'run':
                self.footstepIval = 8 / 24.0
            elif base.localAvatar.playingAnim == 'walk':
                self.footstepIval = 11 / 24.0

            if self.scheme == LocalControls.SSwim:
                self.footstepIval *= 6.0
                
            if time - self.lastFootstepTime >= self.footstepIval:
                self.playFootstep(min(1, speeds / 15.0))
        return task.cont
        
    def __handleUse(self, task):
        #if self.mode == LocalControls.MThirdPerson:
        #    return task.cont
            
        time = globalClock.getFrameTime()
        use = inputState.isSet('use')
        if use:
            # see if there is anything for us to use.

            distance = 7.5
            camQuat = base.camera.getQuat(render)
            camFwd = camQuat.xform(Vec3.forward())
            camPos = base.camera.getPos(render)
            if self.mode == LocalControls.MFirstPerson:
                start = camPos
            else:
                # Move the line out to their character.
                # This prevents the player from using things that
                # are behind their character, but in front of
                # the camera.
                laPos = base.localAvatar.getPos(render)
                camToPlyr = (camPos.getXy() - laPos.getXy()).length()
                start = camPos + (camFwd * camToPlyr)
            stop = start + (camFwd * distance)
            hit = PhysicsUtils.rayTestClosestNotMe(base.localAvatar, start, stop, BitMask32.allOn())
            
            somethingToUse = False
            if hit is not None:
                node = hit.getNode()
                if node.hasPythonTag("useableObject"):
                    somethingToUse = True
                    obj = node.getPythonTag("useableObject")
                    if obj.canUse():
                        if self.currentObjectUsing != obj:
                            if self.currentObjectUsing is not None:
                                self.currentObjectUsing.stopUse()
                            obj.startUse()
                            self.lastUseObjectTime = time
                        elif time - self.lastUseObjectTime >= obj.useIval:
                            obj.use()
                            self.lastUseObjectTime = time
                        
                        self.currentObjectUsing = obj
            
            if not somethingToUse and not self.lastUse:
                self.useInvalidSound.play()
        else:
            if self.currentObjectUsing is not None:
                self.currentObjectUsing.stopUse()
                self.currentObjectUsing = None
            
        self.lastUse = use
        return task.cont

    def __handlePlayerControls(self, task):
        dt = globalClock.getDt()
        time = globalClock.getFrameTime()
        
        forward = inputState.isSet('forward')
        reverse = inputState.isSet('reverse')
        slideLeft = inputState.isSet('slideLeft')
        slideRight = inputState.isSet('slideRight')
        turnLeft = inputState.isSet('turnLeft')
        turnRight = inputState.isSet('turnRight')
        jump = inputState.isSet('jump')
        crouch = inputState.isSet('crouch')
        sprint = inputState.isSet('sprint')
        walk = inputState.isSet('walk')
    
        # Determine goal speeds
        speed = Vec3(0)
        
        if forward:
            speed.setY(self.fwdSpeed)
        elif reverse:
            speed.setY(-self.revSpeed)
        else:
            speed.setY(0)
            
        if reverse and slideLeft:
            speed.setX(-self.revSpeed * LocalControls.SlideFactor)
        elif reverse and slideRight:
            speed.setX(self.revSpeed * LocalControls.SlideFactor)
        elif slideLeft:
            speed.setX(-self.fwdSpeed * LocalControls.SlideFactor)
        elif slideRight:
            speed.setX(self.fwdSpeed * LocalControls.SlideFactor)
        else:
            speed.setX(0)
            
        if speed.getX() != 0 and speed.getY() != 0:
            speed.setX(speed.getX() * LocalControls.DiagonalFactor)
            speed.setY(speed.getY() * LocalControls.DiagonalFactor)

        if turnLeft:
            speed.setZ(self.turnSpeed)
        elif turnRight:
            speed.setZ(-self.turnSpeed)
        else:
            speed.setZ(0)
            
        self.speeds = Vec3(speed)
        if base.localAvatar.battleControls:
            # Apply smoothed out movement in battle controls.

            sFriction = 1 - math.pow(1 - self.staticFriction, dt * 30.0)
            dFriction = 1 - math.pow(1 - self.dynamicFriction, dt * 30.0)
            
            # Apply friction to the goal speeds
            if abs(self.speeds.getX()) < abs(self.lastSpeeds.getX()):
                self.lastSpeeds.setX(self.speeds.getX() * dFriction + self.lastSpeeds.getX() * (1 - dFriction))
            else:
                self.lastSpeeds.setX(self.speeds.getX() * sFriction + self.lastSpeeds.getX() * (1 - sFriction))
                
            if abs(self.speeds.getY()) < abs(self.lastSpeeds.getY()):
                self.lastSpeeds.setY(self.speeds.getY() * dFriction + self.lastSpeeds.getY() * (1 - dFriction))
            else:
                self.lastSpeeds.setY(self.speeds.getY() * sFriction + self.lastSpeeds.getY() * (1 - sFriction))

            if abs(self.speeds.getZ()) < abs(self.lastSpeeds.getZ()):
                self.lastSpeeds.setZ(self.speeds.getZ() * dFriction + self.lastSpeeds.getZ() * (1 - dFriction))
            else:
                self.lastSpeeds.setZ(self.speeds.getZ() * sFriction + self.lastSpeeds.getZ() * (1 - sFriction))
        else:
            self.lastSpeeds = self.speeds

        self.speeds = Vec3(self.lastSpeeds)
        
        if abs(self.speeds.getX()) < 0.1:
            self.speeds.setX(0)
        if abs(self.speeds.getY()) < 0.1:
            self.speeds.setY(0)
        if abs(self.speeds.getZ()) < 0.1:
            self.speeds.setZ(0)

        linearSpeed = Vec3(self.speeds[0], self.speeds[1], 0.0)
        
        if self.scheme == LocalControls.SSwim and self.mode == LocalControls.MFirstPerson:
            # When swimming in first person, move in the direction we are looking, like flying.
            linearSpeed = self.fpsCam.camRoot.getQuat(render).xform(linearSpeed)
        else:
            linearSpeed = base.localAvatar.getQuat(render).xform(linearSpeed)

        self.controller.setLinearMovement(linearSpeed)
        self.controller.setAngularMovement(self.speeds.getZ())

        onGround = self.isOnGround()
        if jump and onGround and not self.airborne and self.allowJump:
            self.controller.startJump(5.0)
            self.playFootstep(1.5)
            self.airborne = True
        elif onGround and self.controller.movementState == "ground":
            # We landed
            self.airborne = False
            
        if walk:
            fctr = 0.6
            self.fwdSpeed = self.BattleWalkSpeed
            self.revSpeed = self.BattleWalkSpeed
        elif sprint:
            self.fwdSpeed = self.BattleRunSpeed
            self.revSpeed = self.BattleRunSpeed
        elif not self.crouching:
            self.fwdSpeed = self.idealFwd
            self.revSpeed = self.idealRev
            
        if crouch and not self.crouching and self.allowCrouch:
            fctr = LocalControls.CrouchSpeedFactor
            self.fwdSpeed = self.idealFwd * fctr
            self.revSpeed = self.idealRev * fctr
            self.controller.startCrouch()
            self.crouching = True
            self.standingUp = False
        elif not crouch and self.crouching:
            self.controller.stopCrouch()
            if self.standingUp:
                self.fwdSpeed = self.idealFwd
                self.revSpeed = self.idealRev
                self.crouching = False

        moveBits = 0

        if self.isMoving():
            moveBits |= CIGlobals.MB_Moving
        if self.crouching:
            moveBits |= CIGlobals.MB_Crouching
        if walk:
            moveBits |= CIGlobals.MB_Walking

        if moveBits != base.localAvatar.moveBits:
            base.localAvatar.b_setMoveBits(moveBits)
        
        return task.cont
