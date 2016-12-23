########################################
# Filename: KOTHGui.py
# Created by: DecodedLogic (16Jun16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, OnscreenText, OnscreenImage

from src.coginvasion.globals import CIGlobals

class KOTHGui(DirectFrame):
    notify = directNotify.newCategory('KOTHGui')
    
    pointsSfx = None
    points = None
    
    def __init__(self):
        # Let's load up the DirectFrame
        DirectFrame.__init__(self, parent = base.a2dTopLeft, relief = None, 
            pos = (0.275, 1, -0.7), sortOrder = 0)
        
        # The variables we're going to be using.
        self.pointsSfx = loader.loadSfx('phase_4/audio/sfx/MG_maze_pickup.ogg')
        self.points = 0
        
        # Background because it won't work for whatever reason.
        gui = loader.loadModel('phase_4/models/gui/purchase_gui.bam')
        panel = gui.find('**/yellowPanel')
        self.bg = OnscreenImage(image = panel, parent = self)
        
        # Let's setup the header text.
        self.title = OnscreenText(text = 'Capture Points', font = CIGlobals.getMinnieFont(), 
            parent = self, scale = 0.0475, pos = (0, 0.18), fg = (1, 0, 0, 1), 
        shadow = (0.2, 0.2, 0.2, 1))
        
        # Let's setup the amount text.
        self.amt_label = OnscreenText(text = str(self.points), font = CIGlobals.getToonFont(),
            parent = self, scale = 0.15, pos = (0, 0.03525), shadow = (0.5, 0.5, 0.5, 0.6))
        
        # Let's setup the info text.
        self.info = OnscreenText(text = 'First Toon to 100 points wins!\nEarn points by standing on the\nhill after capturing it.',
            parent = self, font = CIGlobals.getToonFont(), scale = 0.035, pos = (0, -0.05), 
        fg = (1.5, 0, 0, 1), shadow = (0.2, 0.2, 0.2, 1))
        
        # We're not ready to show the GUI yet.
        self.hide()
        
    def show(self):
        self.title.show()
        self.amt_label.show()
        self.info.show()
        self.bg.show()
        
    def hide(self):
        self.title.hide()
        self.amt_label.hide()
        self.info.hide()
        self.bg.hide()
        
    def destroy(self):
        self.title.destroy()
        self.amt_label.destroy()
        self.info.destroy()
        self.bg.destroy()
        self.title = None
        self.amt_label = None
        self.info = None
        self.bg = None
        
        # Let's get rid of the sound.
        self.pointsSfx.stop()
        self.pointsSfx = None
        
        self.points = None
        DirectFrame.destroy(self)
        
    def setPoints(self, points):
        self.points = points
        self.amt_label.setText(str(self.points))
        self.pointsSfx.play()
        
    def getPoints(self):
        return self.points
        