"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestPage.py
@author Brian Lach
@date 2016-07-27

"""

from src.coginvasion.quests.poster.QuestPoster import QuestPoster
from src.coginvasion.quests.poster.DoubleFrameQuestPoster import DoubleFrameQuestPoster
from src.coginvasion.quests import Objectives
from BookPage import BookPage

class QuestPage(BookPage):

    def __init__(self, book):
        BookPage.__init__(self, book, 'ToonTasks')

        self.posters = []
        #self.notes = []
        self.infoText = None

    def load(self):
        BookPage.load(self)

        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        self.icon = bookModel.find('**/questCard')
        self.iconScale = 0.9
        bookModel.detachNode()

    def enter(self):
        BookPage.enter(self)
        
        positions = [(-0.45, 0.75, 0.3), (0.45, 0.75, 0.3), (-0.45, 0.75, -0.3), (0.45, 0.75, -0.3)]

        for i in xrange(len(base.localAvatar.questManager.quests.values())):
            quest = base.localAvatar.questManager.quests.values()[i]
            objective = quest.currentObjective
            poster = None
            if objective.__class__ in Objectives.DoubleFrameObjectives:
                poster = DoubleFrameQuestPoster(quest, parent = self.book)
            else:
                poster = QuestPoster(quest, parent = self.book)
            poster.setup()
            poster.setPos(positions[i])
            poster.setScale(0.95)
            poster.show()
            self.posters.append(poster)

    def exit(self):
        for poster in self.posters:
            poster.destroy()
        self.posters = []
        if self.infoText:
            self.infoText.destroy()
            self.infoText = None
        BookPage.exit(self)
