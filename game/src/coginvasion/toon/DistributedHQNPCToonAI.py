"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedHQNPCToonAI.py
@author Brian Lach
@date August 2, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import DistributedNPCToonAI
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.quest.QuestGlobals import NPCDialogue

import random

class DistributedHQNPCToonAI(DistributedNPCToonAI.DistributedNPCToonAI):
    notify = directNotify.newCategory("DistributedHQNPCToonAI")

    def doQuestStuffWithThisAvatar(self):
        DistributedNPCToonAI.DistributedNPCToonAI.doQuestStuffWithThisAvatar(self)
        av = self.air.doId2do.get(self.currentAvatar)
        if av:
            if self.currentAvatarQuestOfMe is None:
                self.d_setChat(NPCDialogue.PickQuest)
                questList = av.questManager.getPickableQuestList(self)
                self.sendUpdateToAvatarId(self.currentAvatar, 'makePickableQuests', [questList])

    def ranOutOfTime(self):
        avId = self.air.getAvatarIdFromSender()
        if avId == self.currentAvatar:
            self.d_setChat(NPCDialogue.PickQuestTimeOut)
            self.requestExit(avId)

    def pickedQuest(self, questId):
        av = self.air.doId2do.get(self.currentAvatar)
        if av:
            av.questManager.addNewQuest(questId)

    def hasValidReasonToEnter(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            chat = None
            needToVisitMe = av.questManager.hasAnObjectiveToVisit(self.npcId, self.zoneId)
            
            if not needToVisitMe:
                pickableQuestList = av.questManager.getPickableQuestList(self)
                # We don't need to visit this NPC and we're full on quests.
                if len(av.questManager.quests.keys()) >= 4:
                    array = list(NPCGlobals.NPCEnter_Pointless_Dialogue)
                    chat = random.choice(array)
                elif len(pickableQuestList) == 0:
                    # We don't need to visit this NPC and he doesn't have any quests to give us.
                    chat = NPCGlobals.NPCEnter_HQ_FinishCurrentQuest
            if chat:
                if '%s' in chat:
                    chat = chat % av.getName()
                self.d_setChat(chat)
            return chat is None
