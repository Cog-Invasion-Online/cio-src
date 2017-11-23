"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestEmblemGui.py
@author Maverick Liberty
@date November 22, 2017

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval

from panda3d.core import TransparencyAttrib

QUEST_OBJECTIVE = 0
QUEST_AVAILABLE = 1
DISABLED = 2
LOADED = 3

class QuestEmblemGui(DirectFrame):
    notify = directNotify.newCategory('QuestEmblemGui')
    
    def __init__(self, parent):
        DirectFrame.__init__(self, parent)
        
        self.emblem = OnscreenImage(image = loader.loadTexture('phase_5/maps/quest_available_emblem.png'), 
            parent = self)
        self.emblem.setTransparency(TransparencyAttrib.MAlpha)
        self.emblem.setBillboardAxis()
        self.emblem.setTwoSided(1)
            
        glowMdl = loader.loadModel('phase_4/models/minigames/particleGlow.bam')
        self.glow = OnscreenImage(parent = self.emblem, image = glowMdl,
            color = (1.0, 1.0, 0.4, 1.0), scale = (3.0, 3.0, 3.0),
        pos = (0, 0.05, 0))
        self.glow.setBin('gui-popup', 10)
        
        glowMdl.removeNode()
        
        self.track = None
        self.state = LOADED
        
    def setEmblem(self, questAvailable = QUEST_AVAILABLE):
        # Sets the texture of the emblem.
        texture = loader.loadTexture('phase_5/maps/quest_available_emblem.png')
        if questAvailable is 0:
            texture = loader.loadTexture('phase_5/maps/quest_scroll_emblem.png')
        self.state = questAvailable
        self.emblem.setImage(texture)
        self.emblem.setTransparency(TransparencyAttrib.MAlpha)
        self.emblem.setBillboardAxis()
        self.emblem.setTwoSided(1)
        
    def start(self, bobMinHeight = 0.5, bobMaxHeight = 0.5):
        # Shows the emblem and starts the bobbing animation.
        
        # Stops so we don't have two animations running at once.
        self.stop()
        
        # Shows the emblem
        self.show()
        
        # Let's create the animation and run the animation.
        self.track = Sequence(
            LerpPosInterval(self.emblem, 1.35, pos = (0, 0, self.getZ() - bobMinHeight), 
                startPos = (0, 0, bobMaxHeight),
                blendType = 'easeInOut'),
            LerpPosInterval(self.emblem, 1.35, pos = (0, 0, bobMaxHeight), 
                startPos = (0, 0, self.getZ() - bobMinHeight),
                blendType = 'easeInOut')
        ).loop()
        
    def stop(self):
        # Hides the emblem and stops the animation.
        self.hide()
        
        if self.track:
            self.track.pause()
            self.track = None
            
        self.state = DISABLED
        
    def destroy(self):
        self.stop()
        self.glow.destroy()
        self.emblem.destroy()
        self.state = None
        DirectFrame.destroy(self)
