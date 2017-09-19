"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file OptionsPage.py
@author Brian Lach
@date December 30, 2016

"""

from direct.gui.DirectGui import DirectFrame, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from BookPage import BookPage
from AboutCategory import AboutCategory
from SoundCategory import SoundCategory
from ControlsCategory import ControlsCategory
from DisplayCategory import DisplayCategory
from CategoryTab import CategoryTab

class OptionsPage(BookPage):
    notify = directNotify.newCategory("OptionsPage")

    Categories = [AboutCategory, SoundCategory, ControlsCategory, DisplayCategory]

    def __init__(self, book):
        BookPage.__init__(self, book, "Options")
        self.currentCategory = None
        self.tabs = []

    def load(self):
        BookPage.load(self)
        icons = loader.loadModel('phase_3.5/models/gui/sos_textures.bam')
        self.icon = icons.find('**/switch')
        icons.detachNode()

    def enter(self):
        BookPage.enter(self)
        self.tabsFrame = DirectFrame(parent = self.book)
        Z = 0.77
        
        tabWidth = 0.379136800766
        spacing = 0.075

        totalWidth = 0.0

        for i in xrange(len(self.Categories)):
            if i > 0:
                totalWidth += spacing
            totalWidth += tabWidth
            cl = self.Categories[i]
            tab = CategoryTab(self, cl.Name, [cl], ((tabWidth + spacing) * i, 0, Z))
            self.tabs.append(tab)

        self.tabsFrame.setX(totalWidth / -2.0)

        self.pickCategory(AboutCategory)

    def closeWindow(self):
        if self.currentCategory:
            self.currentCategory.cleanup()
            self.currentCategory = None

    def pickCategory(self, cat):
        if self.currentCategory:
            self.currentCategory.cleanup()
            self.currentCategory = None
        self.currentCategory = cat(self)
        for tab in self.tabs:
            if tab['extraArgs'][0] is cat:
                tab['state'] = DGG.DISABLED
            else:
                tab['state'] = DGG.NORMAL
        #self.currentCategory.show()

    def exit(self):
        if self.currentCategory:
            self.currentCategory.cleanup()
            self.currentCategory = None
        for tab in self.tabs:
            tab.destroy()
        self.tabs = []
        BookPage.exit(self)
