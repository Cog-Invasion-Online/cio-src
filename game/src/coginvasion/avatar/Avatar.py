########################################
# Filename: Avatar.py
# Created by: blach (??Jul14)
########################################

from pandac.PandaModules import CollisionNode, CollisionTube, BitMask32, CollisionSphere, \
                                CollisionHandlerPusher, CollisionHandlerEvent, CollisionRay

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotify import DirectNotify
from direct.controls.ControlManager import CollisionHandlerRayStart

from src.coginvasion.globals import CIGlobals
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.npc import DisneyCharGlobals as DCG
from src.coginvasion.cog import SuitBank
from src.coginvasion.toon import ToonTalker
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.nametag.NametagGroup import NametagGroup
from src.coginvasion.base.ShadowPlacer import ShadowPlacer

import random

notify = DirectNotify().newCategory("Avatar")

class Avatar(ToonTalker.ToonTalker, Actor):

    def __init__(self, mat=0):
        try:
            self.Avatar_initialized
            return
        except:
            self.Avatar_initialized = 1

        ToonTalker.ToonTalker.__init__(self)
        Actor.__init__(self, None, None, None, flattenable=0, setFinal=1)#self.setColorOff()

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

        self.avatarType = None
        self.charName = None
        self._name = None
        self.tag = None
        self.height = 0
        return

    def chatStompComplete(self, text):
        pass

    def deleteNameTag(self):
        self.deleteNametag3d()

    def disable(self):
        try:
            self.Avatar_disabled
        except:
            self.Avatar_disabled = 1
            self.deleteNametag3d()
            self.nametag.destroy()
            del self.nametag
            self.nametag3d.removeNode()
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
            chatString = self.removeThoughtPrefix(chatString)
            self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
            shouldClear = False
        else:
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)
        self.nametag.setChatText(chatString, timeout = shouldClear)

    def setName(self, nameString = None, avatarType = None, charName = None, createNow = 0):
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
        if self.avatarType:
            if self.avatarType in [CIGlobals.Suit]:
                offset = 1.0
                z = self.getHeight()
            elif self.avatarType == CIGlobals.CChar:
                if self.charId in [DCG.MICKEY, DCG.PLUTO, DCG.MINNIE]:
                    offset = 1.0
                else:
                    offset = 0.0
                z = self.getHeight()
            elif self.avatarType == CIGlobals.Toon:
                offset = 0.5
            else:
                z = 0

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
        self.nametag.manage(base.marginManager)
        self.nametag.updateAll()

    def getAirborneHeight(self):
        height = self.getPos(self.shadowPlacer.shadowNodePath)
        return height.getZ() + 0.025

    def initializeBodyCollisions(self, collIdStr, height, radius):
        if hasattr(self, 'collNodePath'):
            if self.collNodePath:
                self.notify.info('Tried to initialize body collisions more than once!')
                return
        height -= 0.5
        cTube = CollisionTube(0, 0, height, 0, 0, 0, radius)
        cNode = CollisionNode('cNode')
        cNode.addSolid(cTube)
        cNode.setCollideMask(CIGlobals.WallBitmask)
        self.collNodePath = self.attachNewNode(cNode)
        self.collNodePath.setZ(0.5)
        #self.collNodePath.show()

    def collisionFix(self, task):
        self.collNodePath.forceRecomputeBounds()
        return task.cont

    def initializeRay(self, name, radius):
        if hasattr(self, 'rayNodePath'):
            if self.rayNodePath:
                self.notify.warning('Tried to initialize ray collisions more than once!')
                return

        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        cRayNode = CollisionNode(name + 'r')
        cRayNode.addSolid(cRay)
        self.cRayNodePath = self.attachNewNode(cRayNode)
        cRayBitMask = CIGlobals.FloorBitmask
        cRayNode.setFromCollideMask(cRayBitMask)
        cRayNode.setIntoCollideMask(BitMask32.allOff())
        base.lifter.addCollider(self.cRayNodePath, self)

        cSphere = CollisionSphere(0.0, 0.0, radius, 0.01)
        cSphereNode = CollisionNode(name + 'fc')
        cSphereNode.addSolid(cSphere)
        cSphereNodePath = self.attachNewNode(cSphereNode)
        #cSphereNodePath.show()

        cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
        cSphereNode.setIntoCollideMask(BitMask32.allOff())

        base.pusher.addCollider(cSphereNodePath, self)
        self.floorCollNodePath = cSphereNodePath
        base.cTrav.addCollider(self.floorCollNodePath, base.pusher)
        base.shadowTrav.addCollider(self.cRayNodePath, base.lifter)

    def disableRay(self):
        if hasattr(self, 'cRayNodePath'):
            base.shadowTrav.removeCollider(self.cRayNodePath)
            base.lifter.removeCollider(self.cRayNodePath)
            self.cRayNodePath.removeNode()
            del self.cRayNodePath
            base.cTrav.removeCollider(self.floorCollNodePath)
            base.pusher.removeCollider(self.floorCollNodePath)
            self.floorCollNodePath.removeNode()
            del self.floorCollNodePath
        self.rayNode = None

    def initializeLocalCollisions(self, senRadius, senZ, name):
        self.collNodePath.setCollideMask(BitMask32(0))
        self.collNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)

        pusher = CollisionHandlerPusher()
        pusher.setInPattern("%in")
        pusher.addCollider(self.collNodePath, self)

        base.cTrav.addCollider(self.collNodePath, pusher)

        collisionSphere = CollisionSphere(0, 0, 0, senRadius)
        sensorNode = CollisionNode(name + "s")
        sensorNode.addSolid(collisionSphere)
        self.sensorNodePath = self.attachNewNode(sensorNode)
        self.sensorNodePath.setZ(senZ)
        self.sensorNodePath.setCollideMask(BitMask32(0))
        self.sensorNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)

        event = CollisionHandlerEvent()
        event.setInPattern("%fn-into")
        event.setOutPattern("%fn-out")
        base.cTrav.addCollider(self.sensorNodePath, event)

    def stashBodyCollisions(self):
        if hasattr(self, 'collNodePath'):
            self.collNodePath.stash()

    def unstashBodyCollisions(self):
        if hasattr(self, 'collNodePath'):
            self.collNodePath.unstash()

    def stashRay(self):
        if hasattr(self, 'rayNodePath'):
            self.rayNodePath.stash()

    def unstashRay(self):
        if hasattr(self, 'rayNodePath'):
            self.rayNodePath.unstash()

    def disableBodyCollisions(self):
        self.notify.info('Disabling body collisions')
        if hasattr(self, 'collNodePath'):
            taskMgr.remove(self.uniqueName('collisionFixTask'))
            self.collNodePath.removeNode()
            del self.collNodePath
        return

    def deleteLocalCollisions(self):
        self.notify.info('Deleting local collisions!')
        base.cTrav.removeCollider(self.rayNodePath)
        base.cTrav.removeCollider(self.sensorNodePath)
        self.rayNodePath.remove_node()
        self.sensorNodePath.remove_node()

    def setAvatarScale(self, scale):
        self.getGeomNode().setScale(scale)

    def getShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                return self.shadow
        return None

    def initShadow(self):
        #self.shadow = arbitraryShadow(self.getGeomNode())

        self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
        self.shadow.setScale(CIGlobals.ShadowScales[self.avatarType])
        self.shadow.flattenMedium()
        self.shadow.setBillboardAxis(4)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        self.shadowPlacer = ShadowPlacer(self.shadow, self.mat)
        if self.avatarType == CIGlobals.Toon:
            self.shadow.reparentTo(self.getPart('legs').find('**/joint_shadow'))
        elif self.avatarType == CIGlobals.Suit:
            self.shadow.reparentTo(self)#.find('**/joint_shadow'))
        else:
            self.shadow.reparentTo(self)

    def deleteShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                self.shadowPlacer.delete_shadow_ray()
                self.shadowPlacer = None
                self.shadow.removeNode()
                self.shadow = None
                #self.shadow.clear()
                #self.shadow = None

    def disableShadowRay(self):
        self.shadowPlacer.delete_shadow_ray()

    def enableShadowRay(self):
        self.shadowPlacer.setup_shadow_ray(self.shadow, self.mat)

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
        Actor.removePart(self, partName, lodName = lodName)

    def loopTask(self, animName, restart, partName, task):
        self.loop(animName, restart, partName)
        return task.done

    def loop(self, animName, restart = 1, partName = None, fromFrame = None, toFrame = None):
        return Actor.loop(self, animName, restart, partName, fromFrame, toFrame)

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
        iconNodePath = self.nametag.getIcon()
        for cJoint in self.getNametagJoints():
            cJoint.clearNetTransforms()
            cJoint.addNetTransform(nametagNode)

    def deleteNametag3d(self):
        if self.nametagNodePath:
            self.nametagNodePath.removeNode()
            self.nametagNodePath = None

    def getNameVisible(self):
        return self.__nameVisible

    def setNameVisible(self, bool):
        self.__nameVisible = bool
        if bool:
            self.showName()
        if not bool:
            self.hideName()
