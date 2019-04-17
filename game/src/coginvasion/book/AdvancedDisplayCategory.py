"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdvancedDisplayCategory.py
@author Brian Lach
@date September 28, 2017

"""

from ChoiceWidget import ChoiceWidget, INDEX
from OptionsCategory import OptionsCategory

class AdvancedDisplayCategory(OptionsCategory):
    Name = "Graphics"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)

        self.hdr = ChoiceWidget(page, None, pos = (0, 0, 0.47),
            widgetName = "HDR Lighting", settingKeyName = 'hdr', 
            requirement = base.hdr.isSupported)

        self.bloom = ChoiceWidget(page, None, pos = (0, 0, 0.28), 
            widgetName = "Bloom Filter", settingKeyName = 'bloom')
        
        self.waterRefl = ChoiceWidget(page, None, pos = (0, 0, 0.09), 
            widgetName = "Water Reflections", settingKeyName = 'refl')
            
        self.shadows = ChoiceWidget(page, None, pos = (0, 0, -0.1), settingKeyName = 'shadows',
                                 widgetName = "Shadows", choiceTextScale = 0.058, mode = INDEX)
                                 
        self.ao = ChoiceWidget(page, None, pos = (0, 0, -0.29), settingKeyName = 'ao',
                                widgetName = "Ambient Occlusion")
                                
        self.shaders = ChoiceWidget(page, None, pos = (0, 0, -0.48), settingKeyName = 'shaderquality',
                                widgetName = "Shader Quality", mode = INDEX, choiceTextScale = 0.075)
        
        self.widgets = [self.waterRefl, self.hdr, self.bloom, self.shadows, self.ao, self.shaders]

        self.discardChanges()

    def _setDefaults(self):
        for widget in self.widgets:
            widget.reset()

    def discardChanges(self):
        OptionsCategory.discardChanges(self)
        self._setDefaults()

    def cleanup(self):
        for widget in self.widgets:
            widget.cleanup()
        
        self.widgets = []
        del self.waterRefl
        del self.hdr
        del self.bloom
        del self.widgets
        del self.shadows
        del self.ao
        del self.shaders

        OptionsCategory.cleanup(self)
