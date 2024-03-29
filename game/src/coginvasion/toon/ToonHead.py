"""

  Filename: ToonHead.py
  Created by: blach (??July14)
  Remade: (28Oct14)

"""

from panda3d.core import PerspectiveLens, LensNode, Texture, Point3, Mat4, ModelNode, NodePath, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, Sequence, LerpHprInterval
from direct.actor import Actor
from src.coginvasion.toon import ToonGlobals

from src.coginvasion.globals import CIGlobals

import random

class ToonHead(Actor.Actor):
    notify = directNotify.newCategory('ToonHead')

    if metadata.PROCESS == 'client':
        EyesOpen = 'phase_3/maps/eyes.mat'
        EyesClosed = 'phase_3/maps/eyesClosed.mat'
        EyesOpenSad = 'phase_3/maps/eyesSad.mat'
        EyesClosedSad = 'phase_3/maps/eyesSadClosed.mat'
        
    LeftA = Point3(0.06, 0.0, 0.14)
    LeftB = Point3(-0.13, 0.0, 0.1)
    LeftC = Point3(-0.05, 0.0, 0.0)
    LeftD = Point3(0.06, 0.0, 0.0)
    RightA = Point3(0.13, 0.0, 0.1)
    RightB = Point3(-0.06, 0.0, 0.14)
    RightC = Point3(-0.06, 0.0, 0.0)
    RightD = Point3(0.05, 0.0, 0.0)
    LeftAD = Point3(LeftA[0] - LeftA[2] * (LeftD[0] - LeftA[0]) / (LeftD[2] - LeftA[2]), 0.0, 0.0)
    LeftBC = Point3(LeftB[0] - LeftB[2] * (LeftC[0] - LeftB[0]) / (LeftC[2] - LeftB[2]), 0.0, 0.0)
    RightAD = Point3(RightA[0] - RightA[2] * (RightD[0] - RightA[0]) / (RightD[2] - RightA[2]), 0.0, 0.0)
    RightBC = Point3(RightB[0] - RightB[2] * (RightC[0] - RightB[0]) / (RightC[2] - RightB[2]), 0.0, 0.0)
    LeftMid = (LeftA + LeftB + LeftC + LeftD) / 4.0
    RightMid = (RightA + RightB + RightC + RightD) / 4.0
    
    MaxPupilLook = 0.07
    
    EyeStateClosed = 0
    EyeStateOpened = 1
    ClosedDuration = 0.15

    def __init__(self, cr):
        try:
            self.ToonHead_initialized
            return
        except:
            self.ToonHead_initialized = 1
        Actor.Actor.__init__(self)
        self.cr = cr
        self.head = None
        self.headType = None
        self.gender = None
        self.eyeLensNP = None
        self.__eyelashOpened = None
        self.__eyelashClosed = None
        self.__eyes = None
        self.__lpupil = None
        self.__rpupil = None
        self.pupils = []
        self.lookAroundTaskName = "lookAroundTask" + str(id(self))
        self.doLookAroundTaskName = "doLookAround" + str(id(self))
        self.doBlinkTaskName = "doBlinkTask" + str(id(self))
        
        self.eyeTarget = None
        self.targetIsNew = True
        self.lastEyeTarget = None
        self.eyeTargetLastPos = Point3(0)
        self.eyeTargetBoredTime = 0.0
        self.eyeTargetLastMove = 0
        self.eyeTargetTime = 0
        
        self.eyeStateTime = 0
        self.eyeState = self.EyeStateOpened
        self.eyesOpenDuration = 5
        
        return
        
    def getPupilDistance(self):
        """
        Returns the average distance of the two pupils from center.
        """
        left, right = self.getPupils()
        return (left.getPos().length() + right.getPos().length()) / 2.0
    
    def getLeftPupil(self):
        return self.__lpupil

    def getRightPupil(self):
        return self.__rpupil

    def getPupils(self):
        return [self.__lpupil, self.__rpupil]

    def generateHead(self, gender, head, headType, forGui = 0):

        def stashMuzzles(length, stashNeutral=0):
            if stashNeutral:
                if length == "short":
                    self.findAllMatches('**/muzzle-long-neutral;+s').stash()
                elif length == "long":
                    self.findAllMatches('**/muzzle-short-neutral;+s').stash()
            else:
                if length == "short":
                    if self.find('**/muzzle-long-neutral;+s').isStashed():
                        self.find('**/muzzle-long-neutral;+s').unstash()
                elif length == "long":
                    if self.find('**/muzzle-short-neutral;+s').isStashed():
                        self.find('**/muzzle-short-neutral;+s').unstash()
            self.findAllMatches('**/muzzle-' + length + '-s*;+s').stash()
            self.findAllMatches('**/muzzle-' + length + '-laugh;+s').stash()
            self.findAllMatches('**/muzzle-' + length + '-angry;+s').stash()

        def stashParts(length):
            for part in self.findAllMatches('**/*' + length + '*;+s'):
                part.stash()

        self.gender = gender
        self.animal = head
        self.head = headType
        _modelDetail = "1000"
        if head != "dog":
            self.loadModel("phase_3/models/char/%s-heads-%s.bam" % (head, _modelDetail), 'head')
        else:
            self.loadModel("phase_3/models/char/tt_a_chr_%s_head_%s.bam" % (headType, _modelDetail), 'head')
            partAnimations = {}

            # Load the body part animations.
            for animName in ToonGlobals.ANIMATIONS:
                animationData = list(ToonGlobals.ANIMATIONS[animName])
                animPath = None

                if len(animationData) == 2:
                    animPhase = animationData[0]
                    animFile = animationData[1]

                    # Let's create the path for the animation.
                    animPath = ToonGlobals.BASE_MODEL % (animPhase, headType, '',
                        'head', animFile)

                    if '_-' in animPath:
                        animPath = animPath.replace('_-', '-')

                    if '__' in animPath:
                        animPath = animPath.replace('__', '_')

                partAnimations[animName] = animPath

            self.loadAnims(partAnimations, 'head')

            _pupilL = self.findAllMatches('**/def_left_pupil')
            _pupilR = self.findAllMatches('**/def_right_pupil')
        if headType == "1":
            stashParts("long")
            stashMuzzles("long", stashNeutral=0)
            stashMuzzles("short", stashNeutral=1)
            _pupilL = self.findAllMatches('**/joint_pupilL_short')
            _pupilR = self.findAllMatches('**/joint_pupilR_short')
        elif headType == "2":
            if head == "mouse":
                stashParts("short")
                stashMuzzles("short", stashNeutral=1)
                stashMuzzles("long", stashNeutral=0)
                _pupilL = self.findAllMatches('**/joint_pupilL_long')
                _pupilR = self.findAllMatches('**/joint_pupilR_long')
            else:
                stashParts("long")
                stashMuzzles("short", stashNeutral=0)
                stashMuzzles("long", stashNeutral=1)
                _pupilL = self.findAllMatches('**/joint_pupilL_short')
                _pupilR = self.findAllMatches('**/joint_pupilR_short')
            if head == "rabbit":
                self.findAllMatches('**/head-long').unstash()
                self.findAllMatches('**/head-front-long').unstash()
                #self.findAllMatches('**/head-front-short').stash()
                #self.findAllMatches('**/head-short').stash()
        elif headType == "3":
            stashParts("short")
            stashMuzzles("long", stashNeutral=0)
            stashMuzzles("short", stashNeutral=1)
            _pupilL = self.findAllMatches('**/joint_pupilL_long')
            _pupilR = self.findAllMatches('**/joint_pupilR_long')
            if head == "rabbit":
                self.findAllMatches('**/head-long').stash()
                self.findAllMatches('**/head-front-long').stash()
                self.findAllMatches('**/head-front-short').unstash()
                self.findAllMatches('**/head-short').unstash()
        elif headType == "4":
            stashParts("short")
            stashMuzzles("short", stashNeutral=0)
            stashMuzzles("long", stashNeutral=1)
            _pupilL = self.findAllMatches('**/joint_pupilL_long')
            _pupilR = self.findAllMatches('**/joint_pupilR_long')
        self.pupils.append(_pupilL)
        self.pupils.append(_pupilR)
        self.fixEyes()
        if self.gender == "girl":
            self.setupEyelashes()
        
        if not forGui:
            if not self.eyeLensNP:
                lens = PerspectiveLens()
                lens.setMinFov(180.0 / (4./3.))
                node = LensNode('toonEyes', lens)
                node.activateLens(0)
                #node.showFrustum()
                self.eyeLensNP = self.attachNewNode(node)
                self.eyeLensNP.setZ(self.getHeight() - 0.5)
                self.eyeLensNP.setY(-1)
            self.setEyesOpenDuration()
            taskMgr.add(self.__eyesLookTask, "toonHeadEyesLook-" + str(id(self)))
        return
        
    def setEyesOpenDuration(self):
        self.eyesOpenDuration = random.uniform(0.5, 7.0)
        
    def hasPupils(self):
        return CIGlobals.isNodePathOk(self.__lpupil) and CIGlobals.isNodePathOk(self.__rpupil)
        
    def setEyeTarget(self, target):
        self.lastEyeTarget = self.eyeTarget
        self.targetIsNew = True
        self.eyeTarget = target
        self.eyeTargetTime = globalClock.getFrameTime()
        self.eyeTargetLastMove = self.eyeTargetTime
        if isinstance(target, NodePath):
            self.eyeTargetLastPos = target.getPos(render)
        else:
            self.eyeTargetLastPos = target
        # How long until we get bored of this eye target?
        self.eyeTargetBoredTime = random.uniform(6.0, 10.0)
        
        # Blink when we get a new eye target, so our eyes don't strangely teleport
        self.blink()
        
    def clearEyeTarget(self):
        self.lastEyeTarget = self.eyeTarget
        self.eyeTarget = None
        self.eyeTargetTime = 0
        self.eyeTargetLastMove = 0
        self.eyeTargetLastPos = Point3(0)
        
    def hasEyeTarget(self):
        if isinstance(self.eyeTarget, NodePath):
            return CIGlobals.isNodePathOk(self.eyeTarget)
            
        return self.eyeTarget is not None
        
    def blink(self):
        self.closeEyes()
        self.setEyeState(self.EyeStateClosed)
        
    def setEyeState(self, state):
        self.eyeState = state
        self.eyeStateTime = globalClock.getFrameTime()
        
    def lookEyesAtTarget(self, eyeTarget):
        if isinstance(eyeTarget, NodePath):
            if hasattr(base, 'localAvatar') and eyeTarget == base.localAvatar and base.localAvatar.isFirstPerson():
                self.lookPupilsAt(camera, Point3(0))
            elif hasattr(eyeTarget, 'getHeight'):
                self.lookPupilsAt(eyeTarget, Point3(0, 0, eyeTarget.getHeight() * 0.85))
            else:
                self.lookPupilsAt(eyeTarget, Point3(0))
        else:
            self.lookPupilsAt(None, eyeTarget)
        
    def __eyesLookTask(self, task):
        if not self.hasPupils():
            return task.done
        
        now = globalClock.getFrameTime()
        
        eyeStateElapsed = now - self.eyeStateTime
        # Should we blink?
        if self.eyeState == self.EyeStateClosed and eyeStateElapsed >= self.ClosedDuration:
            self.openEyes()
            self.setEyeState(self.EyeStateOpened)
            self.setEyesOpenDuration()
        elif self.eyeState == self.EyeStateOpened and eyeStateElapsed >= self.eyesOpenDuration:
            self.blink()
            
        if self.hasEyeTarget():
            if self.targetIsNew:
                self.lookPupilsMiddle()
                self.targetIsNew = False
            pDist = self.getPupilDistance()
            # did our eye target move?
            if isinstance(self.eyeTarget, NodePath):
                targetIsPoint = False
                # actual objects are more interesting, look longer
                boredTime = self.eyeTargetBoredTime * 2
                currTargetPos = self.eyeTarget.getPos(self.eyeLensNP)
            else:
                targetIsPoint = True
                boredTime = self.eyeTargetBoredTime * 0.5
                currTargetPos = self.eyeTarget
            
            if pDist > self.MaxPupilLook or not self.eyeLensNP.node().isInView(currTargetPos):
                # Target no longer in line-of-sight
                self.clearEyeTarget()
                return task.cont
            
            if not targetIsPoint:
                if (currTargetPos - self.eyeTargetLastPos).lengthSquared() > 0.01:
                    self.eyeTargetLastMove = now
                elif (now - self.eyeTargetLastMove) > boredTime * 0.5:
                    # We get bored twice as fast if our eye target is not moving
                    self.clearEyeTarget()
                    return task.cont
                
            if (now - self.eyeTargetTime) > boredTime:
                self.clearEyeTarget()
                return task.cont
                
            self.lookEyesAtTarget(self.eyeTarget)

            self.eyeTargetLastPos = currTargetPos
        else:            
            # find a new eye target
            target = None
            
            avOrPoint = random.randint(0, 1)
            if avOrPoint == 0:
                visible = []
                avs = list(base.avatars)
                if hasattr(base, 'localAvatar'):
                    avs.append(base.localAvatar)
                for avatar in avs:
                    if avatar == self.lastEyeTarget or avatar == self:
                        continue
                    apos = avatar.getPos(self.eyeLensNP)
                    lastPupils = [self.__lpupil.getPos(), self.__rpupil.getPos()]
                    self.lookEyesAtTarget(avatar)
                    pDist = self.getPupilDistance()
                    self.__lpupil.setPos(lastPupils[0])
                    self.__rpupil.setPos(lastPupils[1])
                    if self.eyeLensNP.node().isInView(apos):
                        visible.append(avatar)
                if len(visible):
                    target = random.choice(visible)
                
            if not target:
                target = random.choice([Vec3(0, 25, 0),
                                        Vec3(10, 25, 0),
                                        Vec3(10, 25, 10),
                                        Vec3(0, 25, 10),
                                        Vec3(0, 25, -10),
                                        Vec3(-10, 25, -10),
                                        Vec3(-10, 25, 10),
                                        Vec3(-10, 25, 0),
                                        Vec3(10, 25, -10)])
                                        
            self.setEyeTarget(target)
            
        return task.cont
        
    def fixEyes(self):
        mode = -3
        self.drawInFront("eyes*", "head-front*", mode)
        if not self.find('**/joint_pupil*').isEmpty():
            self.drawInFront('joint_pupil*', 'eyes*', -1)
        else:
            self.drawInFront('def_*_pupil', 'eyes*', -1)
                
        self.__eyes = self.find('**/eyes*')
        if not self.__eyes.isEmpty():
            self.__eyes.setColorOff()
            self.__lpupil = None
            self.__rpupil = None
            lp = self.pupils[0]
            rp = self.pupils[1]
            # ModelNodes don't get flattened
            leye = self.__eyes.attachNewNode(ModelNode('leye'))
            reye = self.__eyes.attachNewNode(ModelNode('reye'))
            lmat = Mat4(0.802174, 0.59709, 0, 0, -0.586191, 0.787531, 0.190197, 0, 0.113565,
                        -0.152571, 0.981746, 0, -0.233634, 0.418062, 0.0196875, 1)
            leye.setMat(lmat)
            rmat = Mat4(0.786788, -0.617224, 0, 0, 0.602836, 0.768447, 0.214658, 0, -0.132492,
                        -0.16889, 0.976689, 0, 0.233634, 0.418062, 0.0196875, 1)
            reye.setMat(rmat)
            self.__lpupil = leye.attachNewNode('lpupil')
            self.__rpupil = reye.attachNewNode('rpupil')
            lpt = self.__eyes.attachNewNode('')
            rpt = self.__eyes.attachNewNode('')
            lpt.wrtReparentTo(self.__lpupil)
            rpt.wrtReparentTo(self.__rpupil)
            lp.reparentTo(lpt)
            rp.reparentTo(rpt)
            self.__lpupil.adjustAllPriorities(1)
            self.__rpupil.adjustAllPriorities(1)
            if self.animal != 'dog':
                self.__lpupil.flattenStrong()
                self.__rpupil.flattenStrong()
     
    def setPupilDirection(self, x, y):
        if y < 0.0:
            y2 = -y
            left1 = self.LeftAD + (self.LeftD - self.LeftAD) * y2
            left2 = self.LeftBC + (self.LeftC - self.LeftBC) * y2
            right1 = self.RightAD + (self.RightD - self.RightAD) * y2
            right2 = self.RightBC + (self.RightC - self.RightBC) * y2
        else:
            y2 = y
            left1 = self.LeftAD + (self.LeftA - self.LeftAD) * y2
            left2 = self.LeftBC + (self.LeftB - self.LeftBC) * y2
            right1 = self.RightAD + (self.RightA - self.RightAD) * y2
            right2 = self.RightBC + (self.RightB - self.RightBC) * y2
        left0 = Point3(0.0, 0.0, left1[2] - left1[0] * (left2[2] - left1[2]) / (left2[0] - left1[0]))
        right0 = Point3(0.0, 0.0, right1[2] - right1[0] * (right2[2] - right1[2]) / (right2[0] - right1[0]))
        if x < 0.0:
            x2 = -x
            left = left0 + (left2 - left0) * x2
            right = right0 + (right2 - right0) * x2
        else:
            x2 = x
            left = left0 + (left1 - left0) * x2
            right = right0 + (right1 - right0) * x2
        self.__lpupil.setPos(left)
        self.__rpupil.setPos(right)
        
    def lookPupilsAt(self, node, point):
        if node != None:
            mat = node.getMat(self.__eyes)
            point = mat.xformPoint(point)
        distance = 1.0
        recip_z = 1.0 / max(0.1, point[1])
        x = distance * point[0] * recip_z
        y = distance * point[2] * recip_z
        x = min(max(x, -1), 1)
        y = min(max(y, -1), 1)
        self.setPupilDirection(x, y)

    def lookPupilsMiddle(self):
        self.__lpupil.setPos(0, 0, 0)
        self.__rpupil.setPos(0, 0, 0)

    def guiFix(self):
        #if self.animal in ['monkey', 'rabbit', 'cat', 'duck']:
        #    return

        #self.drawInFront('eyes*', 'head-front*', -2)
        #if not self.find('**/joint_pupil*').isEmpty():
        #    self.drawInFront('joint_pupil*', 'eyes*', -1)
        #else:
        #    self.drawInFront('def_*_pupil', 'eyes*', -1)
        """
        
        """


    def setupEyelashes(self):
        head = self.getPart('head')
        lashes = loader.loadModel("phase_3/models/char/%s-lashes.bam" % self.animal)
        openString = "open-short"
        closedString = "closed-short"
        if self.head == "mouse":
            if self.head == "1":
                openString = "open-short"
                closedString = "closed-short"
            elif self.head == "2":
                openString = "open-long"
                closedString = "closed-long"
        else:
            if self.head == "1":
                openString = "open-short"
                closedString = "closed-short"
            elif self.head == "2":
                openString = "open-short"
                closedString = "closed-short"
            elif self.head == "3":
                openString = "open-long"
                closedString = "closed-long"
            elif self.head == "4":
                openString = "open-long"
                closedString = "closed-long"
        self.__eyelashOpened = lashes.find('**/' + openString).copyTo(head)
        self.__eyelashClosed = lashes.find('**/' + closedString).copyTo(head)
        self.__eyelashClosed.hide()

    def doBlink(self, task):
        self.blink()
        return task.done

    def doOpenEyes(self, task):
        self.openEyes()
        return task.done

    def closeEyes(self):
        if self.gender == "girl":
            self.__eyelashOpened.hide()
            self.__eyelashClosed.show()
        for pupil in self.pupils:
            pupil.hide()
        if hasattr(self, 'getHealth'):
            if self.getHealth() > 1:
                try:
                    self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesClosed, 1)
                except:
                    pass
            else:
                try:
                    self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesClosedSad, 1)
                except:
                    pass
        else:
            try:
                self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesClosed, 1)
            except:
                pass

    def openEyes(self):
        if self.gender == "girl":
            self.__eyelashOpened.show()
            self.__eyelashClosed.hide()
        for pupil in self.pupils:
            pupil.show()
        if hasattr(self, 'getHealth'):
            if self.getHealth() > 0:
                try:
                    self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesOpen, 1)
                except:
                    pass
            else:
                try:
                    self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesOpenSad, 1)
                except:
                    pass
        else:
            try:
                self.findAllMatches('**/eyes*').setBSPMaterial(self.EyesOpen, 1)
            except:
                pass

    def startLookAround(self):
        return

        delay = random.randint(3, 15)
        taskMgr.doMethodLater(delay, self.lookAroundTask, self.lookAroundTaskName)

    def stopLookAround(self):
        if hasattr(self, 'lookAroundTaskName') and hasattr(self, 'doLookAroundTaskName'):
            taskMgr.remove(self.lookAroundTaskName)
            taskMgr.remove(self.doLookAroundTaskName)

    def lookAroundTask(self, task):
        taskMgr.add(self.doLookAround, self.doLookAroundTaskName)
        delay = random.uniform(3, 10)
        task.delayTime = delay
        return task.again

    def doLookAround(self, task):
        hpr = self.findSomethingToLookAt()
        h, p, r = hpr
        if not hpr:
            return task.done
        if hasattr(self, 'doId') and hasattr(base, 'localAvatar') and self.doId == base.localAvatar.doId:
            self.b_lookAtObject(h, p, r, blink = 1)
        else:
            self.lerpLookAt(self.getPart('head'), hpr)
        return task.done

    def findSomethingToLookAt(self):
        toons = []
        if hasattr(self, 'doId'):
            for key in self.cr.doId2do.keys():
                val = self.cr.doId2do[key]
                if not val.doId == self.doId:
                    if CIGlobals.isSuit(val) or CIGlobals.isToon(val) or CIGlobals.isDisneyChar(val):
                        if self.eyeLensNP.node().isInView(val.getPos(self.eyeLensNP)):
                            if CIGlobals.isToon(val):
                                toons.append(val.getPart('head'))
                            elif CIGlobals.isSuit(val):
                                toons.append(val.headModel)
                            elif CIGlobals.isDisneyChar(val):
                                toons.append(val.headNode)

        decision = random.randint(0, 3)
        if toons == [] or decision == 3:
            return self.randomLookSpot()
        else:
            startH = self.getPart('head').getH()
            startP = self.getPart('head').getP()
            startR = self.getPart('head').getR()

            toon = random.randint(0, len(toons) - 1)
            if toons[toon]:
                self.getPart('head').lookAt(toons[toon], 0, 0, -0.75)
            else:
                self.notify.warning('toons[toon] is None -- I cannot look at nothing.')
            endH = self.getPart('head').getH()
            endP = self.getPart('head').getP()
            endR = self.getPart('head').getR()

            self.getPart('head').setHpr(startH, startP, startR)
            return (endH, endP, endR)

    def randomLookSpot(self):
        spots = [(0, 0, 0),
                (35, 0, 0),
                (-35, 0, -0),
                (35, -20, 0),
                (-35, -20, -0),
                (35, 20, 0),
                (-35, 20, -0),
                (0, 20, 0),
                (0, -20, 0)]
        spot = random.randint(0, len(spots) - 1)
        h, p, r = spots[spot]
        return tuple((h, p, r))

    def getEyes(self):
        return self.find("**/eyes*")

    def lerpLookAtNode(self, node):
        head = self.getPart("head")
        startHpr = head.getHpr()
        head.lookAt(node, Point3(0, 0, -2))
        endHpr = head.getHpr()
        head.setHpr(startHpr)
        self.lerpLookAt(head, endHpr)

    def lerpLookAt(self, head, hpr, time = 1.0):
        self.lookAtTrack = Parallel(Sequence(LerpHprInterval(head, time, hpr, blendType='easeInOut')))
        self.lookAtTrack.start()
        return 1

    def setHeadColor(self, color = None):
        if color is None:
            color = self.headcolor
        self.findAllMatches('**/head*').setColor(color)
        if (self.animal == "rabbit" or self.animal == "cat" or
            self.animal == "bear" or self.animal == "pig" or
            self.animal == "mouse"):
            self.findAllMatches('**/ears*').setColor(color)

    def delete(self):
        try:
            self.ToonHead_deleted
        except:
            self.ToonHead_deleted = 1
            taskMgr.remove("toonHeadEyesLook-" + str(id(self)))
            del self.lookAroundTaskName
            del self.doLookAroundTaskName
            del self.doBlinkTaskName
            if self.eyeLensNP:
                self.eyeLensNP.removeNode()
                self.eyeLensNP = None
            self.gender = None
            self.head = None
            self.headType = None
        return
