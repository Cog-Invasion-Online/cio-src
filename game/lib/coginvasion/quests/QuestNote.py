# Filename: QuestNote.py
# Created by:  blach (29Jul15)

from pandac.PandaModules import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectWaitBar, DGG

from lib.coginvasion.globals import CIGlobals
import QuestGlobals

HDR_RETURN = "Return"

class QuestNote(DirectFrame):
    notify = directNotify.newCategory("QuestNote")

    spots = [(-0.45, 0, 0.3), (0.45, 0, 0.3), (0.45, 0, -0.25), (-0.45, 0, -0.25)]
    RewardTextPos = (0, -0.4)
    RewardTextScale = 0.06
    ProgressTextScale = 0.07
    ProgressBarPos = (0, 0, -0.19)
    ProgressTextPos = (0, -0.19)
    TaskInfoTextPos = (0, 0.05)
    NonHeadingTextScale = 0.08
    HeadingTextPos = (0, 0.23)
    HeadingTextScale = 0.1

    def __init__(self, index):
        DirectFrame.__init__(self, scale = 0.5)
        stickergui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        self['image'] = stickergui.find('**/paper_note')
        self['image_scale'] = (1.3, 1, 1)
        self.setPos(self.spots[index])
        self.useProgressBar = False
        self.headingText = OnscreenText(parent = self, text = "", font = CIGlobals.getToonFont(), pos = self.HeadingTextPos, scale = self.HeadingTextScale)
        self.taskInfoText = OnscreenText(parent = self, text= "", font = CIGlobals.getToonFont(), pos = self.TaskInfoTextPos, scale = self.NonHeadingTextScale)
        self.progressText = OnscreenText(parent = self, text = "", font = CIGlobals.getToonFont(), pos = self.ProgressTextPos, scale = self.ProgressTextScale)
        self.progressBar = DirectWaitBar(parent = self, relief = DGG.SUNKEN,
            frameSize=(-0.95, 0.95, -0.1, 0.12),
            borderWidth = (0.025, 0.025),
            scale = 0.4,
            frameColor = (0.945, 0.875, 0.706, 1.0),
            barColor=(0.5, 0.7, 0.5, 1),
            text='0/0',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.19,
            text_fg = (0.05, 0.14, 0.4, 1),
            text_align = TextNode.ACenter,
            text_pos = (0, -0.05), #-0.02
            pos = self.ProgressBarPos)
        self.progressBar.hide()
        self.rewardText = OnscreenText(parent = self, text = "", font = CIGlobals.getToonFont(),
                                       pos = self.RewardTextPos, scale = self.RewardTextScale,
                                       fg = (1, 0.1, 0.1, 1.0))
        self.hide()

    def setHeading(self, text):
        self.headingText.setText(text)

    def setTaskInfo(self, text):
        self.taskInfoText.setText(text)

    def setProgress(self, text, range = 0, value = 0):
        if self.useProgressBar:
            self.progressBar.show()
            self.progressBar['text'] = text
            self.progressBar['range'] = range
            self.progressBar['value'] = value
        else:
            self.progressText['text'] = text

    def setReward(self, text):
        self.rewardText.setText(text)

    def setCompleted(self, value):
        if value:
            self.progressBar.hide()
            self['image_color'] = QuestGlobals.LIGHT_GREEN
