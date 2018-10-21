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
        
        self.lighting = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.47), self.__updateLighting, "Lighting",
            desc = 'Toggles basic per-vertex lighting.\nShould not affect performance.', settingKeyName = 'lighting')
        
        self.ppl = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.24), self.__updatePPL, "Per-Pixel Lighting",
            desc = 'Toggles more advanced per-pixel shaders.\nRequires Lighting to be enabled.\nAffects performance.', settingKeyName = 'ppl')

        self.hdr = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.01),
            self.__updateHDR, "HDR Lighting", desc = 'Increases perceived range of colors and brightness on screen.\nRequires Per-Pixel Lighting to be enabled.\nRequires at least OpenGL 4.3.',
            settingKeyName = 'hdr', requirement = base.hdr.isSupported)

        self.bloom = ChoiceWidget(page, ["Off", "On"], (0, 0, -0.22), self.__updateBloom, "Bloom Filter",
            desc = "Increases perceived brightness by glowing objects that are very bright.\nAffects performance.", settingKeyName = 'bloom')
        
        self.waterRefl = ChoiceWidget(page, ["Off", "Low", "Medium", "High", "Ultra"], (0, 0, -0.45), self.__updateWater, "Water Reflections",
            desc = 'Sets the resolution of water reflection textures around the game.\Affects performance.', settingKeyName = 'refl')
        
        self.widgets = [self.lighting, self.ppl, self.waterRefl, self.hdr, self.bloom]

        self.discardChanges()
        
    def __updateLighting(self, useLighting):
        metadata.USE_LIGHTING = useLighting
        
    def __updatePPL(self, ppl):
        if ppl:
            render.setShaderAuto()
        else:
            render.setShaderOff(1)
            
    def __updateWater(self, quality):
        resolution = CIGlobals.getSettingsMgr().ReflectionQuality.get(quality)
        base.waterReflectionMgr.handleResolutionUpdate(resolution)

    def __handleBadHdrAck(self, value):
        self.cleanupBadHdrDlg()
            
    def __updateHDR(self, hdr):
        #if hdr and not base.hdr.isSupported():
        #    self.cleanupBadHdrDlg()

        #    self.badHdrDlg = GlobalDialog(
        #        ("Sorry, but HDR is not supported by your graphics hardware.\n\n" +
        #         "Minimum OpenGL requirement: 4.3\n" +
        #         "Your OpenGL version: {0}".format(base.win.getGsg().getDriverVersion())),
        #         style = Ok, doneEvent = 'badHdrAck')
        #    self.acceptOnce('badHdrAck', self.__handleBadHdrAck)
        #    self.badHdrDlg.show()

        #    return

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
        del self.lighting
        del self.ppl
        del self.waterRefl
        del self.hdr
        del self.bloom
        del self.widgets

        OptionsCategory.cleanup(self)
