"""

Copyright (c) Brian Lach. All rights reserved.

@file SmoothWalker.py
@author Brian Lach
@date 2016-07-20

@purpose Gradually accellerates/decellerates movement instead of abruptly starting and stopping.

"""

from panda3d.core import Vec3, Mat3, Point3

from direct.showbase.InputStateGlobal import inputState

from direct.task.Task import Task

from direct.controls.GravityWalker import GravityWalker
from direct.directnotify.DirectNotifyGlobal import directNotify

class SmoothWalker(GravityWalker):
    notify = directNotify.newCategory('SmoothWalker')

    def __init__(self):
        GravityWalker.__init__(self)

        self.hasSetForwardInitTime = False
        self.hasSetForwardStopTime = False
        self.isAtZeroForward = False
        self.fowardInitTime = 0.0
        self.forwardStopTime = 0.0

        self.hasSetReverseInitTime = False
        self.hasSetReverseStopTime = False
        self.isAtZeroReverse = False
        self.reverseStopTime = 0.0
        self.reverseInitTime = 0.0

        self.hasSetSLeftInitTime = False
        self.hasSetSLeftStopTime = False
        self.isAtZeroSLeft = False
        self.sLeftInitTime = 0.0
        self.sLeftStopTime = 0.0

        self.hasSetSRightInitTime = False
        self.hasSetSRightStopTime = False
        self.isAtZeroSRight = False
        self.sRightInitTime = 0.0
        self.sRightStopTime = 0.0


    def handleAvatarControls(self, task):
        """
        Check on the arrow keys and update the avatar.
        """
        # get the button states:
        run = inputState.isSet("run")
        forward = inputState.isSet("forward")
        reverse = inputState.isSet("reverse")
        turnLeft = inputState.isSet("turnLeft")
        turnRight = inputState.isSet("turnRight")
        slideLeft = inputState.isSet("slideLeft")
        slideRight = inputState.isSet("slideRight")
        jump = inputState.isSet("jump")

        avatarControlForwardSpeed = 0
        avatarControlReverseSpeed = 0
        avatarControlSLeftSpeed = 0
        avatarControlSRightSpeed = 0

        if forward:
            if not self.hasSetForwardInitTime:
                self.forwardInitTime = globalClock.getFrameTime()
                self.hasSetForwardInitTime = True
                self.isAtZeroForward = False
                self.hasSetForwardStopTime = False
            timeSinceForwardSet = globalClock.getFrameTime() - self.forwardInitTime
            if timeSinceForwardSet == 0:
                avatarControlForwardSpeed = 0.0
            else:
                avatarControlForwardSpeed = min((timeSinceForwardSet / self.avatarControlForwardSpeed) * 750,
                                            self.avatarControlForwardSpeed)
                print avatarControlForwardSpeed
        else:
            if self.hasSetForwardInitTime:
                self.hasSetForwardInitTime = False
            if not self.hasSetForwardStopTime:
                self.forwardStopTime = globalClock.getFrameTime()
                self.hasSetForwardStopTime = True
            timeSinceForwardStop = globalClock.getFrameTime() - self.forwardStopTime
            if timeSinceForwardStop == 0:
                avatarControlForwardSpeed = 16.0
            elif not self.isAtZeroForward:
                avatarControlForwardSpeed = self.avatarControlForwardSpeed - (timeSinceForwardStop * 50)
                print avatarControlForwardSpeed
                if avatarControlForwardSpeed <= 0.5:
                    avatarControlForwardSpeed = 0.0
                    self.isAtZeroForward = True
                    self.hasSetForwardStopTime = False

        if reverse:
            if not self.hasSetReverseInitTime:
                self.reverseInitTime = globalClock.getFrameTime()
                self.hasSetReverseInitTime = True
                self.isAtZeroReverse = False
                self.hasSetReverseStopTime = False
            timeSinceReverseSet = globalClock.getFrameTime() - self.reverseInitTime
            if timeSinceReverseSet == 0:
                avatarControlReverseSpeed = 0.0
            else:
                avatarControlReverseSpeed = min((timeSinceReverseSet / self.avatarControlReverseSpeed) * 400,
                                            self.avatarControlReverseSpeed)
                print avatarControlReverseSpeed
        else:
            if self.hasSetReverseInitTime:
                self.hasSetReverseInitTime = False
            if not self.hasSetReverseStopTime:
                self.reverseStopTime = globalClock.getFrameTime()
                self.hasSetReverseStopTime = True
            timeSinceReverseStop = globalClock.getFrameTime() - self.reverseStopTime
            if timeSinceReverseStop == 0:
                avatarControlReverseSpeed = 16.0
            elif not self.isAtZeroReverse:
                avatarControlReverseSpeed = self.avatarControlReverseSpeed - (timeSinceReverseStop * 20)
                print avatarControlReverseSpeed
                if avatarControlReverseSpeed <= 0.5:
                    avatarControlReverseSpeed = 0.0
                    self.isAtZeroReverse = True
                    self.hasSetReverseStopTime = False

        if slideLeft:
            if not self.hasSetSLeftInitTime:
                self.sLeftInitTime = globalClock.getFrameTime()
                self.hasSetSLeftInitTime = True
                self.isAtZeroSLeft = False
                self.hasSetSLeftStopTime = False
            timeSinceSLeftSet = globalClock.getFrameTime() - self.sLeftInitTime
            if timeSinceSLeftSet == 0:
                avatarControlSLeftSpeed = 0.0
            else:
                avatarControlSLeftSpeed = min((timeSinceSLeftSet / self.avatarControlForwardSpeed) * 750,
                                            self.avatarControlForwardSpeed)
                print avatarControlSLeftSpeed
        else:
            if self.hasSetSLeftInitTime:
                self.hasSetSLeftInitTime = False
            if not self.hasSetSLeftStopTime:
                self.sLeftStopTime = globalClock.getFrameTime()
                self.hasSetSLeftStopTime = True
            timeSinceSLeftStop = globalClock.getFrameTime() - self.sLeftStopTime
            if timeSinceSLeftStop == 0:
                avatarControlSLeftSpeed = 16.0
            elif not self.isAtZeroSLeft:
                avatarControlSLeftSpeed = self.avatarControlForwardSpeed - (timeSinceSLeftStop * 50)
                print avatarControlSLeftSpeed
                if avatarControlSLeftSpeed <= 0.5:
                    avatarControlSLeftSpeed = 0.0
                    self.isAtZeroSLeft = True
                    self.hasSetSLeftStopTime = False

        if slideRight:
            if not self.hasSetSRightInitTime:
                self.sRightInitTime = globalClock.getFrameTime()
                self.hasSetSRightInitTime = True
                self.isAtZeroSRight = False
                self.hasSetSRightStopTime = False
            timeSinceSRightSet = globalClock.getFrameTime() - self.sRightInitTime
            if timeSinceSRightSet == 0:
                avatarControlSRightSpeed = 0.0
            else:
                avatarControlSRightSpeed = min((timeSinceSRightSet / self.avatarControlForwardSpeed) * 750,
                                            self.avatarControlForwardSpeed)
                print avatarControlSRightSpeed
        else:
            if self.hasSetSRightInitTime:
                self.hasSetSRightInitTime = False
            if not self.hasSetSRightStopTime:
                self.sRightStopTime = globalClock.getFrameTime()
                self.hasSetSRightStopTime = True
            timeSinceSRightStop = globalClock.getFrameTime() - self.sRightStopTime
            if timeSinceSRightStop == 0:
                avatarControlSRightSpeed = 16.0
            elif not self.isAtZeroSRight:
                avatarControlSRightSpeed = self.avatarControlForwardSpeed - (timeSinceSRightStop * 50)
                print avatarControlSRightSpeed
                if avatarControlSRightSpeed <= 0.5:
                    avatarControlSRightSpeed = 0.0
                    self.isAtZeroSRight = True
                    self.hasSetSRightStopTime = False

        # Check for Auto-Run
        #if 'localAvatar' in __builtins__:
        #    if base.localAvatar and base.localAvatar.getAutoRun():
        #        forward = 1
        #        reverse = 0

        # Determine what the speeds are based on the buttons:
        self.speed=(avatarControlForwardSpeed or
                    -avatarControlReverseSpeed)
        # Slide speed is a scaled down version of forward speed
        # Note: you can multiply a factor in here if you want slide to
        # be slower than normal walk/run. Let's try full speed.
        #self.slideSpeed=(slideLeft and -self.avatarControlForwardSpeed*0.75 or
        #                 slideRight and self.avatarControlForwardSpeed*0.75)
        self.slideSpeed=(-avatarControlSLeftSpeed or
                        avatarControlSRightSpeed)
        self.rotationSpeed=not (slideLeft or slideRight) and (
                (turnLeft and self.avatarControlRotateSpeed) or
                (turnRight and -self.avatarControlRotateSpeed))

        if self.speed and self.slideSpeed:
            self.speed *= GravityWalker.DiagonalFactor
            self.slideSpeed *= GravityWalker.DiagonalFactor

        debugRunning = inputState.isSet("debugRunning")
        if(debugRunning):
            self.speed*=base.debugRunningMultiplier
            self.slideSpeed*=base.debugRunningMultiplier
            self.rotationSpeed*=1.25

        if self.needToDeltaPos:
            self.setPriorParentVector()
            self.needToDeltaPos = 0
        if self.wantDebugIndicator:
            self.displayDebugInfo()
        if self.lifter.isOnGround():
            if self.isAirborne:
                self.isAirborne = 0
                assert self.debugPrint("isAirborne 0 due to isOnGround() true")
                impact = self.lifter.getImpactVelocity()
                if impact < -30.0:
                    messenger.send("jumpHardLand")
                    self.startJumpDelay(0.3)
                else:
                    messenger.send("jumpLand")
                    if impact < -5.0:
                        self.startJumpDelay(0.2)
                    # else, ignore the little potholes.
            assert self.isAirborne == 0
            self.priorParent = Vec3.zero()
            if jump and self.mayJump:
                # The jump button is down and we're close
                # enough to the ground to jump.
                self.lifter.addVelocity(self.avatarControlJumpForce)
                messenger.send("jumpStart")
                self.isAirborne = 1
                assert self.debugPrint("isAirborne 1 due to jump")
        else:
            if self.isAirborne == 0:
                assert self.debugPrint("isAirborne 1 due to isOnGround() false")
            self.isAirborne = 1

        self.__oldPosDelta = self.avatarNodePath.getPosDelta(render)
        # How far did we move based on the amount of time elapsed?
        self.__oldDt = ClockObject.getGlobalClock().getDt()
        dt=self.__oldDt

        # Check to see if we're moving at all:
        self.moving = self.speed or self.slideSpeed or self.rotationSpeed or (self.priorParent!=Vec3.zero())
        if self.moving:
            distance = dt * self.speed
            slideDistance = dt * self.slideSpeed
            rotation = dt * self.rotationSpeed

            # Take a step in the direction of our previous heading.
            if distance or slideDistance or self.priorParent != Vec3.zero():
                # rotMat is the rotation matrix corresponding to
                # our previous heading.
                rotMat=Mat3.rotateMatNormaxis(self.avatarNodePath.getH(), Vec3.up())
                if self.isAirborne:
                    forward = Vec3.forward()
                else:
                    contact = self.lifter.getContactNormal()
                    forward = contact.cross(Vec3.right())
                    # Consider commenting out this normalize.  If you do so
                    # then going up and down slops is a touch slower and
                    # steeper terrain can cut the movement in half.  Without
                    # the normalize the movement is slowed by the cosine of
                    # the slope (i.e. it is multiplied by the sign as a
                    # side effect of the cross product above).
                    forward.normalize()
                self.vel=Vec3(forward * distance)
                if slideDistance:
                    if self.isAirborne:
                        right = Vec3.right()
                    else:
                        right = forward.cross(contact)
                        # See note above for forward.normalize()
                        right.normalize()
                    self.vel=Vec3(self.vel + (right * slideDistance))
                self.vel=Vec3(rotMat.xform(self.vel))
                step=self.vel + (self.priorParent * dt)
                self.avatarNodePath.setFluidPos(Point3(
                        self.avatarNodePath.getPos()+step))
            self.avatarNodePath.setH(self.avatarNodePath.getH()+rotation)
        else:
            self.vel.set(0.0, 0.0, 0.0)
        if self.moving or jump:
            messenger.send("avatarMoving")
        return Task.cont
