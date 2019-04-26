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
from src.coginvasion.battle.GameRules import GameRules
from src.coginvasion.gui.RewardPanel import RewardPanel
from src.coginvasion.globals import CIGlobals
import BattleGlobals

from direct.interval.IntervalGlobal import Sequence, Func, Wait

from collections import OrderedDict

class DistributedBattleZone(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleZone')
    notify.setInfo(True)
    
    MapFormatString = "phase_14/etc/{0}/{0}.bsp"
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.avIds = []
        self.suits = {}
        self.debris = {}
        
        # Keys: avId
        # Values: RPToonData objects
        self.rewardPanelData = OrderedDict()
        self.rewardPanel = None
        self.rewardSeq = Sequence()

        self.gameRules = self.makeGameRules()
        
        self.lastCameraIndex = 0

        self.map = ""
        
        self.firstMapLoad = True
        
        self.entZoneHandle = None
        self.entZone = 0
        
    def emitSound(self, soundPath, worldPos, volume):
        CIGlobals.emitSound(soundPath, worldPos, volume)
        
    def setEntZone(self, zone):
        self.entZone = zone
        
    def enterEntZone(self, callback = None):
        self.notify.info("Entering the ent zone")
        if callback:
            self.acceptOnce("enterEntZoneComplete", callback)
        self.entZoneHandle = self.cr.addInterest(base.localAvatar.defaultShard, self.entZone,
                                                 'entZone', 'enterEntZoneComplete')
        
    def leaveEntZone(self, callback = None):
        if self.entZoneHandle:
            self.notify.info("Leaving the ent zone")
            if callback:
                self.acceptOnce("leaveEntZoneComplete", callback)
            self.cr.removeInterest(self.entZoneHandle, event = "leaveEntZoneComplete")
            self.entZoneHandle = None
        elif callback:
            # We didn't have interest
            callback()
        
    def getEntZone(self):
        return self.entZone
        
    def __onEnterEntZone_loadMap(self):
        self.notify.info("Map loaded, now in ent zone")
        # We've loaded up the map and are now listening in the
        # entity zone.
        self.d_loadedMap()
        
    def loadTheMap(self):
        base.loadBSPLevel(self.MapFormatString.format(self.map))
        base.bspLevel.reparentTo(render)

    def setMap(self, map):
        self.map = map
        if len(map):
            if self.firstMapLoad and self.entZoneHandle is None:
                self.loadTheMap()
                self.enterEntZone(self.__onEnterEntZone_loadMap)
                self.firstMapLoad = False
            else:
                # We are already in the ent zone, just load the map.
                self.loadTheMap()
                self.d_loadedMap()

    def d_loadedMap(self):
        self.sendUpdate('loadedMap')

    def getMap(self):
        return self.map

    def makeGameRules(self):
        return GameRules(self)

    def getGameRules(self):
        return self.gameRules
        
    def addDebris(self, debris, creatorDoId):
        if debris and not debris.isEmpty():
            self.debris.update({debris : creatorDoId})
        
    def removeDebris(self, debris, silently = 1):
        if not debris or debris.isEmpty():
            return
        
        if not silently:
            clearTasks = base.taskMgr.getTasksNamed('{0}-Clear'.format(debris.getName()))
            usedTaskClear = False
            
            for clearTask in clearTasks:
                if not silently and not usedTaskClear:
                    clearTask.step()
                    usedTaskClear = True
                base.taskMgr.removeTask(clearTask)

        del self.debris[debris]
        
    def clearAvatarDebris(self, avId):
        if avId in self.debris.values():
            for debris, creatorId in self.debris.iteritems():
                if creatorId == avId:
                    self.removeDebris(debris, silently = 0)
        
    def __clearAllDebris(self, silently = 1):
        for debris in self.debris.keys():
            if not debris.isEmpty:
                debris.removeNode()
            self.removeDebris(debris, silently)
        
        self.debris = {}
        
    def d_readyToStart(self):
        self.sendUpdate('readyToStart')

    def generate(self):
        DistributedObject.generate(self)
        
        self.accept('suitCreate', self.__handleSuitCreate)
        self.accept('suitDelete', self.__handleSuitDelete)
        base.localAvatar.setBattleZone(self)
        self.lastCameraIndex = base.localAvatar.smartCamera.cameraIndex
        # Change to over the shoulder mode
        #base.localAvatar.smartCamera.setCameraPositionByIndex(base.localAvatar.smartCamera.OTSIndex)
        base.localAvatar.battleControls = True
        
        from src.coginvasion.szboss import AmbientGeneric, FuncWater, Ropes, InfoBgm, InfoPlayerRelocate, EnvLightGlow, EnvParticleSystem, PointSpotlight
        #base.bspLoader.linkEntityToClass("ambient_generic", AmbientGeneric.AmbientGeneric)
        base.bspLoader.linkEntityToClass("func_water", FuncWater.FuncWater)
        base.bspLoader.linkEntityToClass("rope_begin", Ropes.RopeBegin)
        base.bspLoader.linkEntityToClass("rope_keyframe", Ropes.RopeKeyframe)
        base.bspLoader.linkEntityToClass("info_bgm", InfoBgm.InfoBgm)
        base.bspLoader.linkEntityToClass("info_player_relocate", InfoPlayerRelocate.InfoPlayerRelocate)
        base.bspLoader.linkEntityToClass("env_lightglow", EnvLightGlow.EnvLightGlow)
        base.bspLoader.linkEntityToClass("env_particlesystem", EnvParticleSystem.EnvParticleSystem)
        base.bspLoader.linkEntityToClass("point_spotlight", PointSpotlight.PointSpotlight)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        
        self.d_readyToStart()

    def __handleSuitCreate(self, obj):
        self.suits[obj.doId] = obj

    def __handleSuitDelete(self, obj):
        if self.suits.has_key(obj.doId):
            del self.suits[obj.doId]
        
    def disable(self):
        self.reset()
        self.ignore('suitCreate')
        self.ignore('suitDelete')
        self.ignore('enterEntZoneComplete')
        self.ignore('leaveEntZoneComplete')
        base.localAvatar.setBattleZone(None)
        #base.localAvatar.smartCamera.setCameraPositionByIndex(self.lastCameraIndex)
        base.localAvatar.battleControls = False
        self.lastCameraIndex = None
        self.gameRules.cleanup()
        self.gameRules = None
        self.leaveEntZone()
        self.firstMapLoad = None
        self.entZone = None
        self.entZoneHandle = None
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

        if place:
            place.fsm.request('stop')

        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopSmartCamera()
        base.camera.wrtReparentTo(render)
        base.localAvatar.collisionsOff()
        base.localAvatar.disableGags()
        base.localAvatar.stopTrackAnimToSpeed()
            
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
        if not base.localAvatar.walkControls.getCollisionsActive():
            base.localAvatar.walkControls.setCollisionsActive(1)
        base.localAvatar.enableAvatarControls()

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
        self.__clearAllDebris()
        self.rewardPanelData = OrderedDict()
        if self.rewardPanel:
            self.rewardPanel.destroy()
        self.rewardPanel = None
        if self.rewardSeq:
            self.rewardSeq.pause()
        self.rewardSeq = Sequence()
