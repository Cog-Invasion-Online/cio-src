"""

  Filename: Toon.py
  Created by: blach (??July14)

"""


from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval
from direct.interval.IntervalGlobal import Wait, Parallel, SoundInterval, LerpPosInterval
from direct.interval.IntervalGlobal import ActorInterval, LerpHprInterval, Func
from direct.distributed import DelayDelete

from src.coginvasion.gags.GagState import GagState
from src.coginvasion.toon import ToonGlobals
from src.coginvasion.toon.ToonHead import ToonHead
from src.coginvasion.distributed import AdminCommands
from src.coginvasion.globals import CIGlobals
from src.coginvasion.avatar import Avatar

import AccessoryGlobals

from panda3d.core import VBase3, VBase4, Point3, Vec3, ConfigVariableBool
from panda3d.core import BitMask32, CollisionHandlerPusher
from panda3d.core import Material, NodePath, rad2Deg
import ToonDNA, random, math

import types

def uniqueName(toon, string):
    return string + "-" + str(id(toon))

class Toon(Avatar.Avatar, ToonHead, ToonDNA.ToonDNA):
    notify = directNotify.newCategory("Toon")

    def __init__(self, cr, mat=0):
        self.cr = cr
        try:
            self.Toon_initialized
            return
        except:
            self.Toon_initialized = 1
        Avatar.Avatar.__init__(self, mat)
        ToonDNA.ToonDNA.__init__(self)
        ToonHead.__init__(self, cr)
        self.collsSetup = False
        self.forwardSpeed = 0.0
        self.rotateSpeed = 0.0
        self.strafeSpeed = 0.0
        self.avatarType = CIGlobals.Toon
        self.track = None
        self.standWalkRunReverse = None
        self.playingAnim = None
        self.playingRate = None
        self.tag = None
        self.money = 0
        self.lookAtTrack = None
        self.portal1 = None
        self.portal2 = None
        self.gunAttached = False
        self.spineA = NodePath()
        self.gun = None
        self.tokenIcon = None
        self.tokenIconIval = None
        self.forcedTorsoAnim = None
        self.lastForcedTorsoAnim = None
        self.fallSfx = base.audio3d.loadSfx("phase_4/audio/sfx/MG_cannon_hit_dirt.ogg")
        base.audio3d.attachSoundToObject(self.fallSfx, self)
        self.eyes = loader.loadTexture("phase_3/maps/eyes.jpg", "phase_3/maps/eyes_a.rgb")
        self.myTaskId = random.uniform(0, 1231231232132131231232)
        self.closedEyes = loader.loadTexture("phase_3/maps/eyesClosed.jpg", "phase_3/maps/eyesClosed_a.rgb")
        self.soundChatBubble = loader.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.ogg")
        self.shadowCaster = None
        self.accessories = []
        self.chatSoundDict = {}
        self.backpack = None
        self.forceRunSpeed = False
        self.animFSM = ClassicFSM('Toon', [State('off', self.enterOff, self.exitOff),
            State('neutral', self.enterNeutral, self.exitNeutral),
            State('swim', self.enterSwim, self.exitSwim),
            State('walk', self.enterWalk, self.exitWalk),
            State('run', self.enterRun, self.exitRun),
            State('openBook', self.enterOpenBook, self.exitOpenBook),
            State('readBook', self.enterReadBook, self.exitReadBook),
            State('closeBook', self.enterCloseBook, self.exitCloseBook),
            State('teleportOut', self.enterTeleportOut, self.exitTeleportOut),
            State('teleportIn', self.enterTeleportIn, self.exitTeleportIn),
            State('died', self.enterDied, self.exitDied),
            State('fallFWD', self.enterFallFWD, self.exitFallFWD),
            State('fallBCK', self.enterFallBCK, self.exitFallBCK),
            State('jump', self.enterJump, self.exitJump),
            State('leap', self.enterLeap, self.exitLeap),
            State('laugh', self.enterLaugh, self.exitLaugh),
            State('happy', self.enterHappyJump, self.exitHappyJump),
            State('shrug', self.enterShrug, self.exitShrug),
            State('hdance', self.enterHDance, self.exitHDance),
            State('wave', self.enterWave, self.exitWave),
            State('scientistEmcee', self.enterScientistEmcee, self.exitScientistEmcee),
            State('scientistWork', self.enterScientistWork, self.exitScientistWork),
            State('scientistGame', self.enterScientistGame, self.exitScientistGame),
            State('scientistJealous', self.enterScientistJealous, self.exitScientistJealous),
            State('cringe', self.enterCringe, self.exitCringe),
            State('conked', self.enterConked, self.exitConked),
            State('win', self.enterWin, self.exitWin),
            State('walkBack', self.enterWalkBack, self.exitWalkBack),
            State('deadNeutral', self.enterDeadNeutral, self.exitDeadNeutral),
            State('deadWalk', self.enterDeadWalk, self.exitDeadWalk),
            State('squish', self.enterSquish, self.exitSquish),
            State('Happy', self.enterHappy, self.exitHappy),
            State('Sad', self.enterSad, self.exitSad),
            State('Swim', self.enterSwim, self.exitSwim)],
            'off', 'off')
        animStateList = self.animFSM.getStates()
        self.animFSM.enterInitialState()
        
        if not hasattr(self, 'uniqueName'):
            self.uniqueName = types.MethodType(uniqueName, self)

    def getEyePoint(self):
        # middle of the head
        return Point3(0, 0, self.getHeight() - (self.getHeadHeight() / 2.0))
            
    def setForceRunSpeed(self, flag):
        self.forceRunSpeed = flag

    def setForcedTorsoAnim(self, anim):
        self.forcedTorsoAnim = anim

    def hasForcedTorsoAnim(self):
        return self.forcedTorsoAnim is not None

    def getForcedTorsoAnim(self):
        return self.forcedTorsoAnim

    def clearForcedTorsoAnim(self):
        if not self.forcedTorsoAnim is None:
            # Let's switch our current torso and head animation to the
            # animation the legs are running.
            legs = self.__getLowerHalfPartNames()[0]
            legAnimation = self.getCurrentAnim(partName = legs)
            frame = self.getCurrentFrame(partName = legs, animName = legAnimation)
            for part in self.__getUpperHalfPartNames():
                self.stop(partName = part)
                self.play(animName = legAnimation, partName = part, fromFrame = frame)
        self.forcedTorsoAnim = None
            
    def resetTorsoRotation(self):
        if not self.isEmpty():
            spine = self.find("**/def_spineB")
            if not spine.isEmpty():
                spine.setH(0)
                spine.detachNode()
                self.getPart("legs").setH(0)
                self.releaseJoint("torso", "def_spineB")

    def showAvId(self):
        pass

    def showName(self):
        pass

    def getNametagJoints(self):
        joints = []
        for lodName in self.getLODNames():
            bundle = self.getPartBundle('legs', lodName)
            joint = bundle.findChild('joint_nameTag')
            if joint:
                joints.append(joint)

        return joints

    def enterHappy(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = None
        self.standWalkRunReverse = (('neutral', 1.0), ('walk', 1.0), ('run', 1.0), ('walk', -1.0),
                                    ('strafe', 1.0), ('strafe', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)

    def exitHappy(self):
        self.standWalkRunReverse = None
        self.stop()

    def enterSad(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'sad'
        self.standWalkRunReverse = (('dneutral', 1.0), ('dwalk', 1.2), ('dwalk', 1.2), ('dwalk', -1.0))
        self.setSpeed(0, 0)

    def exitSad(self):
        self.standWalkRunReverse = None
        self.stop()
        #if hasattr(self, 'doId'):
        #    if hasattr(base, 'localAvatar'):
        #        if base.localAvatar.doId == self.doId:
        #            self.controlManager.enableAvatarJump()
        
    def setPlayRate(self, rate, animName, partName = None):
        if partName or not self.forcedTorsoAnim:
            Actor.setPlayRate(self, rate, animName, partName)
        else:
            parts = self.__getLowerHalfPartNames() + self.__getUpperHalfPartNames()
            for part in parts:
                Actor.setPlayRate(self, rate, animName, part)
        
    def play(self, animName, partName=None, fromFrame=None, toFrame=None):
        lowerHalfNames = self.__getLowerHalfPartNames()
        if self.forcedTorsoAnim is None or (not (partName in lowerHalfNames)):
            Actor.play(self, animName, partName=partName, fromFrame=fromFrame, toFrame=toFrame)
        else:
            # The torso and the head must stay in its current animation.
            # Let's only update the pants and the legs animation.
            for part in lowerHalfNames:
                Actor.play(self, animName, partName=part, fromFrame=fromFrame, toFrame=toFrame)
            
    def loop(self, animName, restart=1, partName=None, fromFrame=None, toFrame=None):
        lowerHalfNames = self.__getLowerHalfPartNames()
        if self.forcedTorsoAnim is None:
            return Actor.loop(self, animName, restart=restart, partName=partName, fromFrame=fromFrame, toFrame=toFrame)
        else:
            # The torso and the head must stay in its current animation.
            # Let's only update the pants and the legs animation.
            for index, part in enumerate(lowerHalfNames):
                output = Actor.loop(self, animName, restart=restart, partName=part, fromFrame=fromFrame, toFrame=toFrame)
                
                    
    def __getUpperHalfPartNames(self):
        return ['head', 'torso-top']
            
    def __getLowerHalfPartNames(self):
        return ['torso-pants', 'legs']

    def setSpeed(self, forwardSpeed, rotateSpeed, strafeSpeed = 0.0):
        if self.forceRunSpeed:
            forwardSpeed = CIGlobals.RunCutOff
        self.forwardSpeed = forwardSpeed
        self.rotateSpeed = rotateSpeed
        self.strafeSpeed = strafeSpeed
        action = None
        if self.standWalkRunReverse != None:

            rotateCutOff = CIGlobals.RotateCutOff if not self.isLocalAvatar() else CIGlobals.WalkCutOff
        
            if strafeSpeed < CIGlobals.StrafeCutOff and strafeSpeed > -CIGlobals.StrafeCutOff:
                self.resetTorsoRotation()

            if forwardSpeed >= CIGlobals.RunCutOff:
                action = CIGlobals.RUN_INDEX
            elif forwardSpeed > CIGlobals.WalkCutOff:
                action = CIGlobals.WALK_INDEX
            elif forwardSpeed < -CIGlobals.WalkCutOff:
                action = CIGlobals.REVERSE_INDEX
            elif abs(rotateSpeed) > rotateCutOff:
                action = CIGlobals.WALK_INDEX
            elif abs(strafeSpeed) > CIGlobals.RunCutOff:
                action = CIGlobals.RUN_INDEX
            elif abs(strafeSpeed) > CIGlobals.WalkCutOff:
                action = CIGlobals.WALK_INDEX
            else:
                action = CIGlobals.STAND_INDEX

            if abs(strafeSpeed) > CIGlobals.WalkCutOff:
                spine = self.find("**/def_spineB")

                if spine.isEmpty():
                    spine = self.controlJoint(None, "torso", "def_spineB")

                movementVec = Vec3(strafeSpeed, forwardSpeed, 0)
                movementVec.normalize()
                movementAngle = rad2Deg(math.atan2(movementVec[1], movementVec[0])) - 90.0
                
                if action == CIGlobals.REVERSE_INDEX:
                    movementAngle -= 180
                
                spine.setH(-movementAngle)
                self.getPart('legs').setH(movementAngle)
            
            anim, rate = self.standWalkRunReverse[action]
            if anim != self.playingAnim or rate != self.playingRate or self.forcedTorsoAnim != self.lastForcedTorsoAnim:
                self.playingAnim = anim
                self.playingRate = rate
                self.lastForcedTorsoAnim = self.forcedTorsoAnim
                
                if self.forcedTorsoAnim is None:
                    self.loop(anim)
                else:

                    # Whatever happens to the legs should also happen on the pants.
                    self.loop(anim, partName = 'torso-pants')
                    self.loop(anim, partName = 'legs')
                self.setPlayRate(rate, anim)
        return action

    def enterSquish(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'squish'
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getGeomNode().getChild(0)
        origScale = node.getScale()
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('getSquished')
        else:
            name = 'getSquished'
        self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'),
            Wait(1.0),
            Parallel(Sequence(Wait(0.4),
            LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'),
            LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'),
            LerpScaleInterval(node, lerpTime / 3.0, origScale, blendType='easeInOut')),
            ActorInterval(self, 'happy', startTime=0.2), SoundInterval(sound)), name = name)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.squishDone, [callback, extraArgs])
        self.track.delayDelete = DelayDelete.DelayDelete(self, name)
        self.track.start(ts)

    def squishDone(self, callback = None, extraArgs = []):
        self.__doCallback(callback, extraArgs)

    def exitSquish(self):
        if self.track:
            self.ignore(self.track.getName())
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track.finish()
            self.track = None
        self.playingAnim = 'neutral'

    def enterDeadNeutral(self, ts = 0, callback = None, extraArgs = []):
        self.loop('dneutral')

    def exitDeadNeutral(self):
        self.stop()

    def enterDeadWalk(self, ts = 0, callback = None, extraArgs = []):
        self.loop('dwalk')

    def exitDeadWalk(self):
        self.stop()

    def setBackpack(self, pack):
        self.backpack = pack

    def getGhost(self):
        return 0

    def updateChatSoundDict(self):
        self.chatSoundDict['exclaim'] = base.audio3d.loadSfx(self.getToonAnimalNoise('exclaim'))
        self.chatSoundDict['question'] = base.audio3d.loadSfx(self.getToonAnimalNoise('question'))
        self.chatSoundDict['short'] = base.audio3d.loadSfx(self.getToonAnimalNoise('short'))
        self.chatSoundDict['medium'] = base.audio3d.loadSfx(self.getToonAnimalNoise('med'))
        self.chatSoundDict['long'] = base.audio3d.loadSfx(self.getToonAnimalNoise('long'))
        self.chatSoundDict['howl'] = base.audio3d.loadSfx(self.getToonAnimalNoise('howl'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['exclaim'], self.getPart('head'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['question'], self.getPart('head'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['short'], self.getPart('head'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['medium'], self.getPart('head'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['long'], self.getPart('head'))
        base.audio3d.attachSoundToObject(self.chatSoundDict['howl'], self.getPart('head'))
        
    def __actAsGone(self):
        self.nametag3d.hide()
        self.getShadow().hide()
        if self.tokenIcon:
            self.tokenIcon.hide()
        #self.stashBodyCollisions()
        
    def __restoreHide(self):
        if self.tokenIcon:
            self.tokenIcon.show()
        self.getShadow().show()
        self.nametag3d.show()
        self.getGeomNode().setTransparency(False)
        self.getGeomNode().setAlphaScale(1.0)
        self.getGeomNode().show()
        #self.unstashBodyCollisions()
        
    def handleGhost(self, flag):
        alpha = 1.0 if not flag else 0.25
        local = self == base.localAvatar
        if flag:
            if self.getAccessLevel() >= base.localAvatar.getAccessLevel():
                # Other staff members at this access level or higher should
                # be able to see this avatar still.
                alpha = 0.25
                #self.stashBodyCollisions()
            elif not local:
                self.getGeomNode().setTransparency(True)
                self.getGeomNode().setColorScale(1.0, 1.0, 1.0, 0.0)
                self.__actAsGone()
        else:
            self.__restoreHide()
        if local:
            self.getGeomNode().setTransparency(flag)
            self.getGeomNode().setColorScale(1.0, 1.0, 1.0, alpha)
        

    def attachGun(self, gunName):
        self.detachGun()
        if gunName == "pistol":
            self.gun = loader.loadModel("phase_4/models/props/water-gun.bam")
            self.gun.reparentTo(self.find('**/def_joint_right_hold'))
            self.gun.setPos(Point3(0.28, 0.1, 0.08))
            self.gun.setHpr(VBase3(85.6, -4.44, 94.43))
            self.gunAttached = True
        elif gunName == "shotgun":
            self.gun = loader.loadModel("phase_4/models/props/shotgun.egg")
            self.gun.setScale(0.75)
            self.gun.reparentTo(self.find('**/def_joint_right_hold'))
            self.gun.setPos(Point3(-0.5, -0.2, 0.19))
            self.gun.setHpr(Vec3(350, 272.05, 0))
            color = random.choice(
                [
                    VBase4(1, 0.25, 0.25, 1),
                    VBase4(0.25, 1, 0.25, 1),
                    VBase4(0.25, 0.25, 1, 1)
                ]
            )
            self.gun.setColorScale(color)
            self.gunAttached = True
        elif gunName == "sniper":
            self.gun = loader.loadModel("phase_4/models/props/sniper.egg")
            self.gun.setScale(0.75)
            self.gun.reparentTo(self.find('**/def_joint_right_hold'))
            self.gun.setPos(Point3(-0.5, -0.2, 0.19))
            self.gun.setHpr(Vec3(350, 272.05, 0))
            color = random.choice(
                [
                    VBase4(1, 0.25, 0.25, 1),
                    VBase4(0.25, 1, 0.25, 1),
                    VBase4(0.25, 0.25, 1, 1)
                ]
            )
            self.gun.setColorScale(color)
            self.gunAttached = True


    def detachGun(self):
        if self.gun and self.gunAttached:
            self.gun.removeNode()
            self.gun = None
            self.gunAttached = False

    def stopAnimations(self):
        if hasattr(self, 'animFSM'):
            if not self.animFSM.isInternalStateInFlux():
                self.animFSM.request('off')
            else:
                self.notify.warning("animFSM in flux, state=%s, not requesting off" % self.animFSM.getCurrentState().getName())
        else:
            self.notify.warning("animFSM has been deleted")
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        return

    def disable(self):
        try:
            self.Toon_disabled
        except:
            self.Toon_disabled = 1
            self.ignoreAll()
            self.backpack = None
            self.collsSetup = False
            self.stopAnimations()
            self.removeAdminToken()
            ToonHead.delete(self)
            self.deleteCurrentToon()
            self.chatSoundDict = {}
            Avatar.Avatar.disable(self)

    def delete(self):
        try:
            self.Toon_deleted
        except:
            self.Toon_deleted = 1
            del self.animFSM
            self.forwardSpeed = None
            self.chatSoundDict = None
            self.rotateSpeed = None
            self.avatarType = None
            self.track = None
            self.standWalkRunReverse = None
            self.currentAnim = None
            self.toon_head = None
            self.forcedTorsoAnim = None
            self.lastForcedTorsoAnim = None
            self.toon_torso = None
            self.toon_legs = None
            self.gender = None
            self.headtype = None
            self.head = None
            self.legtype = None
            self.torsotype = None
            self.hr = None
            self.hg = None
            self.hb = None
            self.tr = None
            self.tg = None
            self.tb = None
            self.lr = None
            self.lg = None
            self.lb = None
            self.shir = None
            self.shig = None
            self.shib = None
            self.shor = None
            self.shog = None
            self.shob = None
            self.shirt = None
            self.sleeve = None
            self.short = None
            self.tag = None
            self.money = None
            self.lookAtTrack = None
            self.portal1 = None
            self.portal2 = None
            self.backpack = None
            self.fallSfx = None
            self.eyes = None
            self.myTaskId = None
            self.closedEyes = None
            self.soundChatBubble = None
            self.lastAction = None
            self.lastState = None
            self.playingAnim = None
            self.playingRate = None
            self.accessories = None
            Avatar.Avatar.delete(self)
        return

    def initCollisions(self):
        self.collNodePath.setCollideMask(BitMask32(0))
        self.collNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)

        pusher = CollisionHandlerPusher()
        pusher.setInPattern("%in")
        pusher.addCollider(self.collNodePath, self)
        base.cTrav.addCollider(self.collNodePath, pusher)

    def deleteCurrentToon(self):
        if self.shadowCaster:
            self.shadowCaster.clear()
            self.shadowCaster = None

        try:
            self.stopLookAround()
            self.stopBlink()
        except:
            pass

        for accessory in self.accessories:
            accessory.removeNode()
        self.accessories = []

        self.pupils = []

        if 'head' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['head']
        if 'torso' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['torso']
        if 'legs' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['legs']
        
        self.deleteShadow()
        self.removePart('head')
        self.removePart('torso')
        self.removePart('legs')
        self.detachGun()

        self.clearPythonData()
        self.flush()

    def setAdminToken(self, tokenInstance):
        if tokenInstance and tokenInstance.assetId > -1:
            icons = loader.loadModel("phase_3/models/props/gm_icons.bam")
            self.tokenIcon = icons.find('**/access_level_%s' % (tokenInstance.assetId))
            self.tokenIcon.reparentTo(self)
            x = self.nametag3d.getX()
            y = self.nametag3d.getY()
            z = self.nametag3d.getZ()
            self.tokenIcon.setPos(Vec3(x, y, z) + (0, 0, 0.5))
            self.tokenIcon.setScale(0.4)
            self.tokenIconIval = Sequence(LerpHprInterval(self.tokenIcon, duration = 3.0, hpr = Vec3(360, 0, 0), startHpr = Vec3(0, 0, 0)))
            self.tokenIconIval.loop()
            icons.removeNode()
        else:
            self.removeAdminToken()

    def removeAdminToken(self):
        if self.tokenIcon != None and self.tokenIconIval != None:
            self.tokenIconIval.finish()
            self.tokenIcon.removeNode()
            self.tokenIconIval = None
            self.tokenIcon = None

    def playChatSfx(self, chatString):
        if not self.getGhost() or self.doId == base.localAvatar.doId:
            if "ooo" in chatString.lower():
                sfx = self.chatSoundDict['howl']
            elif "!" in chatString.lower():
                sfx = self.chatSoundDict['exclaim']
            elif "?" in chatString.lower():
                sfx = self.chatSoundDict['question']
            elif len(chatString) <= 9:
                sfx = self.chatSoundDict['short']
            elif 10 <= len(chatString) <= 19:
                sfx = self.chatSoundDict['medium']
            elif len(chatString) >= 20:
                sfx = self.chatSoundDict['long']
            base.playSfx(sfx, node = self)

    def chatStompComplete(self, chatString):
        if not self.thoughtInProg and CIGlobals.getSettingsMgr().getSetting("chs") is True:
            self.playChatSfx(chatString)

    def setName(self, nameString):
        Avatar.Avatar.setName(self, nameString)

    def setDNAStrand(self, dnaStrand, makeTag = 1):
        ToonDNA.ToonDNA.setDNAStrand(self, dnaStrand)
        self.deleteCurrentToon()
        self.generateToon(makeTag)

    def generateMask(self):
        # No accessories yet.

        if self.shirt == self.maleTopDNA2maleTop['135'][0] or self.shirt == self.maleTopDNA2maleTop['136'][0]:
            # This toon is wearing the tsa suit, give them some sweet shades.
            name = 'tsaGlasses'
            glasses = loader.loadModel(AccessoryGlobals.AccessoryName2Model[name])
            glassesNode = self.getPart('head').attachNewNode('glassesNode')
            glasses.reparentTo(glassesNode)
            data = AccessoryGlobals.MaskTransExtended[name].get(self.animal)
            if not data:
                data = AccessoryGlobals.MaskTrans.get(self.animal)
                posHprScale = AccessoryGlobals.MaskTrans[self.animal][self.headLength]
            else:
                posHprScale = AccessoryGlobals.MaskTransExtended[name][self.animal].get(self.headLength)
                if not posHprScale:
                    posHprScale = AccessoryGlobals.MaskTrans[self.animal][self.headLength]

            glasses.setPos(posHprScale[0])
            glasses.setHpr(posHprScale[1])
            glasses.setScale(posHprScale[2])

            self.accessories.append(glassesNode)

    def generateToon(self, makeTag = 1):
        self.generateLegs()
        self.generateTorso()
        self.generateHead()
        self.setToonColor()
        self.setClothes()
        self.setGloves()
        self.parentToonParts()
        self.rescaleToon()
        self.generateMask()

        # Make torso subparts so we can play a run animation on the pants but another animation on the spine and arms.
        if self.gender == 'boy':
            self.makeSubpart("torso-pants", ["def_left_pant_bottom", "def_left_pant_top", "def_right_pant_bottom", "def_right_pant_top"], parent = "torso")
        elif self.gender == 'girl':
            if self.torso == 'dgs_skirt':
                self.makeSubpart("torso-pants", ["def_left_skirt_backA", "def_left_skirt_frontA", "def_left_skirt_topA",
                                                 "def_right_skirt_backA", "def_right_skirt_frontA", "def_right_skirt_topA"], parent = "torso")
            elif self.torso == 'dgl_skirt':
                self.makeSubpart("torso-pants", ["def_left_skirt_bottomA", "def_left_skirt_topA", "def_right_hip"], parent = "torso")
            else:
                self.makeSubpart("torso-pants", ["def_left_skirt_bottomA", "def_left_skirt_topA", "def_right_skirt_bottomA", "def_right_skirt_topA"], parent = "torso")
        self.makeSubpart("torso-top", ["def_spineB"], parent = "torso")

        Avatar.Avatar.initShadow(self)
        
        self.updateChatSoundDict()
        self.setBlend(frameBlend = True)

        bodyMat = CIGlobals.getCharacterMaterial(shininess = 5, specular = (0.5, 0.5, 0.5, 1))
        self.setMaterial(bodyMat, 1)

        if not hasattr(base, 'localAvatar') or base.localAvatar != self:
            self.setupPhysics(1.0, self.getHeight())

        # We can safely optimize the scene graph and combine nodes since we're done manipulating
        # the separate pieces. After this point, the separate pieces of the toon are no
        # longer manipulatable, such as arms, sleeves, shirt, etc. If this needs to be done,
        # the toon will have to be regenerated.
        
        # Don't do it in Make-A-Toon though, as we have to be constantly modifying the pieces.
        if not self.mat:
            self.getPart('legs').flattenStrong()
            self.postFlatten()

        if makeTag:
            self.setupNameTag()
        if self.cr.isShowingPlayerIds:
            self.showAvId()

        self.loop('neutral')

    def attachTNT(self):
        self.pies.attachTNT()
        self.holdTNTAnim()

    def detachTNT(self):
        self.pies.detachTNT()
        self.animFSM.request(self.animFSM.getCurrentState().getName())

    def holdTNTAnim(self):
        self.pose("toss", 22, partName = "torso")

    def parentToonParts(self):
        self.attach('head', 'torso', 'def_head')
        self.attach('torso', 'legs', 'joint_hips')

    def unparentToonParts(self):
        self.getPart('head').reparentTo(self.getGeomNode())
        self.getPart('torso').reparentTo(self.getGeomNode())
        self.getPart('legs').reparentTo(self.getGeomNode())
        
    def getHeadHeight(self):
        animal = self.getAnimal()
        headScale = ToonGlobals.HeadScales[animal][2]
        headHeight = ToonGlobals.HeadHeightDict[self.head] * headScale
        return headHeight

    def rescaleToon(self):
        animal = self.getAnimal()
        bodyScale = ToonGlobals.BodyScales[animal]
        headScale = ToonGlobals.HeadScales[animal][2]
        shoulderHeight = ToonGlobals.LegHeightDict[self.legs] * bodyScale + ToonGlobals.TorsoHeightDict[self.torso] * bodyScale
        height = shoulderHeight + ToonGlobals.HeadHeightDict[self.head] * headScale
        bodyScale = ToonGlobals.BodyScales[animal]
        self.setAvatarScale(bodyScale)
        self.getPart('head').setScale(headScale)
        self.setHeight(height)

    def setGloves(self):
        color = self.getGloveColor()
        gloves = self.find('**/hands')
        gloves.setColor(color)

    def setClothes(self):
        shirt, shirtcolor = self.getShirtStyle()
        short, shortcolor = self.getShortStyle()
        sleeve, sleevecolor = self.getSleeveStyle()
        torsot = self.findAllMatches('**/torso-top')
        torsob = self.findAllMatches('**/torso-bot')
        sleeves = self.findAllMatches('**/sleeves')
        torsot.setBSPMaterial(shirt, 1)
        torsob.setBSPMaterial(short, 1)
        sleeves.setBSPMaterial(sleeve, 1)
        torsot.setColor(shirtcolor)
        sleeves.setColor(sleevecolor)
        torsob.setColor(shortcolor)

    def generateLegs(self):
        ToonGlobals.generateBodyPart(self, 'legs', self.getLegs(), 3, 'shorts')
        self.find('**/boots_long').stash()
        self.find('**/boots_short').stash()
        self.find('**/shoes').stash()

    def generateTorso(self):
        ToonGlobals.generateBodyPart(self, 'torso', self.getTorso(), 3, '')

    def generateHead(self, pat=0):
        gender = self.getGender()
        head = self.getAnimal()
        headtype = self.getHead()
        ToonHead.generateHead(self, gender, head, headtype)

    def setToonColor(self):
        self.setHeadColor()
        self.setTorsoColor()
        self.setLegColor()

    def setLegColor(self):
        legcolor = self.getLegColor()
        self.findAllMatches('**/legs').setColor(legcolor)
        self.findAllMatches('**/feet').setColor(legcolor)

    def setTorsoColor(self):
        torsocolor = self.getTorsoColor()
        self.findAllMatches('**/arms').setColor(torsocolor)
        self.findAllMatches('**/neck').setColor(torsocolor)
        self.findAllMatches('**/hands').setColor(1,1,1,1)

    def enterOff(self, ts = 0, callback = None, extraArgs = []):
        self.currentAnim = None
        return

    def exitOff(self):
        pass

    def enterWin(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'win'
        self.sfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_Win.ogg")
        self.sfx.setLoop(True)
        base.audio3d.attachSoundToObject(self.sfx, self)
        base.playSfx(self.sfx, node = self, looping = 1)
        self.loop("win")

    def exitWin(self):
        self.stop()
        self.sfx.stop()
        del self.sfx
        self.playingAnim = 'neutral'

    def enterShrug(self, ts = 0, callback = None, extraArgs = []):
        self.play("shrug")

    def exitShrug(self):
        self.exitGeneral()

    def enterHDance(self, ts = 0, callback = None, extraArgs = []):
        self.play("hdance")

    def exitHDance(self):
        self.exitGeneral()

    def enterScientistWork(self, ts = 0, callback = None, extraArgs = []):
        self.loop("scwork")

    def exitScientistWork(self):
        self.exitGeneral()

    def enterScientistEmcee(self, ts = 0, callback = None, extraArgs = []):
        self.loop("scemcee")

    def exitScientistEmcee(self):
        self.exitGeneral()

    def enterScientistGame(self, ts = 0, callback = None, extraArgs = []):
        self.loop("scgame")

    def exitScientistGame(self):
        self.exitGeneral()

    def enterScientistJealous(self, ts = 0, callback = None, extraArgs = []):
        self.loop("scjealous")

    def exitScientistJealous(self):
        self.exitGeneral()

    def enterWave(self, ts = 0, callback = None, extraArgs = []):
        self.play("wave")

    def exitWave(self):
        self.exitGeneral()

    def enterLaugh(self, ts = 0, callback = None, extraArgs = []):
        self.setPlayRate(5.0, "neutral")
        self.loop("neutral")

    def exitLaugh(self):
        self.setPlayRate(1.0, "neutral")
        self.stop()

    def enterNeutral(self, ts = 0, callback = None, extraArgs = []):
        if self.backpack:
            cg = self.backpack.getCurrentGag()
            if cg and cg.getState() in [GagState.START, GagState.RELEASED]:
                self.loop("neutral", partName = "legs")
                if self.animal == "dog":
                    self.loop("neutral", partName = "head")
                return
        if self.forcedTorsoAnim != None:
            self.loop(self.forcedTorsoAnim, partName = 'torso')
            self.loop("neutral", partName = "legs")
            return
        self.loop("neutral")
        self.playingAnim = 'neutral'

    def exitNeutral(self):
        self.exitGeneral()
        self.playingAnim = 'neutral'

    def exitGeneral(self):
        if self.backpack:
            cg = self.backpack.getCurrentGag()
            if cg and cg.getState() in [GagState.START, GagState.RELEASED]:
                self.stop(partName = 'legs')
                return

        self.stop()

    def enterRun(self, ts = 0, callback = None, extraArgs = []):
        if self.backpack:
            cg = self.backpack.getCurrentGag()
            if cg and cg.getState() in [GagState.START, GagState.RELEASED]:
                self.loop('run', partName = 'legs')
                if self.animal == 'dog':
                    self.loop('run', partName = 'head')
                return
        if self.forcedTorsoAnim != None:
            self.loop(self.forcedTorsoAnim, partName = 'torso')
            self.loop('run', partName = 'legs')
            return
        self.loop("run")

    def exitRun(self):
        self.exitGeneral()

    def enterWalk(self, ts = 0, callback = None, extraArgs = []):
        if self.backpack:
            cg = self.backpack.getCurrentGag()
            if cg and cg.getState() in [GagState.START, GagState.RELEASED]:
                self.loop('walk', partName = 'legs')
                if self.animal == 'dog':
                    self.loop('walk', partName = 'head')
                return
        if self.forcedTorsoAnim != None:
            self.loop(self.forcedTorsoAnim, partName = 'torso')
            self.loop('walk', partName = 'legs')
            return
        self.loop('walk')

    def exitWalk(self):
        self.exitGeneral()

    def enterWalkBack(self, ts = 0, callback = None, extraArgs = []):
        self.setPlayRate(-1.0, "walk")
        self.enterWalk()

    def exitWalkBack(self):
        self.exitWalk()
        self.setPlayRate(1.0, "walk")

    def enterOpenBook(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'book'
        self.book1 = Actor("phase_3.5/models/props/book-mod.bam",
                    {"chan": "phase_3.5/models/props/book-chan.bam"})
        self.book1.reparentTo(self.getPart('torso').find('**/def_joint_right_hold'))
        self.track = ActorInterval(self, "book", startFrame=CIGlobals.OpenBookFromFrame, endFrame=CIGlobals.OpenBookToFrame,
                name = self.uniqueName('enterOpenBook'))
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.__doCallback, [callback, extraArgs])
        self.track.start(ts)
        self.book1.play("chan", fromFrame=CIGlobals.OpenBookFromFrame, toFrame=CIGlobals.OpenBookToFrame)

    def exitOpenBook(self):
        if self.track:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            self.track = None
        if self.book1:
            self.book1.cleanup()
            self.book1 = None
        self.playingAnim = 'neutral'

    def enterReadBook(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'book'
        self.book2 = Actor("phase_3.5/models/props/book-mod.bam",
                    {"chan": "phase_3.5/models/props/book-chan.bam"})
        self.book2.reparentTo(self.getPart('torso').find('**/def_joint_right_hold'))

        self.pingpong("book", fromFrame=CIGlobals.ReadBookFromFrame, toFrame=CIGlobals.ReadBookToFrame)
        self.book2.pingpong("chan", fromFrame=CIGlobals.ReadBookFromFrame, toFrame=CIGlobals.ReadBookToFrame)

    def exitReadBook(self):
        if self.book2:
            self.book2.cleanup()
            self.book2 = None
        self.playingAnim = 'neutral'

    def enterCloseBook(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'book'
        self.book3 = Actor("phase_3.5/models/props/book-mod.bam",
                    {"chan": "phase_3.5/models/props/book-chan.bam"})
        self.book3.reparentTo(self.getPart('torso').find('**/def_joint_right_hold'))
        self.track = ActorInterval(self, "book", startFrame=CIGlobals.CloseBookFromFrame, endFrame=CIGlobals.CloseBookToFrame,
                name = self.uniqueName('enterCloseBook'))
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.__doCallback, [callback, extraArgs])
        self.track.start(ts)
        self.book3.play("chan", fromFrame=CIGlobals.CloseBookFromFrame, toFrame=CIGlobals.CloseBookToFrame)
        self.lerpLookAt(self.getPart('head'), (0, 0, 0))

    def exitCloseBook(self):
        if self.track:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            self.track = None
        if self.book3:
            self.book3.cleanup()
            self.book3 = None
        self.playingAnim = 'neutral'

    def enterTeleportOut(self, ts = 0, callback = None, extraArgs = []):
        self.notify.info(str(self.doId) + "-" + str(self.zoneId) + ": enterTeleportOut")
        self.playingAnim = 'tele'
        self.portal1 = Actor("phase_3.5/models/props/portal-mod.bam",
                            {"chan": "phase_3.5/models/props/portal-chan.bam"})
        self.portal1.play("chan")
        self.portal1.reparentTo(self.getPart('legs').find('**/def_joint_right_hold'))
        self.play("tele")
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('enterTeleportOut')
        else:
            name = 'enterTeleportOut'
            
        self.track = Sequence(Wait(0.4), 
            Func(self.teleportOutSfx), 
            Wait(1.3),
            Func(self.throwPortal), 
            Wait(1.1), 
            Func(self.__actAsGone), 
            Wait(1.5),
        name = name)

        self.track.delayDelete = DelayDelete.DelayDelete(self, name)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getName(), self.teleportOutDone, [callback, extraArgs])
        self.track.start(ts)

    def doPortalBins(self, portal):
        portal.setBin('shadow', 0)
        portal.setDepthWrite(0)
        portal.setDepthTest(0)

    def teleportOutDone(self, callback, requestStatus):
        self.notify.info(str(self.doId) + "-" + str(self.zoneId) + ": teleportOutDone")
        self.__doCallback(callback, requestStatus)
        self.exitTeleportOut()

    def teleportOutSfx(self):
        self.outSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/AV_teleport.ogg")
        base.audio3d.attachSoundToObject(self.outSfx, self.portal1)
        base.playSfx(self.outSfx, node = self)

    def throwPortal(self):
        self.doPortalBins(self.portal1)
        self.portal1.reparentTo(self.getPart('legs').find('**/joint_nameTag'))
        self.portal1.setScale(CIGlobals.PortalScale)
        self.portal1.setY(6.5)
        self.portal1.setH(180)

    def exitTeleportOut(self):
        self.notify.info(str(self.doId) + "-" + str(self.zoneId) + ": exitTeleportOut")
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.portal1:
            self.portal1.cleanup()
            self.portal1 = None
        if hasattr(self, 'shadow') and self.shadow is not None:
            self.shadow.show()
        self.playingAnim = 'neutral'

    def getTeleportInTrack(self, portal):
        self.doPortalBins(portal)

        holeTrack = Sequence()
        holeTrack.append(Func(portal.reparentTo, self))
        pos = Point3(0, -2.4, 0)
        holeTrack.append(Func(portal.setPos, pos))
        holeTrack.append(ActorInterval(portal, 'chan', startTime = 3.4, endTime = 3.1))
        holeTrack.append(Wait(0.6))
        holeTrack.append(ActorInterval(portal, 'chan', startTime = 3.1, endTime = 3.4))

        def restorePortal(portal):
            portal.setPos(0, 0, 0)
            portal.detachNode()
            portal.clearBin()
            portal.clearDepthTest()
            portal.clearDepthWrite()

        holeTrack.append(Func(restorePortal, portal))
        toonTrack = Sequence(
            Wait(0.3), 
            Func(self.__restoreHide),
            ActorInterval(self, 'happy', startTime = 0.45))

        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportIn')
        else:
            trackName = 'teleportIn'
        return Parallel(toonTrack, holeTrack, name = trackName)

    def enterTeleportIn(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'happy'
        self.portal2 = Actor("phase_3.5/models/props/portal-mod.bam",
                            {"chan": "phase_3.5/models/props/portal-chan.bam"})
        self.show()
        self.getGeomNode().hide()
        self.nametag3d.hide()
        self.track = self.getTeleportInTrack(self.portal2)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getName(), self.teleportInDone, [callback, extraArgs])
        if hasattr(self, 'acquireDelayDelete'):
            self.track.delayDelete = DelayDelete.DelayDelete(self, self.track.getName())
        self.track.start(ts)

    def teleportInDone(self, callback, extraArgs):
        self.exitTeleportIn()
        self.__doCallback(callback, extraArgs)

    def exitTeleportIn(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.portal2:
            self.portal2.cleanup()
            self.portal2 = None
        if self.nametag3d:
            self.nametag3d.show()
        self.playingAnim = 'neutral'

    def enterFallFWD(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'fallf'
        self.play("fallf")
        Sequence(Wait(0.5), SoundInterval(self.fallSfx, node = self)).start()

    def exitFallFWD(self):
        self.exitGeneral()
        self.playingAnim = 'neutral'

    def enterFallBCK(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'fallb'
        self.play("fallb")
        Sequence(Wait(0.5), SoundInterval(self.fallSfx, node = self)).start()

    def exitFallBCK(self):
        self.playingAnim = 'neutral'
        self.exitGeneral()

    def enterHappyJump(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'happy'
        self.play("happy")

    def exitHappyJump(self):
        self.exitGeneral()
        self.playingAnim = 'neutral'

    def enterSwim(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'swim'
        self.loop("swim")

        self.resetTorsoRotation()

        toon = self.getGeomNode()
        toon.setP(-89.0)
        
        if self.shadow:
            self.shadow.hide()

        self.swimBobTrack = Sequence(LerpPosInterval(toon, duration = 1, pos = (0, -3, 3), startPos = (0, -3, 4), blendType = 'easeInOut'),
                                     LerpPosInterval(toon, duration = 1, pos = (0, -3, 4), startPos = (0, -3, 3), blendType = 'easeInOut'))
        self.swimBobTrack.loop()
        self.nametag3d.setZ(5.0)

    def exitSwim(self):
        self.swimBobTrack.finish()
        del self.swimBobTrack
        if self.shadow:
            self.shadow.show()
        self.exitGeneral()
        self.getGeomNode().setPosHpr(0, 0, 0, 0, 0, 0)
        nt = self.nametag3d
        nt.setX(0)
        nt.setY(0)
        nt.setZ(self.getHeight() + 0.5)
        self.playingAnim = 'neutral'

    def enterDied(self, ts = 0, callback = None, extraArgs = []):
        
        def shouldDisableGags():
            if hasattr(self, 'disableGags'):
                self.disableGags()
            if hasattr(self, 'b_setCurrentGag'):
                self.b_setCurrentGag(-1)
        
        self.playingAnim = 'lose'
        self.isdying = True
        self.play("lose")
        self.track = Sequence(
            Func(self.clearForcedTorsoAnim),
            Func(shouldDisableGags),
            Wait(2.2), 
            Func(self.dieSfx), 
            Wait(2.8), 
            self.getGeomNode().scaleInterval(2, 
                Point3(0.01), 
            startScale=(self.getGeomNode().getScale())), 
            Func(self.delToon),
        name = self.uniqueName('enterDied'))
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.diedDone, [callback, extraArgs])
        self.track.delayDelete = DelayDelete.DelayDelete(self, 'enterTeleportOut')
        self.track.start(ts)

    def diedDone(self, callback, extraArgs):
        self.__doCallback(callback, extraArgs)
        self.exitDied()

    def __doCallback(self, callback, extraArgs):
        if callback:
            if extraArgs:
                callback(*extraArgs)
            else:
                callback()

    def dieSfx(self):
        self.Losesfx = base.audio3d.loadSfx("phase_5/audio/sfx/ENC_Lose.ogg")
        base.audio3d.attachSoundToObject(self.Losesfx, self)
        base.playSfx(self.Losesfx, node = self)

    def delToon(self):
        self.isdead = True

    def exitDied(self):
        if self.track != None:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'enableGags'):
            self.enableGags()

        self.rescaleToon()
        self.playingAnim = 'neutral'

    def enterJump(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'jump'
        self.loop("jump")

    def exitJump(self):
        self.exitGeneral()
        self.playingAnim = 'neutral'

    def enterLeap(self, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'leap'
        self.loop("leap")

    def exitLeap(self):
        self.exitGeneral()
        self.playingAnim = 'neutral'

    def enterCringe(self, ts = 0, callback = None, extraArgs = []):
        self.play("cringe")

    def exitCringe(self):
        self.exitGeneral()

    def enterConked(self, ts = 0, callback = None, extraArgs = []):
        self.play("conked")

    def exitConked(self):
        self.exitGeneral()

