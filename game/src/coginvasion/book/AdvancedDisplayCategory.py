"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdvancedDisplayCategory.py
@author Brian Lach
@date September 28, 2017

"""

from src.coginvasion.globals import CIGlobals
from ChoiceWidget import ChoiceWidget
from OptionsCategory import OptionsCategory

class AdvancedDisplayCategory(OptionsCategory):
    Name = "Graphics"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.lighting = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.47), self.__updateLighting, "Lighting",
            desc = 'Toggles lights and shaders. Performance intensive.', settingKeyName = 'lighting')
        
        self.ppl = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.2), self.__updatePPL, "Per-Pixel Lighting",
            desc = 'Calculates illumination for each individual pixel.\nPerformance intensive.', settingKeyName = 'ppl')
        
        self.hdr = ChoiceWidget(page, ["None", "Ver. 1", "Ver. 2", "Ver. 3"], (0, 0, -0.07),
            self.__updateHDR, "HDR Tone Mapping", desc = 'Preserves light details that may be lost due to lower\ncontrast ratios. Performance intesive.',
            settingKeyName = 'hdr')
        
        self.bloom = ChoiceWidget(page, ["Off", "On"], (0, 0, -0.34), self.__updateBloom, "Bloom Filter",
            desc = "Toggles realistic \"feathers\" of light. Performance intensive.", settingKeyName = 'bloom')
        
        self.widgets = [self.lighting, self.ppl, self.hdr, self.bloom]

        self.discardChanges()
        
    def __updateLighting(self, useLighting):
        game.uselighting = useLighting
        
    def __updatePPL(self, ppl):
        if ppl:
            render.setShaderAuto()
        else:
            render.setShaderOff()
            
    def __updateHDR(self, hdr):
        CIGlobals.getSettingsMgr().applyHdr(hdr)
            
    def __updateBloom(self, flag):
        base.setBloom(flag)

    def _setDefaults(self):
        for widget in self.widgets:
            widget.reset()

    def applyChanges(self):
        self._showApplying()
        
        OptionsCategory.applyChanges(self)

        self._hideApplying()

    def discardChanges(self):
        OptionsCategory.discardChanges(self)
        self._setDefaults()

    def cleanup(self):
        if hasattr(self, 'lighting'):
            self.lighting.cleanup()
            del self.lighting
            
        if hasattr(self, 'ppl'):
            self.ppl.cleanup()
            del self.ppl
            
        if hasattr(self, 'hdr'):
            self.hdr.cleanup()
            del self.hdr
            
        if hasattr(self, 'bloom'):
            self.bloom.destroy()
            del self.bloom

        OptionsCategory.cleanup(self)
