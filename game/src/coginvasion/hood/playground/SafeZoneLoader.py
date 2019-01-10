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

from src.coginvasion.hood import ZoneUtil
from src.coginvasion.hood.QuietZoneState import QuietZoneState
from src.coginvasion.hood import ToonInterior
from src.coginvasion.hood import LinkTunnel
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.globals import CIGlobals

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
        self.nodeList = []
        self.linkTunnels = []
        self.szHolidayDNAFile = None
        self.animatedFish = None
        self.safeZoneSong = ''
        self.interiorSong = ''
        return
        
    def doBaseOptimizations(self):
        # Performs base optimizations that all playgrounds can benefit from.
        # Combines all flat walls together, optimizes all landmark buildings,
        # tunnels, trees, fishing docks.
        #
        # Any optimizations for a specific playground should be done in
        # doFlatten() in that playground's SafeZoneLoader.
        
        flats = self.geom.attachNewNode('flats')
        for np in self.geom.findAllMatches("**/sz0:*_DNARoot"):
            np.wrtReparentTo(flats)
        for np in self.geom.findAllMatches("**/tb0:*_DNARoot"):
            np.wrtReparentTo(flats)
        for np in self.geom.findAllMatches("**/*random*_DNARoot"):
            np.wrtReparentTo(flats)
        CIGlobals.removeDNACodes(flats)
        flats.clearModelNodes()
        flats.flattenStrong()
        CIGlobals.moveChildren(flats, self.geom)
        
        tunnels = self.geom.findAllMatches("**/*linktunnel*")
        for tunnel in tunnels:
            tunnel.flattenStrong()
            
        for landmark in self.geom.findAllMatches("**/*toon_landmark*_DNARoot"):
            CIGlobals.removeDNACodes(landmark)
            landmark.flattenStrong()
                
        signs = self.geom.attachNewNode("signs")
        CIGlobals.moveNodes(self.geom, "*neighborhood_sign*_DNARoot", signs)
        #for sign in signs.getChildren():
            #sign.clearTransform()
        CIGlobals.removeDNACodes(signs)
        signs.clearModelNodes()
        signs.flattenStrong()
        CIGlobals.moveChildren(signs, self.geom)
        
        fish = self.geom.attachNewNode("fishspots")
        CIGlobals.moveNodes(self.geom, "fishing_spot_DNARoot", fish)
        CIGlobals.removeDNACodes(fish)
        fish.clearModelNodes()
        fish.flattenStrong()
        CIGlobals.moveChildren(fish, self.geom)
        
        trees = self.geom.attachNewNode("trees")
        for np in self.geom.findAllMatches("**/*prop_tree*_DNARoot"):
            np.wrtReparentTo(trees)
        CIGlobals.removeDNACodes(trees)
        trees.clearModelNodes()
        trees.flattenStrong()
        CIGlobals.moveChildren(trees, self.geom)

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

        base.waterReflectionMgr.clearWaterNodes()

        if self.animatedFish:
            self.animatedFish.cleanup()
            self.animatedFish.removeNode()
            self.animatedFish = None

        if self.linkTunnels is not None:
            for link in self.linkTunnels:
                link.cleanup()
        self.linkTunnels = None
        if self.nodeList is not None:
            for node in self.nodeList:
                node.removeNode()
        self.nodeList = None

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

        #CIGlobals.doSceneCleanup()

    def enter(self, requestStatus):
        StateData.enter(self)
        if base.localAvatar.zoneId < ZoneUtil.DynamicZonesBegin:
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
        
        CIGlobals.preRenderScene(self.geom)

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
        CIGlobals.replaceDecalEffectsWithDepthOffsetAttrib(self.geom)
        if flattenNow:
            self.doFlatten()
        base.createPhysicsNodes(self.geom)
        CIGlobals.preRenderScene(self.geom)

    def doFlatten(self):
        self.doBaseOptimizations()
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
