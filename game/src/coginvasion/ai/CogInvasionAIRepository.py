"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CogInvasionAIRepository.py
@author Brian Lach
@date Februrary 14, 2015

"""

from panda3d.bullet import *
from panda3d.bsp import *

from src.coginvasion.distributed.CogInvasionInternalRepository import CogInvasionInternalRepository
from src.coginvasion.distributed.DistributedDistrictAI import DistributedDistrictAI

from direct.distributed.TimeManagerAI import TimeManagerAI
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import STATESERVER_OBJECT_SET_AI

from src.coginvasion.hood.TTHoodAI import TTHoodAI
from src.coginvasion.hood.MGHoodAI import MGHoodAI
from src.coginvasion.hood.BRHoodAI import BRHoodAI
from src.coginvasion.hood.DLHoodAI import DLHoodAI
from src.coginvasion.hood.MLHoodAI import MLHoodAI
from src.coginvasion.hood.DGHoodAI import DGHoodAI
from src.coginvasion.hood.DDHoodAI import DDHoodAI
from src.coginvasion.cogtropolis.CTHoodAI import CTHoodAI

from src.coginvasion.phys import PhysicsUtils

from panda3d.core import UniqueIdAllocator
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.globals.CIGlobals import ToonClasses
from AIZoneData import AIZoneDataStore
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.distributed.CogInvasionDoGlobals import (DO_ID_DISTRICT_NAME_MANAGER,
                                                              DO_ID_HOLIDAY_MANAGER,
                                                              DO_ID_UNIQUE_INTEREST_NOTIFIER,
                                                              DO_ID_CLIENT_SERVICES_MANAGER)

#PStatClient.connect()

import random

DO_SIMULATION = False

class CogInvasionAIRepository(CogInvasionInternalRepository):
    notify = directNotify.newCategory("CogInvasionAIRepository")

    def __init__(self, baseChannel, stateServerChannel):
        CogInvasionInternalRepository.__init__(
            self, baseChannel, stateServerChannel,
            ['resources/phase_3/etc/direct.dc', 'resources/phase_3/etc/toon.dc'], dcSuffix = 'AI'
        )
        self.notify.setInfo(True)
        self.district = None
        self.zoneAllocator = UniqueIdAllocator(ZoneUtil.DynamicZonesBegin,
                                            ZoneUtil.DynamicZonesEnd)
        self.zoneDataStore = AIZoneDataStore()
        self.hoods = {}
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        self.districtNameMgr = self.generateGlobalObject(DO_ID_DISTRICT_NAME_MANAGER, 'DistrictNameManager')
        self.holidayMgr = self.generateGlobalObject(DO_ID_HOLIDAY_MANAGER, 'HolidayManager')
        self.uin = self.generateGlobalObject(DO_ID_UNIQUE_INTEREST_NOTIFIER, 'UniqueInterestNotifier')
        self.csm = self.generateGlobalObject(DO_ID_CLIENT_SERVICES_MANAGER, 'ClientServicesManager')
        
        # Anything that is a DistributedAvatarAI (Toons, Suits, etc).
        # This is a per-zone list of avatars.
        self.avatars = {}
        self.numAvatars = 0

        self.battleZones = {}
        
        if DO_SIMULATION:
            self.zonePhysics = {}
            self.bspLoader = BSPLoader()
            self.bspLoader.setAi(True)
            self.bspLoader.setMaterialsFile("phase_14/etc/materials.txt")
            #self.bspLoader.setTextureContentsFile("phase_14/etc/texturecontents.txt")
            #self.bspLoader.setServerEntityDispatcher(self)
            self.bspLoader.read("phase_14/etc/sewer_entrance_room_indoors/sewer_entrance_room_indoors.bsp")
            PhysicsUtils.makeBulletCollFromGeoms(self.bspLoader.getResult(), enableNow = False)

    def getBattleZone(self, zoneId):
        return self.battleZones.get(zoneId, None)

    def getPhysicsWorld(self, zoneId):
        bz = self.getBattleZone(zoneId)
        if bz:
            return bz.physicsWorld
        return None
        
    def __update(self, task):
        
        # Do a simulation of having battles going on
       
        dt = globalClock.getDt()
        # For each simulated battle zone
        for zonePhysics in self.zonePhysics.values():
            # How many suits are casting rays
            numSuits = 15#random.randint(4, 15)
            zonePhysics.doPhysics(dt, 1, 0.016)
            for i in xrange(numSuits):
                zonePhysics.rayTestClosest((0, 0, 0), (0, 20, 0))
            
        return task.cont
        
    def addAvatar(self, avatar, zoneId = None):
        if zoneId is None:
            zoneId = avatar.zoneId
        
        if not zoneId in self.avatars:
            self.avatars[zoneId] = []
            
        self.avatars[zoneId].append(avatar)
        self.numAvatars += 1

        if zoneId in self.battleZones:
            print "Adding avatar to battle zone at {0}".format(zoneId)
            avatar.battleZone = self.battleZones[zoneId]
            avatar.addToPhysicsWorld(avatar.battleZone.physicsWorld)
        
        if DO_SIMULATION:
            # Setup simulation physics environment for each
            # zone, we will pretend they are battle zones
            if zoneId not in self.zonePhysics:
                print "Making phys world in zone {0}".format(zoneId)
                physicsWorld = BulletWorld()
                # Panda units are in feet, so the gravity is 32 feet per second,
                # not 9.8 meters per second.
                physicsWorld.setGravity(Vec3(0, 0, -32.1740))
            
                # Add the static collision world (worldspawn faces)
                PhysicsUtils.attachBulletNodes(self.bspLoader.getResult(), physicsWorld)
            
                # Add objects that would be dynamic
                # (Avatar capsules, weapon collisions, door collisions, etc)
                dynObjects = 50#random.randint(15, 50)
                for i in xrange(dynObjects):
                    box = BulletCapsuleShape(0.5, 1.0, ZUp)
                    rbnode = BulletRigidBodyNode("testrb")
                    rbnode.setKinematic(True)
                    rbnode.setDeactivationEnabled(True)
                    rbnode.setDeactivationTime(5.0)
                    rbnode.addShape(box, TransformState.makePos((0, 0, 0)))
                    NodePath(rbnode).setPos(random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(-50, 50))
                    physicsWorld.attach(rbnode)
                
                self.zonePhysics[zoneId] = physicsWorld
        
    def removeAvatar(self, avatar):
        removed = False

        zoneOfAv = 0
        
        for zoneId in self.avatars.keys():
            if avatar in self.avatars[zoneId]:
                self.avatars[zoneId].remove(avatar)
                zoneOfAv = zoneId
                removed = True
                break
                
        if removed:
            self.numAvatars -= 1

        if avatar.battleZone:
            print "Removing avatar from battle zone at {0}".format(zoneOfAv)
            avatar.removeFromPhysicsWorld(avatar.battleZone.physicsWorld)
            avatar.battleZone = None
        
    def handleCrash(self, e):
        raise e

    def gotDistrictName(self, name):
        self.notify.info("This District will be called: %s" % name)
        self.districtId = self.allocateChannel()
        self.notify.info("Generating shard; id = %s" % self.districtId)
        self.district = DistributedDistrictAI(self)
        self.district.generateWithRequiredAndId(
            self.districtId, self.getGameDoId(), 3
        )
        self.notify.info("Claiming ownership; channel = %s" % self.districtId)
        self.claimOwnership(self.districtId)
        self.notify.info('Setting District name %s' % name)
        self.district.b_setDistrictName(name)
        self.district.b_setPopRecord(0)

        self.notify.info("Generating time manager...")
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

        self.areas = [TTHoodAI, BRHoodAI, DLHoodAI, MLHoodAI, DGHoodAI, DDHoodAI, CTHoodAI, MGHoodAI]
        self.areaIndex = 0

        taskMgr.add(self.makeAreasTask, 'makeAreasTask')

    def makeAreasTask(self, task):
        if self.areaIndex >= len(self.areas):
            self.done()
            return task.done
        area = self.areas[self.areaIndex]
        area(self)
        self.areaIndex += 1
        task.delayTime = 0.5
        return task.again

    def done(self):
        self.notify.info("Setting shard available.")
        self.district.b_setAvailable(1)
        self.notify.info("Done.")
        
        if DO_SIMULATION:
            print "There are {0} avatars.".format(self.numAvatars)
            print "There are {0} zones.".format(len(self.zonePhysics.keys()))
        
            taskMgr.add(self.__update, "AIUpdate")

    def noDistrictNames(self):
        self.notify.error("Cannot create District: There are no available names!")

    def handleConnected(self):
        CogInvasionInternalRepository.handleConnected(self)
        self.districtNameMgr.d_requestDistrictName()
        self.holidayMgr.d_srvRequestHoliday()

    def toonsAreInZone(self, zoneId):
        numToons = 0
        for obj in self.doId2do.values():
            if obj.__class__.__name__ in ToonClasses:
                if obj.zoneId == zoneId:
                    numToons += 1
        return numToons > 0

    def shutdown(self):
        if DO_SIMULATION:
            taskMgr.remove("AIUpdate")
        for hood in self.hoods.values():
            hood.shutdown()
        if self.timeManager:
            self.timeManager.requestDelete()
            self.timeManager = None
        if self.district:
            self.district.b_setAvailable(0)
            self.district.requestDelete()

    def claimOwnership(self, channel):
        dg = PyDatagram()
        dg.addServerHeader(channel, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        dg.addChannel(self.ourChannel)
        self.send(dg)

    def allocateZone(self):
        return self.zoneAllocator.allocate()

    def deallocateZone(self, zone):
        self.zoneAllocator.free(zone)

    def getZoneDataStore(self):
        return self.zoneDataStore
