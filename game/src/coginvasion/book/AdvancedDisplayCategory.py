"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdvancedDisplayCategory.py
@author Brian Lach
@date September 28, 2017

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gui.Dialog import GlobalDialog, Ok
from ChoiceWidget import ChoiceWidget, INDEX
from OptionsCategory import OptionsCategory

class AdvancedDisplayCategory(OptionsCategory):
    Name = "Graphics"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        #self.lighting = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.47), self.__updateLighting, "Lighting",
        #    desc = 'Toggles basic per-vertex lighting.\nShould not affect performance.', settingKeyName = 'lighting')
        
        #self.ppl = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.24), self.__updatePPL, "Per-Pixel Lighting",
        #    desc = 'Toggles more advanced per-pixel shaders.\nRequires Lighting to be enabled.\nAffects performance.', settingKeyName = 'ppl')

        self.hdr = ChoiceWidget(page, None, pos = (0, 0, 0.01),
            widgetName = "HDR Lighting", settingKeyName = 'hdr', 
            requirement = base.hdr.isSupported)

        self.bloom = ChoiceWidget(page, None, pos = (0, 0, -0.22), 
            widgetName = "Bloom Filter", settingKeyName = 'bloom')
        
        self.waterRefl = ChoiceWidget(page, None, pos = (0, 0, -0.45), 
            widgetName = "Water Reflections", settingKeyName = 'refl')
        
        self.widgets = [self.waterRefl, self.hdr, self.bloom]#self.lighting, self.ppl, self.waterRefl, self.hdr, self.bloom]

        self.discardChanges()
        
    #def __updateLighting(self, useLighting):
    #    metadata.USE_LIGHTING = useLighting
        
    #def __updatePPL(self, ppl):
    #    if ppl:
    #        render.setShaderAuto()
    #    else:
    #        render.setShaderOff(1)

    def __handleBadHdrAck(self, value):
        self.cleanupBadHdrDlg()

    def _setDefaults(self):
        for widget in self.widgets:
            widget.reset()

    def discardChanges(self):
        OptionsCategory.discardChanges(self)
        self._setDefaults()

    def cleanupBadHdrDlg(self):
        self.ignore('badHdrAck')
        if hasattr(self, 'badHdrDlg'):
            self.badHdrDlg.cleanup()
            del self.badHdrDlg

    def cleanup(self):
        self.cleanupBadHdrDlg()

        for widget in self.widgets:
            widget.cleanup()
        
        self.widgets = []
        del self.waterRefl
        del self.hdr
        del self.bloom
        del self.widgets

        OptionsCategory.cleanup(self)
