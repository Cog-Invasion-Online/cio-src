"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Avatar.py
@author Brian Lach
@date July ??, 2014

"""

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectLabel
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func, LerpColorScaleInterval

from panda3d.core import BitMask32, ConfigVariableBool, TransformState, Point3, NodePath, TextNode, Vec2, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape

from src.coginvasion.globals import CIGlobals
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.npc import DisneyCharGlobals as DCG
from src.coginvasion.toon import ToonTalker
from src.coginvasion.nametag.NametagGroup import NametagGroup
from src.coginvasion.phys.PhysicsNodePath import BasePhysicsObject
from src.coginvasion.base.Wake import Wake
from src.coginvasion.base.Splash import Splash
from src.coginvasion.avatar.AvatarShared import AvatarShared
import random
from ChatTypes import *

notify = directNotify.newCategory("Avatar")

class Avatar(ToonTalker.ToonTalker, Actor, AvatarShared):
    """
    Client side implementation of the base Avatar.
	
    An Avatar is an animatable character, playable or non-playable, that can be involved
    in combat. Also has the ability to chat, have a nametag, hitbox, and more.
    """

    RealShadows = ConfigVariableBool('want-real-shadows', False)
    AvatarMovedEpsilon = 0.05

    def __init__(self, mat=0):
        try:
            self.Avatar_initialized
            return
        except:
            self.Avatar_initialized = 1

        ToonTalker.ToonTalker.__init__(self)
        #BasePhysicsObject.__init__(self)
        AvatarShared.__init__(self)
        Actor.__init__(self, None, None, None, flattenable=0, setFinal=1)
        
        # All avatars should be ambient boosted to help them stand out more in BSP levels.
        self.setAmbientBoost()

        self.shapeGroup = CIGlobals.WallGroup | CIGlobals.CharacterGroup

        #self.getGeomNode().showThrough(CIGlobals.ShadowCameraBitmask)
        
        self.usedAnims = []

        self.moveAnimProperties = {}

        self.mat = mat
        self.chat = ''

        self.nametagNodePath = None
        self.__nameVisible = 1
        self.nametag = NametagGroup()
        self.nametag.setAvatar(self)
        font = CIGlobals.getToonFont()
        self.nametag.setFont(font)
        self.nametag.setChatFont(font)
        self.nametag3d = self.attachNewNode('nametag3d')
        self.nametag3d.setTag('cam', 'nametag')

        self.setTwoSided(False)

        self.forwardSpeed = 0.0
        self.rotateSpeed = 0.0
        self.strafeSpeed = 0.0
        self.currentSpeed = 0.0
        self.standWalkRunReverse = None
        self.currentMoveAction = None

        self.enableBlend()

        self.showNametagInMargins = True
        self.avatarType = None
        self.charName = None
        self.tag = None

        self.splashEffect = None
        self.splashSound = None
        
        self.shadow = None

        self.prevPos = Point3(0)
        self.wake = None
        self.lastWakeTime = 0.0

        self.thoughtInProg = False

        self.shadowFloorToggle = False
        self.avatarFloorToggle = False
        self.floorTask = taskMgr.add(self.__keepOnFloorTask, "Avatar.keepOnFloor", sort = 30)
        
        self.ragdoll = None
        self.ragdollMode = False

        self.healthLabel = None
        self.healthLabelTrack = None
        self.dmgFadeIval = None

        self.forcedTorsoAnim = None
        self.lastForcedTorsoAnim = None

        self.activityTrack = None
        self.wasDoingActivity = False
        
        self.fadeTrack = None
        
        self.playedAnims = None
        
        self.chatSoundTable = {}

        return
        
    def doScaleUp(self):
        self.scaleInterval(2.0, (1, 1, 1), (0.01, 0.01, 0.01)).start()
        
    def recordUsedAnim(self, animName):
        if not animName in self.usedAnims:
            self.usedAnims.append(animName)
        
    def clearFadeTrack(self):
        if self.fadeTrack:
            self.fadeTrack.finish()
        self.fadeTrack = None
    
    def fadeOut(self, time = 1.0):
        self.clearFadeTrack()
        self.fadeTrack = Sequence(Func(self.setTransparency, 1),
            LerpColorScaleInterval(self, time, (1, 1, 1, 0), (1, 1, 1, 1)),
            Func(self.hide))
        self.fadeTrack.start()
        
    def fadeIn(self, time = 1.0):
        self.clearFadeTrack()
        self.fadeTrack = Sequence(Func(self.setTransparency, 1),
            LerpColorScaleInterval(self, time, (1, 1, 1, 1), (1, 1, 1, 0)),
            Func(self.setTransparency, 0))
        self.fadeTrack.start()

    def getAttackMgr(self):
        return base.cr.attackMgr
        
    def stopActivity(self):
        if self.activityTrack:
            self.activityTrack.finish()
        self.activityTrack = None
        self.doingActivity = False

    def setActivity(self, activity, timestamp):
        AvatarShared.setActivity(self, activity, timestamp)
        
        self.stopActivity()

        if activity == -1 or activity not in self.activities:
            return

        self.doingActivity = True
        ts = globalClockDelta.localElapsedTime(timestamp)
        act = self.activities[activity]
        loop = act.shouldLoop()
        self.activityTrack = act.doActivity()
        self.activityTrack.start()
        #if loop:
        #    self.activityTrack.loop()
        #else:
        #    self.activityTrack.start()

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
            legs = self.getLowerBodySubpart()[0]
            legAnimation = self.getCurrentAnim(partName = legs)
            frame = self.getCurrentFrame(partName = legs, animName = legAnimation)

            def __anim(partName):
                self.stop(partName = partName)
                self.play(animName = legAnimation, partName = partName, fromFrame = frame)

            parts = self.getUpperBodySubpart()
            for part in parts:
                __anim(part)

        self.forcedTorsoAnim = None

    def setPlayRate(self, rate, animName, partName = None):
        if partName or not self.forcedTorsoAnim:
            Actor.setPlayRate(self, rate, animName, partName)
        else:
            parts = self.getLowerBodySubpart() + self.getUpperBodySubpart()
            for part in parts:
                Actor.setPlayRate(self, rate, animName, part)
        
    def play(self, animName, partName=None, fromFrame=None, toFrame=None):
        self.recordUsedAnim(animName)
        
        lowerHalfNames = self.getLowerBodySubpart()
        if self.forcedTorsoAnim is None or (not (partName in lowerHalfNames)):
            Actor.play(self, animName, partName=partName, fromFrame=fromFrame, toFrame=toFrame)
        else:
            # The torso and the head must stay in its current animation.
            # Let's only update the pants and the legs animation.
            for part in lowerHalfNames:
                Actor.play(self, animName, partName=part, fromFrame=fromFrame, toFrame=toFrame)
            
    def loop(self, animName, restart=1, partName=None, fromFrame=None, toFrame=None):
        self.recordUsedAnim(animName)
        
        lowerHalfNames = self.getLowerBodySubpart()
        if self.forcedTorsoAnim is None or (not (partName in lowerHalfNames)):
            return Actor.loop(self, animName, restart=restart, partName=partName, fromFrame=fromFrame, toFrame=toFrame)
        else:
            # The torso and the head must stay in its current animation.
            # Let's only update the pants and the legs animation.
            for index, part in enumerate(lowerHalfNames):
                output = Actor.loop(self, animName, restart=restart, partName=part, fromFrame=fromFrame, toFrame=toFrame)
                
    def pingpong(self, animName, restart=1, partName=None,
                 fromFrame=None, toFrame=None):
        self.recordUsedAnim(animName)
                     
        lowerHalfNames = self.getLowerBodySubpart()
        if self.forcedTorsoAnim is None or (not (partName in lowerHalfNames)):
            Actor.pingpong(self, animName, restart=restart, partName=partName, fromFrame=fromFrame, toFrame=toFrame)
        else:
            # The torso and the head must stay in its current animation.
            # Let's only update the pants and the legs animation.
            for part in lowerHalfNames:
                Actor.pingpong(self, animName, restart=restart, partName=part, fromFrame=fromFrame, toFrame=toFrame)

    def getMoveAction(self, forward, rotate, strafe):
        return 0

    def performAnim(self, anim, partName = None, animInfo = None):
        if not animInfo:
            self.loop(anim, partName = partName)
        else:
            extraArgs = animInfo.get('args', {})
            meth = animInfo.get('method', 'loop')
            if meth == 'loop':
                self.loop(anim, **extraArgs)
            elif meth == 'pingpong':
                self.pingpong(anim, **extraArgs)

    def resetMoveAnims(self, anim = None, anim2 = None):
        self.resetAnimBlends()
        if self.forcedTorsoAnim is None:
            self.disableBlend()
            self.stop()
            if anim and anim2:
                self.enableBlend()
                self.performAnim(anim, None, self.moveAnimProperties.get(anim, None))
                self.performAnim(anim2, None, self.moveAnimProperties.get(anim2, None))
        else:
            parts = self.getLowerBodySubpart()
            for part in parts:
                self.disableBlend(partName = part)
                self.stop(partName = part)
                if anim and anim2:
                    self.enableBlend(partName = part)
                    self.performAnim(anim, part, self.moveAnimProperties.get(anim, None))
                    self.performAnim(anim2, part, self.moveAnimProperties.get(anim2, None))

    def resetAnimBlends(self):
        for animName in self.usedAnims:
            self.setControlEffect(animName, 0.0)
        self.usedAnims = []

    def setSpeed(self, forwardSpeed, rotateSpeed, strafeSpeed = 0.0):
        if self.ragdollMode:
            return
        
        self.forwardSpeed = forwardSpeed
        self.rotateSpeed = rotateSpeed
        self.strafeSpeed = strafeSpeed

        action = None
        if self.standWalkRunReverse != None and not self.doingActivity:
            action = self.getMoveAction(forwardSpeed, rotateSpeed, strafeSpeed)
            anim, anim2, minSpeed, maxSpeed, rate, rate2 = self.standWalkRunReverse[action]
            if self.currentMoveAction != action or self.lastForcedTorsoAnim != self.forcedTorsoAnim or self.wasDoingActivity:
                self.playingAnim = anim
                self.lastForcedTorsoAnim = self.forcedTorsoAnim
                self.currentMoveAction = action
                self.resetMoveAnims(anim, anim2)

            speed = max(Vec3(forwardSpeed, strafeSpeed, rotateSpeed / 15.0).length(), minSpeed)
            self.currentSpeed = speed
            ratio = speed / maxSpeed
            ratioClamped = CIGlobals.clamp(ratio, 0, 1)
            self.setControlEffect(anim, 1 - ratioClamped)
            self.setControlEffect(anim2, ratioClamped)

            if ratio > 1:
                self.setPlayRate(rate * ratio, anim)
                self.setPlayRate(rate2 * ratio, anim2)
            else:
                self.setPlayRate(rate, anim)
                self.setPlayRate(rate2, anim2)

            self.wasDoingActivity = False
        elif self.doingActivity and not self.wasDoingActivity:
            self.wasDoingActivity = True
            self.resetMoveAnims()

        return action

    def getRightHandNode(self):
        return NodePath("rightHand")

    def getLeftHandNode(self):
        return NodePath("leftHand")

    def getHeadNode(self):
        return NodePath("head")
        
    def handleHitByToon(self, player, gagId, distance):
        pass
        
    def handleHitByEnemy(self, enemy, weaponId, distance):
        pass

    def getLowerBodySubpart(self):
        return ["legs"]

    def getUpperBodySubpart(self):
        return ["torso"]
        
    def taskName(self, name):
        return name + "-" + str(id(self))
        
    def uniqueName(self, name):
        return name + "-" + str(id(self))
        
    def setupHealthLabel(self):
        self.healthLabel = DirectLabel(text = "", text_fg = CIGlobals.PositiveTextColor,
                                    scale = 0.9, relief = None, text_decal = True,
                                    text_font = CIGlobals.getMickeyFont(), text_align = TextNode.ACenter)
        self.healthLabel.reparentTo(self)
        self.healthLabel.setBillboardPointEye()
        self.healthLabel.stash()
        self.healthLabel.setLightOff(1)
        self.healthLabel.hide(CIGlobals.ShadowCameraBitmask|CIGlobals.ReflectionCameraBitmask)

    def showAndMoveHealthLabel(self, zoffset = 0.5, stashWaitTime = 1.0):        
        self.unstashHpLabel()
        self.stopMovingHealthLabel()
        x = self.nametag3d.getX()
        y = self.nametag3d.getY()
        z = self.nametag3d.getZ()
        moveTrack = LerpPosInterval(self.healthLabel,
                                duration = 0.5,
                                pos = (x, y, z + zoffset),
                                startPos = (x, y, z - 2),
                                blendType = 'easeOut')
        self.healthLabelTrack = Sequence(moveTrack, Wait(stashWaitTime), Func(self.stashHpLabel))
        self.healthLabelTrack.start()

    def stopMovingHealthLabel(self):
        if self.healthLabelTrack != None:
            self.healthLabelTrack.pause()
            self.healthLabelTrack = None

    def stashHpLabel(self):
        self.healthLabel.stash()

    def unstashHpLabel(self):
        self.healthLabel.unstash()

    def doDamageFade(self):
        # Stop the current fade interval if it exists.
        if self.dmgFadeIval:
            self.dmgFadeIval.finish()
            self.dmgFadeIval = None

        geomNode = self.getGeomNode()
        # Do a fade effect when we get hit so we are more aware that we were damaged.
        self.dmgFadeIval = Sequence(
            Func(geomNode.setTransparency, 1),
            LerpColorScaleInterval(geomNode, 0.3, (1, 1, 1, 0.5), (1, 1, 1, 1), blendType = 'easeOut'),
            LerpColorScaleInterval(geomNode, 0.3, (1, 1, 1, 1), (1, 1, 1, 0.5), blendType = 'easeIn'),
            Func(geomNode.setTransparency, 0))
        self.dmgFadeIval.start()

    def announceHealth(self, level, hp, extraId):
        if not self.healthLabel:
            return
            
        if hp > 0:
            prefix = "+"
        else:
            prefix = ""

        if extraId != -1:
            prefix = self.EXTRAS[extraId] + "\n" + prefix

        if level == 1:
            self.healthLabel["text_fg"] = CIGlobals.PositiveTextColor
            self.healthLabel['text'] = prefix + str(hp)
        else:
            textFg = CIGlobals.NegativeTextColor
            if level == 2:
                textFg = CIGlobals.OrangeTextColor
            elif level == 3:
                textFg = CIGlobals.YellowTextColor
            self.healthLabel["text_fg"] = textFg
            self.healthLabel['text'] = prefix + str(hp)

        self.showAndMoveHealthLabel(1.0 if extraId != -1 else 0.5)
        
    def doRagdollMode(self, forceX = 0, forceY = 0, forceZ = 0, forcePosX = 0, forcePosY = 0, forcePosZ = 0):
        if self.ragdollMode:
            return
            
        forceVec = Vec3(forceX, forceY, forceZ)
        forcePos = Vec3(forcePosX, forcePosY, forcePosZ)

        self.stop()
        self.disableRay()
        self.disableShadowRay()
        if self.shadow:
            self.shadow.hide()
        self.disableBodyCollisions()
        if self.ragdoll:
            self.ragdoll.mode = self.ragdoll.RMRagdoll
            self.ragdoll.setEnabled(True)
            self.ragdoll.attachActor()
            self.ragdoll.applyForce(forceVec, forcePos)

        self.ragdollMode = True

    def getSplash(self):
        if not self.splashEffect:
            self.splashEffect = Splash(render)
            self.splashSound = base.loadSfxOnNode("phase_5.5/audio/sfx/AV_jump_in_water.ogg", self.splashEffect)

        return self.splashEffect

    def getWake(self):
        if not self.wake:
            self.wake = Wake(render, self)

        return self.wake

    def splash(self, x, y, z):
        spl = self.getSplash()
        spl.setPos(x, y, z)
        spl.setScale(2)
        spl.play()

        self.splashSound.play()

    def isLocalAvatar(self):
        if not hasattr(base, 'localAvatar'):
            return False
        return self == base.localAvatar

    def initializeRay(self, *args, **kwargs):
        pass

    def enableShadowRay(self):
        self.shadowFloorToggle = True

    def disableShadowRay(self):
        self.shadowFloorToggle = False

    def enableRay(self):
        self.avatarFloorToggle = True

    def disableRay(self):
        self.avatarFloorToggle = False

    def updateFloorHeight(self, z):
        if self.avatarFloorToggle:
            self.setZ(render, z)
        if self.shadowFloorToggle and self.shadow:
            self.shadow.setZ(render, z)

    def __keepOnFloorTask(self, task):
        # First, check if we are above a ground.
        # If so, go onto that.
        
        if self.isEmpty():
            return task.done

        # Create water ripples
        time = globalClock.getFrameTime()
        delta = time - self.lastWakeTime
        dt = globalClock.getDt()
        pos = self.getPos(render)
        posDelta = (pos - self.prevPos).lengthSquared()
        moveMag =  posDelta / dt
        if moveMag > 5.0 and delta > 0.1:
            if hasattr(base, 'waterReflectionMgr'):
                result = base.waterReflectionMgr.isTouchingAnyWater(pos, pos + (0, 0, self.getHeight()))
                if result[0]:
                    self.getWake().createRipple(result[1], rate = 1, startFrame = 4)
                    self.lastWakeTime = time
        self.prevPos = pos
        
        # Position is updated from server, don't need to move avatar on client
        return task.cont

        if (not self.avatarFloorToggle and
            not self.shadowFloorToggle or
            moveMag < self.AvatarMovedEpsilon):
                
            # Avoid unnecessary ray casting.
            return task.cont

        pFrom = self.getPos(render) + (0, 0, 0.1)

        z = None

        pTo = pFrom - (0, 0, 2000)
        aboveResult = base.physicsWorld.rayTestAll(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        aboveGround = False
        if aboveResult.hasHits():
            sortedHits = sorted(aboveResult.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).lengthSquared())
            for i in xrange(len(sortedHits)):
                hit = sortedHits[i]
                node = hit.getNode()
                np = NodePath(node)
                if self.isAncestorOf(np):
                    continue
                z = hit.getHitPos().getZ()
                break

        if z is not None:
            self.updateFloorHeight(z)
            return task.cont

        # We're not above a ground, check above?
        pTo = pFrom + (0, 0, 2000)
        belowResult = base.physicsWorld.rayTestAll(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        if belowResult.hasHits():
            sortedHits = sorted(belowResult.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).lengthSquared())
            for i in xrange(len(sortedHits)):
                hit = sortedHits[i]
                node = hit.getNode()
                np = NodePath(node)
                if self.isAncestorOf(np):
                    continue
                z = hit.getHitPos().getZ()
                break

        if z is not None:
            self.updateFloorHeight(z)

        return task.cont 

    def setupPhysics(self, radius = None, height = None):
        if not radius:
            radius = self.getWidth()
        if not height:
            height = self.getHeight()
        self.notify.debug("setupPhysics(r{0}, h{1}) hitboxData: {2}".format(radius, height, self.hitboxData))

        # When the height is passed into BulletCapsuleShape, it's
        # talking about the height only of the cylinder part.
        # But what we want is the height of the entire capsule.
        #height -= (radius * 2)
        # The middle of the capsule is the origin by default. Push the capsule shape up
        # so the very bottom of the capsule is the origin.
        zOfs = (height / 2.0) + radius

        capsule = BulletCapsuleShape(radius, height)
        bodyNode = BulletRigidBodyNode('avatarBodyNode')
        bodyNode.addShape(capsule, TransformState.makePos(Point3(0, 0, zOfs)))
        bodyNode.setKinematic(True)
        bodyNode.setPythonTag("avatar", self)

        BasePhysicsObject.setupPhysics(self, bodyNode, True)
        
        self.stopWaterCheck()

    def isDistributed(self):
        return hasattr(self, 'doId')

    def chatStompComplete(self, text):
        chatType = CHAT_LONG
        
        if "ooo" in text.lower():
            chatType = CHAT_HOWL
        elif "!" in text.lower():
            chatType = CHAT_EXCLAIM
        elif "?" in text.lower():
            chatType = CHAT_QUESTION
        elif len(text) <= 9:
            chatType = CHAT_SHORT
        elif 10 <= len(text) <= 19:
            chatType = CHAT_MEDIUM
        elif len(text) >= 20:
            chatType = CHAT_LONG
            
        snd = self.chatSoundTable.get(chatType, None)
        if isinstance(snd, list):
            snd = random.choice(snd)
        
        if snd:
            self.playSound(snd)

    def deleteNameTag(self):
        self.deleteNametag3d()

    def disableBodyCollisions(self):
        self.cleanupPhysics()
        
    def loadAvatar(self):
        self.setupHealthLabel()
        self.setBlend(frameBlend = base.config.GetBool("interpolate-frames", False))
        base.avatars.append(self)

    def disable(self):
        try:
            self.Avatar_disabled
        except:
            self.Avatar_disabled = 1
            if self.ragdoll:
                self.ragdoll.cleanup()
            self.ragdoll = None
            self.clearFadeTrack()
            if self in base.avatars:
                base.avatars.remove(self)
            if self.dmgFadeIval:
                self.dmgFadeIval.finish()
            self.stopActivity()
            self.dmgFadeIval = None
            self.stopMovingHealthLabel()
            if self.healthLabel:
                self.healthLabel.removeNode()
            self.healthLabel = None
            self.healthLabelTrack = None
            if self.floorTask:
                self.floorTask.remove()
            self.floorTask = None
            self.disableRay()
            self.deleteNametag3d()
            self.nametag.destroy()
            del self.nametag
            self.nametag3d.removeNode()
            self.nametag3d = None
            self.deleteShadow()
            self.removeLoopTask()
            self.mat = None
            self.tag = None
            self.chat = None
            self.avatarType = None
            self.charName = None
            self.nameTag = None
            self.cleanupPhysics()
            self.moveAnimProperties = None
            self.chatSoundTable = None

            self.lastWakeTime = None
            self.prevPos = None

            if self.wake:
                self.wake.destroy()
                self.wake = None

            if self.splashEffect:
                self.splashEffect.destroy()
                self.splashEffect = None

            self.splashSound = None
            
            self.avatarFloorToggle = None
            self.shadowFloorToggle = None

            Actor.cleanup(self)

    def delete(self):
        try:
            self.Avatar_deleted
        except:
            self.Avatar_deleted = 1
            self.removeLoopTask()
            AvatarShared.delete(self)
            Actor.delete(self)

    def getNameTag(self):
        return self.nametag3d
        
    def getNametagJoints(self):
        return []

    def setChat(self, chatString = None):
        print "setChat on", self.__class__.__name__
        self.nametag.setChatType(NametagGlobals.CHAT)
        shouldClear = self.autoClearChat
        if self.isThought(chatString):
            self.thoughtInProg = True
            chatString = self.removeThoughtPrefix(chatString)
            self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
            shouldClear = False
        else:
            self.thoughtInProg = False
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)
        self.nametag.setChatText(chatString, timeout = shouldClear)

    def setName(self, nameString = None, charName = None, createNow = 0):
        if not nameString:
            return
        AvatarShared.setName(self, nameString)
        if charName:
            self.charName = charName
        if createNow:
            self.setupNameTag()
            
    def getName(self):
        return AvatarShared.getName(self)

    def setupNameTag(self, tempName = None):
        if not self._name and not tempName:
            return
        if tempName:
            name = tempName
        else:
            name = self._name
        offset = 0.0
        z = 0.0
        if self.avatarType:
            if self.avatarType in [CIGlobals.Suit]:
                offset = 1.0
                z = self.getHeight()
            elif self.avatarType == CIGlobals.CChar:
                if self.charId in [DCG.MICKEY, DCG.PLUTO, DCG.MINNIE]:
                    offset = 1.0
                z = self.getHeight()
            elif self.avatarType == CIGlobals.Toon:
                offset = 0.5

        self.deleteNametag3d()
        self.initializeNametag3d()

        if self.avatarType == CIGlobals.Toon:
            self.nametag3d.setZ(self.getHeight() + offset)
        elif self.avatarType == CIGlobals.Suit or self.avatarType == CIGlobals.CChar:
            self.nametag3d.setZ(z + offset)

        if self.avatarType == CIGlobals.Suit:
            self.nametag.setFont(CIGlobals.getSuitFont())
            self.nametag.setChatFont(CIGlobals.getSuitFont())
            self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCSuit])
            self.nametag.setActive(0)
        else:
            self.nametag.setFont(CIGlobals.getToonFont())
            self.nametag.setChatFont(CIGlobals.getToonFont())
            self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCOtherPlayer])
        self.nametag.setText(name)
        if self.showNametagInMargins:
            self.nametag.manage(base.marginManager)
        self.nametag.updateAll()

    def setAvatarScale(self, scale):
        self.getGeomNode().setScale(scale)

    def getShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                return self.shadow
        return None

    def initShadow(self):
        if metadata.USE_REAL_SHADOWS:
            self.shadow = None
        else:
            self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
            self.shadow.setScale(CIGlobals.ShadowScales[self.avatarType])
            self.shadow.flattenMedium()
            self.shadow.setBillboardAxis(4)
            self.shadow.setColor(0, 0, 0, 0.5, 1)
            if self.avatarType == CIGlobals.Toon:
                self.shadow.reparentTo(self.getPart('legs').find('**/joint_shadow'))
            elif self.avatarType == CIGlobals.Suit:
                self.shadow.reparentTo(self)
            else:
                self.shadow.reparentTo(self)

        self.enableShadowRay()

    def deleteShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                self.shadow.removeNode()
                self.shadow = None

    def loopFromFrameToZero(self, animName, restart = 1, partName = None, fromFrame = None):
        # Loop an animation from a frame, restarting at 0.
        # This is only used in Make A Toon, but could be used in other things,
        # that are not distributed.
        dur = self.getDuration(animName, fromFrame = fromFrame)
        self.play(animName, partName = partName, fromFrame = fromFrame)
        taskName = self.uniqueName('loopTask')
        taskMgr.doMethodLater(
            dur, self.loopTask, taskName,
            extraArgs = [animName, restart, partName],
            appendTask = True
        )

    def removeLoopTask(self):
        taskMgr.remove(self.uniqueName('loopTask'))

    def removePart(self, partName, lodName = "lodRoot"):
        self.removeLoopTask()
        part = Actor.getPart(self, partName, lodName)
        
        if part:
            Actor.removePart(self, partName, lodName = lodName)

    def loopTask(self, animName, restart, partName, task):
        self.loop(animName, restart, partName)
        return task.done

    def getGhost(self):
        return 0

    def hideName(self):
        nametag3d = self.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.showChat()
        nametag3d.showThought()
        nametag3d.update()

    def showName(self):
        if self.__nameVisible and not self.getGhost():
            nametag3d = self.nametag.getNametag3d()
            nametag3d.showNametag()
            nametag3d.showChat()
            nametag3d.showThought()
            nametag3d.update()

    def hideNametag2d(self):
        nametag2d = self.nametag.getNametag2d()
        nametag2d.hideNametag()
        nametag2d.hideChat()
        nametag2d.update()

    def showNametag2d(self):
        nametag2d = self.nametag.getNametag2d()
        if not self.getGhost():
            nametag2d.showNametag()
            nametag2d.showChat()
        else:
            nametag2d.hideNametag()
            nametag2d.hideChat()
        nametag2d.update()

    def hideNametag3d(self):
        nametag3d = self.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.hideChat()
        nametag3d.hideThought()
        nametag3d.update()

    def showNametag3d(self):
        nametag3d = self.nametag.getNametag3d()
        if self.__nameVisible and (not self.getGhost()):
            nametag3d.showNametag()
            nametag3d.showChat()
            nametag3d.showThought()
        else:
            nametag3d.hideNametag()
            nametag3d.hideChat()
            nametag3d.hideThought()
        nametag3d.update()

    def setPickable(self, flag):
        self.nametag.setActive(flag)

    def clickedNametag(self):
        if self.nametag.getActive():
            messenger.send('clickedNametag', [self])

    def initializeNametag3d(self):
        self.deleteNametag3d()
        nametagNode = self.nametag.getNametag3d()
        self.nametagNodePath = self.nametag3d.attachNewNode(nametagNode)

        for cJoint in self.getNametagJoints():
            cJoint.clearNetTransforms()
            cJoint.addNetTransform(nametagNode)

    def deleteNametag3d(self):
        if self.nametagNodePath:
            self.nametagNodePath.removeNode()
            self.nametagNodePath = None

    def getNameVisible(self):
        return self.__nameVisible

    def setNameVisible(self, visible):
        self.__nameVisible = visible
        if visible:
            self.showName()
        else:
            self.hideName()
