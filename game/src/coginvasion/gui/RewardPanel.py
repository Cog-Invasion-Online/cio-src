"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RewardPanel.py
@author Maverick Liberty
@date October 13, 2017

"""

from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectWaitBar
from direct.gui.DirectGui import OnscreenImage, OnscreenText, DGG
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals

from panda3d.core import Point3, TextNode
import math
import random

GagPanelName = 'Gag Experience'
FavoriteGag = 'Favorite Gag'
FavoriteGagPos = (0, 0, -0.125)
FavoriteGagTitlePos = (0, 0.075, 0)
FavoriteGagNamePos = (0, -0.325, 0)
GagGlowColor = (1.0, 1.0, 0.4, 1.0)
NewGagCongratsMessages = ['Yeah!', 'Wow!', 
    'Cool!', 'Congrats!', 'Awesome!',
    'Toon-tastic!', 'Fantastic!']

class RewardPanel(DirectFrame):
    notify = directNotify.newCategory('RewardPanel')
    
    def __init__(self, panelData):
        dialogBox = loader.loadModel('phase_3/models/gui/dialog_box_gui.bam')
        DirectFrame.__init__(self, relief = None, geom = dialogBox, 
            geom_color = CIGlobals.DialogColor, geom_scale = (1.75, 1, 0.75 * 1.1),
            geom_pos = Point3(0, 0, -0.05), pos = (0, 0, 0.57))
        self.initialiseoptions(RewardPanel)
        
        # The data for the reward panel inside of a RPToonData object.
        self.panelData = panelData
        
        # Top wood panel saying Reward Panel
        gagShopNodes = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui.bam')
        # Original pos: (-0.02, 0, 0.3) scale = (1.55, 1, 1)
        self.titlePanel = OnscreenImage(parent = self, image = gagShopNodes.find('**/Goofys_Sign'),
            pos = (0, 0, 0.3), hpr = (1, 0, 0), scale = (1.3, 1, 0.9))
        
        self.avatarNamePanel = DirectFrame(parent = self.titlePanel, pos = (0, 0.005, 0))
        self.avatarText = OnscreenText(parent = self.avatarNamePanel, text = '', 
            font = CIGlobals.getMickeyFont(), fg = (0.698, 0.13, 0.13, 1),
            mayChange = 1, scale = (0.1, 0.13, 0.1))
        
        self.panelContentsTitle = OnscreenText(parent = self, text = GagPanelName,
            font = CIGlobals.getMickeyFont(), pos = (0, 0.24, 0),
            fg = (0.3725, 0.619, 0.627, 1),
            mayChange = 1)
        
        self.playerInfo = DirectFrame(parent = self, relief = None, pos = (-0.5, 0, 0))
        self.playerInfo.setBin('gui-popup', 0)
        
        self.bonusText = OnscreenText(parent = self.playerInfo, text = '2X Cog Office Bonus!',
            font = CIGlobals.getToonFont(), pos = (0, 0.15, 0),
            scale = (0.055, 0.055, 0.055), align = TextNode.ACenter)
        self.bonusText.hide()
        
        ##################################################################################
        # GUI Elements relating to the Favorite Gag/Gag Popup Used for showing Gag Unlock#
        ##################################################################################
        self.favoriteGagText = OnscreenText(parent = self.playerInfo, text = FavoriteGag,
            font = CIGlobals.getMickeyFont(), pos = FavoriteGagTitlePos,
            fg = (1, 0.2, 0.2, 1), sort = 0)
        
        glow = loader.loadModel('phase_4/models/minigames/particleGlow.bam')
        invIcons = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam')
        gag = invIcons.find(GagGlobals.InventoryIconByName.get(CIGlobals.Foghorn))
        self.favoriteGag = OnscreenImage(parent = self.playerInfo, 
            image = gag, pos = FavoriteGagPos, 
            scale = (1.65, 1.65, 1.65))
        self.favoriteGag.setBin('gui-popup', 20)
        
        self.favoriteGagGlow = OnscreenImage(parent = self.playerInfo,
            image = glow, pos = FavoriteGagPos, color = GagGlowColor,
            scale = (0.8, 0.8, 0.8))
        
        self.favoriteGagGlow.setBin('gui-popup', 10)
        self.favoriteGagGlow.setDepthTest(False)
        self.favoriteGagGlow.setDepthWrite(False)
        
        self.favoriteGagName = OnscreenText(parent = self.playerInfo,
            text = CIGlobals.Foghorn, font = CIGlobals.getToonFont(),
            pos = FavoriteGagNamePos, mayChange = 1)
        ################################################################################
        # GUI elements showing gag experience on the right-side of the gag exp panel   #
        ################################################################################
        
        self.gagExpFrame = DirectFrame(parent = self, relief = None, pos = (0.085, 0, 0.15))
        self.trackLabels = []
        self.trackIncLabels = []
        self.trackBars = []
        self.trackBarsOffset = 0
        
        for i in range(len(GagGlobals.TrackNameById.values())):
            track = GagGlobals.TrackNameById.values()[i]
            color = GagGlobals.TrackColorByName.get(track)
            label = DirectLabel(parent = self.gagExpFrame, relief = None, text = track.upper(), 
                text_scale = 0.05, text_align = TextNode.ARight, pos = (0.13, 0, -0.09 * i),
                text_pos = (0, -0.02))
            incrementLabel = DirectLabel(parent = self.gagExpFrame, relief = None, text = '',
                text_scale = 0.05, text_align = TextNode.ALeft, pos = (0.65, 0, -0.09 * i),
                text_pos = (0, -0.02))
            progressBar = DirectWaitBar(parent = self.gagExpFrame, relief = DGG.SUNKEN,
                frameSize = (-1, 1, -0.15, 0.15), borderWidth = (0.02, 0.02), scale = 0.25,
                frameColor = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1),
                barColor = (color[0], color[1], color[2], 1), text = '0/0',
                text_scale = 0.18, text_fg = (0, 0, 0, 1), text_align = TextNode.ACenter,
                text_pos = (0, -0.05), pos = (0.4, 0, -0.09 * i))
            self.trackLabels.append(label)
            self.trackIncLabels.append(incrementLabel)
            self.trackBars.append(progressBar)
            
        ################################################################################
        
        self.congratsLeft = OnscreenText(parent = self.playerInfo, pos = (-0.1, 0.125, -0.1), text = '',
            scale = 0.06, align = TextNode.ARight)
        self.congratsLeft.setR(-30)
        self.congratsRight = OnscreenText(parent = self.playerInfo, pos = (0.1, 0.125, 0.1), text = '',
            scale = 0.06, align = TextNode.ALeft)
        self.congratsRight.setR(30)
        
        glow.removeNode()
        invIcons.removeNode()
        gagShopNodes.removeNode()
        dialogBox.removeNode()
        
    def __getAvatarTextScale(self):
        totalWidth = self.avatarText.node().getWidth()
        panelWidth = 9.2
        defaultTextScale = 1.0
        
        scale = min(defaultTextScale, defaultTextScale / (totalWidth / panelWidth))
        return (scale, scale, scale)
        
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
    
    def setPanelData(self, panelData):
        self.panelData = panelData
        self.avatarText['text'] = self.panelData.avatarName
        self.avatarNamePanel.setScale(self.__getAvatarTextScale())
        
        # Let's set the data for our gag experience here.
        for i in range(len(self.trackLabels)):
            track = self.panelData.getTrackByName(GagGlobals.TrackNameById.values()[i])
            bar = self.trackBars[i]
            bar['text'] = '%d/%d' % (track.exp, track.maxExp)
            
            # When the maximum experience of a track isn't 0, we know it isn't unlocked.
            if track.maxExp == -1:
                bar.hide()

            self.trackIncLabels[i]['text'] = ''
            self.trackIncLabels[i].show()

    def __chooseRewardShot(self, av):
        shotChoices = [(0, 8, av.getHeight() * 0.66, 179, 15, 0),
                       (5.2, 5.45, av.getHeight() * 0.66, 131.5, 3.6, 0)]
        shot = random.choice(shotChoices)
        return shot
        
    def getGagExperienceInterval(self):
        avatar = self.panelData.avatar
        intervals = []

        shot = self.__chooseRewardShot(avatar)

        intervals.append(Func(base.camera.reparentTo, avatar))
        intervals.append(Func(base.camera.setPosHpr, *shot))
        intervals.append(Func(self.congratsLeft.hide))
        intervals.append(Func(self.congratsRight.hide))
        intervals.append(Func(self.panelContentsTitle.setText, GagPanelName))
        intervals.append(Func(self.setFavoriteGag, self.panelData.favoriteGag))
        intervals.append(Func(self.gagExpFrame.show))
        intervals.append(Func(self.playerInfo.show))
        intervals.append(Wait(1.0))
        
        for i in range(len(self.trackLabels)):
            track = self.panelData.getTrackByName(GagGlobals.TrackNameById.values()[i])
            intervals.extend(self.getTrackIntervalList(track, i))
        
        return intervals
    
    def getNextExpValue(self, newValue, track):
        if newValue < track.maxExp or track.maxExp == 0:
            return track.maxExp
        else:
            levels = GagGlobals.TrackExperienceAmounts[track.name]
            index = levels.index(track.maxExp)
            
            if index + 1 < len(levels):
                return levels[index + 1]
            return -1
    
    def incrementExp(self, trackIndex, track, newValue):
        bar = self.trackBars[trackIndex]
        nextExp = GagGlobals.getMaxExperienceValue(newValue, track.name)
        oldValue = bar['value']
        color = GagGlobals.TrackColorByName.get(track.name)
        
        bar['text'] = '%d/%d' % (newValue, nextExp)
        bar['range'] = nextExp if not nextExp == -1 else newValue
        bar['value'] = newValue
        bar['barColor'] = (color[0], color[1], color[2], 1)
        
    def resetBarColor(self, trackIndex):
        color = GagGlobals.TrackColorByName.get(GagGlobals.TrackNameById.values()[trackIndex])
        self.trackBars[trackIndex]['barColor'] = (color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, 1)
    
    def showTrackIncLabel(self, trackIndex, track, increment):
        label = self.trackIncLabels[trackIndex]

        # Only show increments when that track is unlocked.
        if track.exp != -1:
            label['text'] = '+%d' % increment
        label.show()
    
    def getTrackIntervalList(self, track, trackIndex):
        tickDelay = 1.0 / 60
        intervalList = []
        
        intervalList.append(Func(self.showTrackIncLabel, trackIndex, track, track.increment))
        
        barTime = 2.0 if track.exp > 0 else 0.25
        numTicks = int(math.ceil(barTime / tickDelay))
        for i in range(numTicks):
            t = (i + 1) / float(numTicks)
            newValue = int(track.exp + t * track.increment + 0.5)
            intervalList.append(Func(self.incrementExp, trackIndex, track, newValue))
            intervalList.append(Wait(tickDelay))
        
        intervalList.append(Func(self.resetBarColor, trackIndex))
        intervalList.append(Wait(0.2))
        
        if track.maxExp > 0 and (track.exp + track.increment) >= track.maxExp:
            gagIndex = GagGlobals.TrackExperienceAmounts.get(track.name).index(track.maxExp) + 1
            newGag = GagGlobals.TrackGagNamesByTrackName.get(track.name)[gagIndex]
            intervalList.append(self.getShowGagUnlockedInterval(track.name, newGag))
        
        return intervalList
    
    def getShowGagUnlockedInterval(self, track, gagName):
        seq = Sequence(
            Func(self.gagExpFrame.hide),
            Func(self.panelContentsTitle.setText, 'Gag Unlocked!'),
            Func(self.playerInfo.show),
            Func(self.setFavoriteGag, gagName),
            Func(self.favoriteGagName.setY, -0.35),
            Func(self.favoriteGagText.setY, 0.105),
            Func(self.favoriteGagText.setText, 'New %s Gag' % track),
            Func(self.bonusText.hide),
            Func(self.playerInfo.setPos, 0, 0, 0),
        Func(self.playerInfo.initialiseoptions, DirectFrame))
        seq.append(self.getCongratsInterval())
        seq.append(Wait(1.0))
        seq.append(self.getHideGagUnlockedInterval())
        seq.append(Func(self.gagExpFrame.show))
        seq.append(Wait(0.5))
        return seq
        
    def getHideGagUnlockedInterval(self):

        def correctPositioning(guiElement, pos):
            guiElement['pos'] = pos
        
        seq = Sequence(
            Func(self.panelContentsTitle.setText, GagPanelName),
            Func(self.setFavoriteGag, self.panelData.favoriteGag),
            Func(self.playerInfo.setX, -0.5),
            Func(correctPositioning, self.favoriteGagName, FavoriteGagNamePos),
            Func(self.favoriteGagText.setText, FavoriteGag),
            Func(correctPositioning, self.favoriteGagText, FavoriteGagTitlePos),
            Func(self.congratsLeft.hide),
            Func(self.congratsRight.hide)
        )
        
        return seq
        
    def __getRandomCongratsPair(self):
        msgs = list(NewGagCongratsMessages)
        
        msg = msgs[random.randint(0, len(msgs) - 1)]
        msgs.remove(msg)

        return (msg, msgs[random.randint(0, len(msgs) - 1)])
        
    def getCongratsInterval(self):
        msgs = self.__getRandomCongratsPair()
        self.congratsLeft['text'] = msgs[0]
        self.congratsRight['text'] = msgs[1]
        
        sfx = loader.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')
        sfx.setLoop(False)
        sfx.setVolume(1.0)
        
        def makeSequence(text):
            seq = Sequence(Wait(1.0), Func(text.show))
            seq.append(Func(sfx.play))
            seq.append(CIGlobals.makePulseEffectInterval(text, 1.0, 0.01, 1.05, 0.5, 0.25))
            seq.append(Func(sfx.stop))
            return seq
        
        return Sequence(makeSequence(self.congratsLeft), makeSequence(self.congratsRight))
        
    def setFavoriteGag(self, gagName):
        invIcons = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam')
        gag = invIcons.find(GagGlobals.InventoryIconByName.get(gagName))
        self.favoriteGagName.setText(gagName)
        self.favoriteGag['image'] = gag
        invIcons.removeNode()
        
    def destroy(self):
        if self.titlePanel:
            self.titlePanel.destroy()
        if self.avatarText:
            self.avatarText.destroy()
        if self.avatarNamePanel:
            self.avatarNamePanel.destroy()
        if self.panelContentsTitle:
            self.panelContentsTitle.destroy()
        if self.favoriteGag:
            self.favoriteGag.destroy()
        if self.favoriteGagGlow:
            self.favoriteGagGlow.destroy()
        if self.favoriteGagName:
            self.favoriteGagName.destroy()
        if self.playerInfo:
            self.playerInfo.destroy()
        if self.trackLabels:
            for label in self.trackLabels:
                label.destroy()
        if self.trackIncLabels:
            for label in self.trackIncLabels:
                label.destroy()
        if self.trackBars:
            for bar in self.trackBars:
                bar.destroy()
        if self.congratsLeft:
            self.congratsLeft.destroy()
        if self.congratsRight:
            self.congratsRight.destroy()
        if self.gagExpFrame:
            self.gagExpFrame.destroy()
        if self.panelData:
            self.panelData = None
        del self.titlePanel
        del self.avatarText
        del self.avatarNamePanel
        del self.panelContentsTitle
        del self.favoriteGag
        del self.favoriteGagGlow
        del self.favoriteGagName
        del self.playerInfo
        del self.trackLabels
        del self.trackIncLabels
        del self.trackBars
        del self.gagExpFrame
        del self.congratsLeft
        del self.congratsRight
        del self.panelData
        DirectFrame.destroy(self)
