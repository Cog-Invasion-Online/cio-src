"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DisplayCategory.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import TextNode, WindowProperties, AntialiasAttrib

from direct.gui.DirectGui import DirectCheckButton, OnscreenText

from src.coginvasion.globals import CIGlobals
from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget
from ChoiceWidget import DEGREE, RESOLUTION, INDEX

class DisplayCategory(OptionsCategory):
    Name = "Display"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)

        self.reso = ChoiceWidget(page, None,
            pos = (0, 0, 0.47), widgetName = "Resolution", choiceTextScale = 0.05, 
            settingKeyName = 'resolution', mode = RESOLUTION)

        self.masprText = OnscreenText(text = "Maintain aspect ratio?", scale = 0.045, parent = page.book, align = TextNode.ALeft, pos = (-0.7, 0.4))
        self.maspr = DirectCheckButton(scale = 0.07, parent = page.book, pos = (-0.19, 0, 0.41), command = self.__toggleMaspr)

        self.fs = ChoiceWidget(page, None, pos = (0, 0, 0.24), 
            widgetName = "Fullscreen", settingKeyName = 'fullscreen')

        self.aa = ChoiceWidget(page, None, pos = (0, 0, 0.01), widgetName = "Antialiasing",
            settingKeyName = 'aa', choiceTextScale = 0.05)

        self.af = ChoiceWidget(page, None, (0, 0, -0.22), widgetName = "Anisotropic Filtering",
            settingKeyName = 'af', mode = DEGREE)
        
        self.vsync = ChoiceWidget(page, None, pos = (0, 0, -0.45), widgetName = "V-Sync",
            settingKeyName = 'vsync')
        
        self.widgets = [self.fs, self.aa, self.af, self.reso, self.vsync]

        self.discardChanges()

    def _setDefaults(self):
        self.origMaspr = CIGlobals.getSettingsMgr().getSetting("maspr").getValue()
        self.masprChoice = self.origMaspr

    def __toggleMaspr(self, choice):
        if choice:
            # maintain aspect ratio on!
            self.masprChoice = True
        else:
            # maintain aspect ratio off!
            self.masprChoice = False

    def applyChanges(self):
        self._showApplying()

        if self.widgets:
            for widget in self.widgets:
                widget.saveSetting()

        if (self.masprChoice != self.origMaspr):
            self.settingsMgr.getSetting("maspr").setValue(self.masprChoice)
            
        self.settingsMgr.saveFile()

        self._hideApplying()

    def discardChanges(self):
        OptionsCategory.discardChanges(self)
        self._setDefaults()

        self.maspr['indicatorValue'] = self.masprChoice

    def cleanup(self):
        for widget in self.widgets:
            widget.cleanup()

        if hasattr(self, 'masprText'):
            self.masprText.destroy()
            del self.masprText

        if hasattr(self, 'maspr'):
            self.maspr.destroy()
            del self.maspr

        self.widgets = []
        del self.reso
        del self.fs
        del self.aa
        del self.af
        del self.vsync
        del self.origMaspr
        del self.masprChoice
        del self.widgets
        OptionsCategory.cleanup(self)
