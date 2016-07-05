"""

  Filename: QuestPoster.py
  Created by: DecodedLogic (13Nov15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectWaitBar, DGG
from panda3d.core import TextNode

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quest import QuestGlobals

IMAGE_SCALE_LARGE = 0.2
IMAGE_SCALE_SMALL = 0.15
POSTER_WIDTH = 0.7
TEXT_SCALE = QuestGlobals.QPtextScale
TEXT_WORDWRAP = QuestGlobals.QPtextWordwrap

class QuestPoster(DirectFrame):
    notify = directNotify.newCategory('QuestPoster')
    
    def __init__(self, quest, parent = aspect2d, **kw):
        DirectFrame.__init__(self, relief = None)
        self.quest = quest
        
        # Let's begin building the quest poster.
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        questCard = bookModel.find('**/questCard')
        optiondefs = (('relief', None, None),
         ('image', questCard, None),
         ('image_scale', (0.8, 1.0, 0.58), None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        self._deleteCallback = None
        self.questFrame = DirectFrame(parent=self, relief=None)
        self.headline = DirectLabel(parent=self.questFrame, relief=None, text='', text_font=CIGlobals.getMinnieFont(), text_fg=self.normalTextColor, text_scale=0.05, text_align=TextNode.ACenter, text_wordwrap=12.0, textMayChange=1, pos=(0, 0, 0.23))
        self.questInfo = DirectLabel(parent=self.questFrame, relief=None, text='', text_fg=self.normalTextColor, text_scale=TEXT_SCALE, text_align=TextNode.ACenter, text_wordwrap=TEXT_WORDWRAP, textMayChange=1, pos=(0, 0, -0.0625))
        self.rewardText = DirectLabel(parent=self.questFrame, relief=None, text='', text_fg=self.colors['rewardRed'], text_scale=0.0425, text_align=TextNode.ALeft, text_wordwrap=17.0, textMayChange=1, pos=(-0.36, 0, -0.26))
        self.rewardText.hide()
        self.lPictureFrame = DirectFrame(parent=self.questFrame, relief=None, image=bookModel.find('**/questPictureFrame'), image_scale=IMAGE_SCALE_SMALL, text='', text_pos=(0, -0.11), text_fg=self.normalTextColor, text_scale=TEXT_SCALE, text_align=TextNode.ACenter, text_wordwrap=11.0, textMayChange=1)
        self.lPictureFrame.hide()
        self.rPictureFrame = DirectFrame(parent=self.questFrame, relief=None, image=bookModel.find('**/questPictureFrame'), image_scale=IMAGE_SCALE_SMALL, text='', text_pos=(0, -0.11), text_fg=self.normalTextColor, text_scale=TEXT_SCALE, text_align=TextNode.ACenter, text_wordwrap=11.0, textMayChange=1, pos=(0.18, 0, 0.13))
        self.rPictureFrame.hide()
        self.lQuestIcon = DirectFrame(parent=self.lPictureFrame, relief=None, text=' ', text_font=CIGlobals.getSuitFont(), text_pos=(0, -0.03), text_fg=self.normalTextColor, text_scale=0.13, text_align=TextNode.ACenter, text_wordwrap=13.0, textMayChange=1)
        self.lQuestIcon.setColorOff(-1)
        self.rQuestIcon = DirectFrame(parent=self.rPictureFrame, relief=None, text=' ', text_font=CIGlobals.getSuitFont(), text_pos=(0, -0.03), text_fg=self.normalTextColor, text_scale=0.13, text_align=TextNode.ACenter, text_wordwrap=13.0, textMayChange=1)
        self.rQuestIcon.setColorOff(-1)
        self.auxText = DirectLabel(parent=self.questFrame, relief=None, text='', text_scale=QuestGlobals.QPauxText, text_fg=self.normalTextColor, text_align=TextNode.ACenter, textMayChange=1)
        self.auxText.hide()
        self.questProgress = DirectWaitBar(parent=self.questFrame, relief=DGG.SUNKEN, frameSize=(-0.95,
         0.95,
         -0.1,
         0.12), borderWidth=(0.025, 0.025), scale=0.2, frameColor=(0.945, 0.875, 0.706, 1.0), barColor=(0.5, 0.7, 0.5, 1), text='0/0', text_scale=0.19, text_fg=(0.05, 0.14, 0.4, 1), text_align=TextNode.ACenter, text_pos=(0, -0.04), pos=(0, 0, -0.195))
        self.questProgress.hide()
        
        # This is the rotated text on the side.
        self.sideInfo = DirectLabel(parent=self.questFrame, relief=None, text=QuestGlobals.JUST_FOR_FUN, text_fg=(0.0, 0.439, 1.0, 1.0), text_shadow=(0, 0, 0, 1), pos=(-0.2825, 0, 0.2), scale=0.03)
        self.sideInfo.setR(-30)
        self.sideInfo.hide()

        bookModel.removeNode()
        self.laffMeter = None
        return
        
    def destroy(self):
        self._deleteGeoms()
        DirectFrame.destroy(self)

    def _deleteGeoms(self):
        for icon in (self.lQuestIcon, self.rQuestIcon):
            geom = icon['geom']
            if geom:
                if hasattr(geom, 'delete'):
                    geom.delete()