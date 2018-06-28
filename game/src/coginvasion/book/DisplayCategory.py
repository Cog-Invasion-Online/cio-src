"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DisplayCategory.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import TextNode, WindowProperties, AntialiasAttrib

from direct.gui.DirectGui import DirectCheckButton, OnscreenText

from src.coginvasion.globals import CIGlobals
from OptionsCategory import OptionsCategory
from ChoiceWidget import ChoiceWidget
from ChoiceWidget import DEGREE

class DisplayCategory(OptionsCategory):
    Name = "Display"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)

        self.reso = ChoiceWidget(page, ["640x480", "800x600", "1024x768", "1280x720", "1360x768", "1366x768", "1600x900", "1920x1080"],
            (0, 0, 0.47), self.__updateResolution, "Resolution", 0.05, settingKeyName = 'resolution',
            desc = "Configures the screen resolution.")

        self.masprText = OnscreenText(text = "Maintain aspect ratio?", scale = 0.045, parent = page.book, align = TextNode.ALeft, pos = (-0.7, 0.4))
        self.maspr = DirectCheckButton(scale = 0.07, parent = page.book, pos = (-0.19, 0, 0.41), command = self.__toggleMaspr)

        self.fs = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.24), self.__updateFullscreen, "Fullscreen",
            desc = "Toggles fullscreen mode.", settingKeyName = 'fullscreen')

        self.aa = ChoiceWidget(page, ["None", "x2", "x4", "x8", "x16"], (0, 0, 0.01), self.__updateAA, "Antialiasing",
            desc = "Smooths out jagged edges on screen.\nAffects performance.",
            settingKeyName = 'aa', mode = DEGREE)

        self.af = ChoiceWidget(page, ["None", "x2", "x4", "x8", "x16"], (0, 0, -0.22), widgetName = "Anisotropic Filtering",
            desc = "Improves the quality of textures viewed from an angle.\nAffects performance.",
            settingKeyName = 'af', mode = DEGREE)
        
        #self.shadows = ChoiceWidget(page, ["Low", "Medium", "High", "Ultra High"], (0, 0, -0.21), 
        #                         self.__chooseShadowQuality, "Shadows", 0.06)
        
        self.vsync = ChoiceWidget(page, ["Off", "On"], (0, 0, -0.45), widgetName = "V-Sync",
            desc = "Reduces screen tearing by limiting frame rate to your monitor's refresh rate.\nThis is really only effective in Fullscreen mode.", settingKeyName = 'vsync')
        
        self.widgets = [self.fs, self.aa, self.af, self.reso, self.vsync]

        self.discardChanges()

    def _setDefaults(self):
        self.origMaspr = CIGlobals.getSettingsMgr().getSetting("maspr")
        self.masprChoice = self.origMaspr

    def __toggleMaspr(self, choice):
        if choice:
            # maintain aspect ratio on!
            self.masprChoice = True
        else:
            # maintain aspect ratio off!
            self.masprChoice = False
            
    def __updateAA(self, degree):
        if degree == 0:
            render.clearAntialias()
            aspect2d.clearAntialias()
        else:
            render.setAntialias(AntialiasAttrib.MMultisample)
            aspect2d.setAntialias(AntialiasAttrib.MMultisample)
            
    def __updateFullscreen(self, flag):
        wp = WindowProperties()
        wp.setFullscreen(flag)
        base.win.requestProperties(wp)
        
    def __updateResolution(self, resTuple):
        wp = WindowProperties()
        wp.setSize(resTuple[0], resTuple[1])
        base.win.requestProperties(wp)

    def applyChanges(self):
        self._showApplying()

        OptionsCategory.applyChanges(self)

        if (self.masprChoice != self.origMaspr):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("maspr", self.masprChoice)
            if not (self.masprChoice):
                base.doOldToontownRatio()
            else:
                base.doRegularRatio()

        self._hideApplying()

    def discardChanges(self):
        OptionsCategory.discardChanges(self)
        self._setDefaults()

        self.maspr['indicatorValue'] = self.masprChoice

    def cleanup(self):
        if hasattr(self, 'reso'):
            self.reso.cleanup()
            del self.reso

        if hasattr(self, 'fs'):
            self.fs.cleanup()
            del self.fs

        if hasattr(self, 'aa'):
            self.aa.cleanup()
            del self.aa

        if hasattr(self, 'af'):
            self.af.cleanup()
            del self.af

        if hasattr(self, 'masprText'):
            self.masprText.destroy()
            del self.masprText

        if hasattr(self, 'maspr'):
            self.maspr.destroy()
            del self.maspr
            
        if hasattr(self, 'vsync'):
            self.vsync.cleanup()
            del self.vsync

        del self.origMaspr
        del self.masprChoice

        OptionsCategory.cleanup(self)
