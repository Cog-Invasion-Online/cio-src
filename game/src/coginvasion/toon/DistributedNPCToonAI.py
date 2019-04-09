"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedNPCToonAI.py
@author Brian Lach
@date July 31, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedToonAI import DistributedToonAI
from src.coginvasion.distributed.AvatarWatcher import AvatarWatcher, MONITOR_CRASHED, MONITOR_DELETION, MONITOR_ZONE_CHANGE
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.globals import ChatGlobals

from src.coginvasion.quest.Objectives import VisitNPCObjective

import random

class DistributedNPCToonAI(DistributedToonAI, AvatarWatcher):
    notify = directNotify.newCategory("DistributedNPCToonAI")
    ACCOUNT = 0
    
    Moving = False
    NeedsPhysics = False

    def __init__(self, air, npcId, originIndex):
        DistributedToonAI.__init__(self, air)
        AvatarWatcher.__init__(self, air, flags = MONITOR_CRASHED | MONITOR_DELETION | MONITOR_ZONE_CHANGE)
        self.originIndex = originIndex
        self.npcId = npcId
        npcData = NPCGlobals.NPCToonDict.get(npcId)
        self.dnaStrand = npcData[2]
        self.setName(npcData[1])
        self.place = 0

        self.currentAvatar = None
        # The id of the quest where the current objective is to visit me.
        self.currentAvatarQuestOfMe = None
        
        self.acceptEvents()

    def isHQOfficer(self):
        return NPCGlobals.NPCToonDict[self.npcId][3] == NPCGlobals.NPC_HQ

    def getNpcId(self):
        return self.npcId

    def getOriginIndex(self):
        return self.originIndex

    def delete(self):
        self.ignoreEvents()
        self.currentAvatar = None
        DistributedToonAI.delete(self)

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()

        if not self.hasValidReasonToEnter(avId):
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
        else:
            self.currentAvatar = avId
            av = self.air.doId2do.get(avId)
            self.currentAvatarQuestOfMe = av.questManager.getVisitQuest(self.npcId)
            self.startTrackingAvatarId(avId)
            self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
            self.sendUpdate('lookAtAvatar', [avId])
            self.doQuestStuffWithThisAvatar()
            
    def requestExit(self, avId = None):
        if not avId:
            avId = self.air.getAvatarIdFromSender()

        if self.currentAvatar != None:
            if avId == self.currentAvatar:
                self.stopTrackingAvatarId(avId)
                self.currentAvatar = None
                self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
            else:
                self.notify.warning("Toon %d requested to exit, but they're not the current avatar." % avId)
                
    def handleAvatarLeave(self, avatar, _):
        av = self.air.doId2do.get(self.currentAvatar)
        if av == avatar:
            self.stopTrackingAvatarId(self.currentAvatar)
            self.currentAvatar = None
        else:
            self.notify.warning("Received update that Toon %d has left, but they're not the current avatar." % avatar.doId)
                
    def doQuestStuffWithThisAvatar(self):
        av = self.air.doId2do.get(self.currentAvatar)
        
        if av and self.currentAvatarQuestOfMe:
            objective = self.currentAvatarQuestOfMe[2]
            objective.incrementProgress()

    def hasValidReasonToEnter(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            chatArray = None
            needsToVisit = av.questManager.hasAnObjectiveToVisit(self.npcId, self.zoneId)
            lastVisited = av.questManager.wasLastObjectiveToVisit(self.npcId)
            
            if not lastVisited and not needsToVisit:
                # This avatar entered for no reason. They either have no quests or no objective to visit me.
                chatArray = NPCGlobals.NPCEnter_Pointless_Dialogue
            elif lastVisited or (needsToVisit and (isinstance(needsToVisit, VisitNPCObjective) and not needsToVisit.isPreparedToVisit())):
                # This avatar entered, but still has to complete the objective I gave him/her.
                chatArray = NPCGlobals.NPCEnter_MFCO_Dialogue

            welcomeToShopDialogueIndex = 28

            if chatArray:
                chat = random.choice(chatArray)
                if '{avatarName}' in chat:
                    chat = ChatGlobals.mentionAvatar(chat, av.getName())
                elif '{shopName}' in chat and (chatArray == NPCGlobals.NPCEnter_Pointless_Dialogue and
                    NPCGlobals.NPCEnter_Pointless_Dialogue.index(chat) == welcomeToShopDialogueIndex):
                        chat = chat.format(shopName = ZoneUtil.zone2TitleDict[self.zoneId][0])
                self.d_setChat(chat)
            return chatArray is None
