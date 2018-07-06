"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Avatar.py
@author Brian Lach
@date July ??, 2014

"""

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import BitMask32, ConfigVariableBool, TransformState, Point3, NodePath
from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape

from src.coginvasion.globals import CIGlobals
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.npc import DisneyCharGlobals as DCG
from src.coginvasion.toon import ToonTalker
from src.coginvasion.nametag.NametagGroup import NametagGroup
from src.coginvasion.phys.PhysicsNodePath import PhysicsNodePath
from src.coginvasion.base.Wake import Wake
from src.coginvasion.base.Splash import Splash

notify = directNotify.newCategory("Avatar")

class Avatar(ToonTalker.ToonTalker, Actor, PhysicsNodePath):
    RealShadows = ConfigVariableBool('want-real-shadows', False)

    def __init__(self, mat=0):
        try:
            self.Avatar_initialized
            return
        except:
            self.Avatar_initialized = 1

        ToonTalker.ToonTalker.__init__(self)
        PhysicsNodePath.__init__(self)
        Actor.__init__(self, None, None, None, flattenable=0, setFinal=1)

        self.getGeomNode().showThrough(CIGlobals.ShadowCameraBitmask)

        self.mat = mat
        self._name = ''
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

        self.enableBlend()

        self.showNametagInMargins = True
        self.avatarType = None
        self.charName = None
        self._name = None
        self.tag = None
        self.height = 0

        self.splashEffect = None
        self.splashSound = None

        self.prevPos = Point3(0)
        self.wake = None
        self.lastWakeTime = 0.0

        self.thoughtInProg = False

        self.shadowFloorToggle = False
        self.avatarFloorToggle = False
        self.floorTask = taskMgr.add(self.__keepOnFloorTask, "Avatar.keepOnFloor", sort = 30)

        return

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
        moveMag = (pos - self.prevPos).length() / dt
        if moveMag > 5.0 and delta > 0.1:
            if hasattr(base, 'waterReflectionMgr'):
                result = base.waterReflectionMgr.isTouchingAnyWater(pos, pos + (0, 0, self.height))
                if result[0]:
                    self.getWake().createRipple(result[1], rate = 1, startFrame = 4)
                    self.lastWakeTime = time
        self.prevPos = pos

        if not self.avatarFloorToggle and not self.shadowFloorToggle:
            # Avoid unnecessary ray casting.
            return task.cont

        pFrom = self.getPos(render)

        z = None

        pTo = pFrom - (0, 0, 2000)
        aboveResult = base.physicsWorld.rayTestAll(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        aboveGround = False
        if aboveResult.hasHits():
            sortedHits = sorted(aboveResult.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).length())
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
            sortedHits = sorted(belowResult.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).length())
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

    def setupPhysics(self, radius = 1, height = 2):
        # When the height is passed into BulletCapsuleShape, it's
        # talking about the height only of the cylinder part.
        # But what we want is the height of the entire capsule.
        height -= (radius * 2)
        # The middle of the capsule is the origin by default. Push the capsule shape up
        # so the very bottom of the capsule is the origin.
        zOfs = (height / 2.0) + radius

        capsule = BulletCapsuleShape(radius, height)
        bodyNode = BulletRigidBodyNode('avatarBodyNode')
        bodyNode.addShape(capsule, TransformState.makePos(Point3(0, 0, zOfs)))
        bodyNode.setKinematic(True)

        PhysicsNodePath.setupPhysics(self, bodyNode, True)

    def isDistributed(self):
        return hasattr(self, 'doId')

    def chatStompComplete(self, text):
        pass

    def deleteNameTag(self):
        self.deleteNametag3d()

    def disableBodyCollisions(self):
        self.cleanupPhysics()

    def disable(self):
        try:
            self.Avatar_disabled
        except:
            self.Avatar_disabled = 1
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
            self.height = None
            self.avatarType = None
            self.charName = None
            self.nameTag = None
            self._name = None
            self.cleanupPhysics()

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
            Actor.delete(self)

    def getNameTag(self):
        return self.nametag3d

    def setHeight(self, height):
        self.height = height

    def getHeight(self):
        return self.height

    def setChat(self, chatString = None):
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
        self._name = nameString
        if charName:
            self.charName = charName
        if createNow:
            self.setupNameTag()

    def getName(self):
        return self._name

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
        if game.userealshadows:
            self.shadow = self.attachNewNode("fakeShadow")
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
        if hasattr(self, 'cr'):
            taskName = self.cr.uniqueName('loopTask')
        else:
            taskName = 'loopTask'
        taskMgr.doMethodLater(
            dur, self.loopTask, taskName,
            extraArgs = [animName, restart, partName],
            appendTask = True
        )

    def removeLoopTask(self):
        if hasattr(self, 'cr'):
            taskMgr.remove(self.cr.uniqueName('loopTask'))
        else:
            taskMgr.remove('loopTask')

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
