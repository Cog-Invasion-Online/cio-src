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

from src.coginvasion.globals import CIGlobals

class GeneralCategory(OptionsCategory):
    Name = "General"
    
    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        
        self.cursor = ChoiceWidget(page, CIGlobals.getSettingsMgr().MouseCursors.keys(), (0, 0, 0.47),
                                   self.__chooseCursor, "Mouse Cursor", 0.05)
        self.lighting = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.3), self.__chooseLighting, "Lighting")
                                   
        self.discardChanges()
        
    def _setDefaults(self):
        self.origCursor = CIGlobals.getSettingsMgr().getSetting("cursor")
        self.cursorChoice = self.origCursor
        
        self.origLighting = CIGlobals.getSettingsMgr().getSetting("lighting")
        self.lightingChoice = self.origLighting
                                   
    def __chooseCursor(self, choice):
        self.cursorChoice = self.cursor.options[choice]
        
    def __chooseLighting(self, choice):
        self.lightingChoice = bool(choice)
        
    def applyChanges(self):
        self._showApplying()
        
        if (self.cursorChoice != self.origCursor):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("cursor", self.cursorChoice)
            wp = WindowProperties()
            wp.setCursorFilename(CIGlobals.getSettingsMgr().MouseCursors[self.cursorChoice])
            base.win.requestProperties(wp)
            
        if (self.lightingChoice != self.origLighting):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("lighting", self.lightingChoice)
            game.uselighting = self.lightingChoice
            
        self._setDefaults()
        self._hideApplying()
        
    def discardChanges(self):
        self._setDefaults()
        self.cursor.goto(self.cursor.options.index(self.cursorChoice.title()))
        self.lighting.goto(int(self.lightingChoice))
        
    def cleanup(self):
        if hasattr(self, 'cursor'):
            self.cursor.cleanup()
            del self.cursor
            
        if hasattr(self, 'lighting'):
            self.lighting.cleanup()
            del self.lighting
            
        del self.origCursor
        del self.cursorChoice
        
        del self.lightingChoice
        del self.origLighting
        
        OptionsCategory.cleanup(self)