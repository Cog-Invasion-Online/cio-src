"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SoundCategory.py
@author Brian Lach
@date March 13, 2017

"""

from src.coginvasion.globals import CIGlobals

from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget
from SliderWidget import SliderWidget

class SoundCategory(OptionsCategory):
    Name = "Sound"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
      
        self.musicSlider = SliderWidget(page, "Music Volume", (0.0, 1.0), self.__setMusicVol, (0, 0, 0.475))

        self.sfxSlider = SliderWidget(page, "Sound Volume", (0.0, 1.0), self.__setSfxVol, (0, 0, 0.335))

        self.chatSounds = ChoiceWidget(self.page, ["Off", "On"], (0, 0.1, 0.1), self.__handleChatSoundsChoice, "Chat Sounds")

        self.discardChanges()

    def _setDefaults(self):
        self.origMusicVol = base.musicManager.getVolume()
        self.origSfxVol = base.sfxManagerList[0].getVolume()

        self.origChs = int(CIGlobals.getSettingsMgr().getSetting("chs"))
        self.chsChoice = bool(self.origChs)

    def __handleChatSoundsChoice(self, choice):
        self.chsChoice = bool(choice)

    def __setMusicVol(self):
        val = self.musicSlider.getSliderVal()

        base.musicManager.setVolume(val)

        self.musicSlider.setValText("{:.0f}%".format(val * 100))

    def __setSfxVol(self):
        val = self.sfxSlider.getSliderVal()

        base.sfxManagerList[0].setVolume(val)

        self.sfxSlider.setValText("{:.0f}%".format(val * 100))

    def applyChanges(self):
        self._showApplying()

        if (self.chsChoice != bool(self.origChs)):
            # The chat sounds option has been modified.
            CIGlobals.getSettingsMgr().updateAndWriteSetting("chs", self.chsChoice)
        if (base.musicManager.getVolume() != self.origMusicVol):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("musvol", base.musicManager.getVolume())
        if (base.sfxManagerList[0].getVolume() != self.origSfxVol):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("sfxvol", base.sfxManagerList[0].getVolume())

        self._setDefaults()

        self._hideApplying()

    def discardChanges(self):
        
        if not hasattr(self, 'origMusicVol'):
            self._setDefaults()

        base.musicManager.setVolume(self.origMusicVol)
        self.musicSlider.setSliderVal(self.origMusicVol)
        self.musicSlider.setValText("{:.0f}%".format(self.origMusicVol * 100))

        base.sfxManagerList[0].setVolume(self.origSfxVol)
        self.sfxSlider.setSliderVal(self.origSfxVol)
        self.sfxSlider.setValText("{:.0f}%".format(self.origSfxVol * 100))

        self.origChs = int(CIGlobals.getSettingsMgr().getSetting("chs"))
        self.chsChoice = bool(self.origChs)
        self.chatSounds.goto(self.origChs)

        self._setDefaults()

    def cleanup(self):
        self.discardChanges()

        if hasattr(self, 'musicSlider'):
            self.musicSlider.destroy()
            del self.musicSlider
        if hasattr(self, 'sfxSlider'):
            self.sfxSlider.destroy()
            del self.sfxSlider
        if hasattr(self, 'chatSounds'):
            self.chatSounds.cleanup()
            del self.chatSounds

        del self.origMusicVol
        del self.origSfxVol
        OptionsCategory.cleanup(self)