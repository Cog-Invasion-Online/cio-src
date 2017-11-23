"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedNPCToonAI.py
@author Brian Lach
@date July 31, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedToonAI import DistributedToonAI
from src.coginvasion.globals import CIGlobals

import random

class DistributedNPCToonAI(DistributedToonAI):
    notify = directNotify.newCategory("DistributedNPCToonAI")
    ACCOUNT = 0

    def __init__(self, air, npcId, originIndex):
        DistributedToonAI.__init__(self, air)
        self.originIndex = originIndex
        self.npcId = npcId
        npcData = CIGlobals.NPCToonDict.get(npcId)
        self.dnaStrand = npcData[2]
        self.setName(npcData[1])
        self.backpack = 0
        self.place = 0

        self.ammo = [[1, 2, 3, 4], [1, 2, 3, 4]]

        self.currentAvatar = None
        # The id of the quest where the current objective is to visit me.
        self.currentAvatarQuestOfMe = None

    def isHQOfficer(self):
        return CIGlobals.NPCToonDict[self.npcId][3] == CIGlobals.NPC_HQ

    def getNpcId(self):
        return self.npcId

    def getOriginIndex(self):
        return self.originIndex

    def delete(self):
        self.currentAvatar = None
        DistributedToonAI.delete(self)

    def startWatchingCurrentAvatar(self):
        base.taskMgr.add(self.__watchCurrAv, self.uniqueName('watchCurrentAv'))

    def __watchCurrAv(self, task):
        if not self.air.doId2do.get(self.currentAvatar):
            self.currentAvatar = None
            return task.done
        task.delayTime = 5
        return task.again

    def stopWatchingCurrentAvatar(self):
        base.taskMgr.remove(self.uniqueName('watchCurrentAv'))

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()

        if not self.hasValidReasonToEnter(avId):
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
        else:
            self.currentAvatar = avId
            av = self.air.doId2do.get(avId)
            self.currentAvatarQuestOfMe = av.questManager.getVisitQuest(self.npcId)
            self.startWatchingCurrentAvatar()
            self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
            self.sendUpdate('lookAtAvatar', [avId])
            self.doQuestStuffWithThisAvatar()

    def doQuestStuffWithThisAvatar(self):
        av = self.air.doId2do.get(self.currentAvatar)
        if av:
            if self.currentAvatarQuestOfMe != None:
                quest = self.currentAvatarQuestOfMe[1]
                questId = self.currentAvatarQuestOfMe[0]
                if av.questManager.isOnLastObjectiveOfQuest(questId):
                    if quest.isComplete():
                        av.questManager.completedQuest(questId)
                else:
                    av.questManager.incrementQuestObjective(questId)

    def hasValidReasonToEnter(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            chatArray = None
            needsToVisit = av.questManager.hasAnObjectiveToVisit(self.npcId, self.zoneId)
            lastVisited = av.questManager.wasLastObjectiveToVisit(self.npcId)
            if (len(av.questManager.quests.values()) == 0 or (not needsToVisit and not lastVisited)):
                # This avatar entered for no reason. They either have no quests or no objective to visit me.
                chatArray = CIGlobals.NPCEnter_Pointless_Dialogue
            elif lastVisited:
                # This avatar entered, but still has to complete the objective I gave him/her.
                chatArray = CIGlobals.NPCEnter_MFCO_Dialogue

            welcomeToShopDialogueIndex = 28

            if chatArray:
                chat = random.choice(chatArray)
                if '%s' in chat:
                    if (chatArray == CIGlobals.NPCEnter_Pointless_Dialogue and
                    CIGlobals.NPCEnter_Pointless_Dialogue.index(chat) == welcomeToShopDialogueIndex):
                        chat = chat % CIGlobals.zone2TitleDict[self.zoneId][0]
                    else:
                        chat = chat % av.getName()
                self.d_setChat(chat)
            return chatArray is None

    def requestExit(self, avId = None):
        if not avId:
            avId = self.air.getAvatarIdFromSender()

        if self.currentAvatar != None:
            if avId == self.currentAvatar:
                self.stopWatchingCurrentAvatar()
                self.currentAvatar = None
                self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
            else:
                self.notify.warning("Toon %d requested to exit, but they're not the current avatar." % avId)
