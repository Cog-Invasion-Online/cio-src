# Filename: DistributedNPCToon.py
# Created by:  blach (31Jul15)

from pandac.PandaModules import CollisionNode, CollisionSphere
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval, Sequence, Wait, Func

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil
from lib.coginvasion.quests import Quests
from lib.coginvasion.quests.QuestGlobals import NPCDialogue
from lib.coginvasion.quests import Rewards
from lib.coginvasion.nametag import NametagGlobals
from DistributedToon import DistributedToon

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

    def setNpcId(self, id):
        self.npcId = id

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
        base.localAvatar.stopSmartCamera()
        self.sendUpdate('requestEnter', [])

    def doCameraNPCInteraction(self):
        currCamPos = camera.getPos()
        currCamHpr = camera.getHpr()
        camera.setX(camera.getX() + 5)
        camera.setY(camera.getY() + 5)
        camera.headsUp(self)
        newCamPos = camera.getPos()
        newCamHpr = camera.getHpr()
        camera.setPos(currCamPos)
        camera.setHpr(currCamHpr)

        self.cameraTrack = Parallel(
            LerpPosInterval(camera, duration = 1.0, pos = newCamPos, startPos = currCamPos, blendType = 'easeOut'),
            LerpQuatInterval(camera, duration = 1.0, quat = newCamHpr, startHpr = currCamHpr, blendType = 'easeOut')
        )
        self.cameraTrack.start()

    def stopCameraTrack(self):
        if self.cameraTrack:
            self.cameraTrack.finish()
            self.cameraTrack = None

    def getNPCLocationSpeech(self):
        objective = self.currentQuest.currentObjective

        name = CIGlobals.NPCToonNames[objective.npcId]
        shopName = CIGlobals.zone2TitleDict[objective.npcZone][0]
        chat = random.choice(NPCDialogue.FindNPC) % (name, shopName)
        chat += "\x07"
        locationSpeech = NPCDialogue.WhichIs
        if ZoneUtil.isOnCurrentPlayground(objective.npcZone):
            # The NPC is in the same playground that the quest is being assigned on.
            locationSpeech = locationSpeech % "in this playground."
        elif ZoneUtil.isOnSameStreet(objective.npcZone):
            # The NPC is on the same street that the quest is being assigned on.
            locationSpeech = locationSpeech % "on this street."
        elif ZoneUtil.isAtSamePlaygroundButDifferentBranch(objective.npcZone):
            # The NPC is in the same playground but in a different branch zone.
            locationSpeech = (locationSpeech % "on %s in this playground." %
                ZoneUtil.getStreetName(objective.npcZone))
        else:
            # NPC is in a completely different playground from where we are.
            locationSpeech = (locationSpeech % "on %s in %s." %
                (ZoneUtil.getStreetName(objective.npcZone), ZoneUtil.getHoodId(objective.npcZone, 1)))
        chat += locationSpeech
        chat += "\x07"

        return chat

    def __getRewardChat(self):
        reward = self.currentQuest.reward

        if reward.CustomDialogueBase is not None:
            rewardSpeech = reward.CustomDialogueBase
        else:
            rewardSpeech = random.choice(NPCDialogue.Reward)

        return rewardSpeech % reward.fillInDialogue()

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
        objType = self.currentQuest.getNextObjectiveType()
        if chat.endswith("\x07"):
            if objType == ObjectiveTypes.VisitNPC:
                chat += self.getNPCLocationSpeech()
            chat += random.choice(NPCDialogue.QuestAssignGoodbyes)
        return chat

    def enterAccepted(self):
        self.autoClearChat = False
        self.interacting = True

        self.stopLookAround()
        head = self.getPart("head")
        oldHpr = head.getHpr()
        head.lookAt(base.localAvatar.getPart("head"))
        newHpr = head.getHpr()
        head.setHpr(oldHpr)
        self.lookAtObject(newHpr[0], newHpr[1], newHpr[2])

        self.doCameraNPCInteraction()
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
            self.nametag.setActive(0)
            self.nametag.setChatButton(NametagGlobals.noButton)
            self.nametag.updateAll()

            self.autoClearChat = True
            self.nametag.clearChatText()

            self.ignore(self.uniqueName('chatClicked'))

            self.interacting = False

            self.d_requestExit()

            return

        nextIndex = self.nametag.getChatPageIndex() + 1

        if nextIndex >= self.nametag.getNumChatPages() - 1:
            self.nametag.setChatButton(NametagGlobals.quitButton)
            self.nametag.updateAll()

        self.nametag.setChatPageIndex(nextIndex)

    def b_setChat(self, chat):
        if self.interacting:
            self.nametag.setActive(1)
            length = len(chat.split("\x07"))
            btn = NametagGlobals.pageButton
            if length == 1:
                NametagGlobals.quitButton
            self.nametag.setChatButton(btn)
            self.nametag.updateAll()

            self.nametag.getNametag3d().setClickEvent(self.uniqueName('chatClicked'))
            self.nametag.getNametag2d().setClickEvent(self.uniqueName('chatClicked'))

            self.accept(self.uniqueName('chatClicked'), self.__handlePageChatClicked)

        DistributedToon.b_setChat(self, chat)

    def d_requestExit(self):
        self.sendUpdate('requestExit', [])

    def rejectEnter(self):
        self.exitAccepted()

    def exitAccepted(self):
        self.startLookAround()
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
