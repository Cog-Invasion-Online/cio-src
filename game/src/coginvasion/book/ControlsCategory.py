"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ControlsCategory.py
@author Brian Lach
@date March 13, 2017

"""

from src.coginvasion.globals import CIGlobals

from OptionsCategory import OptionsCategory
from SliderWidget import SliderWidget
from ChoiceWidget import ChoiceWidget
from ChoiceWidget import MULTICHOICE, INDEX

class ControlsCategory(OptionsCategory):
    Name = "Controls"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.gagKey = ChoiceWidget(page, None, pos = (0, 0.47, 0.47), widgetName = "Use Gag",
            settingKeyName = 'gagkey', mode = MULTICHOICE)
            
        self.bpov = ChoiceWidget(page, None, pos = (0, 0.25, 0.25), widgetName = "Battle POV",
                settingKeyName = 'bpov', mode = INDEX, choiceTextScale = 0.053)

        self.fpmsSlider = SliderWidget(page, "Mouse Sensitivity\n(First Person)", (0.05, 0.3), self.__setFPMS, (0, 0, 0.1))
        self.fpfovSlider = SliderWidget(page, "Field of View\n(First Person)", (54.0, 70.0), self.__setFPFov, (0, 0, -0.15))
        self.genFovSlider = SliderWidget(page, "Field of View\n(General Gameplay)", (40.0, 70.0), self.__setGenFov, (0, 0, -0.4))
        
        self.keysChanged = 0
        
        self.discardChanges()

    def _setDefaults(self):
        self.origFPms = float(CIGlobals.getSettingsMgr().getSetting("fpmgms").getValue())
        self.origFPfov = float(CIGlobals.getSettingsMgr().getSetting("fpmgfov").getValue())
        self.origGenFov = float(CIGlobals.getSettingsMgr().getSetting("genfov").getValue())

        self.fpFov = self.origFPfov
        self.fpMs = self.origFPms
        self.genFov = self.origGenFov
        
        self.keysChanged = 0
        self.gagKey.reset()
        self.bpov.reset()
        
    def __updateGagKey(self, _):
        self.keysChanged += 1

    def __setFPMS(self):
        val = self.fpmsSlider.getSliderVal()
        self.fpmsSlider.setValText("{:.2f}".format(val * 10.0))
        self.fpMs = val

    def __setFPFov(self):
        val = self.fpfovSlider.getSliderVal()
        self.fpfovSlider.setValText("{:.0f}".format(val))
        self.fpFov = val

    def __setGenFov(self):
        val = self.genFovSlider.getSliderVal()
        self.genFovSlider.setValText("{:.0f}".format(val))
        self.genFov = val

    def applyChanges(self):
        self._showApplying()
        
        self.gagKey.saveSetting()
        self.bpov.saveSetting()

        if (self.fpFov != self.origFPfov):
            # They changed the first person fov!
            self.settingsMgr.getSetting("fpmgfov").setValue(self.fpFov)

        if (self.fpMs != self.origFPms):
            self.settingsMgr.getSetting("fpmgms").setValue(self.fpMs)

        if (self.genFov != self.origGenFov):
            self.settingsMgr.getSetting("genfov").setValue(self.genFov)

        # We need to let the chat input know when we updated keys.
        if self.keysChanged > 0:
            base.localAvatar.chatInput.setKeyList()
            
        self.settingsMgr.saveFile()

        self._setDefaults()
        self._hideApplying()

    def discardChanges(self):
        self._setDefaults()

        self.fpmsSlider.setSliderVal(self.origFPms)
        self.fpmsSlider.setValText("{:.2f}".format(self.origFPms * 10.0))

        self.fpfovSlider.setSliderVal(self.origFPfov)
        self.fpfovSlider.setValText("{:.0f}".format(self.origFPfov))

        self.genFovSlider.setSliderVal(self.origGenFov)
        self.genFovSlider.setValText("{:.0f}".format(self.origGenFov))

    def cleanup(self):
        self.discardChanges()
        OptionsCategory.cleanup(self)

        for widget in [self.gagKey, self.fpmsSlider, self.fpfovSlider, self.genFovSlider, self.bpov]:
            widget.cleanup()

        del self.gagKey
        del self.bpov
        del self.fpmsSlider
        del self.fpfovSlider
        del self.genFovSlider
        del self.origFPms
        del self.origFPfov
        del self.origGenFov

        del self.fpFov
        del self.fpMs
        del self.genFov
        del self.keysChanged
