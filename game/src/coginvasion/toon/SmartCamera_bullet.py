from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Point3, Vec3

from src.coginvasion.globals import CIGlobals

class SmartCamera:

    def __init__(self):
        self.cameraPositions = []
        self.isPageDown = 0
        self.isPageUp = 0
        self.__cameraHasBeenMoved = 0
        self.cameraIndex = 0
        self.__disableSmartCam = 0
        self.closestObstructionDistance = 0
        self.__idealCameraPos = Point3(0)
        self.__idealCameraObstructed = 0
        self.__curLookAt = Point3(0)
        self.cameraZOffset = 0
        self.__onLevelGround = 0
        self.__camCollCanMove = 0
        self._smartCamEnabled = False
        self.fov = CIGlobals.DefaultCameraFov
        self.__geom = None

    def setGeom(self, geom):
        self.__geom = geom

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

    def setCameraSettings(self, camSettings):
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

    def getVisibilityPoint(self):
        return Point3(0.0, 0.0, base.localAvatar.getHeight())

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
            liftMult = 1.0 - ratio * ratio
            compromisePos = Point3(compromisePos[0], compromisePos[1], compromisePos[2] + base.localAvatar.getHeight() * 0.4 * liftMult)
        compromisePos.setZ(compromisePos[2] + self.cameraZOffset)
        return compromisePos

    def updateSmartCamera(self, task):
        pass