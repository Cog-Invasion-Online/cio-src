"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GeneralCategory.py
@author Brian Lach
@date 2017-09-28

"""

from panda3d.core import WindowProperties

from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget

from src.coginvasion.globals import CIGlobals

class GeneralCategory(OptionsCategory):
    Name = "General"
    
    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.cursor = ChoiceWidget(page, CIGlobals.getSettingsMgr().MouseCursors.keys(), (0, 0, 0.47),
                                   self.__chooseCursor, "Mouse Cursor", 0.05)
                                   
        self.discardChanges()
        
    def _setDefaults(self):
        self.origCursor = CIGlobals.getSettingsMgr().getSetting("cursor")
        self.cursorChoice = self.origCursor
                                   
    def __chooseCursor(self, choice):
        self.cursorChoice = self.cursor.options[choice]
        
    def applyChanges(self):
        self._showApplying()
        
        if (self.cursorChoice != self.origCursor):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("cursor", self.cursorChoice)
            wp = WindowProperties()
            wp.setCursorFilename(CIGlobals.getSettingsMgr().MouseCursors[self.cursorChoice])
            base.win.requestProperties(wp)
            
        self._setDefaults()
        self._hideApplying()
        
    def discardChanges(self):
        self._setDefaults()
        self.cursor.goto(self.cursor.options.index(self.cursorChoice.title()))
        
    def cleanup(self):
        if hasattr(self, 'cursor'):
            self.cursor.cleanup()
            del self.cursor
            
        del self.origCursor
        del self.cursorChoice
        
        OptionsCategory.cleanup(self)