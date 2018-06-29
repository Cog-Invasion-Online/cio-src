from panda3d.core import Vec3, VirtualFileSystem
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from src.coginvasion.phys.BulletCharacterController import BulletCharacterController
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.TestBananaPeel import TestBananaPeel, TestCan, TestSafe
from src.coginvasion.phys.FPSCamera import FPSCamera

import math
import random
import sys

class LocalControls(DirectObject):
    SlideFactor = 0.75
    DiagonalFactor = math.sqrt(2.0) / 2.0
    CrouchSpeedFactor = 0.3
    FootstepIval = 0.6
    FootstepVolumeMod = 1.0

    # Mode
    MThirdPerson = 0
    MFirstPerson = 1

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
        self.footstepSounds = []
        self.currFootstepSound = None
        self.lastFoot = True
        self.setCurrentSurface('hardsurface')

        self.mode = LocalControls.MThirdPerson
        self.fpsCam = FPSCamera()

        self.movementTokens = []

        self.active = False

        self.charUpdateTaskName = "controllerUpdateTask-" + str(id(self))

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterFirstPerson(self):
        self.fpsCam.setup()

        if self.controlsEnabled:
            self.fp_enable()

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
            self.fpsCam.getViewModel().show()
            base.localAvatar.b_setLookMode(base.localAvatar.LMCage)
        else:
            base.localAvatar.b_setLookMode(base.localAvatar.LMHead)

    def exitFirstPerson(self):
        self.fpsCam.disableMouseMovement()
        base.localAvatar.hideCrosshair()

    def enterThirdPerson(self):
        base.localAvatar.b_setLookMode(base.localAvatar.LMOff)
        base.localAvatar.getGeomNode().show()
        self.tp_attachCamera()
        base.localAvatar.showCrosshair()
        self.fpsCam.getViewModel().hide()

    def tp_attachCamera(self):
        camera.reparentTo(base.localAvatar)
        camera.setPos(base.localAvatar.smartCamera.getIdealCameraPos())
        camera.lookAt(base.localAvatar.smartCamera.getLookAtPoint())

    def exitThirdPerson(self):
        pass

    def setMode(self, mode):
        if mode == LocalControls.MFirstPerson:
            self.fsm.request('firstperson')
        elif mode == LocalControls.MThirdPerson:
            self.fsm.request('thirdperson')
        else:
            self.notify.warning("unknown control mode {0}".format(mode))
            return

        self.mode = mode
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

    def setCollisionsActive(self, flag):
        if not flag:
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
        self.currentSurface = surface
        
        self.footstepSounds = []
        
        vfs = VirtualFileSystem.getGlobalPtr()
        for vFile in vfs.scanDirectory("phase_14/audio/sfx/footsteps/"):
            fullPath = vFile.getFilename().getFullpath()
            if 'footstep_' + self.currentSurface in fullPath:
                sound = base.loadSfx(fullPath)
                self.footstepSounds.append(sound)

    def getCurrentSurface(self):
        return self.currentSurface

    def enableControls(self, wantMouse = 0):
        if self.controlsEnabled:
            return
        
        base.taskMgr.add(self.__handlePlayerControls, "LocalControls.handlePlayerControls")
        base.taskMgr.add(self.__handleFootsteps, "LocalControls.handleFootsteps", taskChain = "fpsIndependentStuff")

        #self.accept('alt', self.__throwTestBPeel)
        self.accept('tab', self.switchMode)

        if self.mode == LocalControls.MFirstPerson:
            self.fp_enable(wantMouse)
        elif self.mode == LocalControls.MThirdPerson:
            self.tp_attachCamera()

        self.controlsEnabled = True

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
        taskMgr.add(self.__controllerUpdate, self.charUpdateTaskName, sort = 50)
        
    def stopControllerUpdate(self):
        taskMgr.remove(self.charUpdateTaskName)
        self.active = False

    def setupControls(self):
        self.controller = BulletCharacterController(base.physicsWorld, render, base.localAvatar.getHeight(),
                                                    base.localAvatar.getHeight() / 2.0, 0.3, 1.0)
        self.controller.shapeGroup = CIGlobals.LocalAvGroup
        self.controller.setCollideMask(CIGlobals.LocalAvGroup)
        self.controller.setPythonTag("localAvatar", base.localAvatar)
        self.controller.setStandUpCallback(self.__handleStandUp)
        self.controller.setFallCallback(self.__handleLand)
        #self.controller.enableSpam()
        base.localAvatar.reparentTo(self.controller.movementParent)
        base.localAvatar.assign(self.controller.movementParent)
        base.cr.doId2do[base.localAvatar.doId] = base.localAvatar

        inputState.watchWithModifiers('jump', 'space', inputSource = inputState.WASD)
        inputState.watchWithModifiers('crouch', 'control', inputSource = inputState.WASD)
        inputState.watchWithModifiers('walk', 'shift', inputSource = inputState.WASD)
        inputState.watchWithModifiers('use', 'e', inputSource = inputState.WASD)

    def releaseMovementInputs(self):
        for tok in self.movementTokens:
            tok.release()
        self.movementTokens = []

    def watchMovementInputs(self):
        self.releaseMovementInputs()

        if self.mode == LocalControls.MFirstPerson:
            self.movementTokens.append(inputState.watchWithModifiers('forward', 'w', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('reverse', 's', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('slideLeft', 'a', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('slideRight', 'd', inputSource = inputState.WASD))
        elif self.mode == LocalControls.MThirdPerson:
            self.movementTokens.append(inputState.watchWithModifiers('forward', 'arrow_up', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('reverse', 'arrow_down', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('turnLeft', 'arrow_left', inputSource = inputState.WASD))
            self.movementTokens.append(inputState.watchWithModifiers('turnRight', 'arrow_right', inputSource = inputState.WASD))

    def disableControls(self, chat = False):
        if not self.controlsEnabled:
            return

        if self.mode == LocalControls.MFirstPerson:
            self.fpsCam.disableMouseMovement(False, not chat)

        self.ignore('alt')
        
        inputState.set('forward', False, inputSource = inputState.WASD)
        inputState.set('reverse', False, inputSource = inputState.WASD)
        inputState.set('slideLeft', False, inputSource = inputState.WASD)
        inputState.set('slideRight', False, inputSource = inputState.WASD)
        inputState.set('jump', False, inputSource = inputState.WASD)
        inputState.set('crouch', False, inputSource = inputState.WASD)
        inputState.set('walk', False, inputSource = inputState.WASD)
        inputState.set('use', False, inputSource = inputState.WASD)
        base.taskMgr.remove("LocalControls.handlePlayerControls")
        base.taskMgr.remove("LocalControls.handleFootsteps")
        self.controller.setLinearMovement(Vec3(0))
        self.controller.setAngularMovement(0)
        self.controlsEnabled = False

    def __handleStandUp(self):
        self.standingUp = True

    def __handleLand(self, fallDistance):
        self.playFootstep(1.5)
        if fallDistance > 8:
            base.localAvatar.handleJumpHardLand()
            #if self.mode == LocalControls.MFirstPerson:
            #    self.fpsCam.handleJumpHardLand()
        else:
            base.localAvatar.handleJumpLand()

    def playFootstep(self, volume = 1.0):
        if len(self.footstepSounds) > 0:
            self.lastFoot = not self.lastFoot
            mid = int(len(self.footstepSounds) / 2)
            if self.lastFoot:
                choices = self.footstepSounds[:mid]
            else:
                choices = self.footstepSounds[mid:]
            if self.currFootstepSound:
                self.currFootstepSound.stop()
            sound = random.choice(choices)
            sound.setVolume(volume * LocalControls.FootstepVolumeMod)
            sound.play()
            self.currFootstepSound = sound
        self.lastFootstepTime = globalClock.getFrameTime()
        
    def __handleFootsteps(self, task):
        time = globalClock.getFrameTime()
        speeds = self.speeds.length()
        if speeds > 0.1 and self.isOnGround():
            self.footstepIval = 1 / (min(speeds, self.idealFwd) / 6.0)
                
            if time - self.lastFootstepTime >= self.footstepIval:
                self.playFootstep(min(1, speeds / 15.0))
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

        self.speeds = Vec3(self.lastSpeeds)
        
        if abs(self.speeds.getX()) < 0.1:
            self.speeds.setX(0)
        if abs(self.speeds.getY()) < 0.1:
            self.speeds.setY(0)
        if abs(self.speeds.getZ()) < 0.1:
            self.speeds.setZ(0)
        
        self.controller.setLinearMovement(Vec3(self.speeds.getX(), self.speeds.getY(), 0))
        self.controller.setAngularMovement(self.speeds.getZ())

        onGround = self.isOnGround()
        if jump and onGround and not self.airborne:
            self.controller.startJump(5.0)
            self.playFootstep(1.5)
            self.airborne = True
        elif onGround and self.controller.movementState == "ground":
            # We landed
            self.airborne = False
            
        if walk:
            fctr = 0.6
            self.fwdSpeed = self.idealFwd * fctr
            self.revSpeed = self.idealRev * fctr
        elif not self.crouching:
            self.fwdSpeed = self.idealFwd
            self.revSpeed = self.idealRev
            
        if crouch and not self.crouching:
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
        
        return task.cont