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

class DisplayCategory(OptionsCategory):
    Name = "Display"

    def __init__(self, page):
        OptionsCategory.__init__(self, page)

        self.reso = ChoiceWidget(page, ["640x480", "800x600", "1024x768", "1280x720", "1360x768", "1366x768", "1600x900", "1920x1080"],
                                 (0, 0, 0.47), self.__chooseReso, "Resolution", 0.05)

        self.masprText = OnscreenText(text = "Maintain aspect ratio?", scale = 0.045, parent = page.book, align = TextNode.ALeft, pos = (-0.7, 0.4))
        self.maspr = DirectCheckButton(scale = 0.07, parent = page.book, pos = (-0.19, 0, 0.41), command = self.__toggleMaspr)

        self.fs = ChoiceWidget(page, ["Off", "On"], (0, 0, 0.25), self.__chooseFS, "Fullscreen")

        self.aa = ChoiceWidget(page, ["None", "x2", "x4", "x8", "x16"], (0, 0, 0.07), self.__chooseAA, "Antialiasing")

        self.af = ChoiceWidget(page, ["None", "x2", "x4", "x8", "x16"], (0, 0, -0.11), self.__chooseAF, "Anisotropic Filtering")
        
        self.shadows = ChoiceWidget(page, ["Low", "Medium", "High", "Ultra High"], (0, 0, -0.29), 
                                 self.__chooseShadowQuality, "Shadows", 0.06)

        self.discardChanges()

    def _setDefaults(self):
        self.origReso = CIGlobals.getSettingsMgr().getSetting("resolution")
        self.resoChoice = self.origReso
        self.resoChoiceStr = str(self.resoChoice[0]) + "x" + str(self.resoChoice[1])

        self.origFS = CIGlobals.getSettingsMgr().getSetting("fullscreen")
        self.fsChoice = self.origFS

        self.origAA = CIGlobals.getSettingsMgr().getSetting("aa")
        self.aaChoice = self.origAA

        self.origAF = CIGlobals.getSettingsMgr().getSetting("af")
        self.afChoice = self.origAF

        self.origMaspr = CIGlobals.getSettingsMgr().getSetting("maspr")
        self.masprChoice = self.origMaspr
        
        self.origShadows = CIGlobals.getSettingsMgr().getSetting("shadows")
        self.shadowChoice = self.origShadows

    def __toggleMaspr(self, choice):
        if choice:
            # maintain aspect ratio on!
            self.masprChoice = True
        else:
            # maintain aspect ratio off!
            self.masprChoice = False

    def __chooseReso(self, choice):
        op = self.reso.options[choice]
        spl = op.split('x')
        w = int(spl[0])
        h = int(spl[1])
        self.resoChoice = (w, h)
        self.resoChoiceStr = op

    def __chooseFS(self, choice):
        self.fsChoice = bool(choice)

    def __chooseAA(self, choice):
        if choice == 0:
            degree = 0
        else:
            op = self.aa.options[choice]
            degree = int(op.strip("x"))
            print "chose aa degree", degree

        self.aaChoice = degree

    def __chooseAF(self, choice):
        if choice == 0:
            degree = 0
        else:
            op = self.af.options[choice]
            degree = int(op.strip("x"))
            print "chose af degree", degree

        self.afChoice = degree
        
    def __chooseShadowQuality(self, choice):
        self.shadowChoice = choice

    def applyChanges(self):
        self._showApplying()

        if (self.resoChoice != self.origReso):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("resolution", self.resoChoice)
            wp = WindowProperties()
            wp.setSize(self.resoChoice[0], self.resoChoice[1])
            base.win.requestProperties(wp)

        if (self.fsChoice != self.origFS):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("fullscreen", self.fsChoice)
            wp = WindowProperties()
            wp.setFullscreen(self.fsChoice)
            base.win.requestProperties(wp)

        if (self.aaChoice != self.origAA):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("aa", self.aaChoice)

            if (self.aaChoice == 0):
                render.clearAntialias()
                aspect2d.clearAntialias()
            else:
                render.setAntialias(AntialiasAttrib.MMultisample)
                aspect2d.setAntialias(AntialiasAttrib.MMultisample)

        if (self.afChoice != self.origAF):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("af", self.afChoice)

        if (self.masprChoice != self.origMaspr):
            CIGlobals.getSettingsMgr().updateAndWriteSetting("maspr", self.masprChoice)
            if not (self.masprChoice):
                base.doOldToontownRatio()
            else:
                base.doRegularRatio()
                
        if (self.shadowChoice != self.origShadows):
            # Update the shadow quality choice.
            CIGlobals.getSettingsMgr().updateAndWriteSetting("shadows", self.shadowChoice)

        self._setDefaults()

        self._hideApplying()

    def discardChanges(self):
        self._setDefaults()

        self.reso.goto(self.reso.options.index(self.resoChoiceStr))
        self.fs.goto(int(self.fsChoice))

        if (self.aaChoice == 0):
            self.aa.goto(0)
        else:
            self.aa.goto(self.aa.options.index("x" + str(self.aaChoice)))

        if (self.afChoice == 0):
            self.af.goto(0)
        else:
            self.af.goto(self.af.options.index("x" + str(self.afChoice)))

        self.maspr['indicatorValue'] = self.masprChoice

        self.shadows.goto(int(self.shadowChoice))

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
            
        if hasattr(self, 'shadows'):
            self.shadows.cleanup()
            del self.shadows

        if hasattr(self, 'masprText'):
            self.masprText.destroy()
            del self.masprText

        if hasattr(self, 'maspr'):
            self.maspr.destroy()
            del self.maspr

        del self.origMaspr
        del self.masprChoice

        del self.origAA
        del self.aaChoice

        del self.origAF
        del self.afChoice

        del self.origFS
        del self.fsChoice

        del self.origReso
        del self.resoChoice
        del self.resoChoiceStr
        
        del self.origShadows
        del self.shadowChoice
        OptionsCategory.cleanup(self)
