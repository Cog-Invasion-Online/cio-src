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
            desc = 'Toggles basic per-vertex lighting.\nShould not affect performance.', settingKeyName = 'lighting')
        
        self.ppl = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.24), self.__updatePPL, "Per-Pixel Lighting",
            desc = 'Toggles more advanced per-pixel shaders.\nRequires Lighting to be enabled.\nAffects performance.', settingKeyName = 'ppl')
        
        self.waterRefl = ChoiceWidget(page, ["Off", "Low", "Medium", "High", "Ultra"], (0, 0, 0.01), self.__updateWater, "Water Reflections",
            desc = 'Sets the resolution of water reflection textures around the game.\nMay affect performance.', settingKeyName = 'refl')
        
        self.hdr = ChoiceWidget(page, ["None", "Ver. 1", "Ver. 2", "Ver. 3"], (0, 0, -0.22),
            self.__updateHDR, "HDR Tone Mapping", desc = 'Increases range of colors on screen.\nRequires Per-Pixel Lighting to be enabled.',
            settingKeyName = 'hdr')
        
        self.bloom = ChoiceWidget(page, ["Off", "On"], (0, 0, -0.45), self.__updateBloom, "Bloom Filter",
            desc = "Increases range of brightness by glowing objects that are very bright.\nAffects performance.", settingKeyName = 'bloom')
        
        self.widgets = [self.lighting, self.ppl, self.waterRefl, self.hdr, self.bloom]

        self.discardChanges()
        
    def __updateLighting(self, useLighting):
        game.uselighting = useLighting
        
    def __updatePPL(self, ppl):
        if ppl:
            render.setShaderAuto()
        else:
            render.setShaderOff()
            
    def __updateWater(self, quality):
        resolution = CIGlobals.getSettingsMgr().ReflectionQuality.get(quality)
        print resolution
        base.waterReflectionMgr.handleResolutionUpdate(resolution)
            
    def __updateHDR(self, hdr):
        versionIndex = self.hdr.options.index(hdr)
        CIGlobals.getSettingsMgr().applyHdr(versionIndex)
            
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
