# Filename: FinalScoreGUI.py
# Created by:  blach (09Jul15)

from panda3d.core import TextNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DGG, DirectFrame, OnscreenImage, OnscreenText

from src.coginvasion.globals import CIGlobals
from FinalScore import FinalScore

class FinalScoreGUI:
    notify = directNotify.newCategory("FinalScoreGUI")

    def __init__(self):
        self.finalScoreBg = None
        self.finalScoreTitle = None
        self.finalScoreNameLbl = None
        self.finalScorePointLbl = None
        self.finalScoreContainer = None
        self.finalScores = []

    def load(self):
        font = CIGlobals.getToonFont()
        box = DGG.getDefaultDialogGeom()
        self.finalScoreContainer = DirectFrame()
        self.finalScoreBg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4), parent = self.finalScoreContainer)
        self.finalScoreTitle = OnscreenText(text = "Waiting for final scores...", pos = (0, 0.5, 0), font = font, scale = (0.12), parent = self.finalScoreContainer)
        self.finalScoreNameLbl = OnscreenText(text = "", scale = 0.095, pos = (-0.85, 0.3, 0), font = font, align = TextNode.ALeft, parent = self.finalScoreContainer)
        self.finalScorePointLbl = OnscreenText(text = "", scale = 0.095, pos = (0.85, 0.3, 0), font = font, align = TextNode.ARight, parent = self.finalScoreContainer)
        self.finalScoreContainer.hide()
        self.finalScoreContainer.setBin('gui-popup', 60)
        del font
        del box

    def unload(self):
        if self.finalScoreContainer:
            self.finalScoreContainer.destroy()
            self.finalScoreContainer = None
        if self.finalScoreBg:
            self.finalScoreBg.destroy()
            self.finalScoreBg = None
        if self.finalScoreTitle:
            self.finalScoreTitle.destroy()
            self.finalScoreTitle = None
        if self.finalScoreNameLbl:
            self.finalScoreNameLbl.destroy()
            self.finalScoreNameLbl = None
        if self.finalScorePointLbl:
            self.finalScorePointLbl.destroy()
            self.finalScorePointLbl = None

    def showFinalScores(self):
        self.finalScoreContainer.show()
        base.transitions.fadeScreen(0.5)

    def hideFinalScores(self):
        base.transitions.noTransitions()
        self.finalScoreContainer.hide()

    def handleFinalScores(self, avIdList, scoreList):
        for avId in avIdList:
            score = scoreList[avIdList.index(avId)]
            scoreObj = FinalScore(avId, score)
            self.finalScores.append(scoreObj)
        self.finalScores.sort(key=lambda x: x.score, reverse = True)
        for scoreObj in self.finalScores:
            name = base.cr.doId2do.get(scoreObj.avId).getName()
            self.finalScoreNameLbl['text'] += name + "\n"
            self.finalScorePointLbl['text'] += str(scoreObj.score) + " Points\n"
        self.finalScoreTitle['text'] = "Final Scores"
