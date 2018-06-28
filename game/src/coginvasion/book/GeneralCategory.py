"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GeneralCategory.py
@author Brian Lach
@date September 28, 2017

"""

from panda3d.core import WindowProperties

from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget
from ChoiceWidget import MULTICHOICE

from src.coginvasion.globals import CIGlobals

class GeneralCategory(OptionsCategory):
    Name = "General"
    
    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.cursor = ChoiceWidget(page, CIGlobals.getSettingsMgr().MouseCursors.keys(), (0, 0, 0.47),
            self.__updateCursor, "Mouse Cursor", 0.05, desc = "Updates the game's cursor.", 
            settingKeyName = 'cursor', mode = MULTICHOICE)
        
        self.fps = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.3), self.__updateFPSMeter, 'FPS Meter', 
            desc = 'Enables/Disables an FPS meter in the top-right\n corner of the screen.', settingKeyName = 'fps')
        
        self.widgets = [self.cursor, self.fps]
        
        self.discardChanges()
            
    def __updateCursor(self, cursor):
        wp = WindowProperties()
        wp.setCursorFilename(CIGlobals.getSettingsMgr().MouseCursors[cursor])
        base.win.requestProperties(wp)
            
    def __updateFPSMeter(self, wantMeter):
        base.setFrameRateMeter(wantMeter)
        
    def applyChanges(self):
        self._showApplying()
        
        for widget in self.widgets:
            widget.saveSetting()

        self._hideApplying()
        
    def cleanup(self):
        if hasattr(self, 'cursor'):
            self.cursor.cleanup()
            del self.cursor
            
        if hasattr(self, 'fps'):
            self.fps.cleanup()
            del self.fps
        
        OptionsCategory.cleanup(self)