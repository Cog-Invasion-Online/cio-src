"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedNPCToon.py
@author Brian Lach
@date July 31, 2015

"""

from panda3d.core import CollisionNode, CollisionSphere
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.quests import Quests
from src.coginvasion.quests.Quests import objType
from src.coginvasion.quests.QuestGlobals import NPCDialogue, getPossessive
from src.coginvasion.nametag import NametagGlobals
from DistributedToon import DistributedToon
from src.coginvasion.quests.Objectives import VisitNPCObjective

import random

class DistributedNPCToon(DistributedToon):
    notify = directNotify.newCategory("DistributedNPCToon")

    def __init__(self, cr):
        DistributedToon.__init__(self, cr)
        self.collisionNodePath = None
        self.cameraTrack = None
        self.originIndex = None
        self.npcId = None
        self.currentChatIndex = 0
        self.chatArray = None
        self.interacting = False

    def setLoadout(self, foo):
        pass

    def lookAtAvatar(self, avId):
        av = self.cr.doId2do.get(avId)
        if av:
            self.headsUp(av)

    def setNpcId(self, id_):
        self.npcId = id_

    def getNpcId(self):
        return self.npcId

    def setOriginIndex(self, index):
        self.originIndex = index

    def getOriginIndex(self):
        return self.originIndex

    def __setupCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 4)
        sphere.setTangible(0)
        collisionNode = CollisionNode(self.uniqueName('NPCToonSphere'))
        collisionNode.addSolid(sphere)
        collisionNode.setCollideMask(CIGlobals.WallBitmask)
        self.collisionNodePath = self.attachNewNode(collisionNode)
        self.collisionNodePath.setY(1.5)

    def __removeCollisions(self):
        if self.collisionNodePath:
            self.collisionNodePath.removeNode()
            self.collisionNodePath = None

    def handleEnterCollision(self, entry):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestEnter', [])

    def doCameraNPCInteraction(self, pickingQuest = False):
        self.stopCameraTrack()

        localAvatar.headsUp(self)

        camera.wrtReparentTo(render)

        if not pickingQuest:
            # Left side
            self.cameraTrack = camera.posQuatInterval(1, (-5, 9, self.getHeight() - 0.5), (-150, -2, 0), other=self, blendType='easeOut')
            self.cameraTrack.start()
        else:
            # Right side
            self.cameraTrack = camera.posQuatInterval(1, (5, 9, self.getHeight() - 0.5), (155, -2, 0), other=self, blendType='easeOut')
            self.cameraTrack.start()

    def stopCameraTrack(self):
        if self.cameraTrack:
            self.cameraTrack.pause()
            self.cameraTrack = None

    def getNPCLocationSpeech(self, nextObjective = False):
        if nextObjective:
            objective = self.currentQuest.getNextObjectiveData()
        else:
            objective = self.currentQuest.getCurrObjectiveData()

        npcId = objective[Quests.args][0]
        npcZone = CIGlobals.NPCToonDict[npcId][0]

        name = CIGlobals.NPCToonNames[npcId]
        shopName = CIGlobals.zone2TitleDict[npcZone][0]
        chat = random.choice(NPCDialogue.FindNPC)
        if "[p]" in chat:
            chat = chat.replace("[p]", getPossessive(name))
        chat = chat % (name, shopName)
        chat += "\x07"
        locationSpeech = NPCDialogue.WhichIs
        if ZoneUtil.isOnCurrentPlayground(npcZone):
            # The NPC is in the same playground that the quest is being assigned on.
            locationSpeech = locationSpeech % "in this playground."
        elif ZoneUtil.isOnSameStreet(npcZone):
            # The NPC is on the same street that the quest is being assigned on.
            locationSpeech = locationSpeech % "on this street."
        elif ZoneUtil.isAtSamePlaygroundButDifferentBranch(npcZone):
            # The NPC is in the same playground but in a different branch zone.
            locationSpeech = (locationSpeech % "on %s." %
                ZoneUtil.getStreetName(npcZone))
        else:
            # NPC is in a completely different playground from where we are.
            if ZoneUtil.isStreet(ZoneUtil.getBranchZone(npcZone)):
                loc = "on %s" % ZoneUtil.getStreetName(npcZone)
            else:
                loc = "at the playground"
            locationSpeech = (locationSpeech % "%s in %s." %
                (loc, ZoneUtil.getHoodId(npcZone, 1)))
        chat += locationSpeech
        chat += "\x07"

        return chat

    def __getRewardChat(self):
        if len(self.currentQuest.rewards) < 2:
            reward = self.currentQuest.rewards[0]
    
            if reward.CustomDialogueBase is not None:
                rewardSpeech = reward.CustomDialogueBase
            else:
                rewardSpeech = random.choice(NPCDialogue.Reward)
    
            return rewardSpeech % reward.fillInDialogue()
        else:
            return random.choice(NPCDialogue.Rewards)

    def __getHQOfficerQuestCompletedChat(self):
        chat = ""

        chat += random.choice(NPCDialogue.QuestCompletedIntros) % base.localAvatar.getName()
        chat += "\x07"

        congrats = random.choice(NPCDialogue.QuestCompletedCongrats)
        if '%s' in congrats:
            congrats = congrats % base.localAvatar.getName()

        chat += congrats
        chat += "\x07"

        reward = self.__getRewardChat()

        chat += reward
        chat += "\x07"

        chat += random.choice(NPCDialogue.Goodbyes)

        return chat

    def __getQuestCompletedChat(self):
        chat = self.currentQuest.finishSpeech
        if chat.endswith("\x07"):
            chat += self.__getRewardChat()
        return chat

    def __getNPCObjectiveChat(self):
        chat = self.currentQuest.getNextObjectiveDialogue()
        nextObjType = self.currentQuest.getNextObjectiveData()[objType]
        if chat.endswith("\x07"):
            if nextObjType == VisitNPCObjective:
                chat += self.getNPCLocationSpeech(True)
                chat += random.choice(NPCDialogue.Goodbyes)
            else:
                chat += random.choice(NPCDialogue.QuestAssignGoodbyes)
        return chat

    def enterAccepted(self):
        self.autoClearChat = False
        self.interacting = True

        self.stopLookAround()
        base.localAvatar.stopSmartCamera()
        head = self.getPart("head")
        oldHpr = head.getHpr()
        head.lookAt(base.localAvatar.getPart("head"))
        newHpr = head.getHpr()
        head.setHpr(oldHpr)
        self.lookAtObject(newHpr[0], newHpr[1], newHpr[2])

        #if len(base.localAvatar.questManager.getQuests()) > 0:
        #    objective = base.localAvatar.questManager.getQuests()[0].getCurrentObjective()
        #    self.currentChatIndex = 0
        #    self.doNPCChat(objective.getAssignDialog())

        questData = base.localAvatar.questManager.getVisitQuest(self.npcId)
        if questData:
            quest = questData[1]
            self.currentQuest = quest
            self.currentQuestObjective = quest.currentObjectiveIndex
            self.currentQuestId = questData[0]
            self.currentChatIndex = 0

            self.doCameraNPCInteraction()

            if CIGlobals.NPCToonDict[self.npcId][3] == CIGlobals.NPC_HQ:
                if not quest.isComplete():
                    self.b_setChat(self.__getNPCObjectiveChat())
                else:
                    self.b_setChat(self.__getHQOfficerQuestCompletedChat())
            if CIGlobals.NPCToonDict[self.npcId][3] == CIGlobals.NPC_REGULAR:
                if quest.isComplete():
                    self.b_setChat(self.__getQuestCompletedChat())
                else:
                    self.b_setChat(self.__getNPCObjectiveChat())

    def __handlePageChatClicked(self):
        if self.nametag.getChatPageIndex() >= self.nametag.getNumChatPages() - 1:
            self.d_requestExit()
            return

        nextIndex = self.nametag.getChatPageIndex() + 1

        if nextIndex >= self.nametag.getNumChatPages() - 1:
            self.nametag.setChatButton(NametagGlobals.quitButton)
            self.nametag.updateAll()

        self.b_setChatPageIndex(nextIndex)

    def _stopInteraction(self):
        self.startLookAround()

        self.nametag.setActive(0)
        self.nametag.setChatButton(NametagGlobals.noButton)
        self.nametag.updateAll()

        self.autoClearChat = True
        self.nametag.clearChatText()

        self.ignore(self.uniqueName('chatClicked'))

        self.interacting = False

    def setChatPageIndex(self, index):
        if self.nametag.getNumChatPages() > index:
            self.nametag.setChatPageIndex(index)

    def b_setChatPageIndex(self, index):
        self.sendUpdate('setChatPageIndex', [index])
        self.setChatPageIndex(index)

    def b_setChat(self, chat):
        if self.interacting:
            self.nametag.setActive(1)
            length = len(chat.split("\x07"))
            btn = NametagGlobals.pageButton
            if length == 1:
                btn = NametagGlobals.quitButton
            self.nametag.setChatButton(btn)
            self.nametag.updateAll()

            self.nametag.getNametag3d().setClickEvent(self.uniqueName('chatClicked'))
            self.nametag.getNametag2d().setClickEvent(self.uniqueName('chatClicked'))

            self.accept(self.uniqueName('chatClicked'), self.__handlePageChatClicked)

        DistributedToon.b_setChat(self, chat)

    def d_requestExit(self):
        self._stopInteraction()
        self.sendUpdate('requestExit', [])

    def rejectEnter(self):
        self.exitAccepted()

    def exitAccepted(self):
        self.stopCameraTrack()
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptCollisions()

    def acceptCollisions(self):
        self.acceptOnce('enter' + self.uniqueName('NPCToonSphere'), self.handleEnterCollision)

    def ignoreCollisions(self):
        self.ignore('enter' + self.uniqueName('NPCToonSphere'))

    def __npcOriginPoll(self, task):
        if task.time > 4.0:
            self.notify.warning("Giving up waiting for npc origin after %d seconds. Will parent to render." % task.time)
            self.reparentTo(render)
            return task.done
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            return task.done
        return task.cont

    def startNPCOriginPoll(self):
        base.taskMgr.add(self.__npcOriginPoll, self.uniqueName('NPCOriginPoll'))

    def stopNPCOriginPoll(self):
        base.taskMgr.remove(self.uniqueName('NPCOriginPoll'))

    def setupNameTag(self, tempName = None):
        DistributedToon.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        self.startLookAround()
        self.__setupCollisions()
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
        else:
            self.startNPCOriginPoll()
        self.acceptCollisions()

    def disable(self):
        self.ignore('mouse1-up')
        self.stopLookAround()
        self.stopNPCOriginPoll()
        self.chatArray = None
        self.originIndex = None
        self.npcId = None
        self.stopCameraTrack()
        self.ignoreCollisions()
        self.__removeCollisions()
        DistributedToon.disable(self)
