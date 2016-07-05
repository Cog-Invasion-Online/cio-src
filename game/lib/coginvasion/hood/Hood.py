"""

  Filename: Hood.py
  Created by: blach (14Dec14)

"""


from direct.fsm.StateData import StateData
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.holiday.HolidayManager import HolidayType

from panda3d.core import Vec4, AmbientLight, ModelPool, TexturePool
from panda3d.core import Fog, CompassEffect, NodePath

import ZoneUtil
from QuietZoneState import QuietZoneState

class Hood(StateData):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        StateData.__init__(self, doneEvent)
        self.parentFSM = parentFSM
        self.doneEvent = doneEvent
        self.dnaStore = dnaStore
        self.hoodId = hoodId
        self.id = None
        self.titleText = None
        self.suitFog = None
        self.suitLight = None
        self.suitLightColor = (0.4, 0.4, 0.4, 1)
        self.suitFogData = [(0.3, 0.3, 0.3), 0.0025]
        self.titleColor = (1, 1, 1, 1)
        return

    def enter(self, requestStatus):
        StateData.enter(self)
        hoodId = requestStatus['hoodId']
        zoneId = requestStatus['zoneId']
        rootZone = ZoneUtil.getZoneId(hoodId)
        if base.localAvatar.getLastHood() != rootZone and hoodId != CIGlobals.MinigameArea:
            base.localAvatar.b_setLastHood(rootZone)
        if not base.localAvatar.hasDiscoveredHood(rootZone):
            hoodsDiscovered = list(base.localAvatar.getHoodsDiscovered())
            hoodsDiscovered.append(rootZone)
            base.localAvatar.b_setHoodsDiscovered(hoodsDiscovered)
        text = self.getHoodText(zoneId)
        self.titleText = OnscreenText(
            text, fg = self.titleColor, font = CIGlobals.getMickeyFont(),
            scale = 0.15, pos = (0, -0.65)
        )
        self.titleText.hide()

    def enterTheLoader(self, requestStatus):
        self.fsm.request(requestStatus['loader'], [requestStatus])

    def getHoodText(self, zoneId):
        if ZoneUtil.getWhereName(zoneId) == 'street' and zoneId < 61000:
            hoodText = CIGlobals.BranchZone2StreetName[ZoneUtil.getBranchZone(zoneId)]
            hoodText += '\n' + self.id
        else:
            hoodText = self.id
            if self.id != CIGlobals.MinigameArea:
                hoodText += '\n' + ZoneUtil.getWhereName(zoneId).upper()
        return hoodText

    def spawnTitleText(self, zoneId):
        hoodText = self.getHoodText(zoneId)
        self.doSpawnTitleText(hoodText)

    def doSpawnTitleText(self, hoodText):
        self.titleText.setText(hoodText)
        self.titleText.show()
        self.titleText.setColor(Vec4(*self.titleColor))
        self.titleText.clearColorScale()
        self.titleText.setFg(self.titleColor)
        seq = Sequence(
            Wait(0.1), Wait(6.0),
            self.titleText.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)),
            Func(self.titleText.hide)
        )
        seq.start()

    def hideTitleText(self):
        if self.titleText:
            self.titleText.hide()

    def exit(self):
        if self.titleText:
            self.titleText.cleanup()
            self.titleText = None
        StateData.exit(self)
        return

    def load(self):
        StateData.load(self)
        if self.storageDNAFile:
            loadDNAFile(self.dnaStore, self.storageDNAFile)
        if self.holidayDNAFile:
            loadDNAFile(self.dnaStore, self.holidayDNAFile)
        if not base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.createNormalSky()
        else:
            self.createSpookySky()

    def unload(self):
        self.notify.info("unload()")
        if hasattr(self, 'loader'):
            self.loader.exit()
            self.loader.unload()
            del self.loader
        del self.parentFSM
        del self.fsm
        self.dnaStore.reset_nodes()
        self.dnaStore.reset_hood_nodes()
        self.dnaStore.reset_place_nodes()
        self.dnaStore.reset_hood()
        self.dnaStore.reset_fonts()
        self.dnaStore.reset_DNA_vis_groups()
        self.dnaStore.reset_textures()
        self.dnaStore.reset_block_numbers()
        self.dnaStore.reset_block_zones()
        self.dnaStore.reset_suit_points()
        del self.dnaStore
        self.deleteCurrentSky()
        self.stopSuitEffect(0)
        self.ignoreAll()
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        StateData.unload(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def isSameHood(self, status):
        return status['hoodId'] == self.hoodId and status['shardId'] == None

    def enterQuietZone(self, requestStatus):
        base.transitions.noTransitions()
        loaderName = requestStatus['loader']
        zoneID = requestStatus['zoneId']
        where = requestStatus['where']
        if where == 'playground' or where == 'toonInterior':
            name = self.id
        elif where == 'minigame':
            name = 'Minigame'
        elif where == 'street':
            name = CIGlobals.BranchZone2StreetName[ZoneUtil.getBranchZone(zoneID)]
        if loaderName == 'safeZoneLoader' or loaderName == 'townLoader':
            if not loader.inBulkBlock:
                loader.beginBulkLoad('hood', name, CIGlobals.safeZoneLSRanges.get(self.id, 6))
            self.loadLoader(requestStatus)
        else:
            base.transitions.fadeScreen(1.0)

        self._quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.acceptOnce(self._quietZoneDoneEvent, self.handleQuietZoneDone)
        self.quietZoneStateData = QuietZoneState(self._quietZoneDoneEvent)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def exitQuietZone(self):
        self.ignore(self._quietZoneDoneEvent)
        del self._quietZoneDoneEvent
        self.quietZoneStateData.exit()
        self.quietZoneStateData.unload()
        self.quietZoneStateData = None
        return

    def loadLoader(self, requestStatus):
        pass

    def handleQuietZoneDone(self):
        status = self.quietZoneStateData.getDoneStatus()
        loader.endBulkLoad('hood')
        self.fsm.request(status['loader'], [status])
        if hasattr(self, 'loader'):
            self.loader.enterThePlace(status)

    def enterSafeZoneLoader(self, requestStatus):
        self.accept(self.loaderDoneEvent, self.handleSafeZoneLoaderDone)
        self.loader.enter(requestStatus)
        self.spawnTitleText(requestStatus['zoneId'])

    def exitSafeZoneLoader(self):
        self.ignore(self.loaderDoneEvent)
        self.hideTitleText()
        self.loader.exit()
        self.loader.unload()
        del self.loader

    def handleSafeZoneLoaderDone(self):
        doneStatus = self.loader.getDoneStatus()
        if self.isSameHood(doneStatus) or doneStatus['where'] == 'minigame':
            self.fsm.request('quietZone', [doneStatus])
        else:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)

    def createNormalSky(self):
        self.deleteCurrentSky()
        self.sky = loader.loadModel(self.skyFilename)
        if self.__class__.__name__ != 'CTHood':
            self.sky.setScale(1.0)
            self.sky.setFogOff()
        else:
            self.sky.setScale(5.0)

    def createSpookySky(self):
        self.deleteCurrentSky()
        self.sky = loader.loadModel(self.spookySkyFile)
        self.sky.setScale(5.0)
        self.sky.setFogOff()

    def deleteCurrentSky(self):
        if hasattr(self, 'sky'):
            if self.sky:
                self.sky.removeNode()
                del self.sky

    def startSuitEffect(self):
        self.stopSuitEffect()
        light = AmbientLight("suitLight")
        light.setColor(Vec4(*self.suitLightColor))
        self.suitLight = render.attachNewNode(light)
        render.setLight(self.suitLight)
        self.suitFog = Fog("suitFog")
        self.suitFog.setColor(*self.suitFogData[0])
        self.suitFog.setExpDensity(self.suitFogData[1])
        render.setFog(self.suitFog)
        self.createSpookySky()
        Hood.startSky(self)

    def stopSuitEffect(self, newSky = 1):
        render.clearFog()
        if self.suitLight:
            render.clearLight(self.suitLight)
            self.suitLight.removeNode()
            self.suitLight = None
        if self.suitFog:
            self.suitFog = None
        if newSky:
            if not base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
                self.createNormalSky()
            else:
                self.createSpookySky()
            self.startSky()

    def startSky(self):
        self.sky.reparentTo(camera)
        self.sky.setZ(0.0)
        self.sky.setHpr(0.0, 0.0, 0.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)

    def stopSky(self):
        self.sky.reparentTo(hidden)
