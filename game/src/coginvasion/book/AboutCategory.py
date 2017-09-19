"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AboutCategory.py
@author Brian Lach
@date 2017-03-13

"""

from pandac.PandaModules import PandaSystem

from OptionsCategory import OptionsCategory

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import OnscreenImage, OnscreenText

from src.coginvasion.book.Credits import Credits
from src.coginvasion.globals import CIGlobals

class AboutCategory(OptionsCategory, DirectObject):
    Name = "About"
    AppendOptions = False
    ApplyCancelButtons = False
    WantTitle = False

    def __init__(self, page):
        OptionsCategory.__init__(self, page)
        DirectObject.__init__(self)
        self.defaultLogoScale = 0.75
        self.logo = loader.loadTexture("phase_3/maps/CogInvasion_Logo.png")
        self.logoNode = self.page.book.attachNewNode('logoNode')
        self.logoNode.setScale(self.defaultLogoScale)
        self.logoNode.setPos(0, 0, 0.48)
        self.logoImg = OnscreenImage(image = self.logo, scale = (0.685, 0, 0.325), parent=self.logoNode)
        self.logoImg.setTransparency(True)
        self.creditsScreen = None

        self.gVersionText = OnscreenText(text = "Version {0} (Build {1} : {2})".format(game.version,
                                                                                      game.build, 
                                                                                      game.buildtype),
                                        parent = self.page.book, pos = (0, 0.15, 0.15))
        self.gBuildDate = OnscreenText(text = game.builddate, parent = self.page.book, pos = (0, 0.085, 0.085), scale = 0.06)

        self.eVersionText = OnscreenText(text = "Engine Version {0}".format(PandaSystem.getVersionString()), parent = self.page.book, pos = (0, -0.05))
        self.eBuildDate = OnscreenText(text = PandaSystem.getBuildDate(), parent = self.page.book, pos = (0, -0.115), scale = 0.06)

        self.exitToontown = CIGlobals.makeDefaultBtn("Exit Toontown", pos = (-0.62, -0.62, -0.62), parent = self.page.book, scale = 1.2,
                                                     command = self.page.book.finished, extraArgs = ["exit"], geom_scale = (0.8, 0.8, 0.8))
        
        self.credits = CIGlobals.makeDefaultBtn("Credits", pos = (0.0, 0.5, -0.62), parent = self.page.book, scale = 1.2,
                                                     command = self.rollCredits, geom_scale = (0.8, 0.8, 0.8))
        
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
        del self.defaultLogoScale