"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file QuestPoster.py
@author Maverick Liberty
@date March 17, 2017

"""

""" This is the bare bones, base class for the QuestPosters. """

from direct.gui.DirectGui import DirectFrame, DirectLabel, DGG
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import TextNode, Point3, Vec4

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quests import QuestGlobals
from src.coginvasion.quests.poster.QuestRewardFrame import QuestRewardFrame
from src.coginvasion.quests.Objectives import CogObjective
from src.coginvasion.quests.Objectives import CogBuildingObjective
from src.coginvasion.quests.Objectives import VisitNPCObjective
from src.coginvasion.quests.Objectives import RecoverItemObjective
from src.coginvasion.quests.Objectives import DeliverItemObjective
from src.coginvasion.quests.Objectives import MinigameObjective
from src.coginvasion.cog import Dept, SuitGlobals, SuitBank
from src.coginvasion.toon.ToonHead import ToonHead
from src.coginvasion.toon.ToonDNA import ToonDNA

import random

class QuestPoster(DirectFrame):
    notify = directNotify.newCategory('QuestPoster')
    
    # We need to declare and initialize these variables here
    # because some methods use them as default arguments.
    auxIcon = None
    
    # Requires one parameter, quest, this must be a Quest instance.
    # The next argument, parent, is where to reparent the DirectFrame to.
    # The next arguments are simply additional options when setting up the DirectFrame.
    def __init__(self, quest, parent = aspect2d, **kw):
        # The quest this poster is representing.
        self.quest = quest
        
        isObjComplete = False if not quest else self.quest.currentObjective.isComplete()
        
        # Let's define our options for the DirectFrame.
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        optiondefs = (('relief', None, None),
         ('image', bookModel.find('**/questCard'), None),
         ('image_scale', (0.8, 1.0, 0.58), None),
         ('image_color', (1.0, 1.0, 1.0, 1.0) if not isObjComplete else Vec4(*QuestGlobals.LIGHT_GREEN), None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        
        # Finally, initialize the DirectFrame.
        DirectFrame.__init__(self, relief = None)
        self.initialiseoptions(QuestPoster)
        
        # Let's declare and initialize our barebone GUI element variables.
        questTitle = '' if not self.quest else self.quest.getName()
        self.titleLabel = DirectLabel(parent = self, relief = None,
            text = questTitle,
            text_font = CIGlobals.getMinnieFont(),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = 0.05,
            text_align = TextNode.ACenter,
            text_wordwrap = 25.0,
            textMayChange = 1,
        pos = (0, 0, 0.23))

        ##########################################################################
        #           THE FOLLOWING ELEMENTS BELOW ARE GROUPED TOGETHER            #
        ##########################################################################
        
        # The background frame where the objective image is displayed.
        # This is the colored background frame.
        self.auxFrame = DirectFrame(parent = self, 
            relief = None,
            image = bookModel.find('**/questPictureFrame'),
            image_scale = QuestGlobals.IMAGE_SCALE_SMALL,
            text = '',
            text_pos = (0, -0.11),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = QuestGlobals.QPtextScale,
            text_align = TextNode.ACenter,
            text_wordwrap = 11.0,
        pos = QuestGlobals.DEFAULT_LEFT_PICTURE_POS)
        
        # The icon that goes on top of the aux frame.
        self.auxIcon = DirectFrame(parent = self.auxFrame,
            relief = None,
            text = ' ',
            text_font = CIGlobals.getSuitFont(),
            text_pos = (0, -0.03),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = 0.13,
            text_align = TextNode.ACenter,
            text_wordwrap = 13.0,
        textMayChange = 1)
        self.auxIcon.setColorOff(-1)
        
        # The aux text saying: DEFEAT, RECOVER, etc.
        self.auxText = DirectLabel(parent = self,
            relief = None,
            text = QuestGlobals.RECOVER,
            text_font = CIGlobals.getToonFont(),
            text_scale = QuestGlobals.QPauxText,
            text_fg = QuestGlobals.TEXT_COLOR,
            text_align = TextNode.ACenter,
            textMayChange = 1,
        pos = QuestGlobals.DEFAULT_AUX_POS)
        self.auxText.hide()
        
        ##########################################################################
        
        # Information displayed about the objective.
        self.objectiveInfo = DirectLabel(parent = self,
            relief = None,
            text = '',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = 0.04,
            text_align = TextNode.ACenter,
            text_wordwrap = QuestGlobals.QPtextWordwrap,
            textMayChange = 1,
        pos = (QuestGlobals.DEFAULT_INFO_POS))
        self.objectiveInfo.hide()
        
        # Information displayed showing the location.
        self.locationInfo = DirectLabel(parent = self, 
            relief = None,
            text = 'N/A',
            text_font = CIGlobals.getToonFont(),
            text_fg = QuestGlobals.TEXT_COLOR,
            text_scale = QuestGlobals.QPtextScale,
            text_align = TextNode.ACenter,
            text_wordwrap = QuestGlobals.QPtextWordwrap,
            textMayChange = 1,
        pos = (0, 0, -0.115))
        self.locationInfo.hide()
        
        # The progress bar showing the objective's progress
        self.progressBar = DirectWaitBar(parent = self, 
            relief = DGG.SUNKEN,
            frameSize = (-0.95, 0.95, -0.1, 0.12),
            borderWidth = (0.025, 0.025),
            scale = 0.2,
            frameColor = (0.945, 0.875, 0.706, 1.0),
            barColor = (0.5, 0.7, 0.5, 1),
            text = '0/0',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.19,
            text_fg = (0.05, 0.14, 0.4, 1),
            text_align = TextNode.ACenter,
            text_pos = (0, -0.05),
        pos = (0, 0, -0.2425))
        self.progressBar.hide()
        
        # The wood panel at the bottom where rewards are displayed.
        rewardFrameGeom = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui.bam')
        self.rewardFrame = DirectFrame(parent = self, 
            relief = None,
            geom = rewardFrameGeom.find('**/Goofys_Sign'),
            geom_scale = (0.615, 0, 0.4),
        pos = (-0.01, 0, -0.25))
        
        # Let's setup our reward frames.
        reward = None if not self.quest else self.quest.reward
        self.lReward = QuestRewardFrame(self, reward)
        
        # The text displayed on the right side of the frame with additional information, if necessary.
        self.sideInfo = DirectLabel(parent = self,
            relief = None,
            text = QuestGlobals.JUST_FOR_FUN,
            text_fg = (0.0, 0.439, 1.0, 1.0),
            text_shadow = (0, 0, 0, 1),
            pos = (-0.2825, 0, 0.2),
        scale = 0.03)
        self.sideInfo.setR(-30)
        
        # This side information is usually not needed, let's hide it.
        self.sideInfo.hide()
        
        # Remove the nodes of the loaded models we no longer need.
        bookModel.removeNode()
        rewardFrameGeom.removeNode()
        
        # Let's hide this until it is needed.
        self.hide()
        return
    
    def setup(self):
        if self.quest:
            objective = self.quest.currentObjective
            
            self.objectiveInfo.show()
            self.auxFrame.show()
            
            isShopLoc = QuestGlobals.isShopLocation(objective.area) if not objective.isComplete() else True
            self.locationInfo['text'] = QuestGlobals.getLocationText(objective.area) if not objective.isComplete() else QuestGlobals.getLocationText(None, objective)
            self.locationInfo['text_pos'] = (0, 0 if not isShopLoc else 0.025)
            self.locationInfo.show()
            
            # Let's setup the quest progress bar
            progress = objective.progress if hasattr(objective, 'amount') else None
            
            if progress and objective.goal > 0:
                self.progressBar['range'] = objective.goal
                self.progressBar['value'] = progress & pow(2, 16) - 1
            
            if objective.HasProgress and objective.goal > 1 and not objective.isComplete():
                self.progressBar.show()
            
            self.auxText.show()
            
            # Let's handle the objectives.
            if objective.__class__ == CogObjective:
                self.handleCogObjective()
            elif objective.__class__ == CogBuildingObjective:
                self.handleCogBuildingObjective()
            elif objective.__class__ == MinigameObjective:
                self.handleMinigameObjective()
            elif objective.__class__ == VisitNPCObjective:
                self.handleNPCObjective()
                
            self.lReward.setup()
        else:
            # We want to be able to show empty quest posters.
            self.titleLabel.hide()
            self.auxFrame.hide()
            self.auxIcon.hide()
        
        self.titleLabel.initialiseoptions(DirectLabel)
        self.auxIcon.initialiseoptions(DirectFrame)
        self.auxText.initialiseoptions(DirectLabel)
        self.objectiveInfo.initialiseoptions(DirectLabel)
        self.locationInfo.initialiseoptions(DirectLabel)
        self.rewardFrame.initialiseoptions(DirectFrame)
        self.sideInfo.initialiseoptions(DirectLabel)
        self.lReward.initialiseoptions(DirectFrame)
    
    # Changes geometry and scale of an icon.
    def handleSimpleIcon(self, geom, scale, icon):
        icon['geom'] = geom
        icon['geom_scale'] = scale
        
    def handleComplexIcon(self, geom, icon, scale = QuestGlobals.IMAGE_SCALE_SMALL):
        geom.setDepthWrite(1)
        geom.setDepthTest(1)
        self.fitGeometry(geom, fFlip = 1)
        self.handleSimpleIcon(geom, scale, icon)
        
        # We have to rotate the head and set the scale of the icon.
        if CIGlobals.Suit in geom.getName():
            cogName = geom.getPythonTag('Settings')
            data = QuestGlobals.Suit2PosterZNDScale.get(cogName)
            zOffset = data[0]
            headScale = data[1]
            icon.setScale(headScale)
            icon.setZ(icon.getZ() + zOffset)
            
            geom.setH(180)
    
    def handleCogObjective(self, iconElement = auxIcon, auxText = QuestGlobals.DEFEAT, frameColor = QuestGlobals.BLUE):
        objective = self.quest.currentObjective
        infoText = objective.getTaskInfo()
        
        if objective.__class__ == RecoverItemObjective:
            infoText = QuestGlobals.makePlural(objective.cog)
        
        if not iconElement:
            iconElement = self.auxIcon
        
        # Let's make sure we have a current objective that is
        # an instance of the CogObjective class and this poster isn't destroyed.
        if not objective or not hasattr(self, 'titleLabel') or not isinstance(objective, CogObjective): return
        
        if objective.dept:
            icons = loader.loadModel('phase_3/models/gui/cog_icons.bam')
            deptIcon = None
            
            if objective.dept == Dept.BOSS:
                deptIcon = icons.find('**/CorpIcon')
            else:
                deptIcon = icons.find('**/%sIcon' % objective.dept.getTie().title())
                
            # Correct the medallion color.
            deptIcon.setColor(SuitGlobals.medallionColors[objective.dept])
            
            # Setup the icon and remove the icons node.
            self.handleSimpleIcon(deptIcon, 0.13, iconElement)
            icons.removeNode()
        elif objective.cog == QuestGlobals.Any:
            # We aren't fighting a Cog in particular.
            cogIcon = QuestGlobals.getCogIcon()
            self.handleSimpleIcon(cogIcon, cogIcon.getScale(), iconElement)
        
        # We're fighting a Cog in particular.
        if not objective.cog == QuestGlobals.Any:
            cogHeadInstance = SuitBank.getSuitByName(objective.cog).getHead()
            cogHead = cogHeadInstance.generate()
            cogHead.setName('%sHead' % CIGlobals.Suit)
            cogHead.setPythonTag('Settings', cogHeadInstance.head)
            cogHead.setScale(2)
            self.handleComplexIcon(cogHead, iconElement)
            
            # HACK FIX: Corrects the buggy Flunky glasses.
            glasses = cogHead.find('**/glasses')
            if glasses and not glasses.isEmpty():
                glasses.setScale(1)
                glasses.reparentTo(cogHead)
            
        if not iconElement is self.auxIcon:
            if hasattr(self, 'goalInfo'):
                # We're working with the second frame, on the right.
                # Let's update the information pertaining to this side.
                self.goalInfo['text'] = infoText
                self.goalInfo.setPos(QuestGlobals.RECOVER_INFO2_POS)
                self.auxText.setPos(QuestGlobals.RECOVER_AUX_POS)
            else:
                raise AttributeError('Attempted to setup DoubleFrame information for poster using default style.')
        else:
            self.objectiveInfo['text'] = infoText
            self.auxText['text'] = auxText
            
        # Let's set the progress bar text
        pgBarText = '%d of %d %s' % (objective.progress, objective.goal, 
            QuestGlobals.makePastTense(auxText))
        self.progressBar['text'] = pgBarText
        
        # Let's set the color of the poster.
        frame = self.auxFrame if iconElement is self.auxIcon else self.goalFrame
        frame['image_color'] = Vec4(*frameColor)
        
    def handleCogBuildingObjective(self, iconElement = auxIcon, auxText = QuestGlobals.DEFEAT, frameColor = QuestGlobals.BLUE):
        objective = self.quest.currentObjective
        infoText = objective.getTaskInfo()
        
        if not iconElement:
            iconElement = self.auxIcon
        
        # Let's make sure we have a current objective that is
        # an instance of the CogBuildingObjective class and this poster isn't destroyed.
        if not objective or not hasattr(self, 'titleLabel') or not isinstance(objective, CogBuildingObjective): return
        
        # If we aren't looking for any specific department of building.
        if objective.dept == QuestGlobals.Any:
            # Let's just use the good ol' generic building icon.
            self.handleSimpleIcon(QuestGlobals.getCogBuildingIcon(), 0.12, iconElement)
        else:
            # Ah geez, we're looking for a specific department.
            # Bossbot tie names are messed up, so we need this if statement.
            dept = objective.dept.getTie() if not objective.dept == Dept.BOSS else 'corp'
            bldgMdl = loader.loadModel('phase_4/models/modules/suit_landmark_%s.bam' % dept)
            
            # Next, we need to load the building elevator.
            elevator = loader.loadModel('phase_4/models/modules/elevator.bam')
            elevator.reparentTo(bldgMdl.find('**/*_door_origin'))
            
            self.handleComplexIcon(bldgMdl, iconElement)
        
        # Let's set the progress bar text
        pgBarText = '%d of %d %s' % (objective.progress, objective.goal, 
            QuestGlobals.makePastTense(auxText))
        self.progressBar['text'] = pgBarText    
        
        self.objectiveInfo['text'] = infoText
        self.auxText['text'] = auxText
        self.auxFrame['image_color'] = Vec4(*frameColor)
        
    def handleMinigameObjective(self, iconElement = auxIcon, auxText = QuestGlobals.PLAY, frameColor = QuestGlobals.RED):
        objective = self.quest.currentObjective
        infoText = objective.getTaskInfo()
        
        if not iconElement:
            iconElement = self.auxIcon
        
        # Let's make sure we have a current objective that is
        # an instance of the MinigameObjective class and this poster isn't destroyed.
        if not objective or not hasattr(self, 'titleLabel') or not isinstance(objective, MinigameObjective): return
        
        # Let's set the icon to the minigame icon.
        self.handleSimpleIcon(QuestGlobals.getTrolleyIcon(), 0.12, iconElement)
        
        # Let's set the progress bar text
        pgBarText = '%d of %d %s' % (objective.progress, objective.goal, 
            QuestGlobals.makePastTense(auxText))
        self.progressBar['text'] = pgBarText    
        
        self.objectiveInfo['text'] = infoText
        self.auxText['text'] = auxText
        self.auxFrame['image_color'] = Vec4(*frameColor)
        
    def handleNPCObjective(self, iconElement = auxIcon, auxText = QuestGlobals.VISIT, frameColor = QuestGlobals.BROWN):
        objective = self.quest.currentObjective
        npcId = objective.npcId if hasattr(objective, 'npcId') else objective.assigner

        if npcId == 0:
            infoText = 'A %s' % CIGlobals.lHQOfficerF
        else:
            infoText = CIGlobals.NPCToonNames[npcId]
        
        if not iconElement:
            iconElement = self.auxIcon
        
        # Let's generate the head.
        if not objective.isComplete() and not CIGlobals.NPCToonNames[npcId] == CIGlobals.lHQOfficerF:
            dna = ToonDNA()
            dna.setDNAStrand(CIGlobals.NPCToonDict.get(npcId)[2])
            head = ToonHead(base.cr)
            head.generateHead(dna.getGender(), dna.getAnimal(), dna.getHead(), forGui = 1)
            head.setHeadColor(dna.getHeadColor())
            self.handleComplexIcon(head, iconElement)
        else:
            self.handleSimpleIcon(QuestGlobals.getHQIcon(), 0.12, iconElement)
        
        self.auxText['text'] = auxText
        
        if not iconElement is self.auxIcon:
            if hasattr(self, 'goalInfo'):
                # We're working with the second frame, on the right.
                # Let's update the information pertaining to this side.
                self.goalInfo['text'] = infoText
                self.goalInfo.setPos(QuestGlobals.RECOVER_INFO2_POS)
                self.auxText.setPos(QuestGlobals.RECOVER_AUX_POS)
                self.goalFrame['image_color'] = frameColor
            else:
                raise AttributeError('Attempted to setup DoubleFrame information for poster using default style.')
        else:
            self.objectiveInfo['text'] = infoText
            self.auxFrame['image_color'] = frameColor
    
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
        if hasattr(self, 'titleLabel'):
            self.titleLabel.destroy()
            self.auxFrame.destroy()
            self.auxIcon.destroy()
            self.auxText.destroy()
            self.objectiveInfo.destroy()
            self.locationInfo.destroy()
            self.progressBar.destroy()
            self.rewardFrame.destroy()
            self.sideInfo.destroy()
            self.lReward.destroy()
            del self.titleLabel
            del self.auxFrame
            del self.auxIcon
            del self.auxText
            del self.objectiveInfo
            del self.locationInfo
            del self.progressBar
            del self.rewardFrame
            del self.sideInfo
            del self.lReward
            DirectFrame.destroy(self)
            self.notify.debug('Destroyed all elements.')
