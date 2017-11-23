"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestManager.py
@author Brian Lach
@date July 29, 2015

"""

from direct.showbase.DirectObject import DirectObject

from src.coginvasion.hood import ZoneUtil
from QuestManagerBase import QuestManagerBase
import QuestGlobals

class QuestManager(QuestManagerBase, DirectObject):
    
    def __init__(self, avatar):
        QuestManagerBase.__init__(self, avatar)
        DirectObject.__init__(self)
        
        # The quest posters that are shown when hitting the hotkey.
        self.posters = []
        
    def enableShowQuestsHotkey(self):
        self.acceptOnce(base.inputStore.ViewQuests, self.showQuests)
        
    def disableShowQuestsHotkey(self):
        self.ignore(base.inputStore.ViewQuests)
        
    def showQuests(self):
        assert self is base.localAvatar.questManager
        positions = [(-0.45, 0.75, 0.3), (0.45, 0.75, 0.3), (-0.45, 0.75, -0.3), (0.45, 0.75, -0.3)]
        if len(self.posters) != 0: return
        for i in range(4):
            quest = None
            
            if i < len(self.quests.values()):
                quest = self.quests.values()[i]
            poster = QuestGlobals.generatePoster(quest, parent = aspect2d)
            poster.setPos(positions[i])
            poster.setScale(0.95)
            poster.show()
            self.posters.append(poster)
        self.acceptOnce(base.inputStore.ViewQuests + '-up', self.hideQuests)
        
    def hideQuests(self):
        for poster in self.posters:
            poster.destroy()
        self.posters = []
        self.enableShowQuestsHotkey()

    def makeQuestsFromData(self):
        QuestManagerBase.makeQuestsFromData(self, base.localAvatar)
        self.posters = []
        
    def cleanup(self):
        QuestManagerBase.cleanup(self)
        self.hideQuests()
        self.ignoreAll()

    def getTaskInfo(self, objective, speech = False):
        """
        Returns a string that could be used as speech or for a quest note.
        It gives information about the quest and what you have to do.
        """

        taskInfo = ""

        if speech:
            # If it's speech, add the objective's header (e.g Defeat, Recover, Deliver) to the beginning of the sentence.
            taskInfo += objective.Header + " "

        # Add objective specific task info
        taskInfo += objective.getTaskInfo(speech)

        if objective.AreaSpecific:
            # This objective is sometimes area specific.
            if objective.area == QuestGlobals.Anywhere:
                taskInfo += "\nAnywhere" if not speech else " anywhere"
            else:
                # Say what area the objective must be completed in.
                taskInfo += "\nin " + ZoneUtil.getHoodId(objective.area) if not speech else " in " + ZoneUtil.getHoodId(objective.area)

        if speech:
            # Always put a period at the end of the sentence if it's speech!
            taskInfo += "."

        return taskInfo
