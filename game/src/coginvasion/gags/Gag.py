########################################
# Filename: Gag.py
# Created by: DecodedLogic (07Jul15)
########################################

from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Parallel, Sequence, LerpScaleInterval, SoundInterval, Wait
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.gags import GagGlobals
from pandac.PandaModules import Point3
from abc import ABCMeta
import abc

class Gag(object):

    def __init__(self, name, model, damage, gagType, hitSfx, playRate = 1.0, anim = None, scale = 1, autoRelease = False):
        __metaclass__ = ABCMeta
        self.name = name
        self.model = model
        self.anim = anim
        self.scale = scale
        self.damage = damage
        self.gagType = gagType
        self.playRate = playRate
        self.avatar = None
        self.gag = None
        self.splat = None
        self.splatPos = None
        self.state = GagState.LOADED
        self.woosh = None
        self.handJoint = None
        self.equipped = False
        self.autoRelease = autoRelease
        self.index = None
        self.target = None
        self.health = 0
        self.id = GagGlobals.getIDByName(name)
        self.image = None
        self.timeout = 5

        # Handles the new recharging for certain gags.

        # The time it takes (in seconds) to recharge this gag.
        self.rechargeTime = 0

        # The elapsed time of the current recharge. Should be a float
        self.rechargeElapsedTime = 0

        if game.process == 'client':
            if gagType == GagType.THROW:
                self.woosh = base.audio3d.loadSfx(GagGlobals.PIE_WOOSH_SFX)
            self.hitSfx = base.audio3d.loadSfx(hitSfx)

    def playAnimThatShouldBePlaying(self):
        if self.avatar:
            self.avatar.loop(self.avatar.playingAnim)

    def setRechargeTime(self, time):
        self.rechargeTime = time

    def getRechargeTime(self):
        return self.rechargeTime

    def setRechargeElapsedTime(self, time):
        self.rechargeElapsedTime = time

    def getRechargeElapsedTime(self):
        return self.rechargeElapsedTime

    def __doRecharge(self, task):
        task.delayTime = 0.1
        self.rechargeElapsedTime += 0.1
        messenger.send('%s-Recharge-Tick' % (str(self.getID())))

        if self.rechargeElapsedTime >= self.rechargeTime:
            self.state = GagState.LOADED
            return Task.done
        return Task.again

    def startTimeout(self):
        base.localAvatar.gagsTimedOut = True
        base.taskMgr.doMethodLater(self.timeout, self.__timeoutDone, self.avatar.uniqueName('timeoutDone'))

    def __timeoutDone(self, task):
        base.localAvatar.gagsTimedOut = False
        if base.localAvatar.needsToSwitchToGag != None:
            if base.localAvatar.needsToSwitchToGag != self.getID() and base.localAvatar.needsToSwitchToGag != 'unequip':
                base.localAvatar.b_equip(base.localAvatar.needsToSwitchToGag)
            elif base.localAvatar.needsToSwitchToGag == 'unequip':
                base.localAvatar.b_unEquip()
        if base.localAvatar.avatarMovementEnabled:
            base.localAvatar.enableGagKeys()
        return task.done

    def stopTimeout(self):
        base.taskMgr.remove(self.avatar.uniqueName('timeoutDone'))

    @abc.abstractmethod
    def start(self):
        if not self.avatar:
            return
        if self.avatar.getBackpack().getSupply(self.getID()) == 0 or self.state == GagState.RECHARGING:
            return
        try:
            base.audio3d.detachSound(self.woosh)
            self.track.pause()
            self.cleanupGag()
        except: pass
        self.state = GagState.START
        self.avatar.getBackpack().setActiveGag(self.getID())

    @abc.abstractmethod
    def reset(self):
        if not self.state == GagState.RECHARGING:
            self.state = GagState.LOADED
        self.target = None
        if self.avatar:
            backpack = self.avatar.getBackpack()
            if backpack.getActiveGag():
                if backpack.getActiveGag() == self:
                    backpack.setActiveGag(None)

                    if self.rechargeTime > 0 and self.isLocal():
                        self.state = GagState.RECHARGING
                        self.setRechargeElapsedTime(0)
                        messenger.send('%s-Recharge-Tick' % (str(self.getID())))
                        taskMgr.doMethodLater(0.5, self.__doRecharge, '%s-Recharge' % (str(self.getID())))
                        base.localAvatar.b_unEquip()

    @abc.abstractmethod
    def throw(self):
        return

    @abc.abstractmethod
    def release(self):
        self.state = GagState.RELEASED
        return

    @abc.abstractmethod
    def buildCollisions(self):
        return

    @abc.abstractmethod
    def onCollision(self):
        pass

    def setAvatar(self, avatar):
        self.avatar = avatar

    def getAvatar(self):
        return self.avatar

    def setState(self, paramState):
        self.state = paramState

    def getState(self):
        return self.state

    def setTarget(self, target):
        self.target = target

    def getTarget(self):
        return self.target

    def getType(self):
        return self.gagType

    def build(self):
        if self.anim:
            self.gag = Actor(self.model, {'chan' : self.anim})
        else:
            self.gag = loader.loadModel(self.model)
        self.setHandJoint()
        self.gag.setScale(self.scale)
        self.gag.setName(self.getName())

    def setHandJoint(self):
        if self.avatar:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')

    def equip(self):
        if not self.avatar or not self.avatar.getBackpack() or self.avatar.getBackpack() and self.avatar.getBackpack().getSupply(self.getID()) == 0 or self.state == GagState.RECHARGING:
            return
        self.setHandJoint()
        if not self.gag:
            self.build()
        self.gag.reparentTo(self.handJoint)
        self.equipped = True

    @abc.abstractmethod
    def unEquip(self):
        if game.process != 'client':
            return
        if self.equipped and self.handJoint:
            inHand = self.handJoint.getChildren()
            for item in inHand:
                if(item.getName() == self.getName()):
                    item.removeNode()
            self.equipped = False
            self.reset()

    def setHealth(self, health):
        self.health = health

    def getHealth(self):
        return self.health

    def setImage(self, image):
        self.image = image

    def getImage(self):
        return self.image

    def getDamage(self):
        return self.damage

    def getName(self):
        return self.name

    def delete(self):
        self.unEquip()
        self.handJoint = None
        self.avatar = None
        self.state = None
        self.cleanupGag()
        self.cleanupSplat()
        if self.woosh:
            self.woosh.stop()
            self.woosh = None
        if self.hitSfx:
            self.hitSfx.stop()
            self.hitSfx = None

    def cleanupGag(self):
        try:
            self.track.pause()
        except: pass
        if self.gag and not self.state in [GagState.RELEASED, GagState.START]:
            name = self.gag.getName()
            if self.anim:
                self.gag.cleanup()
            if self.avatar:
                copies = self.avatar.findAllMatches('**/%s' % name)
                for copy in copies:
                    copy.removeNode()
            if self.gag and not self.gag.isEmpty():
                self.gag.removeNode()
            self.gag = None

    def getGag(self):
        return self.gag

    def placeProp(self, handJoint, prop, pos = None, hpr = None, scale = None):
        prop.reparentTo(handJoint)
        if pos:
            prop.setPos(pos)
        if hpr:
            prop.setHpr(hpr)
        if scale:
            prop.setScale(scale)

    def getScaleTrack(self, props, duration, startScale, endScale):
        track = Parallel()
        if not isinstance(props, list):
            props = [props]
        for prop in props:
            track.append(LerpScaleInterval(prop, duration, endScale, startScale = startScale))
        return track

    def getSoundTrack(self, delay, node, duration = None):
        soundTrack = Sequence()
        soundTrack.append(Wait(delay))
        if duration:
            soundTrack.append(SoundInterval(self.hitSfx, duration = duration, node = node))
        else:
            soundTrack.append(SoundInterval(self.hitSfx, node = node))
        return soundTrack

    def getScaleIntervals(self, props, duration, startScale, endScale):
        tracks = Parallel()
        if not isinstance(props, list):
            props = [props]
        for prop in props:
            tracks.append(LerpScaleInterval(prop, duration, endScale, startScale=startScale))
        return tracks

    def getScaleBlendIntervals(self, props, duration, startScale, endScale, blendType):
        tracks = Parallel()
        if not isinstance(props, list):
            props = [props]
        for prop in props:
            tracks.append(LerpScaleInterval(prop, duration, endScale, startScale=startScale, blendType=blendType))
        return tracks

    def buildSplat(self, scale, color):
        self.cleanupSplat()
        self.splat = Actor(GagGlobals.SPLAT_MDL, {'chan' : GagGlobals.SPLAT_CHAN})
        self.splat.setScale(scale)
        self.splat.setColor(color)
        self.splat.setBillboardPointEye()
        self.splat.play('chan')
        return self.splat

    def setSplatPos(self, x, y, z):
        self.cleanupGag()
        self.splatPos = Point3(x, y, z)
        self.handleSplat()

    def cleanupSplat(self):
        if self.splat:
            self.splat.cleanup()
            self.splat

    def setEndPos(self, x, y, z):
        pass

    def handleSplat(self):
        pass

    def delSplat(self, task):
        self.cleanupSplat()
        return Task.done

    def getAudio3D(self):
        return base.audio3d

    def doesAutoRelease(self):
        return self.autoRelease

    def isLocal(self):
        if not self.avatar:
            return False
        return self.avatar.doId == base.localAvatar.doId

    def getID(self):
        return self.id
