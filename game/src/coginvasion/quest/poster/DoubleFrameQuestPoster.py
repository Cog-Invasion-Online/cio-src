"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DoubleFrameQuestPoster.py
@author Maverick Liberty
@date March 17, 2017

"""

from src.coginvasion.quest.poster.QuestPoster import QuestPoster
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.globals import CIGlobals


# Imports for handling the representation of objectives.
from src.coginvasion.quest.Objectives import RecoverItemObjective,\
    CogBuildingObjective, CogObjective, MinigameObjective
from src.coginvasion.quest.Objectives import DeliverItemObjective
from src.coginvasion.quest.Objectives import DoubleFrameObjectives

from panda3d.core import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectLabel, DirectFrame

class DoubleFrameQuestPoster(QuestPoster):
    notify = directNotify.newCategory('DoubleFrameQuestPoster')
    
    def __init__(self, quest, parent = aspect2d, **kw):
        QuestPoster.__init__(self, quest, parent, **kw)
        
        # This text is in between the two frames and it usually says
        # either "from:" or "to:"
        self.fromToMiddleText = DirectLabel(parent = self, 
            relief = None,
            text = QuestGlobals.FROM,
            text_font = CIGlobals.getToonFont(),
            text_scale = QuestGlobals.QPauxText,
            text_fg = QuestGlobals.TEXT_COLOR,
            text_align = TextNode.ACenter,
            textMayChange = 1,
        pos = QuestGlobals.DEFAULT_MIDDLE_POS)
        self.fromToMiddleText.hide()
        
        ##########################################################################
        #           THE FOLLOWING ELEMENTS BELOW ARE GROUPED TOGETHER            #
        ##########################################################################
        # We need this again for certain geometry.
        circleGui = loader.loadModel('phase_4/models/gui/CircleIconBackgroundGui.bam')
        
        # The background frame where the objective image is displayed.
        # This is the colored background frame.
        self.goalFrame = DirectFrame(parent = self, 
            relief = None,
            image = circleGui.find('**/circle_display_interior'),
            image_scale = 0.18,
            text = '',
            text_pos = (0, -0.11),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = QuestGlobals.QPtextScale,
            text_align = TextNode.ACenter,
            text_wordwrap = 11.0,
        pos = QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)
        self.goalFrame.hide()
        
        # The icon that goes on top of the goal frame.
        self.goalIcon = DirectFrame(parent = self.goalFrame,
            relief = None,
            text = ' ',
            text_font = CIGlobals.getSuitFont(),
            text_pos = (0, -0.03),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = 0.13,
            text_align = TextNode.ACenter,
            text_wordwrap = 13.0,
        textMayChange = 1)
        self.goalIcon.setColorOff(-1)
        self.goalIcon.hide()
        
        self.goalOutline = DirectLabel(parent = self.goalFrame,
            relief = None,
            image = circleGui.find('**/circle_display_outline'),
        image_scale = 0.18)
        self.goalOutline.hide()
        
        # Information displayed about the additional goal.
        self.goalInfo = DirectLabel(parent = self,
            relief = None,
            text = '',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = 0.04,
            text_align = TextNode.ACenter,
            text_wordwrap = QuestGlobals.QPtextWordwrap,
            textMayChange = 1,
        pos = (QuestGlobals.DEFAULT_INFO2_POS))
        self.goalInfo.hide()
        
        circleGui.removeNode()
        return
        
        ##########################################################################
        
    def setup(self):
        QuestPoster.setup(self)
        objective = self.viewObjective
        
        # Let's reset our icon.
        self.goalIcon.setScale(1, 1, 1)
        self.goalIcon.setPos(0, 0, 0)
        self.goalIcon.setHpr(0, 0, 0)
        
        if objective.__class__ in DoubleFrameObjectives:
            if objective.__class__ == DeliverItemObjective:
                # It's kind of hard to return delivered stuff to somebody.
                # We're not handling complete objectives from here.
                self.handleDeliverItemObjective()
            elif objective.__class__ == RecoverItemObjective:
                self.handleRecoverItemObjective()
            
            if len(self.quest.accessibleObjectives) > 1:
                self.prevObjArrow.setPos(QuestGlobals.SECONDARY_LEFT_ARROW_POS)
                self.nextObjArrow.setPos(QuestGlobals.SECONDARY_RIGHT_ARROW_POS)
            
            self.goalFrame.show()
            self.goalIcon.show()
            self.goalOutline.show()
            self.goalInfo.show()
            self.fromToMiddleText.show()
        else:
            self.goalFrame.hide()
            self.goalIcon.hide()
            self.goalOutline.hide()
            self.goalInfo.hide()
            self.fromToMiddleText.hide()
        self.goalIcon.initialiseoptions(DirectFrame)
        self.initialiseoptions(DoubleFrameQuestPoster)
        
    def handleRecoverItemObjective(self):
        objective = self.viewObjective

        # Let's make sure we have a current objective that is
        # an instance of the RecoverItemObjective class and this poster isn't destroyed.
        if not objective or not hasattr(self, 'titleLabel') or not isinstance(objective, RecoverItemObjective): return
        
        # Let's make the left icon use the item icon we chose.
        self.handleSimpleIcon(objective.itemIcon, 0.12, self.auxIcon)
        
        # Handle the objective information.
        infoText = '%d %s' % (objective.goal, CIGlobals.makePlural(objective.itemName))
        if objective.goal == 1:
            infoText = objective.itemName
        
        # Update the positions and information regarding the left side.
        self.auxFrame.setPos(QuestGlobals.RECOVER_LEFT_PICTURE_POS)
        self.auxFrame['image_color'] = QuestGlobals.GREEN
        self.objectiveInfo.setPos(QuestGlobals.RECOVER_INFO_POS)
        self.objectiveInfo['text'] = infoText
        self.fromToMiddleText['text'] = QuestGlobals.FROM if not objective.isComplete() else QuestGlobals.TO
        
        if not objective.isComplete():
            self.handleCogObjective(self.goalIcon, auxText = QuestGlobals.RECOVER, frameColor = QuestGlobals.GREEN)
            
            # Let's set the progress bar text
            pgBarText = '%d of %d %s' % (objective.progress, objective.goal, 
                CIGlobals.makePastTense(QuestGlobals.RECOVER))
            self.progressBar['text'] = pgBarText
            self.progressBar['value'] = objective.progress & pow(2, 16) - 1
        else:
            self.handleNPCObjective(self.goalIcon, auxText = QuestGlobals.RETURN, frameColor = QuestGlobals.BLUE)
        
    def handleDeliverItemObjective(self):
        objective = self.viewObjective

        # Let's make sure we have a current objective that is
        # an instance of the DeliverItemObjective class and this poster isn't destroyed.
        if not objective or not hasattr(self, 'titleLabel') or not isinstance(objective, DeliverItemObjective): return
        
        # Correct the scaling if we need to and set the icon.
        scale = 0.12 if objective.itemIcon.getName() == 'package' else 0.85
        self.handleSimpleIcon(objective.itemIcon, scale, self.auxIcon)
        self.auxFrame.setPos(QuestGlobals.RECOVER_LEFT_PICTURE_POS)
        self.auxFrame['image_color'] = QuestGlobals.RED
        
        infoText = '%d %s' % (objective.goal, CIGlobals.makePlural(objective.itemName))
        if objective.goal == 1:
            infoText = objective.itemName
        self.objectiveInfo.setPos(QuestGlobals.RECOVER_INFO_POS)
        self.objectiveInfo['text'] = infoText
        self.fromToMiddleText['text'] = QuestGlobals.TO
        
        # Let's set the progress bar text
        pgBarText = '%d of %d %s' % (objective.progress, objective.goal, 
            CIGlobals.makePastTense(QuestGlobals.DELIVER))
        self.progressBar['text'] = pgBarText
        self.progressBar['value'] = objective.progress & pow(2, 16) - 1
        
        self.handleNPCObjective(self.goalIcon, auxText = QuestGlobals.DELIVER, frameColor = QuestGlobals.RED)
        
    def destroy(self):
        self.fromToMiddleText.destroy()
        self.goalFrame.destroy()
        self.goalIcon.destroy()
        self.goalOutline.destroy()
        self.goalInfo.destroy()
        del self.fromToMiddleText
        del self.goalFrame
        del self.goalIcon
        del self.goalOutline
        del self.goalInfo
        QuestPoster.destroy(self)
    