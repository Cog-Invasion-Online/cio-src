"""

  Filename: QuestPoster.py
  Created by: DecodedLogic (13Nov15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectWaitBar, DGG
from panda3d.core import TextNode, Vec4, Point3

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quest import QuestGlobals, RewardType, CogObjective,\
    VisitNPCObjective
from lib.coginvasion.cog import SuitBank
from lib.coginvasion.gui.LaffOMeter import LaffOMeter
from lib.coginvasion.quest.CogObjective import CogObjective
from lib.coginvasion.cog.Head import Head
from lib.coginvasion.toon.ToonHead import ToonHead

POSTER_WIDTH = 0.7
TEXT_SCALE = QuestGlobals.QPtextScale
TEXT_WORDWRAP = QuestGlobals.QPtextWordwrap

class QuestPoster(DirectFrame):
    notify = directNotify.newCategory('QuestPoster')
    
    def __init__(self, quest, parent = aspect2d, **kw):
        self.quest = quest
        
        # Let's begin building the quest poster.
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        questCard = bookModel.find('**/questCard')
        optiondefs = (('relief', None, None),
         ('image', questCard, None),
         ('image_scale', (0.8, 1.0, 0.58), None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, relief = None)
        self.initialiseoptions(QuestPoster)
    
        self._deleteCallback = None
        self.questFrame = DirectFrame(parent = self, relief = None)
        
        # Quest title text
        self.headline = DirectLabel(parent = self.questFrame, relief = None, 
            text = self.quest.getName(), 
            text_font = CIGlobals.getMinnieFont(), 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = 0.05, 
            text_align = TextNode.ACenter, 
            text_wordwrap = 25.0, textMayChange = 1, 
        pos = (0, 0, 0.23))
        
        # Quest information
        self.questInfo = DirectLabel(parent = self.questFrame, relief = None, 
            text = '',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = 0.04, 
            text_align = TextNode.ACenter, 
            text_wordwrap = TEXT_WORDWRAP, 
            textMayChange = 1, 
        pos = (QuestGlobals.DEFAULT_INFO_POS))
        self.questInfo.hide()
        
        self.questInfo02 = DirectLabel(parent = self.questFrame, relief = None, 
            text = '',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = 0.04, 
            text_align = TextNode.ACenter, 
            text_wordwrap = TEXT_WORDWRAP, 
            textMayChange = 1, 
        pos = (QuestGlobals.DEFAULT_INFO2_POS))
        self.questInfo02.hide()
        
        self.locationInfo = DirectLabel(parent = self.questFrame, relief = None, 
            text = 'N/A',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = TEXT_SCALE, 
            text_align = TextNode.ACenter, 
            text_wordwrap = TEXT_WORDWRAP, 
            textMayChange = 1, 
        pos = (0, 0, -0.115))
        self.locationInfo.hide()
        
        # C'mon Brian this one is obvious
        self.rewardText = DirectLabel(parent = self.questFrame, relief = None, 
            text = '', 
            text_fg = QuestGlobals.REWARD_RED, 
            text_scale = 0.0425, 
            text_align = TextNode.ALeft, 
            text_wordwrap = 17.0, 
            textMayChange = 1, 
        pos = (-0.36, 0, -0.26))
        self.rewardText.hide()
        
        self.lPictureFrame = DirectFrame(parent = self.questFrame, relief = None, 
            image = bookModel.find('**/questPictureFrame'), 
            image_scale = QuestGlobals.IMAGE_SCALE_SMALL, 
            text = '', 
            text_pos = (0, -0.11),
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = TEXT_SCALE, 
            text_align = TextNode.ACenter, 
            text_wordwrap = 11.0,
            pos = (QuestGlobals.DEFAULT_LEFT_PICTURE_POS),
        textMayChange = 1)
        self.lPictureFrame.hide()
        
        self.rPictureFrame = DirectFrame(parent = self.questFrame, relief = None, 
            image = bookModel.find('**/questPictureFrame'), 
            image_scale = QuestGlobals.IMAGE_SCALE_SMALL, 
            text = '', text_pos = (0, -0.11), 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = TEXT_SCALE, 
            text_align = TextNode.ACenter, 
            text_wordwrap = 11.0, 
            textMayChange = 1, 
        pos = (QuestGlobals.DEFAULT_RIGHT_PICTURE_POS))
        self.rPictureFrame['image_color'] = Vec4(*QuestGlobals.GREEN)
        self.rPictureFrame.hide()
        
        self.lQuestIcon = DirectFrame(parent = self.lPictureFrame, relief = None, 
            text = ' ', text_font = CIGlobals.getSuitFont(), 
            text_pos = (0, -0.03), 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = 0.13, 
            text_align = TextNode.ACenter, 
            text_wordwrap = 13.0, 
        textMayChange = 1)
        self.lQuestIcon.setColorOff(-1)
        
        self.rQuestIcon = DirectFrame(parent = self.rPictureFrame, relief = None, 
            text = ' ', 
            text_font = CIGlobals.getSuitFont(), 
            text_pos = (0, -0.03), 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_scale = 0.13, 
            text_align = TextNode.ACenter, 
            text_wordwrap = 13.0, 
        textMayChange = 1)
        self.rQuestIcon.setColorOff(-1)
        
        head = SuitBank.PennyPincher.getHead().generate()
        head.setDepthTest(True)
        head.setDepthWrite(True)
        head.setScale(0.25)
        for part in head.getChildren():
            part.setDepthTest(True)
            part.setDepthWrite(True)
        self.fitGeometry(head, fFlip = 1)
        self.rQuestIcon['geom'] = head
        self.rQuestIcon['geom_scale'] = QuestGlobals.IMAGE_SCALE_SMALL
        self.rQuestIcon['geom_pos'] = Point3(0, 10, -0.05)
        self.rQuestIcon['geom_hpr'] = Point3(180, 0, 0)
        self.rQuestIcon.initialiseoptions(DirectFrame)
        
        self.auxText = DirectLabel(parent = self.questFrame, relief = None, 
            text = 'Recover', 
            text_font = CIGlobals.getToonFont(),
            text_scale = QuestGlobals.QPauxText, 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_align = TextNode.ACenter,
            pos = (QuestGlobals.DEFAULT_AUX_POS),
        textMayChange=1)
        self.auxText.hide()
        
        self.middleText = DirectLabel(parent = self.questFrame, relief = None, 
            text = 'from:', 
            text_font = CIGlobals.getToonFont(),
            text_scale = QuestGlobals.QPauxText, 
            text_fg = QuestGlobals.TEXT_COLOR, 
            text_align = TextNode.ACenter,
            pos = (QuestGlobals.DEFAULT_MIDDLE_POS),
        textMayChange=1)
        self.middleText.hide()
        
        self.questProgress = DirectWaitBar(parent = self.questFrame, relief = DGG.SUNKEN, 
            frameSize=(-0.95, 0.95, -0.1, 0.12), 
            borderWidth = (0.025, 0.025), 
            scale = 0.2, 
            frameColor = (0.945, 0.875, 0.706, 1.0), 
            barColor=(0.5, 0.7, 0.5, 1), 
            text='0/0',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.19, 
            text_fg = (0.05, 0.14, 0.4, 1), 
            text_align = TextNode.ACenter, 
            text_pos = (0, -0.05), #-0.02
        pos = (0, 0, -0.2425))
        self.questProgress.hide()
        
        rewardFrameGeom = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui.bam')
        self.rewardFrame = DirectFrame(parent = self.questFrame, relief = None,
            geom = rewardFrameGeom.find('**/Goofys_Sign'),
            geom_scale = (0.615, 0, 0.4),
            pos = (-0.01, 0, -0.25)
        )

        jellybeanJar = QuestGlobals.getFilmIcon()  
        self.lRewardFrame = DirectFrame(parent = self.rewardFrame, relief = None,
            geom = jellybeanJar,
            geom_scale = QuestGlobals.TP_ACCESS_SCALE,
        pos = (QuestGlobals.LEFT_TP_ACCESS_POS))
        
        self.lRewardInfo = DirectFrame(parent = self.questFrame, relief = None,
            geom = rewardFrameGeom.find('**/Char_Pnl'),
            geom_scale = (0.15, 0, 0.1275),
            text = '#1',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.04,
            text_fg = (0, 0, 0, 1),
            text_align = TextNode.ACenter,
            text_pos = (0, -0.01),
        pos = (-0.285, 0, -0.255))
        self.lRewardInfo.setBin('gui-popup', 40)
        
        self.rRewardFrame = DirectFrame(parent = self.rewardFrame, relief = None,
            geom = QuestGlobals.getJBIcon(),
            geom_scale = QuestGlobals.JB_JAR_SCALE,
        pos = QuestGlobals.RIGHT_JB_JAR_POS)
        
        self.rRewardInfo = DirectFrame(parent = self.questFrame, relief = None,
            geom = rewardFrameGeom.find('**/Char_Pnl'),
            geom_scale = (0.15, 0, 0.1275),
            text = '25',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.04,
            text_fg = (0, 0, 0, 1),
            text_align = TextNode.ACenter,
            text_pos = (0, -0.01),
        pos = (0.2725, 0, -0.255))
        self.rRewardInfo.setBin('gui-popup', 40)
        
        rewardFrameGeom.removeNode()
        
        # This is the rotated text on the side.
        self.sideInfo = DirectLabel(parent = self.questFrame, relief = None, 
            text = QuestGlobals.JUST_FOR_FUN, 
            text_fg = (0.0, 0.439, 1.0, 1.0), 
            text_shadow = (0, 0, 0, 1), 
            pos = (-0.2825, 0, 0.2), 
        scale = 0.03)
        self.sideInfo.setR(-30)
        self.sideInfo.hide()

        bookModel.removeNode()
        self.laffMeter = None
        return
    
    def update(self):
        objective = self.quest.getCurrentObjective()
        objective.updateInfo()
        
        # Let's setup the picture frames and info.
        self.questInfo.setPos(self.quest.getInfoPos())
        self.questInfo['text'] = self.quest.getInfoText()
        self.questInfo02.setPos(self.quest.getInfo02Pos())
        self.questInfo02['text'] = self.quest.getInfo02Text()
        self.lPictureFrame.setPos(self.quest.getLeftPicturePos())
        self.rPictureFrame.setPos(self.quest.getRightPicturePos())
        self.lQuestIcon['geom'] = self.quest.getLeftIconGeom()
        if isinstance(objective, VisitNPCObjective.VisitNPCObjective) or isinstance(objective, CogObjective):
            if objective.getDidEditLeft():
                head = self.quest.getLeftIconGeom()
                icon = self.lQuestIcon
                scale = self.quest.getLeftIconScale()
            else:
                head = self.quest.getRightIconGeom()
                icon = self.rQuestIcon
                scale = self.quest.getRightIconScale()
            
            isHead = True if type(head) == ToonHead else head.getName() == ('%sHead' % CIGlobals.Suit)
            
            if isHead:
                head.setDepthWrite(1)
                head.setDepthTest(1)
                self.fitGeometry(head, fFlip = 1)
            else:
                icon.setScale(scale)
            
            if isinstance(objective, VisitNPCObjective.VisitNPCObjective) and icon == self.rQuestIcon:
                icon.setHpr(180, 0, 0)
                icon.setPos(icon.getX(), icon.getY(), icon.getZ() + 0.05)
            elif isinstance(objective, CogObjective):
                if icon == self.lQuestIcon:
                    if objective.getName():
                        icon.setScale(QuestGlobals.IMAGE_SCALE_SMALL)
                        icon.setPos(icon.getX(), icon.getY(), icon.getZ() - 0.04)
                    else:
                        head.setScale(self.quest.getLeftIconScale())
                else:
                    if objective.getName():
                        head.setScale(1.2)
                    else:
                        icon.setScale(self.quest.getRightIconScale())
            
            icon['geom'] = head
            icon['geom_scale'] = QuestGlobals.IMAGE_SCALE_SMALL
            
            #self.lQuestIcon['geom_hpr'] = (180, 0, 0)
            #self.lQuestIcon['geom_pos'] = (0, 10, -0.04)
        else:
            self.lQuestIcon['geom'] = self.quest.getLeftIconGeom()
            self.lQuestIcon['geom_scale'] = self.quest.getLeftIconScale()
        #self.rQuestIcon['geom'] = self.quest.getRightIconGeom()
        #self.rQuestIcon['geom_scale'] = self.quest.getRightIconScale()
        
        if self.questInfo02['text'] == '':
            self.rPictureFrame.hide()
            self.questInfo02.hide()
        else:
            self.rPictureFrame.show()
            self.questInfo02.show()
        
        self.middleText['text'] = self.quest.getMiddleText()
        if not self.middleText['text'] == '':
            self.middleText.show()
        
        self.questInfo.show()
        self.lPictureFrame.show()
        
        # Let's set the location text.
        self.locationInfo['text'] = self.quest.getLocationText()
        self.locationInfo['text_pos'] = (0, self.quest.getLocationY())
        self.locationInfo.show()
        
        # Let's set the progress bar up.
        self.questProgress['text'] = self.quest.getProgressText()
        if len(self.questProgress['text']) > 0 and not objective.finished():
            self.questProgress.show()
            self.questProgress['range'] = objective.getNeededAmount()
            self.questProgress['value'] = objective.getProgress() & pow(2, 16) - 1
        else:
            self.questProgress.hide()
        
        # Let's setup the aux text.
        self.auxText.setPos(self.quest.getAuxPos())
        self.auxText['text'] = self.quest.getAuxText()
        self.auxText.show()
        
        maxHP = base.localAvatar.getMaxHealth()
        
        # Let's setup the rewards.
        for i in xrange(0, len(self.quest.getRewards())):
            reward = self.quest.getRewards()[i]
            frame = self.lRewardFrame if (i == 0) else self.rRewardFrame
            info = self.lRewardInfo if (i == 0) else self.rRewardInfo
            rType = reward.getType()
            if(rType == RewardType.JELLYBEANS):
                frame['pos'] = QuestGlobals.LEFT_JB_JAR_POS if (i == 0) else QuestGlobals.RIGHT_JB_JAR_POS
                frame['geom'] = QuestGlobals.getJBIcon()
                frame['geom_scale'] = QuestGlobals.JB_JAR_SCALE
                info['text'] = str(reward.getModifier())
            elif(rType == RewardType.TELEPORT_ACCESS or rType == RewardType.GAG_FRAME):
                frame['pos'] = QuestGlobals.LEFT_TP_ACCESS_POS if(i == 0) else QuestGlobals.RIGHT_TP_ACCESS_POS
                frame['geom'] = QuestGlobals.getTPAccessIcon() if(rType == RewardType.TELEPORT_ACCESS) else QuestGlobals.getFilmIcon()
                frame['geom_scale'] = QuestGlobals.TP_ACCESS_SCALE
                info['text'] = 'N/A' if(rType == RewardType.TELEPORT_ACCESS) else '#%s' % (str(reward.getModifier()))
            elif(rType == RewardType.LAFF_POINTS):
                frame.initialiseoptions(DirectFrame)
                r, g, b, _ = base.localAvatar.getHeadColor()
                pos = QuestGlobals.LEFT_LAFF_METER_POS if(i == 0) else QuestGlobals.RIGHT_LAFF_METER_POS
                
                # Create the laff meter with the new health.
                hp = maxHP + reward.getModifier()
                laffMeter = LaffOMeter()
                laffMeter.generate(r, g, b, base.localAvatar.getAnimal(), maxHP = hp, initialHP = hp)
                
                # Let's position the laff meter.
                frame['geom'] = laffMeter
                frame['geom_scale'] = QuestGlobals.LAFF_METER_SCALE
                frame.setPos(pos)
                info['text'] = '+%s' % (str(reward.getModifier()))
                laffMeter.destroy()
                laffMeter = None

        # Hide or show the other reward depending on if there's 2 rewards.
        if(len(self.quest.getRewards()) == 1):
            self.rRewardFrame.hide()
            self.rRewardInfo.hide()
        else:
            self.rRewardFrame.show()
            self.rRewardInfo.show()
            
        if objective.finished():
            self.setColor(Vec4(*QuestGlobals.LIGHT_GREEN))
            self.sideInfo['text'] = 'Completed!'
            self.sideInfo.show()
                    
        self.questInfo.initialiseoptions(DirectLabel)
        self.questInfo02.initialiseoptions(DirectLabel)
        self.locationInfo.initialiseoptions(DirectLabel)
        self.lPictureFrame.initialiseoptions(DirectFrame)
        self.rPictureFrame.initialiseoptions(DirectFrame)
        self.lQuestIcon.initialiseoptions(DirectFrame)
        self.rQuestIcon.initialiseoptions(DirectFrame)
        self.auxText.initialiseoptions(DirectLabel)
        self.middleText.initialiseoptions(DirectLabel)
        #self.lRewardFrame.initialiseoptions(DirectFrame)
        #self.rRewardFrame.initialiseoptions(DirectFrame)
        self.sideInfo.initialiseoptions(DirectLabel)
        self.lPictureFrame['image_color'] = self.quest.getPictureFrameColor()
        self.rPictureFrame['image_color'] = self.quest.getPictureFrameColor()
    
    def fitGeometry(self, geom, fFlip = 0, dimension = 0.8):
        p1 = Point3()
        p2 = Point3()
        geom.calcTightBounds(p1, p2)
        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = dimension / biggest
        mid = (p1 + d / 2.0) * s
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)

        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], 180, 0, 0, s, s, s)
        geomXform.reparentTo(geom)
        
    def destroy(self):
        self._deleteGeoms()
        DirectFrame.destroy(self)

    def _deleteGeoms(self):
        for icon in (self.lQuestIcon, self.rQuestIcon):
            geom = icon['geom']
            if geom and hasattr(geom, 'delete'):
                geom.delete()