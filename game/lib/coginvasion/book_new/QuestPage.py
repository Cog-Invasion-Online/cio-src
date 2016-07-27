"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestPage.py
@author Brian Lach
@date 2016-07-27

"""

from direct.gui.DirectGui import OnscreenText

from lib.coginvasion.quest.QuestPoster import QuestPoster
from BookPage import BookPage

class QuestPage(BookPage):

    def __init__(self, book):
        BookPage.__init__(self, book, 'Quests')

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

        self.posters = []
        for quest in base.localAvatar.questManager.getQuests():
            poster = QuestPoster(quest)
            poster.update()
            self.posters.append(poster)

        self.infoText = OnscreenText(text = "Return completed Quests to an HQ Officer at any Toon HQ building.",
            pos = (0, -0.6), scale = 0.045)

    def exit(self):
        for poster in self.posters:
            poster.destroy()
        self.posters = []
        if self.infoText:
            self.infoText.destroy()
            self.infoText = None
        BookPage.exit(self)
