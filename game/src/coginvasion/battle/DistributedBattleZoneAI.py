"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleZoneAI.py
@author Maverick Liberty
@date July 22, 2016

"""

from panda3d.bullet import BulletWorld
from panda3d.bsp import BSPLoader
from panda3d.core import Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.distributed.AvatarWatcher import AvatarWatcher
from src.coginvasion.battle.RPToonData import RPToonData
from src.coginvasion.gags import GagGlobals
from src.coginvasion.quest.Objectives import DefeatCog, DefeatCogBuilding
from src.coginvasion.phys.PhysicsUtils import makeBulletCollFromGeoms, detachAndRemoveBulletNodes

import BattleGlobals
import itertools

try:
    from scipy.spatial.ckdtree import cKDTree
except:
    raise ImportError("You need to pull in the scipy package")

class DistributedBattleZoneAI(DistributedObjectAI, AvatarWatcher):
    notify = directNotify.newCategory('DistributedBattleZoneAI')

    battleType = BattleGlobals.BTBattle

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        AvatarWatcher.__init__(self, air)

        # Stores the Cogs each avatar kills.
        # Key (Avatar Id)
        # Value:
        # [{GAG_ID : USES}, [DeadCogData...]]
        self.avatarData = {}

        self.avId2suitsTargeting = {}
        
        # List of avatars that have acknowledged that they've completed the reward panel sequence.
        self.avReadyToContinue = []
        
        self.bspLoader = None
        self.navMeshNp = None

        # List of info_hint_cover entites, which indicate cover locations for AIs.
        self.coverKDTree = None
        self.coverHints = []
        
        self.physicsWorld = None

    def getCoverHints(self):
        return self.coverHints

    def traceLine(self, start, end):
        if not self.bspLoader.hasActiveLevel():
            return True
        
        return self.bspLoader.traceLine(start, end)
        
    def deadSuit(self, doId):
        pass
        
    def suitHPAtZero(self, doId):
        pass

    def generate(self):
        DistributedObjectAI.generate(self)
        self.air.battleZones[self.zoneId] = self
        
    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

        self.bspLoader = BSPLoader()
        self.bspLoader.setAi(True)
        self.bspLoader.setMaterialsFile("phase_14/etc/materials.txt")
        #self.bspLoader.setTextureContentsFile("phase_14/etc/texturecontents.txt")
        self.bspLoader.setServerEntityDispatcher(self)
        AvatarWatcher.zoneId = self.zoneId
        
        self.physicsWorld = BulletWorld()
        self.physicsWorld.setGravity(Vec3(0, 0, -32.1740))

        taskMgr.add(self.__updateTask, self.uniqueName('battleZoneUpdate'))

    def __updateTask(self, task):
        dt = globalClock.getDt()
        try:
            #self.physicsWorld.doPhysics(dt, metadata.PHYS_SUBSTEPS, dt / (metadata.PHYS_SUBSTEPS + 1))
            self.physicsWorld.doPhysics(dt, 0)
        except:
            pass
        return task.cont

    def getPhysicsWorld(self):
        return self.physicsWorld

    def loadBSPLevel(self, lfile):
        self.bspLoader.read(lfile)
        self.setupNavMesh(self.bspLoader.getResult())
        makeBulletCollFromGeoms(self.bspLoader.getResult(), world = self.physicsWorld)

        coverPositions = []
        self.coverHints = []
        for hint in self.bspLoader.findAllEntities("info_hint_cover"):
            pos = hint.getCEntity().getOrigin()
            coverPositions.append([pos[0], pos[1], pos[2]])
            self.coverHints.append(hint)
        if len(coverPositions) > 0:
            self.coverKDTree = cKDTree(coverPositions)

    def findClosestCoverPoint(self, currPos, n = 1):
        if not self.coverKDTree:
            return []

        return list(self.coverKDTree.query([currPos[0], currPos[1], currPos[2]], n)[1])

    def unloadBSPLevel(self):
        self.cleanupNavMesh()
        self.coverKDTree = None
        self.coverHints = []
        if self.bspLoader:
            detachAndRemoveBulletNodes(self.bspLoader.getResult(), world = self.physicsWorld)
            self.bspLoader.cleanup()
        
    def cleanupNavMesh(self):
        if self.navMeshNp:
            self.navMeshNp.removeNode()
            self.navMeshNp = None
        
    def setupNavMesh(self, node):
        self.cleanupNavMesh()
        
        nmMgr = base.nmMgr
        self.navMeshNp = nmMgr.create_nav_mesh()
        self.navMeshNp.node().set_owner_node_path(node)
        self.navMeshNp.node().setup()
        
    def planPath(self, startPos, endPos):
        """Uses recast/detour to find a path from the generated nav mesh from the BSP file."""

        if not self.navMeshNp:
            return [startPos, endPos]
        result = []
        valueList = self.navMeshNp.node().path_find_follow(startPos, endPos)
        currDir = Vec3(0)
        for i in xrange(valueList.get_num_values()):
            if i > 0 and i < valueList.get_num_values() - 1:
                dir = (valueList.get_value(i - 1) - valueList.get_value(i)).normalized()
                if dir.almostEqual(currDir, 0.05):
                    continue
                currDir = dir
            result.append(valueList.get_value(i))
        return result
        
    def createServerEntity(self, cls, entnum):
        """
        Called by BSPLoader when it encounters a networked entity that we have to generate.
        """
        dobj = cls(self.air, self)
        dobj.entnum = entnum
        dobj.bspLoader = self.bspLoader
        dobj.zoneId = self.zoneId
        return dobj

    def getBattleType(self):
        return self.battleType

    def toonAvailableForTargeting(self, avId):
        #return len(self.avId2suitsTargeting.get(avId, [])) < 2
        return True

    def clearTargets(self, suitId):
        # Remove the current target of this suit.
        for avId in self.avId2suitsTargeting.keys():
            if suitId in self.avId2suitsTargeting[avId]:
                self.avId2suitsTargeting[avId].remove(suitId)

    def newTarget(self, suitId, targetId):
        self.clearTargets(suitId)

        self.avId2suitsTargeting[targetId].append(suitId)

    def getSuitsTargetingAvId(self, avId):
        return self.avId2suitsTargeting.get(avId, [])

    def getNumSuitsTargeting(self, avId):
        return len(self.getSuitsTargetingAvId(avId))
        
    def acknowledgeAvatarReady(self):
        avId = self.air.getAvatarIdFromSender()
        
        if avId in self.watchingAvatarIds and avId not in self.avReadyToContinue:
            self.avReadyToContinue.append(avId)
        
        if len(self.avReadyToContinue) == len(self.watchingAvatarIds):
            self.b_rewardSequenceComplete()
            
    def b_rewardSequenceComplete(self):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.rewardSequenceComplete(timestamp)
        self.d_rewardSequenceComplete(timestamp)
        
    def d_rewardSequenceComplete(self, timestamp):
        self.sendUpdate('rewardSequenceComplete', [timestamp])
        
    def rewardSequenceComplete(self, timestamp):
        pass
    
    def resetPhysics(self):
        if self.physicsWorld:
            # We are counting on other types of objects never being added on the server side.
            numRigids = self.physicsWorld.getNumRigidBodies()
            numGhosts = self.physicsWorld.getNumGhosts()
            numConstraints = self.physicsWorld.getNumConstraints()
            for i in xrange(numRigids - 1, -1, -1):
                self.physicsWorld.removeRigidBody(self.physicsWorld.getRigidBody(i))
            for i in xrange(numGhosts - 1, -1, -1):
                self.physicsWorld.removeGhost(self.physicsWorld.getGhost(i))
            for i in xrange(numConstraints - 1, -1, -1):
                self.physicsWorld.removeConstraint(self.physicsWorld.getConstraint(i))
        self.physicsWorld = None

    def delete(self):
        taskMgr.remove(self.uniqueName('battleZoneUpdate'))

        self.coverHints = None

        del self.air.battleZones[self.zoneId]

        self.resetStats()

        self.unloadBSPLevel()
        self.bspLoader = None
            
        self.resetPhysics()

        self.avId2suitsTargeting = None
        self.watchingAvatarIds = None
        self.avatarData = None
        DistributedObjectAI.delete(self)

    def resetStats(self):
        self.stopTrackingAll()
        self.avatarData = {}
        self.avId2suitsTargeting = {}

    def addAvatar(self, avId, andUpdateAvatars=0):
        self.setupAvatarData(avId)
        self.startTrackingAvatarId(avId)
        
        if andUpdateAvatars:
            self.b_setAvatars(self.watchingAvatarIds)

    def setupAvatarData(self, avId):
        self.avatarData.update({avId : [{}, []]})
        self.avId2suitsTargeting[avId] = []
        
    def handleAvatarLeave(self, avatar, _):
        self.removeAvatar(avatar.doId)
        
    def handleAvatarChangeHealth(self, avatar, newHealth, prevHealth):
        pass

    def removeAvatar(self, avId, andUpdateAvatars=1):
        if self.watchingAvatarIds != None:
            if avId in self.watchingAvatarIds:
                self.stopTrackingAvatarId(avId)
                self.sendUpdate('clearAvatarDebris', [avId])
                
            if avId in self.avReadyToContinue:
                self.avReadyToContinue.remove(avId)
    
            if avId in self.avId2suitsTargeting.keys():
                del self.avId2suitsTargeting[avId]
    
            if avId in self.avatarData.keys():
                self.avatarData.pop(avId)
            
            if andUpdateAvatars:
                self.b_setAvatars(self.watchingAvatarIds)

    # Send the distributed message and
    # set the avatars on here.
    def b_setAvatars(self, avIds):
        self.d_setAvatars(avIds)
        self.setAvatars(avIds)

    # Send the distributed message.
    def d_setAvatars(self, avIds):
        self.sendUpdate('setAvatars', [avIds])

    # Set the avatar ids array to a list of
    # avatar ids.
    def setAvatars(self, avIds):
        # Let's make sure we're only listening to the avatars
        # we intend to listen to.
        for avId in itertools.chain(self.watchingAvatarIds, avIds):
            if avId in avIds:
                self.addAvatar(avId)
            else:
                self.removeAvatar(avId, andUpdateAvatars=0)
        self.watchingAvatarIds = avIds

    # Get the avatar ids.
    def getAvatars(self):
        return self.watchingAvatarIds
    
    def handleGagUse(self, gagId, user):
        gagUses = {}
        currentKills = []
        uses = 0
        
        if user in self.avatarData.keys():
            data = self.avatarData.get(user)
            gagUses = data[0]
            currentKills = data[1]
        
        if gagId in gagUses.keys():
            uses = gagUses[gagId]
        
        gagUses.update({gagId : uses + 1})

        self.avatarData.update({user : [gagUses, currentKills]})

    def handleCogDeath(self, cog, killerId):
        plan = cog.suitPlan
        cogData = DeadCogData(plan.name, plan.dept, cog.level, cog.variant, cog.hood)
        gagUses = {}
        currentKills = []

        if killerId in self.avatarData.keys():
            data = self.avatarData.get(killerId)
            gagUses = data[0]
            currentKills = data[1]
        currentKills.append(cogData)

        # Add the Cog kill into the player's dictionary.
        self.avatarData.update({killerId : [gagUses, currentKills]})
        
    def setToonData(self, netStrings):
        pass
    
    def d_setToonData(self):
        data = self.parseToonData()
        self.sendUpdate('setToonData', [data])
        
    def getToonData(self):
        return []
    
    def parseToonData(self):
        blobs = []
        for avId, data in self.avatarData.iteritems():
            avatar = base.air.doId2do.get(avId, None)
            deadCogData = data[1]
            favGagId = 0 # Make it whole cream pie by default
            favGagUses = 0
            gagUnlocked = False
            
            if avatar:
                rpData = RPToonData(avatar)
                trackIncrements = {}
                
                for track in avatar.trackExperience.keys():
                    trackIncrements[track] = 0
                
                for gagId, uses in data[0].iteritems():
                    gagName = GagGlobals.getGagByID(gagId)
                    gagData = GagGlobals.gagData.get(gagName)
                    track = gagData['track']
                    if uses > favGagUses:
                        favGagId = gagId
                        
                    trackGags = GagGlobals.TrackGagNamesByTrackName.get(track)
                    
                    incr = (trackGags.index(gagName) + 1) * uses
                    if track in trackIncrements.keys():
                        incr = incr + trackIncrements[track]
                    trackIncrements[track] = incr
                    
                rpData.favoriteGag = GagGlobals.getGagByID(favGagId)
                
                for track, exp in avatar.trackExperience.iteritems():
                    rpDataTrack = rpData.getTrackByName(track)
                    increment = trackIncrements.get(track)
                    maxExp = GagGlobals.getMaxExperienceValue(exp, track)
                    incrMaxExp = GagGlobals.getMaxExperienceValue(exp + increment, track)
                    rpDataTrack.exp = exp
                    rpDataTrack.maxExp = maxExp
                    rpDataTrack.increment = increment
                    avatar.trackExperience[track] = (exp + rpDataTrack.increment)
                    
                    if incrMaxExp != maxExp:
                        # We've unlocked a gag.
                        maxExpIndex = GagGlobals.TrackExperienceAmounts.get(track).index(incrMaxExp)
                        newGagName = GagGlobals.TrackGagNamesByTrackName.get(track)[maxExpIndex]
                        gagId = GagGlobals.getIDByName(newGagName)
                        avatar.backpack.addGag(gagId, 1)
                        gagUnlocked = True
                avatar.b_setTrackExperience(GagGlobals.trackExperienceToNetString(avatar.trackExperience))
                
                if gagUnlocked:
                    netString = avatar.getBackpackAmmo()
                    avatar.d_setBackpackAmmo(netString)
                
                # Let's update quest stuff for this avatar.
                questManager = avatar.questManager
                
                objectiveProgresses = []
                
                for quest in questManager.quests.values():
                    objectiveProgress = []
                    for i, objective in enumerate(quest.accessibleObjectives):
                        objectiveProgress.append(objective.progress)
                        if objective.type == DefeatCog:
                            progress = objective.progress
                            for killData in deadCogData:
                                if not (progress == objective.goal) and objective.isNeededCogFromDeadCogData(killData):
                                    progress += 1
                                elif (progress == objective.goal): break
                            objectiveProgress[i] = progress
                        elif objective.type == DefeatCogBuilding and self.isCogOffice() and objective.isAcceptable(self.hood, self.dept, self.numFloors):
                            objectiveProgress[i] = objectiveProgress[i] + 1
                    objectiveProgresses.append(objectiveProgress)
                questManager.updateQuestData(objectiveProgresses = objectiveProgresses)
                
                blobs.append(rpData.toNetString(avId))
                
        return blobs
    
    def isCogOffice(self):
        return self.battleType == BattleGlobals.BTOffice
    
    def battleComplete(self):
        self.d_setToonData()
        self.startRewardSeq()
    
    def startRewardSeq(self):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startRewardSeq', [timestamp])

class DeadCogData:

    def __init__(self, name, dept, level, variant, location):
        self.name = name
        self.dept = dept
        self.level = level
        self.variant = variant
        self.location = location

    def getName(self):
        return self.name

    def getDept(self):
        return self.dept

    def getLevel(self):
        return self.level

    def getVariant(self):
        return self.variant
