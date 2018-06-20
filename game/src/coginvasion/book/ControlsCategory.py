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

class ControlsCategory(OptionsCategory):
    Name = "Controls"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        gagKeys = base.inputStore.getControlOptions('UseGag')
        self.gagKey = ChoiceWidget(page, gagKeys, (0, 0.47, 0.47), self.__handleChooseGK, "Use Gag Key")

        self.fpmsSlider = SliderWidget(page, "Mouse Sensitivity\n(First Person)", (0.05, 0.3), self.__setFPMS, (0, 0, 0.2))
        self.fpfovSlider = SliderWidget(page, "Field of View\n(First Person)", (54.0, 70.0), self.__setFPFov, (0, 0, -0.1))
        self.genFovSlider = SliderWidget(page, "Field of View\n(General Gameplay)", (40.0, 70.0), self.__setGenFov, (0, 0, -0.4))

        self.discardChanges()

    def _setDefaults(self):
        self.origGagKey = str(CIGlobals.getSettingsMgr().getSetting("gagkey"))
        self.origFPms = float(CIGlobals.getSettingsMgr().getSetting("fpmgms"))
        self.origFPfov = float(CIGlobals.getSettingsMgr().getSetting("fpmgfov"))
        self.origGenFov = float(CIGlobals.getSettingsMgr().getSetting("genfov"))

        self.gagKeyChoice = self.origGagKey
        self.fpFov = self.origFPfov
        self.fpMs = self.origFPms
        self.genFov = self.origGenFov

    def __handleChooseGK(self, choice):
        self.gagKeyChoice = self.gagKey.options[choice]

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
        
        keysChanged = 0

        if (self.gagKeyChoice != self.origGagKey):
            # They changed the gag key!
            CIGlobals.getSettingsMgr().updateAndWriteSetting("gagkey", self.gagKeyChoice)
            keysChanged += 1

        if (self.fpFov != self.origFPfov):
            # They changed the first person fov!
            CIGlobals.getSettingsMgr().updateAndWriteSetting("fpmgfov", self.fpFov)
            CIGlobals.GunGameFov = self.fpFov

        if (self.fpMs != self.origFPms):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("fpmgms", self.fpMs)

        if (self.genFov != self.origGenFov):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("genfov", self.genFov)
            CIGlobals.DefaultCameraFov = self.genFov
            base.camLens.setMinFov(self.genFov / (4. / 3.))

        self._setDefaults()
        
        # We need to let the chat input know when we updated keys.
        if keysChanged > 0:
            base.localAvatar.chatInput.setKeyList()
        
        self._hideApplying()

    def discardChanges(self):
        self._setDefaults()
        self.gagKey.goto(self.gagKey.options.index(self.origGagKey))

        self.fpmsSlider.setSliderVal(self.origFPms)
        self.fpmsSlider.setValText("{:.2f}".format(self.origFPms * 10.0))

        self.fpfovSlider.setSliderVal(self.origFPfov)
        self.fpfovSlider.setValText("{:.0f}".format(self.origFPfov))

        self.genFovSlider.setSliderVal(self.origGenFov)
        self.genFovSlider.setValText("{:.0f}".format(self.origGenFov))

    def cleanup(self):

        self.discardChanges()

        OptionsCategory.cleanup(self)

        if hasattr(self, 'gagKey'):
            self.gagKey.cleanup()
            del self.gagKey

        if hasattr(self, 'fpmsSlider'):
            self.fpmsSlider.cleanup()
            del self.fpmsSlider

        if hasattr(self, 'fpfovSlider'):
            self.fpfovSlider.cleanup()
            del self.fpfovSlider

        if hasattr(self, 'genFovSlider'):
            self.genFovSlider.cleanup()
            del self.genFovSlider

        del self.origGagKey
        del self.origFPms
        del self.origFPfov
        del self.origGenFov

        del self.gagKeyChoice
        del self.fpFov
        del self.fpMs
        del self.genFov
