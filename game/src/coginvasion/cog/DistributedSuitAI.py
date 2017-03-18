# Filename: DistributedSuitAI.py
# Created by:  DecodedLogic (01Sep15)

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.task.Task import Task

from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.suit import CogBattleGlobals
from src.coginvasion.cog.SuitItemDropperAI import SuitItemDropperAI

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.GagType import GagType

from SpawnMode import SpawnMode
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

import types
import random

class DistributedSuitAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory('DistributedSuitAI')

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.anim = 'neutral'
        self.brain = None
        self.track = None
        self.currentPath = None
        self.currentPathQueue = []
        self.suitMgr = None
        self.suitPlan = 0
        self.variant = Variant.NORMAL
        self.itemDropper = SuitItemDropperAI(self)
        self.suitState = 0
        self.startPoint = -1
        self.endPoint = -1
        self.stateTimestamp = 0
        self.level = 0
        self.lateX = 0
        self.lateY = 0
        self.healthChangeEvent = SuitGlobals.healthChangeEvent
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

    def handleToonThreat(self, toon, hasBeenHit):
        if not hasattr(self, 'brain') or self.brain is None:
            return

        if (CIGlobals.areFacingEachOther(self, toon) or hasBeenHit):
            # Woah! This Toon might be trying to attack us!

            doIt = random.choice([True, False])
            if not doIt and not hasBeenHit or not self.brain:
                return

            behav = self.brain.currentBehavior

            if behav.__class__.__name__ == "SuitPursueToonBehaviorAI":

                if behav.fsm.getCurrentState().getName() == "pursue":

                    if self.getDistance(toon) < 40:

                        if toon != behav.target:

                            # We need to make this toon our new target.
                            behav.fsm.request("off")
                            behav.setTarget(toon)

                        # Attack
                        behav.fsm.request("attack", [False])



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
        self.maxHealth = CIGlobals.getSuitHP(self.level)
        self.health = self.maxHealth
        self.itemDropper.calculate(tutorial)

        if self.level == 0:
            self.maxHealth = 1
            self.health = self.maxHealth

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
            if animId == None and anim != 'flyNeutral':
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
        messenger.send(self.healthChangeEvent, [health, prevHealth])

        if not self.isDead() or self.isDead() and self.deathTimeLeft > 0:
            self.d_announceHealth(0, prevHealth - self.health)

    def monitorHealth(self, task):
        if self.health <= 0:
            if hasattr(self, 'brain') and self.brain is not None:
                self.brain.stopThinking()
                self.brain.unloadBehaviors()
                self.brain = None
            self.b_setSuitState(0, -1, -1)
            currentAnim = SuitGlobals.getAnimByName(self.anim)
            self.clearTrack()
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
            return Task.done
        return Task.cont

    def clearComboData(self, task):
        self.comboData = {}

        task.delayTime = self.clearComboDataTime
        return Task.again
            
    def __handleTacticalAttacks(self, avId, gagName, gagData):
        # Factor in any weaknesses / immunities to the damage this gag does.
        weaknessFactor = self.suitPlan.getGagWeaknesses().get(gagName, 1.0)
        baseDmg = float(gagData.get('damage', 0.0))
        dmgOffset = int(math.ceil(baseDmg * weaknessFactor)) - baseDmg

        self.tacticalSeq = Sequence()
        
        # Let's handle combos.
        isCombo, comboDamage = self.__handleCombos(avId, gagName)

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

    def __handleCombos(self, avId, gagName):
        track = GagGlobals.getTrackOfGag(gagName)
        damage = GagGlobals.getGagData(GagGlobals.getIDByName(gagName)).get('damage')
        self.comboData.update({avId : {track : damage}})

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

    # The new method for handling gags.
    def hitByGag(self, gagId):
        avatar = self.air.doId2do.get(self.air.getAvatarIdFromSender(), None)
        gagName = GagGlobals.getGagByID(gagId)
        data = GagGlobals.getGagData(gagId)
        track = GagGlobals.getTrackOfGag(gagId, getId = True)

        if self.canGetHit():
            self.__handleTacticalAttacks(avatar.doId, gagName, data)

            if self.isDead():
                if track == GagType.THROW or gagName == CIGlobals.TNT:
                    self.b_setAnimState('pie', 0)
                elif track == GagType.DROP:
                    majorDrops = [CIGlobals.GrandPiano, CIGlobals.Safe, CIGlobals.BigWeight]
                    if gagName in majorDrops:
                        self.b_setAnimState('drop', 0)
                    else:
                        self.b_setAnimState('drop-react', 0)
                elif track == GagType.SQUIRT or track == GagType.SOUND:
                    if gagName == CIGlobals.StormCloud:
                        self.b_setAnimState('soak', 0)
                    else:
                        self.b_setAnimState('squirt-small', 0)
                avatar.questManager.cogDefeated(self)
            else:
                # I've been hit! Take appropriate actions.
                self.handleToonThreat(avatar, True)

    def __handleDeath(self, task):
        if hasattr(self, 'deathTimeLeft'):
            self.deathTimeLeft -= 1

            # Let's handle when we run out of time.
            if self.deathTimeLeft <= 0:
                self.killSuit()
                return Task.done
            return Task.again
        else:
            return Task.done

    def handleAvatarDefeat(self, av):
        if av.isDead() and hasattr(self, 'brain') and self.brain != None:
            self.b_setAnimState('win')
            self.brain.stopThinking()
            taskMgr.doMethodLater(6.0, self.brain.startThinking, self.uniqueName('Resume Thinking'))

    def disableMovement(self):
        self.brain.stopThinking()

    def enableMovement(self):
        self.brain.startThinking()

    def addBehavior(self, behavior, priority):
        self.requestedBehaviors.append([behavior, priority])

    def toonHitByWeapon(self, weaponId, avId):
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup", "buzzword", "razzledazzle",
                        "jargon", "mumbojumbo", 'doubletalk', 'schmooze', 'fingerwag', 'filibuster']:
            self.d_handleWeaponTouch()
        dmg = int(self.getMaxHealth() / SuitAttacks.SuitAttackDamageFactors[weapon])
        if dmg == 0:
            # Prevents level 1 and 2 Cogs from doing 0 damage.
            dmg = 1

        # Temporary way to nerf VP to Level 12 damage.
        if self.suitPlan.getName() == SuitGlobals.VicePresident:
            dmg = int(200 / SuitAttacks.SuitAttackDamageFactors[weapon])

        toon = self.air.doId2do.get(avId, None)
        if toon:
            hp = toon.getHealth() - dmg
            if hp < 0:
                hp = 0
            toon.b_setHealth(hp)
            toon.d_announceHealth(0, -dmg)
            self.handleAvatarDefeat(toon)

    def turretHitByWeapon(self, weaponId, avId):
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup"]:
            self.d_handleWeaponTouch()
        dmg = int(self.maxHealth / SuitAttacks.SuitAttackDamageFactors[weapon])
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

    def closeSuit(self, dropItem = True):
        if dropItem:
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
        place = CIGlobals.SuitSpawnPoints[self.hood]
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
        DistributedSmoothNodeAI.generate(self)

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
        self.healthChangeEvent = None
        self.animStateChangeEvent = None
        self.requestedBehaviors = None
        self.deathAnim = None
        self.deathTimeLeft = None
        self.comboData = None
        self.clearComboDataTime = None
        self.showComboDamageTime = None
        self.showWeaknessBonusDamageTime = None

    def delete(self):
        self.DELETED = True
        del self.brain
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
        del self.healthChangeEvent
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
        DistributedAvatarAI.delete(self)
        DistributedSmoothNodeAI.delete(self)

    def printPos(self, task):
        print '%s\n%s' % (self.getPos(render), self.getHpr(render))
        return Task.cont

    def getBrain(self):
        return self.brain

    def setCurrentPath(self, curPath):
        self.currentPath = curPath

    def getCurrentPath(self):
        return self.currentPath

    def getPosFromCurrentPath(self):
        # Get the position of the path we are going to.
        return CIGlobals.SuitSpawnPoints[self.getHood()][self.getCurrentPath()]

    def getCurrentPathQueue(self):
        return self.currentPathQueue
