"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SafeZoneLoader.py
@author Brian Lach
@date December 14, 2014

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.StateData import StateData
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.actor.Actor import Actor
from panda3d.core import ModelPool, TexturePool, NodePath

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood.QuietZoneState import QuietZoneState
from src.coginvasion.hood import ToonInterior
from src.coginvasion.hood import LinkTunnel
from src.coginvasion.phys import PhysicsUtils

import types
import random

class SafeZoneLoader(StateData):
    notify = directNotify.newCategory("SafeZoneLoader")

    def __init__(self, hood, parentFSMState, doneEvent):
        StateData.__init__(self, doneEvent)
        self.hood = hood
        self.parentFSMState = parentFSMState
        self.fsm = ClassicFSM('safeZoneLoader', [State('off', self.enterOff, self.exitOff),
            State('playground', self.enterPlayground, self.exitPlayground, ['quietZone']),
            State('toonInterior', self.enterToonInterior, self.exitToonInterior, ['quietZone']),
            State('quietZone', self.enterQuietZone, self.exitQuietZone, ['playground', 'toonInterior'])],
            'off', 'off')
        self.placeDoneEvent = 'placeDone'
        self.place = None
        self.playground = None
        self.linkTunnels = []
        self.szHolidayDNAFile = None
        self.animatedFish = None
        self.safeZoneSong = ''
        self.interiorSong = ''
        return

    def findAndMakeLinkTunnels(self):
        for tunnel in self.geom.findAllMatches('**/*linktunnel*'):
            dnaRootStr = tunnel.getName()
            link = LinkTunnel.SafeZoneLinkTunnel(tunnel, dnaRootStr)
            self.linkTunnels.append(link)

    def load(self, flattenNow = True):
        StateData.load(self)

        self.createSafeZone(self.dnaFile, flattenNow)

        children = self.geom.findAllMatches('**/*doorFrameHole*')

        for child in children:
            child.hide()

        self.parentFSMState.addChild(self.fsm)

    def unload(self):
        StateData.unload(self)

        if self.animatedFish:
            self.animatedFish.cleanup()
            self.animatedFish.removeNode()
            self.animatedFish = None

        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState
        del self.animatedFish
        base.disableAndRemovePhysicsNodes(self.geom)
        self.geom.removeNode()
        del self.geom
        del self.fsm
        del self.hood
        del self.playground
        del self.safeZoneSong
        del self.interiorSong
        self.ignoreAll()
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def enter(self, requestStatus):
        StateData.enter(self)
        if base.localAvatar.zoneId < CIGlobals.DynamicZonesBegin:
            self.findAndMakeLinkTunnels()
        self.fsm.enterInitialState()
        messenger.send('enterSafeZone')
        self.setState(requestStatus['where'], requestStatus)
        # Delete party gate
        partyGate = self.geom.find('**/prop_party_gate_DNARoot')
        if not partyGate.isEmpty():
            partyGate.removeNode()
        del partyGate
        # Delete pet shop
        petShop = self.geom.find('**/*pet_shop_DNARoot*')
        if not petShop.isEmpty():
            fish = petShop.find('**/animated_prop_PetShopFishAnimatedProp_DNARoot')
            if fish:
                self.animatedFish = Actor('phase_4/models/props/exteriorfish-zero.bam', {'chan' :
                    'phase_4/models/props/exteriorfish-swim.bam'})
                self.animatedFish.reparentTo(petShop)
                self.animatedFish.setPos(fish.getPos())
                self.animatedFish.loop('chan')
                fish.removeNode()
            #petShop.removeNode()
        #del petShop

    def exit(self):
        StateData.exit(self)
        messenger.send('exitSafeZone')
        for link in self.linkTunnels:
            link.cleanup()
        if self.animatedFish:
            self.animatedFish.stop('chan')
        self.linkTunnels = []

    def setState(self, stateName, requestStatus):
        self.fsm.request(stateName, [requestStatus])

    def createSafeZone(self, dnaFile, flattenNow = True):
        if self.szStorageDNAFile:
            if isinstance(self.szStorageDNAFile, list):
                # We are loading multiple sz storages.
                for i in xrange(len(self.szStorageDNAFile)):
                    loader.loadDNAFile(self.hood.dnaStore, self.szStorageDNAFile[i])
            else:
                loader.loadDNAFile(self.hood.dnaStore, self.szStorageDNAFile)
                    
        if self.szHolidayDNAFile:
            loader.loadDNAFile(self.hood.dnaStore, self.szHolidayDNAFile)
            
        node = loader.loadDNAFile(self.hood.dnaStore, dnaFile)
        if node.getNumParents() == 1:
            self.geom = NodePath(node.getParent(0))
            self.geom.reparentTo(hidden)
        else:
            self.geom = hidden.attachNewNode(node)
        base.createPhysicsNodes(self.geom)
        if flattenNow:
            self.doFlatten()
        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)

    def doFlatten(self):
        self.makeDictionaries(self.hood.dnaStore)
        self.geom.flattenMedium()

    def makeDictionaries(self, dnaStore):
        self.nodeList = []
        for i in xrange(dnaStore.getNumDNAVisGroups()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            #groupName = base.cr.hoodMgr.extractGroupName(groupFullName)
            groupNode = self.geom.find('**/' + groupFullName)
            if groupNode.isEmpty():
                self.notify.error('Could not find visgroup')
            if not self.__class__.__name__ in ['TTSafeZoneLoader']:
                groupNode.flattenMedium()
            self.nodeList.append(groupNode)

        self.hood.dnaStore.resetPlaceNodes()
        self.hood.dnaStore.resetDNAGroups()
        self.hood.dnaStore.resetDNAVisGroups()
        self.hood.dnaStore.resetDNAVisGroupsAI()

    def enterPlayground(self, requestStatus):
        try:
            self.hood.stopSuitEffect()
        except:
            pass
        self.acceptOnce(self.placeDoneEvent, self.handlePlaygroundDone)
        self.place = self.playground(self, self.fsm, self.placeDoneEvent)
        self.place.load()

    def exitPlayground(self):
        self.ignore(self.placeDoneEvent)
        self.place.exit()
        self.place.unload()
        self.place = None
        base.cr.playGame.setPlace(self.place)
        return

    def handlePlaygroundDone(self):
        status = self.place.doneStatus
        if self.hood.isSameHood(status) and status['loader'] == 'safeZoneLoader' and not status['where'] in ['minigame']:
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)
        return

    def enterToonInterior(self, requestStatus):
        self.acceptOnce(self.placeDoneEvent, self.handleToonInteriorDone)
        self.place = ToonInterior.ToonInterior(self, self.fsm, self.placeDoneEvent)
        self.place.load()

    def enterThePlace(self, requestStatus):
        base.cr.playGame.setPlace(self.place)
        if self.place is not None:
            self.place.enter(requestStatus)

    def exitToonInterior(self):
        self.ignore(self.placeDoneEvent)
        self.place.exit()
        self.place.unload()
        self.place = None
        base.cr.playGame.setPlace(self.place)
        return

    def handleToonInteriorDone(self):
        status = self.place.doneStatus
        if (status['loader'] == 'safeZoneLoader' and
        self.hood.isSameHood(status) and
        status['shardId'] is None or
        status['how'] == 'doorOut'):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)
        return

    def enterQuietZone(self, requestStatus):
        self.fsm.request(requestStatus['where'], [requestStatus], exitCurrent = 0)

        self.quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.acceptOnce(self.quietZoneDoneEvent, self.handleQuietZoneDone)
        self.quietZoneStateData = QuietZoneState(self.quietZoneDoneEvent)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def exitQuietZone(self):
        self.ignore(self.quietZoneDoneEvent)
        del self.quietZoneDoneEvent
        self.quietZoneStateData.exit()
        self.quietZoneStateData.unload()
        self.quietZoneStateData = None
        return

    def handleQuietZoneDone(self):
        status = self.quietZoneStateData.getDoneStatus()
        self.exitQuietZone()
        if status['where'] == 'estate' or status['loader'] == 'townLoader':
            self.doneStatus = status
            messenger.send(self.doneEvent)
        else:
            self.enterThePlace(status)

    def enterOff(self):
        pass

    def exitOff(self):
        pass
