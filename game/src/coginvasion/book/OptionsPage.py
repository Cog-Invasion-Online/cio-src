"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file OptionsPage.py
@author Brian Lach
@date December 30, 2016

"""

from direct.gui.DirectGui import DirectFrame, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from BookPage import BookPage
from AboutCategory import AboutCategory
from SoundCategory import SoundCategory
from ControlsCategory import ControlsCategory
from DisplayCategory import DisplayCategory
from CategoryTab import CategoryTab
from GeneralCategory import GeneralCategory
from AdvancedCategory import AdvancedCategory

from collections import OrderedDict

class OptionsPage(BookPage):
    notify = directNotify.newCategory("OptionsPage")
    
    # Keys are categories and values are x-positions for the text.
    Categories = OrderedDict()
    Categories[AboutCategory] = 0.09
    Categories[GeneralCategory] = 0.07
    Categories[DisplayCategory] = 0.07
    Categories[SoundCategory] = 0.0825
    Categories[ControlsCategory] = 0.05
    Categories[AdvancedCategory] = 0.04

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
        self.tabScaleFrame = DirectFrame(parent = self.book)
        self.tabScaleFrame.setZ(0.7683)
        self.tabsFrame = DirectFrame(parent = self.tabScaleFrame)
        
        tabWidth = 0.379136800766
        spacing = 0.075

        totalWidth = 0.0
        bookWidth = 2.0

        for i in xrange(len(self.Categories.keys())):
            if i > 0:
                totalWidth += spacing
            totalWidth += tabWidth
            cl = self.Categories.keys()[i]
            tab = CategoryTab(self, cl.Name, [cl], ((tabWidth + spacing) * i, 0, 0), self.Categories.values()[i])
            self.tabs.append(tab)

        self.tabsFrame.setX(totalWidth / -2.0)
        self.tabScaleFrame.setScale(min(1.0, 1.0 / (totalWidth / bookWidth)))

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
        self.tabsFrame.destroy()
        del self.tabsFrame
        self.tabScaleFrame.destroy()
        del self.tabScaleFrame
        self.tabs = []
        BookPage.exit(self)
