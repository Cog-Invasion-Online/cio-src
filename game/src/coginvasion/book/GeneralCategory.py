"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GeneralCategory.py
@author Brian Lach
@date September 28, 2017

"""

from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget
from ChoiceWidget import MULTICHOICE

class GeneralCategory(OptionsCategory):
    Name = "General"
    
    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.cursor = ChoiceWidget(page, None, pos = (0, 0, 0.47),
            widgetName = "Mouse Cursor", choiceTextScale = 0.05, 
            settingKeyName = 'cursor', mode = MULTICHOICE)
        
        self.fps = ChoiceWidget(page, None, pos = (0, 0, 0.3), 
            widgetName = 'FPS Meter', settingKeyName = 'fps')
        
        self.widgets = [self.cursor, self.fps]
        
        self.discardChanges()
        
    def cleanup(self):
        for widget in self.widgets:
            widget.cleanup()
        
        self.widgets = []
        del self.cursor
        del self.fps
        del self.widgets
        
        OptionsCategory.cleanup(self)
