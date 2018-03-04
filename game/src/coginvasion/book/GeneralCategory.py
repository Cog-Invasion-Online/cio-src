"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GeneralCategory.py
@author Brian Lach
@date September 28, 2017

"""

from panda3d.core import WindowProperties, LightRampAttrib

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
        self.ppl = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.13), self.__choosePpl, "Per-Pixel Lighting")
        self.hdr = ChoiceWidget(page, ["None", "Ver. 1", "Ver. 2", "Ver. 3"], (0, 0, -0.04),
                                self.__chooseHdr, "HDR Tone Mapping")
        self.refl = ChoiceWidget(page, CIGlobals.getSettingsMgr().ReflectionQuality.keys(), (0, 0, -0.21),
                                 self.__chooseRefl, "Reflection Quality")
                                   
        self.discardChanges()
        
    def _setDefaults(self):
        self.origCursor = CIGlobals.getSettingsMgr().getSetting("cursor")
        self.cursorChoice = self.origCursor
        
        self.origLighting = CIGlobals.getSettingsMgr().getSetting("lighting")
        self.lightingChoice = self.origLighting
        
        self.origHdr = CIGlobals.getSettingsMgr().getSetting("hdr")
        self.hdrChoice = self.origHdr
        
        self.origPpl = CIGlobals.getSettingsMgr().getSetting("ppl")
        self.pplChoice = self.origPpl

        self.origRefl = CIGlobals.getSettingsMgr().getSetting("refl")
        self.reflChoice = self.origRefl
        
    def __choosePpl(self, choice):
        self.pplChoice = bool(choice)
        
    def __chooseHdr(self, choice):
        self.hdrChoice = choice
                                   
    def __chooseCursor(self, choice):
        self.cursorChoice = self.cursor.options[choice]
        
    def __chooseLighting(self, choice):
        self.lightingChoice = bool(choice)

    def __chooseRefl(self, choice):
        self.reflChoice = self.refl.options[choice]
        
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
            
        if (self.hdrChoice != self.origHdr):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("hdr", self.hdrChoice)
            CIGlobals.getSettingsMgr().applyHdr(self.hdrChoice)
            
        if (self.pplChoice != self.origPpl):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("ppl", self.pplChoice)
            if self.pplChoice:
                render.setShaderAuto()
            else:
                render.setShaderOff()

        if (self.reflChoice != self.origRefl):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("refl", self.reflChoice)
            
        self._setDefaults()
        self._hideApplying()
        
    def discardChanges(self):
        self._setDefaults()
        self.cursor.goto(self.cursor.options.index(self.cursorChoice.title()))
        self.lighting.goto(int(self.lightingChoice))
        self.hdr.goto(self.hdrChoice)
        self.ppl.goto(int(self.pplChoice))
        self.refl.goto(self.refl.options.index(self.reflChoice))
        
    def cleanup(self):
        if hasattr(self, 'cursor'):
            self.cursor.cleanup()
            del self.cursor
            
        if hasattr(self, 'lighting'):
            self.lighting.cleanup()
            del self.lighting
            
        if hasattr(self, 'hdr'):
            self.hdr.cleanup()
            del self.hdr
            
        if hasattr(self, 'ppl'):
            self.ppl.cleanup()
            del self.ppl

        if hasattr(self, "refl"):
            self.refl.cleanup()
            del self.refl
            
        del self.origCursor
        del self.cursorChoice
        
        del self.lightingChoice
        del self.origLighting
        
        del self.hdrChoice
        del self.origHdr
        
        del self.pplChoice
        del self.origPpl

        del self.reflChoice
        del self.origRefl
        
        OptionsCategory.cleanup(self)