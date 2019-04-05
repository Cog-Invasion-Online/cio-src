
from panda3d.core import NodePath, Vec3, Point3

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

    def __init__(self, sharedMetadata = None):
        BaseAttackShared.__init__(self)
        self.model = None
        self.crosshair = CrosshairData()
        self.animTrack = None
        
        if sharedMetadata:
            for key in sharedMetadata.__dict__.keys():
                setattr(self, key, sharedMetadata.__dict__.get(key))

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
        if cls.ModelAnimPath:
            precacheActor([cls.ModelPath, {'chan' : cls.ModelAnimPath, 'zero' : cls.ModelPath}])
        elif cls.ModelPath:
            precacheModel(cls.ModelPath)

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

    def __loadAttackModel(self):
        if self.model:
            self.model.removeNode()
            self.model = None

        if self.ModelAnimPath:
            self.model = Actor(self.ModelPath, {'chan': self.ModelAnimPath, 'zero': self.ModelPath})
        else:
            self.model = loader.loadModel(self.ModelPath)
        self.model.setPos(self.ModelOrigin)
        self.model.setHpr(self.ModelAngles)
        self.model.setScale(self.ModelScale)
        self.model.setName(self.Name + "-model")

        # copy the attack model to first person
        if not self.SpecialVM and self.isFirstPerson():
            self.getFPSCam().setVMGag(self.model, self.ModelVMOrigin,
                                      self.ModelVMAngles, self.ModelVMScale,
                                      self.Hold,
                                      self.ModelAnimPath is not None and self.ModelVMAnimate)
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

        if self.ModelPath:
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
            self.getViewModel().hide()

        return True

    def cleanup(self):
        BaseAttackShared.cleanup(self)
        self.crosshair.cleanup()
        del self.crosshair
        del self.model
