"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CutsceneGUI.py
@author Maverick Liberty
@date November 25, 2017

"""

from direct.fsm.StateData import StateData
from direct.gui.DirectFrame import DirectFrame
from direct.interval.IntervalGlobal import ParallelEndTogether, LerpPosInterval

BAR_HEIGHT = 0.30
BAR_MOVE_DURATION = 1.75

class CutsceneGUI(StateData):
    
    def __init__(self):
        StateData.__init__(self, doneEvent = 'cutsceneBarsDown')
        self.topBar = None
        self.btmBar = None
        self.ival = None
        self.load()
        
    def takeCameraControlTo(self, pos, hpr):
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.camera.reparentTo(render)
        base.camera.setPosHpr(pos[0], pos[1], pos[2],
            hpr[0], hpr[1], hpr[2])
        
    def returnCameraControl(self):
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        
    def hideOtherGUIElements(self):
        if base.localAvatarReachable():
            base.aspect2d.hide()
            base.localAvatar.disableGagKeys()
            base.localAvatar.chatInput.fsm.request('idle')
            base.localAvatar.chatInput.disableKeyboardShortcuts()
            base.localAvatar.questManager.disableShowQuestsHotkey()
            base.localAvatar.allowA2dToggle = False
            
    def showOtherGUIElements(self):
        if base.localAvatarReachable():
            base.aspect2d.show()
            base.localAvatar.enableGagKeys()
            base.localAvatar.chatInput.enableKeyboardShortcuts()
            base.localAvatar.questManager.enableShowQuestsHotkey()
            base.localAvatar.allowA2dToggle = True
        
    def hide(self):
        if self.topBar:
            self.topBar.hide()
        if self.btmBar:
            self.btmBar.hide()
            
    def show(self):
        if self.topBar:
            self.topBar.show()
        if self.btmBar:
            self.btmBar.show()
        
    def enter(self):
        self.topBar = DirectFrame(parent = render2d, 
            frameSize = (2,-2,0.3,-0.3), 
            frameColor=(0, 0, 0, 1), pos=(0,1,1.4))
        self.btmBar = DirectFrame(parent = render2d, 
            frameSize = (2,-2,0.3,-0.3), 
            frameColor=(0,0,0,1), pos=(0,-1,-1.4))
    
        self.ival = ParallelEndTogether(
            LerpPosInterval(self.topBar,
                duration=BAR_MOVE_DURATION,
                pos=(0,1,1.0),
                startPos=(0,1,1.4),
                blendType='easeOut'
            ),
                                        
            LerpPosInterval(self.btmBar,
                duration=BAR_MOVE_DURATION,
                pos=(0,-1,-1.0),
                startPos=(0,-1,-1.4),
                blendType='easeOut'
            ),
        )
        
        self.hideOtherGUIElements()
        self.ival.start()
        return StateData.enter(self)
    
    def exit(self):
        if self.ival:
            self.ival.pause()
            self.ival = None
        if self.topBar:
            self.topBar.destroy()
            self.topBar = None
        if self.btmBar:
            self.btmBar.destroy()
            self.btmBar = None
        self.showOtherGUIElements()
        return StateData.exit(self)