"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleZone.py
@author Maverick Liberty
@date July 25, 2016

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.battle.RPToonData import RPToonData
from src.coginvasion.gui.RewardPanel import RewardPanel

from direct.interval.IntervalGlobal import Sequence, Func

from collections import OrderedDict

class DistributedBattleZone(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleZone')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.avIds = []
        self.suits = {}
        
        # Keys: avId
        # Values: RPToonData object
        self.rewardPanelData = OrderedDict()
        self.rewardPanel = None
        self.rewardSeq = Sequence()

    def announceGenerate(self):
        self.accept('suitCreate', self.__handleSuitCreate)
        self.accept('suitDelete', self.__handleSuitDelete)
        base.localAvatar.inBattle = True

    def __handleSuitCreate(self, obj):
        self.suits[obj.doId] = obj

    def __handleSuitDelete(self, obj):
        if self.suits.has_key(obj.doId):
            del self.suits[obj.doId]
        
    def disable(self):
        DistributedObject.disable(self)
        self.ignore('suitCreate')
        self.ignore('suitDelete')
        self.reset()
        base.localAvatar.inBattle = False
        
    def setAvatars(self, avIds):
        self.avIds = avIds
    
    def getAvatars(self):
        return self.avIds
    
    def rewardPanelSequenceComplete(self):
        pass
    
    def startRewardSeq(self, timestamp):
        base.localAvatar.b_setAnimState('win')
        self.rewardSeq.append(Func(base.localAvatar.b_setAnimState, 'neutral'))
        self.rewardSeq.append(Func(self.rewardPanelSequenceComplete))
        self.rewardSeq.start(timestamp)
    
    def setToonData(self, netStrings):
        self.rewardPanel = RewardPanel(None)
        for netString in netStrings:
            data = RPToonData(None)
            avId = data.fromNetString(netString)
            self.rewardPanelData[avId] = data
            self.rewardSeq.append(Func(self.rewardPanel.setPanelData, data))
            
    def getToonData(self):
        return self.rewardPanelData
        
    def reset(self):
        self.avIds = []
        self.suits = {}
