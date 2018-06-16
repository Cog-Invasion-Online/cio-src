"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ArcadeModePage.py
@author Maverick Liberty
@date June 12, 2018

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.gui.DirectGui import DirectFrame, DirectEntry, DirectLabel, DirectButton, DGG
from panda3d.core import TextNode

from src.coginvasion.book.BookPage import BookPage
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.globals import CIGlobals

class ArcadeModePage(BookPage):
    
    def __init__(self, book):
        BookPage.__init__(self, book, 'Arcade Mode')
        
        self.fsm = ClassicFSM('ArcadeModePage', [
            State('off', self.enterOff, self.exitOff),
            State('baseSection', self.enterBaseSection, self.exitBaseSection),
            State('queueSection', self.enterQueueSection, self.exitQueueSection),
            State('createSection', self.enterCreateSection, self.exitCreateSection)
        ], 'off', 'off')
        self.fsm.enterInitialState()
        
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
    
    def enterBaseSection(self):
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui.bam')
        codeBoxGui = cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox')
        
        self.codeBox = DirectFrame(parent = self.book, relief = None, image = loader.loadTexture('phase_4/maps/GreenGUIBox.png'), 
            pos = (-0.45, 0, 0.20), image_scale = (0.435, 0.0, 0.145), image_color = (1.2, 1.2, 1.2, 1.0), image_pos = (0.025, 0.0, 0.0))
        self.codeBox.setTransparency(1)
        
        self.joinMatchLabel = DirectLabel(parent = self.book, relief = None, text = 'Join', pos = (-0.45, 0, 0.48),
            text_scale = 0.1, scale = 1.0)
        
        self.codeLabel = DirectLabel(parent = self.codeBox, relief = None, text = 'Enter a Match Code', 
            pos = (0.0, 0.0, 0.15), text_scale = 0.07, scale = 1.0)
        self.codeInput = DirectEntry(parent = self.codeBox, relief = None, scale = 0.08, 
            pos = (-0.33, 0, 0), 
            borderWidth = (0.05, 0.05), 
            state = DGG.NORMAL, text_align = TextNode.ALeft, 
            text_scale = 0.8, 
            width = 10.5, numLines = 1, focus = 1, backgroundFocus = 0, cursorKeys = 1, 
            text_fg = (0, 0, 0, 1), suppressMouse = 1, 
            autoCapitalize = 0)
        self.codeInput.setTransparency(1)
        
        btnGeom = CIGlobals.getDefaultBtnGeom()
        self.submitCodeBtn = DirectButton(parent = self.codeBox, relief = None, geom = btnGeom,
            text = 'Join', text_scale = 0.07, text_pos = (0.0, -0.015), pos = (0.0, 0.0, -0.225), scale = 0.85)
    
    def exitBaseSection(self):
        self.joinMatchLabel.destroy()
        self.codeBox.destroy()
        self.codeLabel.destroy()
        self.codeInput.destroy()
        self.submitCodeBtn.destroy()
        del self.joinMatchLabel
        del self.codeBox
        del self.codeLabel
        del self.codeInput
        del self.submitCodeBtn
    
    def enterQueueSection(self):
        cogDoGui = loader.loadModel('phase_5/models/cogdominium/tt_m_gui_cmg_miniMap_cards.bam')
        frame = cogDoGui.find('**/tt_t_gui_cmg_miniMap_frame')
        arenaPhoto = loader.loadTexture('phase_14/maps/ttc_arena.png')
        
        self.subTitle = DirectLabel(parent = self.book, relief = None, text = 'Lobby', pos = (0, 0, 0.55),
            text_scale = 0.075)
        
        self.arenaPhoto = DirectLabel(parent = self.book, relief = None, image = arenaPhoto,
            image_scale = 0.29, pos = (-0.45, 0, 0.05))

        self.matchCode = DirectLabel(parent = self.arenaPhoto, relief = None, 
            text = 'Session Code: CIO-UvRX', text_scale = 0.0725, pos = (0, 0, 0.40))

        self.arenaFrame = DirectLabel(parent = self.arenaPhoto, relief = None, image = frame,
            image_scale = 0.65)
        self.arenaFrame.setTransparency(1)

        self.arenaName = DirectLabel(parent = self.arenaFrame, relief = None, text = 'Toontown Central',
            pos = (0, 0, -0.40), text_scale = 0.07)
        
        self.matchPlayers = CIGlobals.makeDefaultScrolledList(parent = self.book, pos = (0.40, 0, 0),
            listFrameSizeZ = 0.54, listZorigin = -0.5)
        self.matchPlayers.decButton['pos'] = (self.matchPlayers.decButton.getX(), 0.0, -0.3)
        
        
        cogDoGui.removeNode()
    
    def exitQueueSection(self):
        self.subTitle.destroy()
        self.arenaPhoto.destroy()
        self.matchCode.destroy()
        self.arenaFrame.destroy()
        self.arenaName.destroy()
        self.matchPlayers.destroy()
        del self.subTitle
        del self.arenaPhoto
        del self.matchCode
        del self.arenaFrame
        del self.arenaName
        del self.matchPlayers
    
    def enterCreateSection(self):
        pass
    
    def exitCreateSection(self):
        pass
    
    def load(self):
        BookPage.load(self)
        
        # This icon is a placeholder until we have a new icon designed.
        self.icon = QuestGlobals.getCogIcon()
    
    def enter(self):
        BookPage.enter(self)
        #self.fsm.request('baseSection')
        self.fsm.request('queueSection')
        
    def exit(self):
        self.fsm.requestFinalState()
        BookPage.exit(self)
        
    def unload(self):
        del self.book
        del self.fsm
        BookPage.unload(self)
