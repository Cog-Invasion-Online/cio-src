"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleZone.py
@author Maverick Liberty
@date July 25, 2016

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.battle.RPToonData import RPToonData
from src.coginvasion.gui.RewardPanel import RewardPanel
from src.coginvasion.globals import CIGlobals
import BattleGlobals

from direct.interval.IntervalGlobal import Sequence, Func, Wait

from collections import OrderedDict

class DistributedBattleZone(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleZone')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.avIds = []
        self.suits = {}
        
        # Keys: avId
        # Values: RPToonData objects
        self.rewardPanelData = OrderedDict()
        self.rewardPanel = None
        self.rewardSeq = Sequence()

    def announceGenerate(self):
        self.accept('suitCreate', self.__handleSuitCreate)
        self.accept('suitDelete', self.__handleSuitDelete)
        base.localAvatar.setMyBattle(self)

    def __handleSuitCreate(self, obj):
        self.suits[obj.doId] = obj

    def __handleSuitDelete(self, obj):
        if self.suits.has_key(obj.doId):
            del self.suits[obj.doId]
        
    def disable(self):
        self.reset()
        self.ignore('suitCreate')
        self.ignore('suitDelete')
        base.localAvatar.setMyBattle(None)
        DistributedObject.disable(self)
        
    def setAvatars(self, avIds):
        self.avIds = avIds
    
    def getAvatars(self):
        return self.avIds
    
    def rewardSequenceComplete(self, timestamp):
        pass
    
    def startRewardSeq(self, timestamp):
        timestamp = globalClockDelta.localElapsedTime(timestamp)
        self.rewardSeq.start(timestamp)
        
    def disableAvatarControls(self):
        # place will be None if the avatar is in the tutorial.
        place = base.cr.playGame.getPlace()
        
        # This quirky walkData if-else is because the current tutorial isn't
        # programmed in as a "Place"
        walkData = place.walkStateData if place else self

        if not place and base.localAvatar.GTAControls:
            walkData.mouseMov.disableMovement(allowReEnable = False)
        if place:
            place.fsm.request('stop')

        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopSmartCamera()
        base.camera.wrtReparentTo(render)
        base.localAvatar.collisionsOff()
        base.localAvatar.disableGags()
        base.localAvatar.stopTrackAnimToSpeed()
        base.localAvatar.hideGagButton()
            
    def enableAvatarControls(self):
        # place will be None if the avatar is in the tutorial.
        place = base.cr.playGame.getPlace()
        
        # This quirky walkData if-else is because the current tutorial isn't
        # programmed in as a "Place"
        walkData = place.walkStateData if place else self
        
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableGags()
        base.localAvatar.startTrackAnimToSpeed()
        base.localAvatar.showGagButton()
        if not base.localAvatar.walkControls.getCollisionsActive():
            base.localAvatar.walkControls.setCollisionsActive(1)
        base.localAvatar.enableAvatarControls()
        if not place and base.localAvatar.GTAControls:
            walkData.mouseMov.enableMovement()

        base.localAvatar.setBusy(1)
    
    def setToonData(self, netStrings):
        self.rewardPanel = RewardPanel(None)
        self.rewardSeq.append(Func(self.disableAvatarControls))
        self.rewardSeq.append(Func(base.camLens.setMinFov, BattleGlobals.VictoryCamFov / (4. / 3.)))
        self.rewardSeq.append(Func(base.localAvatar.detachCamera))
        self.rewardSeq.append(Func(base.localAvatar.b_setAnimState, 'win'))
        self.rewardSeq.append(Func(base.localAvatar.loop, 'win'))
        
        for netString in netStrings:
            data = RPToonData(None)
            avId = data.fromNetString(netString)
            self.rewardPanelData[avId] = data
            self.rewardPanel.setPanelData(data)
            intervalList = self.rewardPanel.getGagExperienceInterval()
            
            self.rewardSeq.append(Func(self.rewardPanel.setPanelData, data))
            self.rewardSeq.extend(intervalList)
            self.rewardSeq.append(Wait(1.0))
        self.rewardSeq.append(Func(self.rewardPanel.destroy))
        
        if base.localAvatar.inTutorial:
            self.rewardSeq.append(Func(self.enableAvatarControls))
        self.rewardSeq.append(Func(base.localAvatar.b_setAnimState, 'neutral'))
        self.rewardSeq.append(Func(base.camLens.setMinFov, CIGlobals.DefaultCameraFov / (4. / 3.)))
        self.rewardSeq.append(Func(self.sendUpdate, 'acknowledgeAvatarReady', []))
            
    def getToonData(self):
        return self.rewardPanelData
        
    def reset(self):
        self.avIds = []
        self.suits = {}
        self.rewardPanelData = OrderedDict()
        if self.rewardPanel:
            self.rewardPanel.destroy()
        self.rewardPanel = None
        if self.rewardSeq:
            self.rewardSeq.pause()
        self.rewardSeq = Sequence()
