"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleZoneAI.py
@author Maverick Liberty
@date July 22, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.battle.RPToonData import RPToonData
from src.coginvasion.gags import GagGlobals

class DistributedBattleZoneAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBattleZoneAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.avIds = []

        # Stores the Cogs each avatar kills.
        # Key (Avatar Id)
        # Value:
        # [{GAG_ID : USES}, [DeadCogData...]]
        self.avatarData = {}
        
        # List of avatars that have acknowledged that they've completed the reward panel sequence.
        self.avReadyToContinue = []
        
    def acknowledgeAvatarReady(self):
        avId = self.air.getAvatarIdFromSender()
        
        if avId in self.avIds and avId not in self.avReadyToContinue:
            self.avReadyToContinue.append(avId)
        
        if len(self.avReadyToContinue) == len(self.avIds):
            self.b_rewardSequenceComplete()
            
    def b_rewardSequenceComplete(self):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.rewardSequenceComplete(timestamp)
        self.d_rewardSequenceComplete(timestamp)
        
    def d_rewardSequenceComplete(self, timestamp):
        self.sendUpdate('rewardSequenceComplete', [timestamp])
        
    def rewardSequenceComplete(self, timestamp):
        pass

    def delete(self):
        self.ignoreAvatarDeleteEvents()
        self.resetStats()

        self.avIds = None
        self.avatarData = None
        DistributedObjectAI.delete(self)

    def resetStats(self):
        self.avIds = []
        self.avatarData = {}

    def ignoreAvatarDeleteEvents(self):
        for avId in self.avIds:
            toon = self.air.doId2do.get(avId)
            self.ignore(toon.getDeleteEvent())
            break

    def addAvatar(self, avId):
        self.avIds.append(avId)
        self.avatarData.update({avId : [{}, []]})
        self.b_setAvatars(self.avIds)

    def removeAvatar(self, avId):
        if avId in self.avIds:
            self.avIds.remove(avId)
            
        if avId in self.avReadyToContinue:
            self.avReadyToContinue.remove(avId)

        if avId in self.avatarData.keys():
            self.avatarData.pop(avId)
        self.b_setAvatars(self.avIds)

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
        self.avIds = avIds

    # Get the avatar ids.
    def getAvatars(self):
        return self.avIds
    
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
        cogData = DeadCogData(plan.name, plan.dept, cog.level, cog.variant)
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
            favGagId = -1
            favGagUses = 0
            gagUnlocked = False
            
            if avatar:
                rpData = RPToonData(avatar)
                trackIncrements = {}
                
                for track in avatar.trackExperience.keys():
                    trackIncrements[track] = 0
                
                for gagId, uses in data[0].iteritems():
                    gagName = GagGlobals.gagIds[gagId]
                    track = GagGlobals.gagData.get(gagName)['track']
                    if uses > favGagUses:
                        favGagId = gagId
                        
                    trackGags = GagGlobals.TrackGagNamesByTrackName.get(track)
                    
                    incr = (trackGags.index(gagName) + 1) * uses
                    if track in trackIncrements.keys():
                        incr = incr + trackIncrements[track]
                    trackIncrements[track] = incr
                rpData.favoriteGag = GagGlobals.gagIds[favGagId]
                
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
                        gagId = GagGlobals.gagIdByName.get(newGagName)
                        avatar.backpack.addGag(gagId, 1)
                        gagUnlocked = True
                avatar.b_setTrackExperience(GagGlobals.trackExperienceToNetString(avatar.trackExperience))
                
                if gagUnlocked:
                    netString = avatar.getBackpackAmmo()
                    avatar.d_setBackpackAmmo(netString)
                blobs.append(rpData.toNetString(avId))
                
        return blobs
    
    def battleComplete(self):
        self.d_setToonData()
        self.startRewardSeq()
    
    def startRewardSeq(self):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startRewardSeq', [timestamp])

class DeadCogData:

    def __init__(self, name, dept, level, variant):
        self.name = name
        self.dept = dept
        self.level = level
        self.variant = variant

    def getName(self):
        return self.name

    def getDept(self):
        return self.dept

    def getLevel(self):
        return self.level

    def getVariant(self):
        return self.variant
