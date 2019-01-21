"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSuitAI.py
@author Maverick Liberty
@date September 01, 2015

"""

from panda3d.core import ConfigVariableBool

from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog import CogBattleGlobals
from src.coginvasion.cog.SuitItemDropperAI import SuitItemDropperAI

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.GagType import GagType

import SpawnMode
from SuitBrainAI import SuitBrain
from SuitBank import SuitPlan
from SuitFlyToRandomSpotBehaviorAI import SuitFlyToRandomSpotBehaviorAI
from SuitCallInBackupBehaviorAI import SuitCallInBackupBehaviorAI
from SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI
from SuitAttackTurretBehaviorAI import SuitAttackTurretBehaviorAI
from SuitAttackBehaviorAI import SuitAttackBehaviorAI
from SuitPathDataAI import *
import SuitAttacks
import SuitBank
import SuitGlobals
import Variant
import GagEffects

import types
import random

class DistributedSuitAI(DistributedAvatarAI):
    notify = directNotify.newCategory('DistributedSuitAI')
    dropItems = ConfigVariableBool('want-suit-drops', True)

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        self.anim = 'neutral'
        self.brain = None
        self.track = None
        self.currentPath = None
        self.currentPathQueue = []
        self.suitMgr = None
        self.suitPlan = 0
        self.variant = Variant.NORMAL
        if self.dropItems.getValue():
            self.itemDropper = SuitItemDropperAI(self)
        self.suitState = 0
        self.startPoint = -1
        self.endPoint = -1
        self.stateTimestamp = 0
        self.level = 0
        self.lateX = 0
        self.lateY = 0
        self.animStateChangeEvent = SuitGlobals.animStateChangeEvent
        self.requestedBehaviors = []

        # This is for handling death.
        self.deathAnim = None
        self.deathTimeLeft = 0
        self.deathTaskName = None

        # This is for handling combos.
        # Combo data stores an avId and gag type pair.
        # Avatar Ids are cheaper to store, so we use those.
        # comboDataTaskName is the name of the task that clears the data.
        self.comboData = {}
        self.comboDataTaskName = None
        self.clearComboDataTime = 3
        self.showComboDamageTime = 0.75
        
        # These variables are for handling gag weaknesses.
        self.showWeaknessBonusDamageTime = 0.50
        
        # The variable that stores the special sequence that handles tactical attacks.
        self.tacticalSeq = None

        self.allowHits = True
        self.firstTimeDead = True
        self.stunned = False
        
        # This variable stores what avatarIds have damaged us.
        self.damagers = []

    def handleToonThreat(self, toon, hasBeenHit, gagId=None):
        if not hasattr(self, 'brain') or self.brain is None:
            return

        if (CIGlobals.areFacingEachOther(self, toon) or hasBeenHit):
            # Woah! This Toon might be trying to attack us!

            doIt = random.choice([True, False])
            if not doIt and not hasBeenHit or not self.brain:
                return

            behav = self.brain.currentBehavior

            if behav.__class__.__name__ == "SuitPursueToonBehaviorAI":

                if behav.fsm.getCurrentState().getName() != "attack":

                    if self.getDistance(toon) < 40 and self.battleZone.toonAvailableForTargeting(toon.doId):

                        if toon != behav.target:

                            # We need to make this toon our new target.
                            behav.fsm.request("off")
                            behav.setTarget(toon)

                        # Attack
                        behav.fsm.request("attack", [False])
                    #else:
                    #    # We can't attack them, run away?
                    #    behav.fsm.request("divert")



    def d_setWalkPath(self, path):
        # Send out a list of Point2s for the client to create a path for the suit to walk.
        timestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setWalkPath', [path, timestamp])

    def setAllowHits(self, flag):
        self.allowHits = flag

    def canGetHit(self):
        return self.allowHits

    def b_setSuit(self, plan, variant = 0):
        self.d_setSuit(plan, variant)
        self.setSuit(plan, variant)

    def d_setSuit(self, plan, variant = 0):
        if isinstance(plan, SuitPlan):
            plan = SuitBank.getIdFromSuit(plan)
        self.sendUpdate('setSuit', [plan, variant])

    def setSuit(self, plan, variant = 0, tutorial = None):
        self.suitPlan = plan
        self.variant = Variant.getVariantById(variant)

        classAttrs = plan.getCogClassAttrs()
        self.maxHealth = classAttrs.baseHp
        self.maxHealth += SuitGlobals.calculateHP(self.level)
        self.maxHealth *= classAttrs.hpMod

        self.health = self.maxHealth

        if self.dropItems.getValue():
            self.itemDropper.calculate(tutorial)

        if self.level == 0:
            self.maxHealth = 1
            self.health = self.maxHealth
            
        self.d_setMaxHealth(self.maxHealth)
        self.d_setHealth(self.health)

    def getSuit(self):
        return tuple((self.suitPlan, self.variant))

    def setSuitState(self, index, startPoint, endPoint):
        if index == 0 and not self.isEmpty():
            self.setLatePos(self.getX(render), self.getY(render))
        self.suitState = index
        self.startPoint = startPoint
        self.endPoint = endPoint

    def d_setSuitState(self, index, startPoint, endPoint):
        self.stateTimestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setSuitState', [index, startPoint, endPoint, self.stateTimestamp])

    def b_setSuitState(self, index, startPoint, endPoint):
        self.d_setSuitState(index, startPoint, endPoint)
        self.setSuitState(index, startPoint, endPoint)

    def getSuitState(self):
        return [self.suitState, self.startPoint, self.endPoint, self.stateTimestamp]

    def setAnimState(self, anim):
        if hasattr(self, 'animStateChangeEvent'):
            messenger.send(self.animStateChangeEvent, [anim, self.anim])
            self.anim = anim
            if type(self.anim) == types.IntType:
                if anim != 44 and anim != 45:
                    self.anim = SuitGlobals.getAnimById(anim).getName()
                elif anim == 44:
                    self.anim = 'die'
                elif anim == 45:
                    self.anim = 'flyNeutral'

    def b_setAnimState(self, anim, loop = 1):
        if type(anim) == types.StringType:
            animId = SuitGlobals.getAnimId(SuitGlobals.getAnimByName(anim))
            if animId is None and anim != 'flyNeutral':
                animId = 44
            elif anim == 'flyNeutral':
                animId = 45
        else:
            animId = anim
        self.d_setAnimState(animId, loop)
        self.setAnimState(animId)

    def d_setAnimState(self, anim, loop):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [anim, loop, timestamp])

    def getAnimState(self):
        return self.anim

    def d_startMoveInterval(self, startPos, endPos, durationFactor = 0.2):
        durationFactor = durationFactor * 10
        self.sendUpdate('startMoveInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), durationFactor])

    def d_stopMoveInterval(self, andTurnAround = 0):
        self.sendUpdate('stopMoveInterval', [andTurnAround])

    def d_startProjInterval(self, startPos, endPos, duration, gravityMult):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startProjInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), duration, gravityMult, timestamp])

    def d_startPosInterval(self, startPos, endPos, duration, blendType):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startPosInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), duration, blendType, timestamp])

    def setLatePos(self, lateX, lateY):
        self.lateX = lateX
        self.lateY = lateY

    def getLatePos(self):
        return [self.lateX, self.lateY]

    def setLevel(self, level):
        self.level = level

    def d_setLevel(self, level):
        self.sendUpdate('setLevel', [level])

    def b_setLevel(self, level):
        self.setLevel(level)
        self.d_setLevel(level)

    def getLevel(self):
        return self.level

    def setHealth(self, health):
        prevHealth = self.health
        DistributedAvatarAI.setHealth(self, health)

        if not self.isDead() or self.isDead() and self.deathTimeLeft > 0:
            self.d_announceHealth(0, prevHealth - self.health)

    def stopSuitInPlace(self, killBrain = True):
        if hasattr(self, 'brain') and self.brain is not None:
            self.brain.stopThinking()
            if killBrain:
                self.brain.unloadBehaviors()
                self.brain = None
        self.b_setSuitState(0, -1, -1)
        self.clearTrack()

    def restartSuit(self):
        if self.brain is not None:
            self.brain.startThinking()

    def monitorHealth(self, task):
        if self.health <= 0:
            self.stopSuitInPlace()
            currentAnim = SuitGlobals.getAnimByName(self.anim)
            if currentAnim:
                if not self.deathAnim:
                    self.deathAnim = currentAnim
                    self.deathTimeLeft = currentAnim.getDeathHoldTime()
                    self.deathTaskName = self.uniqueName('__handleDeath')
                    taskMgr.doMethodLater(1, self.__handleDeath, name = self.deathTaskName)
                else:
                    taskMgr.remove(self.deathTaskName)
                    delayTime = currentAnim.getDeathHoldTime()
                    self.deathTimeLeft = delayTime
                    taskMgr.doMethodLater(1, self.__handleDeath, name = self.deathTaskName)
            else:
                self.killSuit()
            return task.done
        return task.cont

    def clearComboData(self, task):
        self.comboData = {}

        if not hasattr(self, 'clearComboDataTime'):
            return task.done

        task.delayTime = self.clearComboDataTime
        return task.again
            
    def __handleTacticalAttacks(self, avId, gagName, gagData):
        # Gets the damage and the damage offset.
        baseDmg, dmgOffset = self.__getGagEffectOnMe(avId, gagName, gagData)

        self.tacticalSeq = Sequence()
        
        # Let's handle combos.
        isCombo, comboDamage = self.__handleCombos(avId, (baseDmg + dmgOffset), gagData.get('track'))

        finalDmg = baseDmg + dmgOffset + comboDamage

        self.b_setHealth(self.getHealth() - finalDmg)
        if dmgOffset < 0.0:
            # Take damage and announce the damage we just took.
            self.tacticalSeq.append(Func(self.d_announceHealth, 3, -(baseDmg + dmgOffset), 0))
        else:
            self.tacticalSeq.append(Func(self.d_announceHealth, 0, -baseDmg))

        if dmgOffset > 0.0:
            # There is some sort of damage offset bonus.
            self.tacticalSeq.append(Wait(self.showWeaknessBonusDamageTime))
            # Show the opposite of the dmgOffset because a negative damage offset means less damage the gag does,
            # meaning adding health to the cog. Vice-versa
            self.tacticalSeq.append(Func(self.d_announceHealth, 3, -dmgOffset, 2))
            
        if isCombo and comboDamage > 0:
            # Great job, team! We just did a combo attack!
            self.tacticalSeq.append(Wait(self.showComboDamageTime))
            self.tacticalSeq.append(Func(self.d_announceHealth, 2, -comboDamage, 1))
        
        self.tacticalSeq.start()

        return finalDmg
        
    def __getGagEffectOnMe(self, avId, gagName, gagData):
        """ Returns the base damage and the damage offset a specified gag name used by "avId" has on this Cog """
        weaknessFactor = self.suitPlan.getGagWeaknesses().get(gagName, 1.0)
        classWeakness = self.suitPlan.getCogClassAttrs().getGagDmgRamp(GagGlobals.getTrackOfGag(gagName))
        baseDmg = GagGlobals.calculateDamage(avId, gagName, gagData)
        dmgOffset = int(math.ceil(baseDmg * weaknessFactor * classWeakness)) - baseDmg
        return baseDmg, dmgOffset

    def __handleCombos(self, avId, effectiveGagDmg, gagTrack):
        self.comboData.update({avId : {gagTrack : effectiveGagDmg}})

        data = self.comboData.values()
        tracks = []
        damages = []
        
        for hitData in data:
            for track, damage in hitData.iteritems():
                tracks.append(track)
                damages.append(damage)

        isCombo = False
        comboDamage = 0
        comboPerct = 0.35
        totalDamage = 0
        totalGags = 0

        for track in tracks:
            if tracks.count(track) > 1 and track == track:
                # Get the indices of each occurrence of this track in the tracks list.
                # For example, tracks could equal [GagType.THROW, GagType.SQUIRT, GagType.THROW]
                # If, the variable 'track' equaled GagType.THROW, then the next line would
                # return: [0, 2]
                damageIndices = [i for i, x in enumerate(tracks) if x == track]
                totalGags = len(damageIndices)
                for i in damageIndices:
                    if i < len(damageIndices) and i >= 0:
                        totalDamage += damages[damageIndices[i]]
                isCombo = True
                break
            continue

        if isCombo:
            comboDamage = int((float(totalDamage) / float(totalGags)) * comboPerct)
            self.b_setHealth(self.getHealth() - comboDamage)
            self.comboData.clear()
            taskMgr.remove(self.comboDataTaskName)
            
        return isCombo, comboDamage

    def __getAnimForGag(self, track, gagName):
        if track == GagType.THROW or gagName == GagGlobals.TNT:
            return 'pie'
        elif track == GagType.DROP:
            if gagName in GagGlobals.MajorDrops:
                return 'drop'
            else:
                return 'drop-react'
        elif track == GagType.SQUIRT or track == GagType.SOUND:
            if gagName == GagGlobals.StormCloud:
                return 'soak'
            else:
                return 'squirt-small'

    def stopStun(self, restart = False):
        taskMgr.remove(self.taskName('stunTask'))
        self.stunned = False
        if restart and not self.isDead():
            self.restartSuit()

    def __stunTask(self, task):
        self.stopStun(restart = True)
        return task.done

    # The new method for handling gags.
    def hitByGag(self, gagId, distance):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId, None)
        gagName = GagGlobals.getGagByID(gagId)
        data = dict(GagGlobals.getGagData(gagId))
        data['distance'] = distance
        track = GagGlobals.getTrackOfGag(gagId, getId = True)

        if self.canGetHit():
            damage = self.__handleTacticalAttacks(avatar.doId, gagName, data)
            
            if self.battleZone:
                # We only want to award credit when Toons use gags that are less than or at the level of the Cog
                # they're using them on.
                gagLevel = GagGlobals.TrackGagNamesByTrackName.get(data.get('track')).index(gagName)
                
                if gagLevel <= self.level:
                    self.battleZone.handleGagUse(gagId, avId)
            
            if not avId in self.damagers:
                self.damagers.append(avId)

            if self.isDead():
                self.stopStun()

                if self.firstTimeDead:
                    self.sendUpdate('doStunEffect')

                deathAnim = self.__getAnimForGag(track, gagName)
                self.b_setAnimState(deathAnim, 0)
                
                # Let's give everyone credit who damaged me.
                if self.battleZone:
                    for damager in self.damagers:
                        self.battleZone.handleCogDeath(self, damager)
                        
                self.firstTimeDead = False

            elif gagName in GagGlobals.Stunnables and not self.stunned:
                # We have been stunned.
                self.stopSuitInPlace(killBrain = False)

                animName = self.__getAnimForGag(track, gagName)
                animB4Stun = SuitGlobals.getAnimIdByName(animName)
                self.sendUpdate('stun', [animB4Stun])

                baseStunTime = 6.0
                stunTime = (baseStunTime / self.suitPlan.getCogClassAttrs().dmgMod) * (damage / 95.0)
                taskMgr.doMethodLater(stunTime, self.__stunTask, self.taskName('stunTask'))

                self.stunned = True

            else:
                # Sound will wake me up.
                if self.stunned and track == GagType.SOUND:
                    self.stopStun(restart = True)

                # I've been hit! Take appropriate actions.
                self.handleToonThreat(avatar, True)

            # Do appropriate gag effects.
            flags = 0
            if gagName == GagGlobals.TNT:
                flags |= GagEffects.GEAsh
            if flags != 0:
                self.sendUpdate('doGagEffect', [flags])

    def __handleDeath(self, task):
        if hasattr(self, 'deathTimeLeft'):
            self.deathTimeLeft -= 1

            # Let's handle when we run out of time.
            if self.deathTimeLeft <= 0:
                self.killSuit()
                return task.done
            return task.again
        else:
            return task.done

    def handleAvatarDefeat(self, av):
        if av.isDead() and hasattr(self, 'brain') and self.brain != None:
            self.b_setAnimState('win')
            self.brain.stopThinking()
            taskMgr.doMethodLater(8.5, self.brain.startThinking, self.uniqueName('Resume Thinking'))

    def disableMovement(self):
        self.brain.stopThinking()

    def enableMovement(self):
        self.brain.startThinking()

    def addBehavior(self, behavior, priority):
        self.requestedBehaviors.append([behavior, priority])

    def toonHitByWeapon(self, weaponId, avId, distance):
        weapon = SuitAttacks.SuitAttacks.attack2attackClass[weaponId]
        dmg = CIGlobals.calcAttackDamage(distance, weapon.baseDamage, weapon.maxDist)

        # Factor in class damage modifier
        dmg *= self.suitPlan.getCogClassAttrs().dmgMod

        dmg = int(round(max(1, dmg)))
        print "Cog did {0} damage".format(dmg)

        toon = self.air.doId2do.get(avId, None)
        if toon:
            toon.takeDamage(dmg)
            self.handleAvatarDefeat(toon)

    def turretHitByWeapon(self, weaponId, avId):
        weapon = SuitAttacks.SuitAttacks.attack2attackClass[weaponId]
        dmg = CIGlobals.calcAttackDamage(10.0, weapon.baseDamage, weapon.maxDist)
        turret = self.air.doId2do.get(avId, None)
        if turret:
            turret.b_setHealth(turret.getHealth() - 1)
            turret.d_announceHealth(0, dmg)
            self.handleAvatarDefeat(turret)

    def d_handleWeaponTouch(self):
        self.sendUpdate('handleWeaponTouch', [])

    def d_interruptAttack(self):
        self.sendUpdate('interruptAttack', [])

    def killSuit(self):
        if self.level > 0 and self.health <= 0:
            self.allowHits = False
            self.b_setAnimState('die')
            self.clearTrack()
            self.track = Sequence(Wait(6.0), Func(self.closeSuit))
            self.track.start()

    def closeSuit(self):
        if self.dropItems.getValue():
            self.itemDropper.drop()
        if self.getManager():
            self.getManager().deadSuit(self.doId)
        self.disable()
        self.requestDelete()

    def spawn(self, spawnMode = SpawnMode.FLYDOWN):
        self.brain = SuitBrain(self)
        for behavior, priority in self.requestedBehaviors:
            self.brain.addBehavior(behavior, priority)
        self.requestedBehaviors = []
        if self.suitPlan.getName() in [SuitGlobals.VicePresident]:
            self.brain.addBehavior(SuitCallInBackupBehaviorAI(self), priority = 1)
            self.brain.addBehavior(SuitFlyToRandomSpotBehaviorAI(self), priority = 2)
            self.brain.addBehavior(SuitAttackBehaviorAI(self), priority = 3)
        else:
            pursue = SuitPursueToonBehaviorAI(self, getPathFinder(self.hood))
            pursue.setSuitDict(self.getManager().suits)
            pursue.battle = self.getManager().getBattle()
            self.brain.addBehavior(pursue, priority = 1)
            self.brain.addBehavior(SuitAttackTurretBehaviorAI(self), priority = 2)
        place = CogBattleGlobals.SuitSpawnPoints[self.hood]
        landspot = random.choice(place.keys())
        path = place[landspot]
        index = place.keys().index(landspot)
        self.currentPath = landspot
        yaw = random.uniform(0.0, 360.0)
        self.setH(yaw)
        self.d_setH(yaw)
        self.clearTrack()
        self.track = Sequence()
        if spawnMode == SpawnMode.FLYDOWN:
            flyTrack = self.posInterval(3.5,
                path, startPos = path + (0, 0, 6.5 * 4.8)
            )
            flyTrack.start()
            self.b_setSuitState(2, index, index)
            self.track.append(Wait(6.5))
        self.track.append(Func(self.b_setAnimState, 'neutral'))
        self.track.append(Wait(1.0))
        self.track.append(Func(self.brain.startThinking))
        self.track.start()
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def clearTrack(self):
        if self.track:
            self.track.pause()
            self.track = None

    def setManager(self, suitMgr):
        self.suitMgr = suitMgr
        if hasattr(self.getManager(), 'getBattle'):
            self.hood = CogBattleGlobals.HoodIndex2HoodName[self.getManager().getBattle().getHoodIndex()]

    def getManager(self):
        if hasattr(self, 'suitMgr'):
            return self.suitMgr
        return None

    def generate(self):
        DistributedAvatarAI.generate(self)

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        self.clearTrack()
        self.track = Sequence(Wait(0.1), Func(self.spawn))
        self.track.start()

        # Let's set the combo data task name and start the task.
        self.comboDataTaskName = self.uniqueName('clearComboData')
        taskMgr.add(self.clearComboData, self.comboDataTaskName)

    def disable(self):
        DistributedAvatarAI.disable(self)
        self.clearTrack()
        self.stopStun()
        taskMgr.remove(self.uniqueName('__handleDeath'))
        taskMgr.remove(self.uniqueName('Resume Thinking'))
        taskMgr.remove(self.uniqueName('monitorHealth'))
        taskMgr.remove(self.comboDataTaskName)
        if self.brain:
            self.brain.stopThinking()
            self.brain.unloadBehaviors()
            self.brain = None
        if self.tacticalSeq:
            self.tacticalSeq.pause()
            self.tacticalSeq = None
        if self.dropItems.getValue():
            self.itemDropper.cleanup()
            self.itemDropper = None
        self.lateX = None
        self.lateY = None
        self.anim = None
        self.currentPath = None
        self.currentPathQueue = None
        self.suitState = None
        self.suitPlan = None
        self.variant = None
        self.stateTimestamp = None
        self.startPoint = None
        self.endPoint = None
        self.level = None
        self.suitMgr = None
        self.animStateChangeEvent = None
        self.requestedBehaviors = None
        self.deathAnim = None
        self.deathTimeLeft = None
        self.comboData = None
        self.firstTimeDead = None
        self.clearComboDataTime = None
        self.showComboDamageTime = None
        self.showWeaknessBonusDamageTime = None
        self.stunned = None
        self.damagers = []

    def delete(self):
        self.DELETED = True
        del self.brain
        if self.dropItems.getValue():
            del self.itemDropper
        del self.lateX
        del self.lateY
        del self.anim
        del self.currentPath
        del self.currentPathQueue
        del self.suitState
        del self.suitPlan
        del self.variant
        del self.stateTimestamp
        del self.startPoint
        del self.endPoint
        del self.level
        del self.suitMgr
        del self.animStateChangeEvent
        del self.requestedBehaviors
        del self.track
        del self.deathAnim
        del self.deathTimeLeft
        del self.comboData
        del self.comboDataTaskName
        del self.clearComboDataTime
        del self.showComboDamageTime
        del self.showWeaknessBonusDamageTime
        del self.tacticalSeq
        del self.damagers
        del self.stunned
        DistributedAvatarAI.delete(self)

    def printPos(self, task):
        self.notify.info('%s\n%s' % (self.getPos(render), self.getHpr(render)))
        return task.cont

    def getBrain(self):
        return self.brain

    def setCurrentPath(self, curPath):
        self.currentPath = curPath

    def getCurrentPath(self):
        return self.currentPath

    def getPosFromCurrentPath(self):
        # Get the position of the path we are going to.
        return CogBattleGlobals.SuitSpawnPoints[self.getHood()][self.getCurrentPath()]

    def getCurrentPathQueue(self):
        return self.currentPathQueue
