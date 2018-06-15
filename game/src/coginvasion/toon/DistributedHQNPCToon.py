"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedHQNPCToon.py
@author Brian Lach
@date August 2, 2015

"""

from panda3d.core import Vec4
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectButton, DGG

import DistributedNPCToon
from src.coginvasion.globals import CIGlobals
from src.coginvasion.quest.Quest import Quest
from src.coginvasion.quest import Objectives
from src.coginvasion.quest.QuestGlobals import NPCDialogue
from src.coginvasion.minigame.Timer import Timer

from src.coginvasion.quest import QuestGlobals

import random

class DistributedHQNPCToon(DistributedNPCToon.DistributedNPCToon):
    notify = directNotify.newCategory("DistributedHQNPCToon")

    def __init__(self, cr):
        DistributedNPCToon.DistributedNPCToon.__init__(self, cr)
        self.questFrame = None
        self.questBtns = None
        self.questPosters = None
        self.cancelBtn = None
        self.timer = None

    def __getHQOfficerQuestAssignChat(self):
        objective = self.currentQuest.accessibleObjectives[0]

        chat = self.currentQuest.assignSpeech
        if chat is None:
            chat = ''
            if objective.type == Objectives.VisitNPC:
                chat += self.getNPCLocationSpeech()
            else:
                chat = base.localAvatar.questManager.getTaskInfo(objective, True)
                chat += "\x07"
            chat += random.choice(NPCDialogue.QuestAssignGoodbyes)
        if chat.endswith("\x07"):
            if objective.type == Objectives.VisitNPC:
                chat += self.getNPCLocationSpeech()
            chat += random.choice(NPCDialogue.QuestAssignGoodbyes)

        return chat

    def __cancelQuestPicker(self, ranOutOfTime = True):
        self.removePickableQuests()
        if not ranOutOfTime:
            self.b_setChat(NPCDialogue.CancelQuestPicker)
        else:
            self._stopInteraction()
            self.sendUpdate('ranOutOfTime')

    def makePickableQuests(self, questList):
        self.doCameraNPCInteraction(True)

        quests = []

        for questId in questList:
            quest = Quest(questId, base.localAvatar.questManager)
            quest.setupCurrentObjectiveFromData(-1, 0, None)
            quests.append(quest)

        positions = [(0, 0, 0.65), (0, 0, 0.1), (0, 0, -0.45)]
        
        self.questFrame = DirectFrame(relief = None, pos = (-0.8, 0, 0),
            geom = DGG.getDefaultDialogGeom(), geom_color=Vec4(0.8, 0.6, 0.4, 1),
            geom_scale=(1.85, 1, 0.9), geom_hpr=(0, 0, -90))
        
        self.cancelBtn = DirectButton(text = "Cancel", geom = CIGlobals.getDefaultBtnGeom(), geom_scale = (0.6, 0.75, 0.75), relief = None, parent = self.questFrame,
                                      pos = (0.2, 0, -0.8), text_scale=0.045, text_pos = (0, -0.015), scale = 1.1, command = self.__cancelQuestPicker, extraArgs = [False])

        
        self.timer = Timer()
        self.timer.load()
        self.timer.setScale(0.3)
        self.timer.reparentTo(self.questFrame)
        self.timer.setPos(-0.1, 0, -0.8)
        self.timer.setInitialTime(20)
        self.timer.setZeroCommand(self.__cancelQuestPicker)
        self.timer.startTiming()

        self.questPosters = []
        self.questBtns = []
        
        for i in xrange(len(quests)):
            poster = None
            quest = quests[i]
            poster = QuestGlobals.generatePoster(quest, parent = aspect2d)
            poster.setScale(0.85)
            poster.setPos(0, 0, 0)
            poster.progressBar.hide()
            self.questPosters.append(poster)
            
            # Let's setup the choose button.
            btn = DirectButton(geom = CIGlobals.getDefaultBtnGeom(), parent = poster,
                pos = (0.35, 0, 0.215), text = 'Choose', text_scale = 0.08, 
                text_pos = (0, -0.025), relief = None, command = self.d_pickedQuest, extraArgs = [quests[i]])
            btn.setScale(0.4)
            btn.setBin('gui-popup', 60)
            btn.initialiseoptions(DirectButton)
            
            poster.reparentTo(self.questFrame.stateNodePath[0], 20)
            poster.setPos(positions[i])
            poster.show()
            
            self.questBtns.append(btn)

    def removePickableQuests(self):
        if self.timer:
            self.timer.unload()
            self.timer.cleanup()
            self.timer = None
        if self.questPosters:
            for poster in self.questPosters:
                poster.destroy()
            self.questPosters = None
        if self.questBtns:
            for btn in self.questBtns:
                btn.destroy()
            self.questBtns = None
        if self.questFrame:
            self.questFrame.destroy()
            self.questFrame = None
        if self.cancelBtn:
            self.cancelBtn.destroy()
            self.cancelBtn = None

    def d_pickedQuest(self, quest):
        self.removePickableQuests()
        self.sendUpdate('pickedQuest', [quest.id])
        self.currentQuest = quest
        self.currentQuestId = quest.id
        self.currentQuestObjective = 0
        self.currentChatIndex = 0
        self.b_setChat(self.__getHQOfficerQuestAssignChat())

        self.doCameraNPCInteraction()

    def disable(self):
        self.removePickableQuests()
        DistributedNPCToon.DistributedNPCToon.disable(self)
