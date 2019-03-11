
from panda3d.core import NodePath, Vec3, Point3

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.PyDatagram import PyDatagram
from direct.interval.IntervalGlobal import Parallel, Sequence, ActorInterval, Func, Wait

from Attacks import ATTACK_NONE, ATTACKTYPE_NONE, ATTACK_HOLD_NONE, ATTACK_HOLD_LEFT, ATTACK_HOLD_RIGHT

#from src.coginvasion.avatar.AvatarShared import AvatarShared
from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.Precache import Precacheable, precacheModel, precacheActor
from src.coginvasion.gui.Crosshair import CrosshairData

class BaseAttackShared:
    """
    Shared client/server functionality for an attack, useable by Avatars.

    This new attack system is designed to be character/interface-agnostic, meaning
    that attack code can be shared between Toons, Cogs, NPCs, etc, on the Client or Server.

    The design is tightly coupled with the new AI, which is also designed to be
    character/interface-agnostic.
    """

    notify = directNotify.newCategory("BaseAttackShared")

    HasClip = False
    HasSecondary = False
    ID = ATTACK_NONE
    Name = "Base Attack"

    Server = False

    StateIdle = 0

    PlayRate = 1.0

    def __init__(self):
        self.maxClip = 10
        self.clip = 10
        self.maxAmmo = 10
        self.ammo = 10
        self.baseDamage = 10
        self.damageMaxDistance = 40.0

        self.secondaryAmmo = 1
        self.secondaryMaxAmmo = 1

        self.action = self.StateIdle
        self.actionStartTime = 0
        self.nextAction = None

        self.equipped = False
        self.thinkTask = None

        self.avatar = None

    def canUse(self):
        if self.HasClip:
            return self.hasClip() and self.hasAmmo()
        return self.hasAmmo() and self.action == self.StateIdle

    def getBaseDamage(self):
        return self.baseDamage

    def getDamageMaxDistance(self):
        return self.damageMaxDistance

    def calcDamage(self, distance = 10.0):
        return CIGlobals.calcAttackDamage(distance, self.getBaseDamage(), self.getDamageMaxDistance())

    def getID(self):
        return self.ID

    def isServer(self):
        return self.Server

    def setAvatar(self, avatar):
        #assert isinstance(avatar, AvatarShared), "BaseAttackShared.setAvatar(): not a valid avatar"

        self.avatar = avatar

    def hasAvatar(self):
        return CIGlobals.isNodePathOk(self.avatar)

    def getAvatar(self):
        return self.avatar
        
    def getActionTime(self):
        return (globalClock.getFrameTime() - self.actionStartTime)
        
    def setNextAction(self, action):
        self.nextAction = action

    def getNextAction(self):
        return self.nextAction
        
    def setAction(self, action):
        self.actionStartTime = globalClock.getFrameTime()
        self.action = action
        self.onSetAction(action)
        
    def onSetAction(self, action):
        pass

    def getAction(self):
        return self.action

    def equip(self):
        if self.equipped:
            return False

        self.equipped = True

        return True

    def unEquip(self):
        if not self.equipped:
            return False

        self.equipped = False

        return True

    def primaryFirePress(self, data = None):
        pass

    def primaryFireRelease(self, data = None):
        pass

    def secondaryFirePress(self, data = None):
        pass

    def secondaryFireRelease(self, data = None):
        pass

    def reloadPress(self, data = None):
        pass

    def reloadRelease(self, data = None):
        pass

    def getSecondaryAmmo(self):
        return self.secondaryAmmo

    def getSecondaryMaxAmmo(self):
        return self.getSecondaryMaxAmmo

    def usesSecondary(self):
        return self.HasSecondary

    def hasSecondaryAmmo(self):
        return self.secondaryAmmo > 0

    def needsReload(self):
        return self.clip == 0

    def usesClip(self):
        return self.HasClip

    def hasClip(self):
        return self.clip > 0

    def isClipFull(self):
        return self.clip >= self.maxClip

    def isAmmoFull(self):
        return self.ammo >= self.maxAmmo

    def getClip(self):
        return self.clip

    def getMaxClip(self):
        return self.maxClip

    def setMaxAmmo(self, ammo):
        self.maxAmmo = ammo

    def getMaxAmmo(self):
        return self.maxAmmo

    def setAmmo(self, ammo):
        self.ammo = ammo

    def getAmmo(self):
        return self.ammo

    def hasAmmo(self):
        return self.ammo > 0

    def cleanup(self):
        self.unEquip()
        del self.ammo
        del self.maxAmmo
        del self.avatar
        del self.secondaryAmmo
        del self.secondaryMaxAmmo
        del self.maxClip
        del self.clip
        del self.equipped
        del self.thinkTask
        del self.nextAction
        del self.action
        del self.actionStartTime

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
    
    SpecialVM = False

    def __init__(self):
        BaseAttackShared.__init__(self)
        self.model = None
        self.crosshair = CrosshairData()
        self.animTrack = None

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
                                      self.Hold, self.ModelAnimPath is not None)
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

class BaseAttackAI(BaseAttackShared):
    notify = directNotify.newCategory("BaseAttackAI")

    Server = True

    def __init__(self):
        BaseAttackShared.__init__(self)
        self.actionLengths = {self.StateIdle: 0}

    def getPostAttackSchedule(self):
        return None

    def cleanup(self):
        del self.actionLengths
        BaseAttackShared.cleanup(self)

    def takeAmmo(self, amount):
        self.ammo += amount
        if self.hasAvatar():
            self.avatar.sendUpdate('updateAttackAmmo', [self.getID(), self.ammo])

    def isActionComplete(self):            
        return self.getActionTime() >= self.actionLengths[self.action]

    def shouldGoToNextAction(self, complete):
        return complete

    def determineNextAction(self, completedAction):
        return self.StateIdle

    def b_setAction(self, action):
        if self.hasAvatar():
            self.avatar.sendUpdate('setAttackState', [action])
        self.setAction(action)

    def think(self):
        complete = self.isActionComplete()

        if complete and self.nextAction is None:
            nextAction = self.determineNextAction(self.action)
            if self.action != nextAction or nextAction != self.StateIdle:
                self.b_setAction(nextAction)
        elif self.shouldGoToNextAction(complete):
            self.b_setAction(self.nextAction)
            self.nextAction = None

    def __thinkTask(self, task):
        if not self.equipped:
            return task.done

        self.think()

        return task.cont

    def equip(self):
        if not BaseAttackShared.equip(self):
            return False

        self.thinkTask = taskMgr.add(self.__thinkTask, "attackThink-" + str(id(self)))

        return True

    def unEquip(self):
        if not BaseAttackShared.unEquip(self):
            return False

        if self.thinkTask:
            self.thinkTask.remove()
            self.thinkTask = None

        return True

    def checkCapable(self, dot, squaredDistance):
        """
        Returns whether or not this attack is capable of being performed by an AI,
        based on how much the NPC is facing the target, and the distance to the target.

        NOTE: It's squared distance
        """
        return True
    
    def npcUseAttack(self, target):
        """
        Called when an NPC wants to fire this attack on `target`.
        Each attack should override this function to implement
        specific functionality for how an NPC aims and fires
        this attack.
        """
        pass
