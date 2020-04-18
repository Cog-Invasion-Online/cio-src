"""

  Filename: ToonHead.py
  Created by: blach (??July14)
  Remade: (28Oct14)

"""

from panda3d.core import PerspectiveLens, LensNode, Texture, Point3, Mat4, ModelNode, NodePath, Vec3
from libpandabsp import CIOLib

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

    def __init__(self, cr = None):
        Actor.Actor.__init__(self)
        self.__eyelashOpened = None
        self.__eyelashClosed = None
        self.__eyes = None
        self.__lpupil = None
        self.__rpupil = None
        self.pupils = []
        
        self.eyeTarget = None
        self.newTarget = False
        
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
            taskMgr.add(self.__eyesLookTask, "toonHeadEyesLook-" + str(id(self)))
        return
        
    def hasPupils(self):
        return CIGlobals.isNodePathOk(self.__lpupil) and CIGlobals.isNodePathOk(self.__rpupil)
        
    def setEyeTarget(self, target):
        self.eyeTarget = target
        self.newTarget = True
        
    def hasEyeTarget(self):
        if isinstance(self.eyeTarget, NodePath):
            return CIGlobals.isNodePathOk(self.eyeTarget)
            
        return self.eyeTarget is not None
        
    def setEyeState(self, state):
        if state == ToonGlobals.EyeStateClosed:
            self.closeEyes()
        elif state == ToonGlobals.EyeStateOpened:
            self.openEyes()
        
    def lookEyesAt(self, pos):
        self.setEyeTarget(Point3(*pos))
        
    def lookEyesAtObject(self, doId):
        if not hasattr(base, 'cr'):
            return
        do = base.cr.doId2do.get(doId)
        if do and isinstance(do, NodePath):
            if (hasattr(base, 'localAvatar') and do.doId == base.localAvatar.doId
            and base.localAvatar.isFirstPerson()):
                self.setEyeTarget(camera)
            else:
                self.setEyeTarget(do)
        
    def lookEyesAtTarget(self, eyeTarget):
        if isinstance(eyeTarget, NodePath):
            if hasattr(eyeTarget, 'getHeight'):
                self.lookPupilsAt(eyeTarget, Point3(0, 0, eyeTarget.getHeight() * 0.85))
            else:
                self.lookPupilsAt(eyeTarget, Point3(0))
        else:
            self.lookPupilsAt(None, eyeTarget)
        
    def __eyesLookTask(self, task):
        if (hasattr(base, 'localAvatar') and self == base.localAvatar and base.localAvatar.isFirstPerson()) or not self.hasPupils():
            return task.cont
            
        if self.hasEyeTarget():
            if self.newTarget or isinstance(self.eyeTarget, NodePath):
                self.lookEyesAtTarget(self.eyeTarget)
                self.newTarget = False
            
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
                
            # Make sure pupils don't clip through the head or eyes
            self.__lpupil.setDepthOffset(4, 1)
            self.__rpupil.setDepthOffset(4, 1)
     
    def setPupilDirection(self, x, y):
        left = Vec3()
        right = Vec3()
        CIOLib.setPupilDirection(x, y, left, right)
        self.__lpupil.setPos(left)
        self.__rpupil.setPos(right)
        
    def lookPupilsAt(self, node, point):
        if not node:
            node = NodePath()
        xy = CIOLib.lookPupilsAt(node, point, self.__eyes)
        self.setPupilDirection(xy[0], xy[1])

    def lookPupilsMiddle(self):
        self.__lpupil.setPos(0, 0, 0)
        self.__rpupil.setPos(0, 0, 0)

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
        pass
        
    def stopLookAround(self):
        pass

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
            
            if self.__lpupil:
                self.__lpupil.removeNode()
            self.__lpupil = None
            
            if self.__rpupil:
                self.__rpupil.removeNode()
            self.__rpupil = None
            
            if self.__eyes:
                self.__eyes.removeNode()
            self.__eyes = None
            
            if self.__eyelashClosed:
                self.__eyelashClosed.removeNode()
            self.__eyelashClosed = None
            
            if self.__eyelashOpened:
                self.__eyelashOpened.removeNode()
            self.__eyelashOpened = None
            
            for pupilC in self.pupils:
                if not pupilC.isEmpty():
                    for pupil in pupilC:
                        pupil.removeNode()
            self.pupils = None
            
            self.eyeTarget = None
            self.newTarget = None
            
            self.gender = None
            self.animal = None
            self.head = None
