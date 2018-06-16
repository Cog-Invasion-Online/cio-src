"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDisneyChar.py
@author Brian Lach
@date June 21, 2016

"""

from panda3d.core import ModelNode, CharacterJointEffect, Texture

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from src.coginvasion.avatar.Avatar import Avatar
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.npc.NPCWalker import NPCWalkInterval, NPCLookInterval
from src.coginvasion.globals import CIGlobals

from DisneyCharGlobals import *

import random

class DistributedDisneyChar(DistributedAvatar, DistributedSmoothNode):
    notify = directNotify.newCategory('DistributedDisneyChar')

    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)

        self.fsm = ClassicFSM('DDisneyChar',
                              [State('off', self.enterOff, self.exitOff),
                               State('walking', self.enterWalking, self.exitWalking),
                               State('neutral', self.enterNeutral, self.exitNeutral)],
                              'off', 'off')
        self.fsm.enterInitialState()
        self.neutralFSM = ClassicFSM('DDisneyChar-neutral',
                                     [State('off', self.enterOff, self.exitOff),
                                      State('turn2target', self.enterTurn2Target, self.exitTurn2Target),
                                      State('talk2target', self.enterTalk2Target, self.exitTalk2Target)],
                                     'off', 'off')
        self.neutralFSM.enterInitialState()

        self.charId = 0
        self.geoEyes = 0
        self.avatarType = CIGlobals.CChar
        self.headNode = None
        self.isInRange = False
        self.currentPointLetter = "a"
        self.walkIval = None
        self.currentChat = ""
        self.talkEnabled = True
        self.speechSound = None

        self.chatsSinceLastNoise = 0
        self.chatsWithoutNoise = 5

        self.eyes = None
        self.lpupil = None
        self.rpupil = None
        self.eyesOpen = None
        self.eyesClosed = None
        
        self.santaHat = None

    def setCharId(self, charId):
        self.charId = charId

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def doNeutral(self, pointLetter):
        self.fsm.request('neutral', [pointLetter])

    def doWalking(self, pointLetter, startPointLetter, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.fsm.request('walking', [pointLetter, startPointLetter, ts])

    def enterWalking(self, pointLetter, startPointLetter, ts):

        if self.walkIval:
            self.walkIval.finish()
            self.walkIval = None

        self.nametag.clearChatText()

        self.loop('walk')

        point = WALK_POINTS[self.charId][pointLetter][0]
        lastPoint = WALK_POINTS[self.charId][startPointLetter][0]

        seq = Sequence(name = self.uniqueName('DCharWalkIval'))
        if self.charId == PLUTO:
            seq.append(ActorInterval(self, 'stand'))
        elif self.charId == SLEEP_DONALD:
            seq.append(ActorInterval(self, 'neutral2walk'))
        seq.append(Func(self.loop, 'walk'))
        ival = NPCWalkInterval(self, point,
            startPos = lastPoint,
            fluid = 1, bakeInStart = 0)
        seq.append(ival)
        seq.append(Func(self.loop, 'neutral'))
        seq.start(ts)

        self.enableRay()

        self.currentPointLetter = pointLetter

        self.walkIval = ival

    def exitWalking(self):
        self.disableRay()
        if self.walkIval:
            self.walkIval.finish()
            self.walkIval = None

    def enterNeutral(self, pointLetter):
        point = WALK_POINTS[self.charId][pointLetter][0]
        self.setPos(point)
        if self.charId == PLUTO:
            seq = Sequence(ActorInterval(self, 'sit'), Func(self.loop, 'neutral'))
            seq.start()
        elif self.charId == SLEEP_DONALD:
            seq = Sequence(ActorInterval(self, 'walk2neutral'), Func(self.loop, 'neutral'))
            seq.start()
        else:
            self.loop('neutral')

    def talk2Toon(self, chatType, chatIndex, avId):
        toon = self.cr.doId2do.get(avId)
        if not toon:
            return

        if chatType in [SHARED_GREETINGS, SHARED_COMMENTS, SHARED_GOODBYES]:
            self.currentChat = CHATTER[chatType][chatIndex]
        elif chatType in [CHAR_GREETINGS, CHAR_COMMENTS, CHAR_GOODBYES]:
            self.currentChat = CHATTER[chatType][self.charId][chatIndex]

        if '%s' in self.currentChat:
            self.currentChat = self.currentChat % toon.getName()

        self.neutralFSM.request('turn2target', [toon])

    def enterTurn2Target(self, toon):
        self.turnIval = NPCLookInterval(self, toon, fluid = 1, name = self.uniqueName('turnIval'), durationFactor = 0.005)
        if self.turnIval.distance > 30:
            self.loop('walk')
        elif self.turnIval.distance < 10.0:
            self.headsUp(toon)
            self.neutralFSM.request('talk2target')
            return
        self.turnIval.setDoneEvent(self.turnIval.getName())
        self.acceptOnce(self.turnIval.getDoneEvent(), self.__handleTurningDone)
        self.turnIval.start()

    def __handleTurningDone(self):
        self.neutralFSM.request('talk2target')

    def exitTurn2Target(self):
        self.ignore(self.turnIval.getDoneEvent())
        self.turnIval.finish()
        del self.turnIval

    def enterTalk2Target(self):
        self.setChat(self.currentChat)
        if self.getCurrentAnim() != 'neutral':
            if self.charId == SLEEP_DONALD:
                seq = Sequence(ActorInterval(self, 'walk2neutral'), Func(self.loop, 'neutral'))
                seq.start()
            else:
                self.loop('neutral')

    def exitTalk2Target(self):
        pass

    def exitNeutral(self):
        self.neutralFSM.request('off')
        self.stop()

    def chatStompComplete(self, chatString):
        if CIGlobals.getSettingsMgr().getSetting("chs") is False:
            # No chat sounds!
            return

        if self.chatsSinceLastNoise >= self.chatsWithoutNoise or self.chatsSinceLastNoise == 0:
            base.playSfx(self.speechSound)
            self.chatsSinceLastNoise = 0
            self.chatsWithoutNoise = random.randint(1, 5)
        self.chatsSinceLastNoise += 1

    def setChat(self, chat):
        if self.charId == SLEEP_DONALD:
            chat = "." + chat
        DistributedAvatar.setChat(self, chat)

    def loadChar(self):
        

        data = CHAR_DATA[self.charId]
        self.loadModel(data[0], 'modelRoot')
        self.loadAnims(data[1], 'modelRoot')
        if self.charId == SLEEP_DONALD:
            self.setPlayRate(0.5, 'neutral')
        self.setHeight(data[2])
        self.setupPhysics(1.0, data[2])
        self.setName(data[3])
        self.talkEnabled = data[4]
        if self.talkEnabled:
            self.speechSound = data[5]
            if self.speechSound is not None:
                base.audio3d.attachSoundToObject(self.speechSound, self)
        self.setupNameTag()

        self.headNode = self.attachNewNode('headNode')
        self.headNode.setZ(self.getHeight() - 0.5)
        #smiley = loader.loadModel('models/smiley.egg.pz')
        #smiley.reparentTo(self.headNode)

        self.ears = []
        
        if self.cr.isChristmas():
            self.santaHat = loader.loadModel("phase_4/models/accessories/tt_m_chr_avt_acc_hat_elfhat.bam")
            tex = loader.loadTexture("phase_4/maps/tt_t_chr_avt_acc_hat_elfhat8.jpg")
            self.santaHat.setTexture(tex, 1)

        if self.charId in [MINNIE, MICKEY]:
            for bundle in self.getPartBundleDict().values():
                bundle = bundle['modelRoot'].getBundle()
                earNull = bundle.findChild('sphere3')
                if not earNull:
                    earNull = bundle.findChild('*sphere3')
                earNull.clearNetTransforms()

            for bundle in self.getPartBundleDict().values():
                charNodepath = bundle['modelRoot'].partBundleNP
                bundle = bundle['modelRoot'].getBundle()
                earNull = bundle.findChild('sphere3')
                if not earNull:
                    earNull = bundle.findChild('*sphere3')
                ears = charNodepath.find('**/sphere3')
                if ears.isEmpty():
                    ears = charNodepath.find('**/*sphere3')
                ears.clearEffect(CharacterJointEffect.getClassType())
                earRoot = charNodepath.attachNewNode('earRoot')
                earPitch = earRoot.attachNewNode('earPitch')
                earPitch.setP(40.0)
                ears.reparentTo(earPitch)
                earNull.addNetTransform(earRoot.node())
                ears.clearMat()
                ears.node().setPreserveTransform(ModelNode.PTNone)
                ears.setP(-40.0)
                ears.flattenMedium()
                self.ears.append(ears)
                ears.setBillboardAxis()
                if self.cr.isChristmas():
                    ears.hide()
                    self.santaHat.reparentTo(earRoot)
                    self.santaHat.setScale(self, 1.5)
                    self.santaHat.setPos(0, -0.15 * 1000, 0.35 * 1000)
                    self.santaHat.setHpr(0, 10, 0)
                    if self.charId == MINNIE:
                        self.santaHat.setZ(0.25 * 1000)

            self.eyesOpen = loader.loadTexture('phase_3/maps/eyes1.jpg', 'phase_3/maps/eyes1_a.rgb')
            self.eyesClosed = loader.loadTexture('phase_3/maps/mickey_eyes_closed.jpg', 'phase_3/maps/mickey_eyes_closed_a.rgb')
            self.eyes = self.find('**/eyes')
            self.eyes.setBin('transparent', 0)
            self.lpupil = self.find('**/joint_pupilL')
            self.rpupil = self.find('**/joint_pupilR')
            self.drawInFront('joint_pupil?', 'eyes*', -3)
        elif self.charId == PLUTO:
            self.eyesOpen = loader.loadTexture('phase_6/maps/plutoEyesOpen.jpg', 'phase_6/maps/plutoEyesOpen_a.rgb')
            self.eyesClosed = loader.loadTexture('phase_6/maps/plutoEyesClosed.jpg', 'phase_6/maps/plutoEyesClosed_a.rgb')
            self.eyes = self.find('**/eyes')
            self.lpupil = self.find('**/joint_pupilL')
            self.rpupil = self.find('**/joint_pupilR')
            self.drawInFront('joint_pupil?', 'eyes*', -3)
        elif self.charId == DAISY:
            self.geoEyes = 1
            self.eyeOpenList = []
            self.eyeCloseList = []
            self.eyeCloseList.append(self.find('**/eyesclose'))
            self.eyeOpenList.append(self.find('**/eyesclose'))
            self.eyeOpenList.append(self.find('**/eyespupil'))
            self.eyeOpenList.append(self.find('**/eyesopen'))
            for part in self.eyeOpenList:
                part.show()

            for part in self.eyeCloseList:
                part.hide()
        elif self.charId == SAILOR_DONALD:
            self.eyes = self.find('**/eyes')
            self.lpupil = self.find('**/joint_pupilL')
            self.rpupil = self.find('**/joint_pupilR')
            self.drawInFront('joint_pupil?', 'eyes*', -3)

        if self.lpupil is not None:
            self.lpupil.adjustAllPriorities(1)
            self.rpupil.adjustAllPriorities(1)
        if self.eyesOpen:
            self.eyesOpen.setMinfilter(Texture.FTLinear)
            self.eyesOpen.setMagfilter(Texture.FTLinear)
        if self.eyesClosed:
            self.eyesClosed.setMinfilter(Texture.FTLinear)
            self.eyesClosed.setMagfilter(Texture.FTLinear)

        if self.charId == MICKEY:
            pupilParent = self.rpupil.getParent()
            pupilOffsetNode = pupilParent.attachNewNode('pupilOffsetNode')
            pupilOffsetNode.setPos(0, 0.025, 0)
            self.rpupil.reparentTo(pupilOffsetNode)

        self.initShadow()
        self.shadow.setScale(0.6)
        
        self.disableShadowRay()
        
        bodyMat = CIGlobals.getCharacterMaterial(shininess = 20.0, specular = (0.2, 0.2, 0.2, 1.0))
        self.setMaterial(bodyMat)

        self.__blinkName = 'blink-' + data[3]

    def setupNameTag(self):
        DistributedAvatar.setupNameTag(self)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def __monitorRange(self, task):
        if not self.isEmpty() and base.localAvatarReachable() and not base.localAvatar.isEmpty():
            if base.localAvatar.getDistance(self) <= MAX_RANGE:
                if self.isInRange is False:
                    self.sendUpdate('avatarEnter')
                    self.isInRange = True
            else:
                if self.isInRange is True:
                    self.sendUpdate('avatarExit')
                    self.isInRange = False
    
            return task.cont
        return task.done

    def __blinkOpenEyes(self, task):
        self.openEyes()
        r = random.random()
        if r < 0.1:
            t = 0.2
        else:
            t = r * 4.0 + 1.0
        taskMgr.doMethodLater(t, self.__blinkCloseEyes, self.__blinkName)
        return task.done

    def __blinkCloseEyes(self, task):
        self.closeEyes()
        taskMgr.doMethodLater(0.125, self.__blinkOpenEyes, self.__blinkName)
        return task.done

    def openEyes(self):
        if self.geoEyes:
            for part in self.eyeOpenList:
                part.show()

            for part in self.eyeCloseList:
                part.hide()

        else:
            if self.eyes:
                self.eyes.setTexture(self.eyesOpen, 1)
            self.lpupil.show()
            self.rpupil.show()

    def closeEyes(self):
        if self.geoEyes:
            for part in self.eyeOpenList:
                part.hide()

            for part in self.eyeCloseList:
                part.show()

        else:
            if self.eyes:
                self.eyes.setTexture(self.eyesClosed, 1)
            self.lpupil.hide()
            self.rpupil.hide()

    def startBlink(self):
        if self.eyesOpen or self.geoEyes:
            taskMgr.remove(self.__blinkName)
            taskMgr.doMethodLater(random.random() * 4 + 1, self.__blinkCloseEyes, self.__blinkName)

    def stopBlink(self):
        if self.eyesOpen or self.geoEyes:
            taskMgr.remove(self.__blinkName)
            self.openEyes()

    def getNametagJoints(self):
        return []

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        DistributedSmoothNode.announceGenerate(self)
        self.loadChar()
        self.startBlink()
        base.taskMgr.add(self.__monitorRange, self.uniqueName('monitorRange'))
        self.sendUpdate('requestStateData')
        if self.charId == SAILOR_DONALD:
            self.disableRay()
            self.cleanupPhysics()
            boat = self.cr.playGame.hood.loader.geom.find('**/*donalds_boat*')
            boat.find('**/wheel').hide()
            self.setPos(0, -1, 3.95)
            self.reparentTo(boat)
            self.loop('wheel')
        else:
            self.reparentTo(render)

    def disable(self):
        base.taskMgr.remove(self.uniqueName('monitorRange'))
        self.stopBlink()
        self.fsm.requestFinalState()
        self.fsm = None
        self.neutralFSM.requestFinalState()
        self.neutralFSM = None
        self.charId = None
        self.geoEyes = None
        self.avatarType = None
        self.isInRange = None
        self.currentPointLetter = None
        self.walkIval = None
        self.currentChat = None
        self.talkEnabled = None
        self.speechSound = None
        self.chatsSinceLastNoise = None
        
        if self.santaHat:
            self.santaHat.removeNode()
            self.santaHat = None

        if self.headNode:
            self.headNode.removeNode()
            self.headNode = None

        self.eyes = None
        self.lpupil = None
        self.rpupil = None
        self.eyesOpen = None
        self.eyesClosed = None
        DistributedAvatar.disable(self)
        Avatar.disable(self)
        DistributedSmoothNode.disable(self)
