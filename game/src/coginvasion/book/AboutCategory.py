"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AboutCategory.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import PandaSystem

from OptionsCategory import OptionsCategory

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import OnscreenImage, OnscreenText

from src.coginvasion.book.Credits import Credits
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gui.Dialog import GlobalDialog, YesCancel

class AboutCategory(OptionsCategory, DirectObject):
    Name = "About"
    AppendOptions = False
    ApplyCancelButtons = False
    WantTitle = False

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        DirectObject.__init__(self)
        
        self.logoNode, self.logoImg = CIGlobals.getLogoImage(self.page.book, 0.75, (0, 0, 0.48))
        
        self.creditsScreen = None

        self.exitConfirmDlg = None
        
        font = CIGlobals.getToonLogoFont()

        self.gVersionText = OnscreenText(metadata.getBuildInformation(),
                                        parent = self.page.book, pos = (0, 0.15, 0.15), font = font, fg = (1, 1, 1, 1))
        self.gBuildDate = OnscreenText(text = metadata.BUILD_DATE, parent = self.page.book, pos = (0, 0.085, 0.085), scale = 0.06, font = font, fg = (1, 1, 1, 1))

        self.eVersionText = OnscreenText(text = "Engine Version {0}".format(PandaSystem.getVersionString()), parent = self.page.book, pos = (0, -0.05), font = font, fg = (1, 1, 1, 1))
        self.eBuildDate = OnscreenText(text = PandaSystem.getBuildDate(), parent = self.page.book, pos = (0, -0.115), scale = 0.06, font = font, fg = (1, 1, 1, 1))

        self.exitToontown = CIGlobals.makeDefaultBtn("Exit Toontown", pos = (-0.62, -0.62, -0.62), parent = self.page.book, scale = 1.2,
                                                     command = self.showConfirmDlg, geom_scale = (0.8, 0.8, 0.8))
        
        self.credits = CIGlobals.makeDefaultBtn("Credits", pos = (0.0, 0.5, -0.62), parent = self.page.book, scale = 1.2,
                                                     command = self.rollCredits, geom_scale = (0.8, 0.8, 0.8))

    def showConfirmDlg(self):
        self.hideConfirmDlg()
        self.acceptOnce('exitToontownChoice', self.__handleExitToontownChoice)
        self.exitConfirmDlg = GlobalDialog('Exit Toontown?', doneEvent = 'exitToontownChoice', style = YesCancel)
        self.exitConfirmDlg.show()

    def hideConfirmDlg(self):
        self.ignore('exitToontownChoice')
        if self.exitConfirmDlg:
            self.exitConfirmDlg.cleanup()
            self.exitConfirmDlg = None
    
    def __handleExitToontownChoice(self):
        if self.exitConfirmDlg.getValue():
            self.page.book.finished("exit")
        self.hideConfirmDlg()
        
    def rollCredits(self):
        base.muteMusic()
        base.muteSfx()
        base.transitions.fadeOut(1.0)
        base.taskMgr.doMethodLater(1.1, self.__rollCreditsTask, "doRollCredits")

    def __rollCreditsTask(self, task):
        self.creditsScreen = Credits()
        self.creditsScreen.setup()
        base.localAvatar.toggleAspect2d()
        self.page.book.hide()
        self.acceptOnce('credits-Complete', self.showBook)
        base.transitions.fadeIn(1.0)
        return task.done
        
    def showBook(self):
        self.page.book.show()
        base.localAvatar.toggleAspect2d()

    def cleanup(self):
        self.hideConfirmDlg()
        if hasattr(self, 'gVersionText'):
            self.gVersionText.destroy()
            del self.gVersionText
        if hasattr(self, 'gBuildDate'):
            self.gBuildDate.destroy()
            del self.gBuildDate
        if hasattr(self, 'eVersionText'):
            self.eVersionText.destroy()
            del self.eVersionText
        if hasattr(self, 'eBuildDate'):
            self.eBuildDate.destroy()
            del self.eBuildDate
        if hasattr(self, 'logoImg'):
            self.logoImg.destroy()
            del self.logoImg
        if hasattr(self, 'logoNode'):
            self.logoNode.removeNode()
            del self.logoNode
        if hasattr(self, 'exitToontown'):
            self.exitToontown.destroy()
            del self.exitToontown
        if hasattr(self, 'credits'):
            self.credits.destroy()
            del self.credits
        if hasattr(self, 'creditsScreen'):
            self.creditsScreen = None
            del self.creditsScreen
