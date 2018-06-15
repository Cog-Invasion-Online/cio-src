"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file QuestPage.py
@author Brian Lach
@date July 27, 2016

"""

from src.coginvasion.quest.poster.QuestPoster import QuestPoster
from src.coginvasion.quest.poster.DoubleFrameQuestPoster import DoubleFrameQuestPoster
from src.coginvasion.quest import QuestGlobals
from BookPage import BookPage

class QuestPage(BookPage):

    def __init__(self, book):
        BookPage.__init__(self, book, 'ToonTasks')

        self.posters = []
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
        quests = base.localAvatar.questManager.quests.values()
        
        for i in range(4):
            quest = None
            if i < len(quests):
                quest = quests[i]
            poster = QuestGlobals.generatePoster(quest, parent = self.book)
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
