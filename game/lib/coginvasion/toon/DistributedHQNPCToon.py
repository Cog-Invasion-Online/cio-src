# Filename: DistributedHQNPCToon.py
# Created by:  blach (2Aug15)

from panda3d.core import Vec4
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectButton, DGG

import DistributedNPCToon
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quests import Quests, QuestNote, Objectives
from lib.coginvasion.quests.QuestGlobals import NPCDialogue

import random

class DistributedHQNPCToon(DistributedNPCToon.DistributedNPCToon):
    notify = directNotify.newCategory("DistributedHQNPCToon")

    def __init__(self, cr):
        DistributedNPCToon.DistributedNPCToon.__init__(self, cr)
        self.questFrame = None
        self.questBtns = None
        self.questNotes = None

    def __getHQOfficerQuestAssignChat(self):
        objective = self.currentQuest.currentObjective

        chat = self.currentQuest.assignSpeech
        if chat is None:
            chat = base.localAvatar.questManager.getTaskInfo(objective, True)
            chat += "\x07"
            chat += random.choice(NPCDialogue.QuestAssignGoodbyes)
        if chat.endswith("\x07"):
            if objective.type == Objectives.VisitNPC:
                chat += self.getNPCLocationSpeech()
            chat += random.choice(NPCDialogue.QuestAssignGoodbyes)

        return chat

    def makePickableQuests(self, list):
        quests = []
        for questId in list:
            quests.append(Quests.Quest(questId, 0, 0, list.index(questId), base.localAvatar.questManager))
        positions = [(0, 0, 0.6), (0, 0, 0), (0, 0, -0.6)]
        self.questNotes = base.localAvatar.questManager.makeQuestNotes(quests = quests)
        self.questFrame = DirectFrame(parent = base.a2dLeftCenter, relief = None, pos = (0.5, 0, 0),
            geom = DGG.getDefaultDialogGeom(), geom_color=Vec4(0.8, 0.6, 0.4, 1),
            geom_scale=(1.85, 1, 0.9), geom_hpr=(0, 0, -90))
        self.questBtns = []
        for i in xrange(len(self.questNotes)):
            note = self.questNotes[i]
            note.setPos(0, 0, 0)
            if quests[i].currentObjective.HasProgress:
                note.progressText.hide()
            btn = DirectButton(geom = note, parent = self.questFrame,
                pos = positions[i], command = self.d_pickedQuest, extraArgs = [quests[i]], relief = None)
            btn.setScale(1.15)
            note.reparentTo(btn.stateNodePath[0], 20)
            note.instanceTo(btn.stateNodePath[1], 20)
            note.instanceTo(btn.stateNodePath[2], 20)
            note.show()
            self.questBtns.append(btn)

    def removePickableQuests(self):
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

    def d_pickedQuest(self, quest):
        self.removePickableQuests()
        self.sendUpdate('pickedQuest', [quest.questId])
        self.currentQuest = quest
        self.currentQuestId = quest.questId
        self.currentQuestObjective = 0
        self.currentChatIndex = 0
        self.b_setChat(self.__getHQOfficerQuestAssignChat())

    def disable(self):
        self.removePickableQuests()
        DistributedNPCToon.DistributedNPCToon.disable(self)
