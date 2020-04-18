
from panda3d.core import NodePath, Vec3, Point3, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.PyDatagram import PyDatagram
from direct.interval.IntervalGlobal import Parallel, Sequence, ActorInterval, Func

from Attacks import ATTACKTYPE_NONE, ATTACK_HOLD_NONE, ATTACK_HOLD_LEFT, ATTACK_HOLD_RIGHT
from src.coginvasion.attack.BaseAttackShared import BaseAttackShared

from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.Precache import Precacheable, precacheModel, precacheActor
from src.coginvasion.gui.Crosshair import CrosshairData

class BaseAttack(Precacheable, BaseAttackShared):
    notify = directNotify.newCategory("BaseAttack")

    ModelPath = None
    ModelAnimPath = None
    ModelScale = 1
    ModelAngles = Vec3(0, 0, 0)
    ModelOrigin = Point3(0, 0, 0)
    AttackType = ATTACKTYPE_NONE
    Hold = ATTACK_HOLD_NONE

    ModelVMOrigin = Point3(0, 0, 0)
    ModelVMAngles = Point3(0, 0, 0)
    ModelVMScale = 1
    ModelVMAnimate = True
    
    SpecialVM = False
    SpecialVMCull = True
    SpecialVMActor = None
    SpecialVMFov = 54.0
    SpecialVMOrigin = Point3(0)
    SpecialVMAngles = Vec3(0)
    SpecialVMScale = 1

    def __init__(self, sharedMetadata = None):
        BaseAttackShared.__init__(self, sharedMetadata)
        self.model = None
        self.specialViewModel = None
        self.crosshair = CrosshairData()
        self.animTrack = None
    
    def hasSpecialViewModel(self):
        return self.SpecialVM and (self.specialViewModel is not None) and self.isFirstPerson()

    def unloadViewModel(self):
        if self.specialViewModel:
            self.specialViewModel.cleanup()
        self.specialViewModel = None

    def loadViewModel(self):
        self.unloadViewModel()

        if self.SpecialVM and self.SpecialVMActor:
            modelName, anims = self.SpecialVMActor
            self.specialViewModel = Actor(modelName, anims)
            self.specialViewModel.setPos(self.SpecialVMOrigin)
            self.specialViewModel.setHpr(self.SpecialVMAngles)
            self.specialViewModel.setScale(self.SpecialVMScale)
            self.specialViewModel.setBlend(frameBlend = base.config.GetBool('interpolate-frames', False))
            if not self.SpecialVMCull:
                self.specialViewModel.node().setBounds(OmniBoundingVolume())
                self.specialViewModel.node().setFinal(1)

    def doDrawNoHold(self, drawAnim, drawAnimStart = None, drawAnimEnd = None,
                     drawAnimSpeed = 1.0):

        self.setAnimTrack(Sequence(Func(self.avatar.setForcedTorsoAnim, drawAnim),
                                   self.getAnimationTrack(drawAnim, drawAnimStart, drawAnimEnd, drawAnimSpeed)),
                          startNow = True)

    def doHold(self, anim, bobStart, bobEnd, bobSpeed):
        self.setAnimTrack(self.getBobSequence(anim, bobStart, bobEnd, bobSpeed), startNow = True, looping = True)

    def doDrawAndHold(self, drawAnim, drawAnimStart = None, drawAnimEnd = None,
                      drawAnimSpeed = 1.0, bobStart = None, bobEnd = None, bobSpeed = 1.0,
                      holdCallback = None):

        def __doHold():
            if holdCallback:
                holdCallback()
            self.doHold(drawAnim, bobStart, bobEnd, bobSpeed)

        self.setAnimTrack(Sequence(Func(self.avatar.setForcedTorsoAnim, drawAnim),
                                   self.getAnimationTrack(drawAnim, drawAnimStart, drawAnimEnd, drawAnimSpeed),
                                   Func(__doHold)), startNow = True)
    
    # This should be called to change the 'animTrack' variable.
    def setAnimTrack(self, track, startNow = False, looping = False):
        """ Sets the animation track for this gag. """
        if track is None:
            # If we try to set the animation track to None, we should
            # just call clearAnimTrack.
            self.clearAnimTrack()
            return

        # Stop the one that was playing before.
        self.clearAnimTrack()
        
        self.animTrack = track

        if startNow:
            if looping:
                self.animTrack.loop()
            else:
                self.animTrack.start()
    
    # This should be called whenever we want to clear the 'animTrack' variable.
    def clearAnimTrack(self):
        if self.animTrack is not None:
            self.animTrack.pause()
            self.animTrack = None

    def playAnimThatShouldBePlaying(self):
        if self.avatar and hasattr(self.avatar, 'playingAnim'):
            self.avatar.loop(self.avatar.playingAnim)
            
    def getAnimationTrack(self, animName, startFrame = None, endFrame = None,
                          playRate = 1.0, startTime = None, endTime = None, fullBody = False):
        seq = Parallel()

        def __animTrack(partName):
            return ActorInterval(self.avatar, 
                animName, 
                startFrame = startFrame, 
                endFrame = endFrame,
                partName = partName,
                playRate = playRate,
                startTime = startTime,
                endTime = endTime)

        if not fullBody:
            uppers = self.avatar.getUpperBodySubpart()
            for part in uppers:
                seq.append(__animTrack(part))
        else:
            seq.append(__animTrack(None))

        return seq
            
    def getBobSequence(self, animName, startFrame, endFrame, playRate):

        def __animTrack_bobUp(partName):
            return ActorInterval(self.avatar, 
                    animName, 
                    startFrame = startFrame,
                    endFrame = endFrame,
                    partName = partName,
                    playRate = playRate)

        def __animTrack_bobDown(partName):
            return ActorInterval(self.avatar, 
                    animName, 
                    startFrame = endFrame,
                    endFrame = startFrame,
                    partName = partName,
                    playRate = playRate)

        uppers = self.avatar.getUpperBodySubpart()

        seq = Sequence()

        bobUp = Parallel()
        for part in uppers:
            bobUp.append(__animTrack_bobUp(part))

        bobDown = Parallel()
        for part in uppers:
            bobDown.append(__animTrack_bobDown(part))

        seq.append(bobUp)
        seq.append(bobDown)

        return seq

    def getCrosshair(self):
        return self.crosshair

    # ===========================================
    # These functions are to be overridden by child classes
    # to add any arbitrary data when we send these fire
    # events to the server.

    def addPrimaryPressData(self, dg):
        pass

    def addPrimaryReleaseData(self, dg):
        pass

    def addSecondaryPressData(self, dg):
        pass

    def addSecondaryReleaseData(self, dg):
        pass

    def addReloadPressData(self, dg):
        pass

    def addReloadReleaseData(self, dg):
        pass

    # ===========================================

    def primaryFirePress(self, data = None):
        dg = PyDatagram()
        self.addPrimaryPressData(dg)
        self.avatar.sendUpdate('primaryFirePress', [dg.getMessage()])

    def primaryFireRelease(self, data = None):
        dg = PyDatagram()
        self.addPrimaryReleaseData(dg)
        self.avatar.sendUpdate('primaryFireRelease', [dg.getMessage()])

    def secondaryFirePress(self, data = None):
        dg = PyDatagram()
        self.addSecondaryPressData(dg)
        self.avatar.sendUpdate('secondaryFirePress', [dg.getMessage()])

    def secondaryFireRelease(self, data = None):
        dg = PyDatagram()
        self.addSecondaryReleaseData(dg)
        self.avatar.sendUpdate('secondaryFireRelease', [dg.getMessage()])

    def reloadPress(self, data = None):
        dg = PyDatagram()
        self.addReloadPressData(dg)
        self.avatar.sendUpdate('reloadPress', [dg.getMessage()])

    def reloadRelease(self, data = None):
        dg = PyDatagram()
        self.addReloadReleaseData(dg)
        self.avatar.sendUpdate('reloadRelease', [dg.getMessage()])

    @classmethod
    def doPrecache(cls):
        print "BaseAttack(%s).doPrecache()" % cls.ModelPath
        if cls.ModelAnimPath:
            precacheActor([cls.ModelPath, {'chan' : cls.ModelAnimPath, 'zero' : cls.ModelPath}])
        elif cls.ModelPath:
            precacheModel(cls.ModelPath)

        if cls.SpecialVM and cls.SpecialVMActor:
            precacheActor(cls.SpecialVMActor)

    def getName(self):
        return self.Name

    def isLocal(self):
        return self.avatar == base.localAvatar

    def isFirstPerson(self):
        return self.isLocal() and base.localAvatar.isFirstPerson()

    def getViewModel(self):
        return base.localAvatar.getViewModel()

    def getFPSCam(self):
        return base.localAvatar.getFPSCam()

    def getVMGag(self):
        return base.localAvatar.getFPSCam().vmGag

    def getViewPunch(self):
        """
        Return the angles of the view "punch" that is applied to the camera when this
        attack is used by the local avatar.
        """
        return Vec3.zero()

    def load(self):
        BaseAttackShared.load(self)
        if self.isLocal():
            self.loadViewModel()

    def __loadAttackModel(self):
        if self.model:
            self.model.removeNode()
            self.model = None

        if self.ModelPath:
            if self.ModelAnimPath:
                self.model = Actor(self.ModelPath, {'chan': self.ModelAnimPath, 'zero': self.ModelPath})
            else:
                self.model = loader.loadModel(self.ModelPath)
            self.model.setPos(self.ModelOrigin)
            self.model.setHpr(self.ModelAngles)
            self.model.setScale(self.ModelScale)
            self.model.setName(self.Name + "-model")

        # copy the attack model to first person
        if self.isFirstPerson():

            if self.hasSpecialViewModel():
                self.getFPSCam().swapViewModel(self.specialViewModel, self.SpecialVMFov)
            elif self.model:
                self.getFPSCam().setVMGag(self.model, self.ModelVMOrigin,
                                          self.ModelVMAngles, self.ModelVMScale,
                                          self.Hold,
                                          self.ModelAnimPath is not None and self.ModelVMAnimate)

            if not self.getViewModel().isEmpty() and self.action != self.StateOff:
                self.getViewModel().show()

    def __holdAttackModel(self):
        if not self.hasAvatar():
            self.notify.warning("Tried to hold attack model, but no valid avatar.")
            return

        if not CIGlobals.isNodePathOk(self.model):
            return

        if self.Hold == ATTACK_HOLD_LEFT:
            self.model.reparentTo(self.avatar.getLeftHandNode())
        elif self.Hold == ATTACK_HOLD_RIGHT:
            self.model.reparentTo(self.avatar.getRightHandNode())
        else:
            self.model.reparentTo(NodePath())

    def equip(self):
        if not BaseAttackShared.equip(self):
            return False

        if not self.hasAvatar():
            self.notify.warning("Tried to equip attack, but no valid avatar.")
            return False

        self.__loadAttackModel()
        self.__holdAttackModel()

        return True

    def unEquip(self):
        if not BaseAttackShared.unEquip(self):
            return False

        if self.model:
            if isinstance(self.model, Actor):
                self.model.cleanup()
            self.model.removeNode()
            self.model = None
        self.clearAnimTrack()
        if self.hasAvatar():
            self.avatar.clearForcedTorsoAnim()
        if self.isFirstPerson():
            self.getFPSCam().clearVMGag()
            self.getFPSCam().clearVMAnimTrack()
            self.getFPSCam().restoreViewModelFOV()
            if self.hasSpecialViewModel():
                self.getFPSCam().restoreViewModel()
            if not self.getViewModel().isEmpty():
                self.getViewModel().hide()

        return True

    def cleanup(self):
        BaseAttackShared.cleanup(self)
        self.unloadViewModel()
        self.crosshair.cleanup()
        del self.crosshair
        del self.model
