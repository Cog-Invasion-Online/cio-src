"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ChoiceWidget.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import TextNode

from direct.gui.DirectGui import DirectFrame, OnscreenText, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

DISABLED_COLOR = (0.45, 0.45, 0.45, 1)

class ChoiceWidget(DirectFrame):
    notify = directNotify.newCategory("ChoiceWidget")

    def __init__(self, page, options, pos = (0, 0, 0), command = None, widgetname = "", choiceTextScale = 0.08):
        self.options = options
        self.command = command
        self.currentChoiceIndex = 0
        bg = loader.loadModel('phase_3/models/gui/ChatPanel.bam')
        DirectFrame.__init__(self, parent = page.book, pos = pos)

        self.selFrame = DirectFrame(pos = (0.4, 0, 0), image = bg, relief = None, image_scale = (0.22, 0.11, 0.11), image_pos = (-0.107, 0.062, 0.062), parent = self)
        self.choiceText = OnscreenText(text = "Hello!", align = TextNode.ACenter, parent = self.selFrame, pos = (0, -0.01), scale = choiceTextScale)
        self.fwdBtn = CIGlobals.makeDirectionalBtn(1, self.selFrame, pos = (0.2, 0, 0), command = self.__goFwd)
        self.bckBtn = CIGlobals.makeDirectionalBtn(0, self.selFrame, pos = (-0.2, 0, 0), command = self.__goBck)

        self.lbl = OnscreenText(text = widgetname + ":", pos = (-0.7, 0, 0), align = TextNode.ALeft, parent = self)

        self.initialiseoptions(ChoiceWidget)

        self.goto(0)

        bg.detachNode()
        del bg

    def cleanup(self):
        if hasattr(self, 'choiceText'):
            self.choiceText.destroy()
            del self.choiceText
        if hasattr(self, 'fwdBtn'):
            self.fwdBtn.destroy()
            del self.fwdBtn
        if hasattr(self, 'bckBtn'):
            self.bckBtn.destroy()
            del self.bckBtn
        if hasattr(self, 'lbl'):
            self.lbl.destroy()
            del self.lbl
        if hasattr(self, 'selFrame'):
            self.selFrame.destroy()
            del self.selFrame
        del self.options
        del self.command
        del self.currentChoiceIndex
        self.destroy()

    def goto(self, index):
        self.currentChoiceIndex = index
        self.updateDirectionalBtns()
        self.__setCurrentData(False)

    def __setCurrentData(self, doCmd = True):
        self.choiceText.setText(self.options[self.currentChoiceIndex])
        if (doCmd):
            self.command(self.currentChoiceIndex)

    def updateDirectionalBtns(self):
        self.fwdBtn['state'] = DGG.NORMAL
        self.bckBtn['state'] = DGG.NORMAL
        self.fwdBtn.setColorScale(1, 1, 1, 1)
        self.bckBtn.setColorScale(1, 1, 1, 1)
        if self.currentChoiceIndex == 0:
            self.bckBtn['state'] = DGG.DISABLED
            self.bckBtn.setColorScale(DISABLED_COLOR)
        elif self.currentChoiceIndex == len(self.options) - 1:
            self.fwdBtn['state'] = DGG.DISABLED
            self.fwdBtn.setColorScale(DISABLED_COLOR)

    def __goFwd(self):
        if self.currentChoiceIndex < len(self.options) - 1:
            self.currentChoiceIndex += 1
            self.__setCurrentData()
        self.updateDirectionalBtns()

    def __goBck(self):
        if self.currentChoiceIndex > 0:
            self.currentChoiceIndex -= 1
            self.__setCurrentData()
        self.updateDirectionalBtns()
