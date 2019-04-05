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
from src.coginvasion.avatar.Activities import ACT_WAKE_ANGRY, ACT_SMALL_FLINCH, ACT_DIE, ACT_VICTORY_DANCE
from src.coginvasion.avatar.AvatarTypes import *
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.AIGlobal import *
from src.coginvasion.globals import CIGlobals

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.GagType import GagType

from SuitBank import SuitPlan
import SuitBank
import SuitGlobals
import SuitType
import Variant
import GagEffects

import types
import random
import math

class DistributedSuitAI(DistributedAvatarAI, BaseNPCAI):
    notify = directNotify.newCategory('DistributedSuitAI')
    
    AvatarType = AVATAR_SUIT
    Relationships = {
        AVATAR_SUIT     :   RELATIONSHIP_FRIEND,
        AVATAR_TOON     :   RELATIONSHIP_HATE,
        AVATAR_CCHAR    :   RELATIONSHIP_DISLIKE
    }

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        BaseNPCAI.__init__(self)
        self.anim = 'neutral'
        self.track = None
        self.currentPath = None
        self.currentPathQueue = []
        self.suitMgr = None
        self.suitPlan = 0
        self.variant = Variant.NORMAL
        self.suitState = 0
        self.startPoint = -1
        self.endPoint = -1
        self.stateTimestamp = 0
        self.level = 0
        self.animStateChangeEvent = SuitGlobals.animStateChangeEvent

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

        self.damagers = []

        from src.coginvasion.attack.Attacks import ATTACK_CLIPONTIE, ATTACK_BOMB, ATTACK_PICKPOCKET, ATTACK_FIRED, ATTACK_EVIL_EYE
        self.attackIds = [ATTACK_CLIPONTIE, ATTACK_BOMB, ATTACK_PICKPOCKET, ATTACK_FIRED, ATTACK_EVIL_EYE]

        self.activities = {ACT_WAKE_ANGRY   :   0.564,
                           ACT_SMALL_FLINCH :   2.25,
                           ACT_DIE          :   6.0,
                           ACT_VICTORY_DANCE:   9.0}
                           
        self.schedules.update({
        
            "VICTORY_TAUNT" :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_Speak(self, 0.5, ["Aha, Toon! You thought you could get past me!",
                                           "Caught tweakin, jit!",
                                           "I told you it was my turn to play on the XBOX!"]),
                    Task_SetActivity(self, ACT_VICTORY_DANCE),
                    Task_AwaitActivity(self)
                ],
                interruptMask = COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE
            )
        
        })

    def setNPCState(self, state):
        if state != self.npcState:
            if state == STATE_COMBAT:
                if self.hasConditions(COND_NEW_TARGET):
                    task_oneOff(Task_Speak(self, 0.3, ["Your silly jokes can't stop me, Toon.",
                                                       "Contact confirmed. Subject: Anarchy",
                                                       "Toon spotted!",
                                                       "Cogs, catch that Toon!"]))
        BaseNPCAI.setNPCState(self, state)
        
    def getSchedule(self):
        if self.npcState == STATE_COMBAT:
            if self.hasConditions(COND_TARGET_DEAD):
                return self.getScheduleByName("VICTORY_TAUNT")
                
        return BaseNPCAI.getSchedule(self)

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
        self.d_setHitboxData(*self.getHitboxData())
        self.d_setMaxHealth(self.maxHealth)
        self.d_setHealth(self.health)

    def d_setSuit(self, plan, variant = 0):
        if isinstance(plan, SuitPlan):
            plan = SuitBank.getIdFromSuit(plan)
        self.sendUpdate('setSuit', [plan, variant])

    def setSuit(self, plan, variant = 0, tutorial = None):
        self.suitPlan = plan
        self.variant = Variant.getVariantById(variant)

        # setup the hitbox
        self.setHitboxData(0, 2, self.suitPlan.getHeight())

        classAttrs = plan.getCogClassAttrs()
        self.maxHealth = classAttrs.baseHp
        self.maxHealth += SuitGlobals.calculateHP(self.level)
        self.maxHealth *= classAttrs.hpMod

        self.health = self.maxHealth

        if self.level == 0:
            self.maxHealth = 1
            self.health = self.maxHealth
            
        self.setMaxHealth(self.maxHealth)
        self.setHealth(self.health)
        
        # Let's add type specific attacks
        if self.suitPlan.getSuitType() == SuitType.C:
            from src.coginvasion.attack.Attacks import ATTACK_WATER_COOLER
            self.attackIds.append(ATTACK_WATER_COOLER)

    def getSuit(self):
        if isinstance(self.suitPlan, int):
            return tuple((self.suitPlan, self.variant))
            
        return tuple((SuitBank.getIdFromSuit(self.suitPlan), self.variant))

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
        #self.stopAI()
        #self.b_setSuitState(0, -1, -1)
        self.clearTrack()

    def restartSuit(self):
        self.startAI()

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
            
    def __handleTacticalAttacks(self, avId, gagName, gagData, damageInfo, isPlayer):
        # Gets the damage and the damage offset.
        baseDmg, dmgOffset = self.__getGagEffectOnMe(avId, gagName, gagData, damageInfo, isPlayer)

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
        
    def __getGagEffectOnMe(self, avId, gagName, gagData, damageInfo, isPlayer):
        """ Returns the base damage and the damage offset a specified gag name used by "avId" has on this Cog """
        weaknessFactor = self.suitPlan.getGagWeaknesses().get(gagName, 1.0)
        classWeakness = self.suitPlan.getCogClassAttrs().getGagDmgRamp(GagGlobals.getTrackOfGag(gagName))
        if isPlayer:
            baseDmg = GagGlobals.calculateDamage(avId, gagName, gagData)
        else:
            baseDmg = damageInfo.damageAmount
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
        
        # Do the pie flail by default
        return 'pie'

    def stopStun(self, restart = False):
        taskMgr.remove(self.taskName('stunTask'))
        self.stunned = False
        if restart and not self.isDead():
            self.restartSuit()

    def __stunTask(self, task):
        self.stopStun(restart = True)
        return task.done

    # The new method for handling gags.
    def takeDamage(self, damageInfo):#, gagId, distance):
        gagId = damageInfo.attackID
        distance = damageInfo.damageDistance
        avId = damageInfo.damager.doId
        avatar = damageInfo.damager
        gagName = GagGlobals.getGagByID(gagId)
        data = dict(GagGlobals.getGagData(gagId))
        data['distance'] = distance
        track = GagGlobals.getTrackOfGag(gagId, getId = True)

        isPlayer = hasattr(avatar, "trackExperience")

        if self.canGetHit():
            damage = self.__handleTacticalAttacks(avatar.doId, gagName, data, damageInfo, isPlayer)

            self.setDamageConditions(damage)
            
            if isPlayer and self.battleZone:
                # We only want to award credit when Toons use gags that are less than or at the level of the Cog
                # they're using them on.
                gagLevel = GagGlobals.TrackGagNamesByTrackName.get(data.get('track')).index(gagName)
                
                if gagLevel <= self.level:
                    self.battleZone.handleGagUse(gagId, avId)
            
            if isPlayer and not avId in self.damagers:
                self.damagers.append(avId)

            if self.isDead():
                self.stopStun()

                #if self.firstTimeDead:
                #    self.sendUpdate('doStunEffect')

                deathAnim = self.__getAnimForGag(track, gagName)
                #self.b_setAnimState(deathAnim, 0)

                #self.stopAI()
                
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
                #self.handleToonThreat(avatar, True)

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

    def __resumeThinking(self, task):
        self.startAI()
        return task.done

    def handleAvatarDefeat(self, av):
        if av.isDead() and hasattr(self, 'brain') and self.brain != None:
            #self.b_setAnimState('win')
            self.stopAI()
            taskMgr.doMethodLater(8.5, self.__resumeThinking, self.uniqueName('Resume Thinking'))

    def toonHitByWeapon(self, weaponId, avId, distance):
        weapon = SuitAttacks.SuitAttacks.attack2attackClass[weaponId]
        dmg = CIGlobals.calcAttackDamage(distance, weapon.baseDamage, weapon.maxDist)

        # Factor in class damage modifier
        dmg *= self.suitPlan.getCogClassAttrs().dmgMod

        dmg = int(round(max(1, dmg)))
        print "Cog did {0} damage".format(dmg)

        toon = self.air.doId2do.get(avId, None)
        if toon:
            dmgInfo = TakeDamageInfo(self, weaponId, dmg)
            toon.takeDamage(dmgInfo)
            self.handleAvatarDefeat(toon)

    def killSuit(self):
        if self.level > 0 and self.health <= 0:
            self.allowHits = False
            #self.b_setAnimState('die')
            #print "Setting death activity"
            #self.b_setActivity(ACT_DIE)
            self.clearTrack()
            self.track = Sequence(Wait(6.0), Func(self.closeSuit))
            self.track.start()

    def closeSuit(self):
        print "Closing suit"
        if self.battleZone:
            self.battleZone.deadSuit(self.doId)
        self.disable()
        self.requestDelete()

    def clearTrack(self):
        if self.track:
            self.track.pause()
            self.track = None

    def generate(self):
        DistributedAvatarAI.generate(self)
        
    def spawnGeneric(self):
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        self.clearTrack()
        
        self.startAI()

        # Let's set the combo data task name and start the task.
        self.comboDataTaskName = self.uniqueName('clearComboData')
        taskMgr.add(self.clearComboData, self.comboDataTaskName)

        #dur = 8

        #Sequence(
        #    Func(self.setH, 90),
        #    Wait(0.5),
        #    self.posInterval(dur, (-25, 0, 0), (25, 0, 0), blendType = 'easeInOut'),
        #    Wait(0.5),
        #    Func(self.setH, -90),
        #    Wait(0.5),
        #    self.posInterval(dur, (25, 0, 0), (-25, 0, 0), blendType = 'easeInOut'),
        #    Wait(0.5)
        #    )#.loop()
        #self.setH(90)

        self.startPosHprBroadcast()

    def disable(self):
        self.stopPosHprBroadcast()
        DistributedAvatarAI.disable(self)
        self.stopAI()
        self.clearTrack()
        self.stopStun()
        taskMgr.remove(self.uniqueName('__handleDeath'))
        taskMgr.remove(self.uniqueName('Resume Thinking'))
        taskMgr.remove(self.uniqueName('monitorHealth'))
        taskMgr.remove(self.comboDataTaskName)
        if self.tacticalSeq:
            self.tacticalSeq.pause()
            self.tacticalSeq = None
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
        BaseNPCAI.delete(self)
        self.DELETED = True
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

    def setCurrentPath(self, curPath):
        self.currentPath = curPath

    def getCurrentPath(self):
        return self.currentPath

    def getPosFromCurrentPath(self):
        # Get the position of the path we are going to.
        return CogBattleGlobals.SuitSpawnPoints[self.getHood()][self.getCurrentPath()]

    def getCurrentPathQueue(self):
        return self.currentPathQueue
