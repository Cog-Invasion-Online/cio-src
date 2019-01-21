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

        self.chatSounds = ChoiceWidget(self.page, None, (0, 0.1, 0.1), widgetName = "Chat Sounds",
            settingKeyName = 'chs')

        self.discardChanges()

    def _setDefaults(self):
        self.origMusicVol = base.musicManager.getVolume()
        self.origSfxVol = base.sfxManagerList[0].getVolume()

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
        
        self.chatSounds.saveSetting()

        if (base.musicManager.getVolume() != self.origMusicVol):
            self.settingsMgr.getSetting("musvol").setValue(base.musicManager.getVolume())
        if (base.sfxManagerList[0].getVolume() != self.origSfxVol):
            self.settingsMgr.getSetting("sfxvol").setValue(base.sfxManagerList[0].getVolume())

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

        self.chatSounds.reset()

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