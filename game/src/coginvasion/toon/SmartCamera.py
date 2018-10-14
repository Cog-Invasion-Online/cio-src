"""

  Filename: SmartCamera.py
  Created by: blach (27July14)

"""

from panda3d.core import CollisionTraverser, Point3, Vec3, CollisionNode
from panda3d.core import CollisionSegment, CollisionHandlerPusher
from panda3d.core import CollisionSphere, BitMask32, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionHandlerFloor
from panda3d.core import deg2Rad, TransformState

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import LerpFunctionInterval
from src.coginvasion.phys import PhysicsUtils
import math

class SmartCamera:
    UPDATE_TASK_NAME = "update_smartcamera"
    notify = directNotify.newCategory("SmartCamera")
    OTSIndex = 0

    def __init__(self):
        self.cTrav = CollisionTraverser('cam_traverser')
        base.pushCTrav(self.cTrav)
        self.cTrav.setRespectPrevTransform(1)
        self.default_pos = None
        self.parent = None
        self.initialized = False
        self.started = False
        self.camFloorRayNode = None
        self.ccRay2 = None
        self.ccRay2Node = None
        self.ccRay2NodePath = None
        self.ccRay2BitMask = None
        self.ccRay2MoveNodePath = None
        self.camFloorCollisionBroadcaster = None
        self.pointA = Point3(0)
        self.pointB = Point3(0)

        self.floorLineStart = Point3(0)
        self.camRadiusPoint = Point3(0)

        self.notify.debug("SmartCamera initialized!")

    def lerpCameraFov(self, fov, time):
        taskMgr.remove('cam-fov-lerp-play')
        oldFov = base.camLens.getHfov()
        if abs(fov - oldFov) > 0.1:

            def setCamFov(fov):
                base.camLens.setMinFov(fov/(4./3.))

            self.camLerpInterval = LerpFunctionInterval(setCamFov, fromData=oldFov, toData=fov, duration=time, name='cam-fov-lerp')
            self.camLerpInterval.start()

    def setCameraFov(self, fov):
        self.fov = fov
        if not (self.isPageDown or self.isPageUp):
            base.camLens.setMinFov(self.fov/(4./3.))

    def initCameraPositions(self):
        camHeight = max(base.localAvatar.getHeight(), 3.0)
        nrCamHeight = base.localAvatar.getHeight()
        heightScaleFactor = camHeight * 0.3333333333
        defLookAt = Point3(0.0, 1.5, camHeight)
        self.firstPersonCamPos = Point3(0.0, 0.7, nrCamHeight * 5.0)
        scXoffset = 3.0
        scPosition = (Point3(scXoffset - 1, -10.0, camHeight + 5.0), Point3(scXoffset, 2.0, camHeight))
        self.cameraPositions = [(Point3(0.0, -9.0 * heightScaleFactor, camHeight),
          defLookAt,
          Point3(0.0, camHeight, camHeight * 4.0),
          Point3(0.0, camHeight, camHeight * -1.0),
          0),
         (Point3(0.0, 0.7, camHeight),
          defLookAt,
          Point3(0.0, camHeight, camHeight * 1.33),
          Point3(0.0, camHeight, camHeight * 0.66),
          1),
         (Point3(0.0, -24.0 * heightScaleFactor, camHeight + 4.0),
          defLookAt,
          Point3(0.0, 1.5, camHeight * 4.0),
          Point3(0.0, 1.5, camHeight * -1.0),
          0),
         (Point3(0.0, -12.0 * heightScaleFactor, camHeight + 4.0),
          defLookAt,
          Point3(0.0, 1.5, camHeight * 4.0),
          Point3(0.0, 1.5, camHeight * -1.0),
          0)]
          
        gta = base.config.GetBool("want-gta-controls", False)
        if not gta:
            # Insert the two front facing camera angles.
            self.cameraPositions.insert(2, (Point3(5.7 * heightScaleFactor, 7.65 * heightScaleFactor, camHeight + 2.0),
                                            Point3(0.0, 1.0, camHeight),
                                            Point3(0.0, 1.0, camHeight * 4.0),
                                            Point3(0.0, 1.0, camHeight * -1.0),
                                            0))
            self.cameraPositions.insert(3,(Point3(0.0, 8.65 * heightScaleFactor, camHeight),
                                           Point3(0.0, 1.0, camHeight),
                                           Point3(0.0, 1.0, camHeight * 4.0),
                                           Point3(0.0, 1.0, camHeight * -1.0),
                                           0))
        else:
            # Insert an over the shoulder camera angle.
            self.cameraPositions.insert(self.OTSIndex, (Point3(1.0, -4.25 * heightScaleFactor, camHeight),
                                            Point3(1.0, 1.5, camHeight),
                                            Point3(0.0, camHeight, camHeight * 4.0),
                                            Point3(0.0, camHeight, camHeight * -1.0),
                                            0))

    def pageUp(self):
        if not base.localAvatar.avatarMovementEnabled:
            return
        if not self.isPageUp:
            self.isPageDown = 0
            self.isPageUp = 1
            self.lerpCameraFov(70, 0.6)
            self.setCameraPositionByIndex(self.cameraIndex)
        else:
            self.clearPageUpDown()

    def pageDown(self):
        if not base.localAvatar.avatarMovementEnabled:
            return
        if not self.isPageDown:
            self.isPageUp = 0
            self.isPageDown = 1
            self.lerpCameraFov(70, 0.6)
            self.setCameraPositionByIndex(self.cameraIndex)
        else:
            self.clearPageUpDown()

    def clearPageUpDown(self):
        if self.isPageDown or self.isPageUp:
            self.lerpCameraFov(self.fov, 0.6)
            self.isPageDown = 0
            self.isPageUp = 0
            self.setCameraPositionByIndex(self.cameraIndex)

    def nextCameraPos(self, forward):
        if not base.localAvatar.avatarMovementEnabled:
            return
        self.__cameraHasBeenMoved = 1
        if forward:
            self.cameraIndex += 1
            if self.cameraIndex > len(self.cameraPositions) - 1:
                self.cameraIndex = 0
        else:
            self.cameraIndex -= 1
            if self.cameraIndex < 0:
                self.cameraIndex = len(self.cameraPositions) - 1
        self.setCameraPositionByIndex(self.cameraIndex)

    def setCameraPositionByIndex(self, index):
        self.notify.debug('switching to camera position %s' % index)
        self.cameraIndex = index
        self.setCameraSettings(self.cameraPositions[index])
        
    def isOverTheShoulder(self):
        return self.cameraIndex == self.OTSIndex

    def setCameraSettings(self, camSettings):
        base.localAvatar.hideCrosshair()
        #if self.isOverTheShoulder() and base.localAvatar.avatarMovementEnabled:
        #    base.localAvatar.showCrosshair()
        #    spine = base.localAvatar.find("**/def_cageA")
        #    if spine.isEmpty():
        #        base.localAvatar.controlJoint(None, "torso", "def_cageA")
        #else:
        #    base.localAvatar.hideCrosshair()
        #    spine = base.localAvatar.find("**/def_spineA")
        #    if not spine.isEmpty():
        #        spine.detachNode()
        #        base.localAvatar.releaseJoint("torso", "def_cageA")
        self.setIdealCameraPos(camSettings[0])
        if self.isPageUp and self.isPageDown or not self.isPageUp and not self.isPageDown:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[1])
        elif self.isPageUp:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[2])
        elif self.isPageDown:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[3])
        else:
            self.notify.error('This case should be impossible.')
        self.__disableSmartCam = camSettings[4]
        if self.__disableSmartCam:
            self.putCameraFloorRayOnAvatar()
            self.cameraZOffset = 0.0

    def set_default_pos(self, pos):
        self.default_pos = pos
        #self.notify.debug("default camera position set as (%s, %s, %s)" % (x, y, z))

    def get_default_pos(self):
        return self.default_pos

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def getVisibilityPoint(self):
        return Point3(0.0, 0.0, self.getIdealCameraPos()[2])

    def setLookAtPoint(self, la):
        self.__curLookAt = Point3(la)

    def getLookAtPoint(self):
        return Point3(self.__curLookAt)

    def setIdealCameraPos(self, pos):
        self.__idealCameraPos = Point3(pos)
        self.updateSmartCameraCollisionLineSegment()

    def getIdealCameraPos(self):
        return Point3(self.__idealCameraPos)

    def getCompromiseCameraPos(self):
        if self.__idealCameraObstructed == 0:
            compromisePos = self.getIdealCameraPos()
        else:
            visPnt = self.getVisibilityPoint()
            idealPos = self.getIdealCameraPos()
            distance = Vec3(idealPos - visPnt).length()
            ratio = self.closestObstructionDistance / distance
            compromisePos = idealPos * ratio + visPnt * (1 - ratio)
            
            if not base.localAvatar.battleControls:
                # Lift the camera up in classic controls.
                # In third person battle controls, we want to just move the camera closer to the player.
                liftMult = 1.0 - ratio * ratio
                compromisePos = Point3(compromisePos[0], compromisePos[1], compromisePos[2] + base.localAvatar.getHeight() * 0.4 * liftMult)
        if not base.localAvatar.battleControls:
            compromisePos.setZ(compromisePos[2] + self.cameraZOffset)
        return compromisePos

    def updateSmartCameraCollisionLineSegment(self):
        pointB = self.getIdealCameraPos()
        pointA = self.getVisibilityPoint()
        vectorAB = Vec3(pointB - pointA)
        lengthAB = vectorAB.length()
        if lengthAB > 0.001:
            self.pointA = pointA
            self.pointB = pointB

    def initializeSmartCamera(self):
        self.__idealCameraObstructed = 0
        self.closestObstructionDistance = 0.0
        self.cameraIndex = 0
        self.cameraPositions = []
        self.auxCameraPositions = []
        self.cameraZOffset = 0.0
        self.setGeom(render)
        self.__onLevelGround = 0
        self.__camCollCanMove = 0
        self.__disableSmartCam = 0
        self.initializeSmartCameraCollisions()
        self._smartCamEnabled = False
        self.isPageUp = 0
        self.isPageDown = 0
        self.fov = CIGlobals.DefaultCameraFov

    def enterFirstPerson(self):
        self.stop_smartcamera()
        if hasattr(self.get_parent(), 'toon_head'):
            head = self.get_parent().toon_head
            camera.reparentTo(head)
        camera.setPos(0, -0.35, 0)
        camera.setHpr(0, 0, 0)

    def exitFirstPerson(self):
        self.initialize_smartcamera()
        self.initialize_smartcamera_collisions()
        self.start_smartcamera()

    def putCameraFloorRayOnAvatar(self):
        self.floorLineStart = Point3(0, 0, 5)

    def putCameraFloorRayOnCamera(self):
        self.floorLineStart = self.getIdealCameraPos() + (0, 0, 10)

    def recalcCameraSphere(self):
        nearPlaneDist = base.camLens.getNear()
        hFov = base.camLens.getHfov()
        vFov = base.camLens.getVfov()
        hOff = nearPlaneDist * math.tan(deg2Rad(hFov / 2.0))
        vOff = nearPlaneDist * math.tan(deg2Rad(vFov / 2.0))
        camPnts = [Point3(hOff, nearPlaneDist, vOff),
         Point3(-hOff, nearPlaneDist, vOff),
         Point3(hOff, nearPlaneDist, -vOff),
         Point3(-hOff, nearPlaneDist, -vOff),
         Point3(0.0, 0.0, 0.0)]
        avgPnt = Point3(0.0, 0.0, 0.0)
        for camPnt in camPnts:
            avgPnt = avgPnt + camPnt

        avgPnt = avgPnt / len(camPnts)
        sphereRadius = 0.0
        for camPnt in camPnts:
            dist = Vec3(camPnt - avgPnt).length()
            if dist > sphereRadius:
                sphereRadius = dist

        avgPnt = Point3(avgPnt)
        self.camRadiusPoint = avgPnt

    def setGeom(self, geom):
        self.__geom = geom

    def initializeSmartCameraCollisions(self):
        if self.initialized:
            return
        self.initialized = True

    def deleteSmartCameraCollisions(self):
        self.initialized = False
        return

    def startUpdateSmartCamera(self):
        if self.started:
            return
        self.__floorDetected = 0
        self.__cameraHasBeenMoved = 1
        self.recalcCameraSphere()
        self.__instantaneousCamPos = camera.getPos()
        self.__disableSmartCam = 0
        self.__lastPosWrtRender = camera.getPos(render) + 1
        self.__lastHprWrtRender = camera.getHpr(render) + 1
        self.updateSmartCameraCollisionLineSegment()
        taskName = base.localAvatar.taskName('updateSmartCamera')
        taskMgr.remove(taskName)
        taskMgr.add(self.updateSmartCamera, taskName, priority=47)
        self.started = True

    def stopUpdateSmartCamera(self):
        taskName = base.localAvatar.taskName('updateSmartCamera')
        taskMgr.remove(taskName)
        camera.setPos(self.getIdealCameraPos())
        self.started = False

    def updateSmartCamera(self, task):
        if base.localAvatar.battleControls and base.localAvatar.isFirstPerson():
            return Task.cont

        if not self.__camCollCanMove and not self.__cameraHasBeenMoved:
            if self.__lastPosWrtRender == camera.getPos(render):
                if self.__lastHprWrtRender == camera.getHpr(render):
                    return Task.cont
        self.__cameraHasBeenMoved = 0
        self.__lastPosWrtRender = camera.getPos(render)
        self.__lastHprWrtRender = camera.getHpr(render)
        self.__idealCameraObstructed = 0
        
        self.updateSmartCameraCollisionLineSegment()
        
        if not self.__disableSmartCam:

            pointA = render.getRelativePoint(camera.getParent(), self.pointA)
            pointB = render.getRelativePoint(camera.getParent(), self.pointB)

            mask = CIGlobals.WallGroup | CIGlobals.CameraGroup
            if base.localAvatar.battleControls:
                mask |= (CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)

            result = PhysicsUtils.rayTestClosestNotMe(base.localAvatar, pointA, pointB, mask)
            if result:
                self.handleCameraObstruction(result)

            if not self.__onLevelGround:
                self.handleCameraFloorInteraction()
        if not self.__idealCameraObstructed:
            self.nudgeCamera()
        
        return Task.cont

    def positionCameraWithPusher(self, pos, lookAt):
        camera.setPos(pos)
        #self.ccPusherTrav.traverse(self.__geom)
        camera.lookAt(lookAt)

    def nudgeCamera(self):
        CLOSE_ENOUGH = 0.1
        curCamPos = self.__instantaneousCamPos
        curCamHpr = camera.getHpr()
        targetCamPos = self.getCompromiseCameraPos()
        targetCamLookAt = self.getLookAtPoint()
        posDone = 0
        if Vec3(curCamPos - targetCamPos).length() <= CLOSE_ENOUGH:
            camera.setPos(targetCamPos)
            posDone = 1
        camera.setPos(targetCamPos)
        camera.lookAt(targetCamLookAt)
        targetCamHpr = camera.getHpr()
        hprDone = 0
        if Vec3(curCamHpr - targetCamHpr).length() <= CLOSE_ENOUGH:
            hprDone = 1
        if posDone and hprDone:
            return
        lerpRatio = 0.15
        lerpRatio = 1 - pow(1 - lerpRatio, globalClock.getDt() * 30.0)
        self.__instantaneousCamPos = targetCamPos * lerpRatio + curCamPos * (1 - lerpRatio)
        if self.__disableSmartCam or not self.__idealCameraObstructed:
            newHpr = targetCamHpr * lerpRatio + curCamHpr * (1 - lerpRatio)
        else:
            newHpr = targetCamHpr
        camera.setPos(self.__instantaneousCamPos)
        camera.setHpr(newHpr)

    def popCameraToDest(self):
        newCamPos = self.getCompromiseCameraPos()
        newCamLookAt = self.getLookAtPoint()
        self.positionCameraWithPusher(newCamPos, newCamLookAt)
        self.__instantaneousCamPos = camera.getPos()

    def handleCameraObstruction(self, camObstrCollisionEntry):

        # Convert world space hit position to avatar space.
        collisionPoint = camera.getParent().getRelativePoint(render, camObstrCollisionEntry.getHitPos())

        collisionVec = Vec3(collisionPoint - self.pointA)
        distance = collisionVec.length()
        self.__idealCameraObstructed = 1
        self.closestObstructionDistance = distance
        self.popCameraToDest()

    def handleCameraFloorInteraction(self):
        if self.__onLevelGround or base.localAvatar.battleControls:
            return

        self.putCameraFloorRayOnCamera()

        pointA = render.getRelativePoint(camera.getParent(), self.floorLineStart)
        pointB = pointA + (Vec3.down() * 1000)
        result = PhysicsUtils.rayTestClosestNotMe(base.localAvatar, pointA, pointB, CIGlobals.FloorGroup)
        if not result:
            return

        camObstrCollisionEntry = result
        camHeightFromFloor = (camera.getRelativePoint(render, camObstrCollisionEntry.getHitPos())).getZ()
        heightOfFloorUnderCamera = (camera.getPos()[2] - CIGlobals.FloorOffset) + camHeightFromFloor
        self.cameraZOffset = camera.getPos()[2] + camHeightFromFloor
        if self.cameraZOffset < 0:
            self.cameraZOffset = self.cameraZOffset * 0.33333333329999998
            camHeight = max(base.localAvatar.getHeight(), 3.0)
            if self.cameraZOffset < -(camHeight * 0.5):
                if self.cameraZOffset < -camHeight:
                    self.cameraZOffset = 0.0
                else:
                    self.cameraZOffset = -(camHeight * 0.5)
        if self.__floorDetected == 0:
            self.__floorDetected = 1
            self.popCameraToDest()
