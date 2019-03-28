"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file KOTHKingGui.py
@author Maverick Liberty
@date June 17, 2016

HAPPY BIRTHDAY COG INVASION ONLINE!!!
        2 YEAR ANNIVERSARY!

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, OnscreenText, OnscreenImage, DGG
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals
from src.coginvasion.base import ToontownIntervals

import random
from src.coginvasion.toon import ToonGlobals

class KOTHKingGui(DirectFrame):
    notify = directNotify.newCategory('KOTHKingGui')
    
    def __init__(self, mg, king, points):
        DirectFrame.__init__(self, parent = aspect2d)
        self.setBin('gui-popup', 60)
        self.mg = mg
        
        # Let's create the background
        box = DGG.getDefaultDialogGeom()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4), parent = self)
        
        # Let's create the header
        toonFont = CIGlobals.getToonFont()
        minnieFont = CIGlobals.getMinnieFont()
        
        name = 'Nobody'
        
        if king:
            name = king.getName()
            self.kingId = king.doId
        else:
            king = base.localAvatar
            self.kingId = 0
        
        self.title = OnscreenText(text = '%s is King!' % name, pos = (0, 0.5, 0), font = toonFont, 
            scale = 0.12, parent = self, shadow = (0.5, 0.5, 0.5, 0.6))
        
        # Let's create the Toon head
        headFrame = self.attachNewNode('head')
        headFrame.setPosHprScale(0, 0, -0.1, 180, 0, 0, 0.3, 0.3, 0.3)
        head = ToonGlobals.generateGuiHead(king)
        head.reparentTo(headFrame)
        
        # Let's create the points text
        self.amt_label = OnscreenText(text = 'Your Points: 0', pos = (-0.012, -0.4, 0), font = toonFont,
            scale = 0.12, parent = self, shadow = (0.5, 0.5, 0.5, 0.6))
        self.amt_label.hide()
        
        # Let's create the bad news text
        self.motivator = OnscreenText(text = 'Better luck next time!', pos = (0, -0.6, 0), font = minnieFont,
            scale = 0.125, parent = self, fg = (1, 0, 0, 1), shadow = (0.2, 0.2, 0.2, 1))
        self.motivator.hide()
        
        self.easterEgg = False
        
        if 50 < points != 100:
            self.motivator['fg'] = (0, 1, 0, 1)
            self.motivator.setText('Great job!')
        elif points == 100:
            self.motivator['fg'] = (0, 1, 0, 1)
            if random.randint(0, 100) <= 10:
                self.motivator.setText('YOU THE REAL MVP!')
                self.easterEgg = True
            else:
                self.motivator.setText('AMAZING!')
        
        # Let's create the sound effects
        self.zeroPointsSfx = loader.loadSfx('phase_4/audio/sfx/MG_neg_buzzer.ogg')
        self.poorScoreSfx = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_no_bonus.ogg')
        self.goodScoreSfx = loader.loadSfx('phase_4/audio/sfx/MG_pairing_match_bonus_both.ogg')
        self.stomperSfx = loader.loadSfx('phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg')
        self.fireworkSfx = loader.loadSfx('phase_4/audio/sfx/firework_explosion_02.ogg')
        self.perfectSfx = loader.loadSfx('phase_5/audio/sfx/SZ_MM_fanfare.ogg')
        self.tick_fastSfx = loader.loadSfx('phase_4/audio/sfx/MG_maze_pickup.ogg')
        self.tick_slowSfx = loader.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        self.easterEggSfx = loader.loadSfx('phase_4/audio/sfx/avatar_emotion_very_sad.ogg')
        
        # Let's create the basic sequence
        self.pointsSeq = Sequence(Func(self.amt_label.show),
            Wait(0.25))
        
        self.seqLevel = 0
        self.fakeNumber = 0
        self.points = points
    
    def start(self):
        base.transitions.fadeScreen(0.5)
        if self.points == 0:
            self.__doZero()
        else:
            self.__doRegular()
            
    def destroy(self):
        # Let's stop the sequence.
        if self.pointsSeq:
            self.pointsSeq.finish()
        self.pointsSeq = None
        
        # Let's stop and destroy all the sounds.
        if self.zeroPointsSfx:
            self.zeroPointsSfx.stop()
            self.poorScoreSfx.stop()
            self.goodScoreSfx.stop()
            self.stomperSfx.stop()
            self.fireworkSfx.stop()
            self.perfectSfx.stop()
            self.tick_fastSfx.stop()
            self.tick_slowSfx.stop()
            self.easterEggSfx.stop()
        self.zeroPointsSfx = None
        self.poorScoreSfx = None
        self.goodScoreSfx = None
        self.stomperSfx = None
        self.fireworkSfx = None
        self.perfectSfx = None
        self.tick_fastSfx = None
        self.tick_slowSfx = None
        self.easterEggSfx = None
        
        # Let's destroy all the variables.
        self.points = None
        self.easterEgg = None
        self.seqLevel = None
        self.fakeNumber = None
        self.kingId = None
        self.mg = None
        
        # Let's destroy all the frames.
        if self.bg:
            self.bg.destroy()
            self.title.destroy()
            self.amt_label.destroy()
            self.motivator.destroy()
        self.bg = None
        self.title = None
        self.amt_label = None
        self.motivator = None
        
        DirectFrame.destroy(self)
        
    def unload(self):
        pass
    
    def hideFinalScores(self):
        base.transitions.noTransitions()
        self.hide()
        
    def handleExit(self):
        winner = 0
        if self.kingId != 0:
            winner = 1
        self.pointsSeq.append(Sequence(Wait(5), Func(self.mg.gameOver, winner, [self.kingId])))
        return
        
    def __doZeroEffect(self, task):
        if self.seqLevel == 0:
            task.delayTime = 0.2
            self.tick_fastSfx.play()
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.fakeNumber += 1
            
            if self.fakeNumber == 3:
                self.seqLevel = 1
        elif self.seqLevel == 1:
            task.delayTime = 0.35
            self.tick_slowSfx.play()
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.fakeNumber += 1
            
            if self.fakeNumber == 6:
                self.seqLevel = 2
                task.delayTime = 0.35
                
        elif self.seqLevel == 2:
            task.delayTime = 0.10
            self.tick_fastSfx.play()
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.fakeNumber -= 1
            
            if self.fakeNumber == -1:
                self.stomperSfx.play()
                ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self.amt_label, 'effect'))
                self.pointsSeq = Sequence(Wait(0.25), Func(self.zeroPointsSfx.play), Func(self.motivator.show))
                self.handleExit()
                self.pointsSeq.start()
                return task.done
        return task.again
    
    def __doRegularEffect(self, task):
        if self.points <= 5 and self.seqLevel == 0:
            self.seqLevel = 2
            
        if self.seqLevel == 0:
            task.delayTime = 0.35
            self.fakeNumber += 1
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.tick_slowSfx.play()
            
            if self.fakeNumber == 2:
                task.delayTime = 0.25
                self.seqLevel = 1
        
        elif self.seqLevel == 1:
            if self.points <= 50:
                task.delayTime = 0.12
            elif 50 < self.points != 100:
                task.delayTime = 0.075
            else:
                task.delayTime = 0.065
            self.fakeNumber += 1
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.tick_fastSfx.play()
            
            if self.fakeNumber == self.points - 5:
                task.delayTime = 0.25
                self.seqLevel = 2
        
        elif self.seqLevel == 2:
            task.delayTime = 0.35
            self.fakeNumber += 1
            self.amt_label.setText('Your Points: %s' % str(self.fakeNumber))
            self.tick_slowSfx.play()
            
            if self.fakeNumber == self.points:
                if self.points <= 50:
                    self.pointsSeq = Sequence(Wait(0.25), Func(self.poorScoreSfx.play), Func(self.motivator.show))
                elif 50 < self.points != 100:
                    pulse = ToontownIntervals.getPulseLargerIval(self.amt_label, 'effect')
                    self.pointsSeq = Sequence(Wait(0.25), Func(self.goodScoreSfx.play),
                        Func(ToontownIntervals.start, pulse), Func(self.motivator.show))
                elif self.points == 100:
                    pulse = ToontownIntervals.getPulseLargerIval(self.amt_label, 'effect')
                    self.pointsSeq = Sequence(Wait(0.25), Func(ToontownIntervals.start, pulse), 
                        Func(self.fireworkSfx.play), Wait(0.25), Func(self.perfectSfx.play), Func(self.motivator.show))
                    
                    if self.easterEgg:
                        self.pointsSeq.append(Sequence(Wait(0.30), Func(self.easterEggSfx.play)))
                self.handleExit()
                self.pointsSeq.start()
                return task.done
        return task.again
        
    def __doZero(self):
        self.pointsSeq.append(Sequence(
            Func(taskMgr.add, self.__doZeroEffect, 'Point Effect')
        ))
        self.pointsSeq.start()
        
    def __doRegular(self):
        self.pointsSeq.append(Sequence(
            Func(taskMgr.add, self.__doRegularEffect, 'Point Effect')
        ))
        self.pointsSeq.start()