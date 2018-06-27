"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdvancedCategory.py
@author Brian Lach
@date September 28, 2017

"""

from src.coginvasion.globals import CIGlobals
from ChoiceWidget import ChoiceWidget
from OptionsCategory import OptionsCategory

class AdvancedCategory(OptionsCategory):
    Name = "Advanced"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)

        self.vsync = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.47), self.__chooseVSync, "V-Sync")

        self.discardChanges()

    def __chooseVSync(self, choice):
        self.vsyncChoice = bool(choice)

    def _setDefaults(self):
        self.origVSync = CIGlobals.getSettingsMgr().getSetting("vsync")
        self.vsyncChoice = self.origVSync

    def applyChanges(self):
        self._showApplying()

        if (self.vsyncChoice != self.origVSync):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("vsync", self.vsyncChoice)

        self._setDefaults()
        self._hideApplying()

    def discardChanges(self):
        self._setDefaults()

        self.vsync.goto(int(self.vsyncChoice))

    def cleanup(self):
        if hasattr(self, 'vsync'):
            self.vsync.cleanup()
            del self.vsync

        del self.vsyncChoice
        del self.origVSync

        OptionsCategory.cleanup(self)