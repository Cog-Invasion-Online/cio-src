# Filename: DistributedHQNPCToon.py
# Created by:  blach (2Aug15)

from pandac.PandaModules import Vec4
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectButton, DGG

import DistributedNPCToon
from src.coginvasion.globals import CIGlobals
from src.coginvasion.quests import Quests, QuestNote, Objectives
from src.coginvasion.quests.QuestGlobals import NPCDialogue
from src.coginvasion.minigame.Timer import Timer

import random

class DistributedHQNPCToon(DistributedNPCToon.DistributedNPCToon):
    notify = directNotify.newCategory("DistributedHQNPCToon")

    def __init__(self, cr):
        DistributedNPCToon.DistributedNPCToon.__init__(self, cr)
        self.questFrame = None
        self.questBtns = None
        self.questNotes = None
        self.cancelBtn = None
        self.timer = None

    def __getHQOfficerQuestAssignChat(self):
        objective = self.currentQuest.currentObjective

        chat = self.currentQuest.assignSpeech
        if chat is None:
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

    def makePickableQuests(self, list):
        self.doCameraNPCInteraction(True)

        quests = []

        for questId in list:
            quests.append(Quests.Quest(questId, 0, 0, list.index(questId), base.localAvatar.questManager))

        positions = [(0, 0, 0.6), (0, 0, 0.1), (0, 0, -0.4)]

        self.questNotes = base.localAvatar.questManager.makeQuestNotes(quests = quests)

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

        self.questBtns = []

        for i in xrange(len(self.questNotes)):
            
            note = self.questNotes[i]
            note.reparentTo(self.questFrame)
            note.setPos(positions[i])
            if quests[i].currentObjective.HasProgress:
                note.progressBar.hide()
                note.progressText.hide()
            note.show()

            btn = DirectButton(text = "Choose", geom = CIGlobals.getDefaultBtnGeom(), geom_scale = (0.6, 0.75, 0.75), relief = None,
                               parent = note, pos = (0.03, 0.42, 0.42), hpr = (0, 0, -3.5), text_scale=0.045, text_pos = (0, -0.015), scale = 1.2,
                               command = self.d_pickedQuest, extraArgs = [quests[i]])

            self.questBtns.append(btn)

    def removePickableQuests(self):
        if self.timer:
            self.timer.unload()
            self.timer.cleanup()
            self.timer = None
        if self.questNotes:
            for note in self.questNotes:
                note.destroy()
            self.questNotes = None
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
        self.sendUpdate('pickedQuest', [quest.questId])
        self.currentQuest = quest
        self.currentQuestId = quest.questId
        self.currentQuestObjective = 0
        self.currentChatIndex = 0
        self.b_setChat(self.__getHQOfficerQuestAssignChat())

        self.doCameraNPCInteraction()

    def disable(self):
        self.removePickableQuests()
        DistributedNPCToon.DistributedNPCToon.disable(self)
