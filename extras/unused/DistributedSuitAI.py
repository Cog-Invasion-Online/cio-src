# Filename: DistributedSuitAI.py
# Created by:  blach (01Nov14)

from panda3d.core import *
from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from lib.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import *
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
import SuitBoss
import CogBrainAI
from SuitItemDropper import SuitItemDropper
from direct.distributed.ClockDelta import globalClockDelta
import random
import types
import CogBattleGlobals
import SuitAttacks

class DistributedSuitAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory("DistributedSuitAI")

    def __init__(self, air):
        try:
            self.DistributedSuitAI_initialized
            return
        except:
            self.DistributedSuitAI_initialized = 1
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.itemDropper = SuitItemDropper(self)
        self.avatarType = CIGlobals.Suit
        self.aiChar = None
        self.aiBehaviors = None
        self.walkTrack = None
        self.name = ""
        self.anim = "neutral"
        self.state = "alive"
        self.damage = 0
        self.health = 132
        self.type = "A"
        self.team = "c"
        self.head = "bigcheese"
        self.name = "The Big Cheese"
        self.skeleton = 0
        self.dmg_lbl = None
        self.lbl_int = None
        self.bean = None
        self.boss = None
        self.brain = None
        self.startPoint = -1
        self.endPoint = -1
        self.suitState = 0
        self.walkPaused = 0
        self.attacking = False
        self.suitHealTrack = None
        self.continuePathId = 0
        self.attackId = 0
        self.mgr = None
        self.backup = 0
        self.difficulty = None
        self.track = None
        self.lateX = 0
        self.lateY = 0
        self.stateTimestamp = 0
        self.animState2animId = {
            'off': 13,
            'neutral': 10,
            'walk': 9,
            'die': 5,
            'attack': 7,
            'flydown': 1,
            'pie': 4,
            'win': 12,
            'flyaway': 14,
            'rollodex': 3,
            'flyNeutral': 15,
            'flail': 0,
            'drop': 6,
            'drop-react' : 16,
            'squirt-large': 8,
            'squirt-small': 11,
            'soak' : 2,
        }
        self.animId2animState = {v: k for k, v in self.animState2animId.items()}
        self.level = 0
        self.currentPathQueue = []
        return

    def resetPathQueue(self):
        self.currentPathQueue = []

    def setLevel(self, level):
        self.level = level

    def d_setLevel(self, level):
        self.sendUpdate('setLevel', [level])

    def b_setLevel(self, level):
        self.d_setLevel(level)
        self.setLevel(level)

    def getLevel(self):
        return self.level

    def setLatePos(self, x, y):
        self.lateX = x
        self.lateY = y

    def getLatePos(self):
        return [self.lateX, self.lateY]

    def setSuitState(self, index, startPoint, endPoint):
        if index == 0:
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

    def setDifficulty(self, difficulty):
        self.difficulty = difficulty

    def getDifficulty(self):
        return self.difficulty

    def setBackup(self, backup):
        self.backup = backup

    def isBackup(self):
        return self.backup

    def setManager(self, mgr):
        self.mgr = mgr
        self.hood = CogBattleGlobals.HoodIndex2HoodName[self.getManager().getBattle().getHoodIndex()]

    def getManager(self):
        return self.mgr

    def printPos(self, task):
        print self.getPos(render)
        print self.getHpr(render)
        return task.cont

    def spawn(self):
        self.brain = CogBrainAI.CogBrain(self)
        landspot = random.choice(CIGlobals.SuitSpawnPoints[self.hood].keys())
        path = CIGlobals.SuitSpawnPoints[self.hood][landspot]
        index = CIGlobals.SuitSpawnPoints[self.hood].keys().index(landspot)
        self.b_setSuitState(2, index, index)
        self.currentPath = landspot
        track = self.posInterval(3,
                    path,
                    startPos = path + (0, 0, 50))
        track.start()
        yaw = random.uniform(0.0, 360.0)
        self.setH(yaw)
        if self.track:
            self.track.pause()
            self.track = None
        self.track = Sequence(Wait(5.4),
            Func(self.b_setAnimState, 'neutral'),
            Wait(1.0),
            Func(self.startRoaming))
        self.track.start()
        self.b_setParent(CIGlobals.SPRender)

    def startRoaming(self):
        if self.head == "vp" or self.isBackup():
            # If this is a vp or a backup cog, do the random attacks.
            self.startAttacks()
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
        if self.head == "vp":
            self.boss = SuitBoss.SuitBoss(self)
            self.boss.startBoss()
        else:
            self.brain.start()

    def startAttacks(self):
        if self.head != "vp":
            attackTime = random.randint(8, 20)
        else:
            attackTime = random.randint(8, 12)
        taskMgr.doMethodLater(attackTime, self.attackTask, self.uniqueName('attackTask'))

    def attackTask(self, task):
        if self.brain.fsm.getCurrentState().getName() == "runAway":
            # Attack while running away... ain't nobody got time for that!
            delay = random.randint(6, 12)
            task.delayTime = delay
            return task.again
        if self.head == "vp":
            # We can't attack while we're flying
            if not self.boss.getFlying():
                self.chooseVictim()
        else:
            self.chooseVictim()
        if self.head != "vp":
            delay = random.randint(6, 15)
        else:
            delay = random.randint(6, 12)
        task.delayTime = delay
        return task.again

    def enableMovement(self):
        self.brain.start()
        if self.head != "vp":
            attackTime = random.randint(8, 20)
        else:
            attackTime = random.randint(8, 12)
        taskMgr.doMethodLater(attackTime, self.attackTask, self.uniqueName('attackTask'))

    def disableMovement(self):
        taskMgr.remove(self.uniqueName('attackTask'))
        taskMgr.remove(self.uniqueName('continueSuitRoam'))
        if self.suitHealTrack:
            self.suitHealTrack.pause()
            self.suitHealTrack = None
        self.brain.end()
        self.b_setSuitState(3, -1, -1)
        if self.head != "vp":
            if self.walkTrack:
                self.ignore(self.walkTrack.getName())
                self.walkTrack.clearToInitial()
                self.walkTrack = None
        self.d_interruptAttack()

    def chooseVictim(self):
        toons = []
        for key in self.air.doId2do.keys():
            val = self.air.doId2do[key]
            if val.__class__.__name__ == "DistributedToonAI" or val.__class__.__name__ == "DistributedSuitAI" or val.__class__.__name__ == "DistributedPieTurretAI":
                if val.zoneId == self.zoneId:
                    if val.__class__.__name__ == "DistributedSuitAI" and val.head == "vp" \
                    and val.doId != self.doId or val.__class__.__name__ == "DistributedToonAI" or val.__class__.__name__ == "DistributedPieTurretAI":
                        # We can be a medic and heal the fellow VP...
                        if not val.isDead():
                            if self.getDistance(val) <= 40:
                                if val.__class__.__name__== "DistributedToonAI":
                                    if not val.getGhost():
                                        toons.append(val)
                                else:
                                    toons.append(val)
        if toons == []:
            return
        toon = random.randint(0, len(toons) - 1)
        self.disableMovement()
        self.headsUp(toons[toon])
        self.attackToon(toons[toon])
        self.setAttacking(True)

    def attackToon(self, av):
        if av.__class__.__name__ in ["DistributedSuitAI", "DistributedPieTurretAI"]:
            # Why would I pick pocket my boss?
            attack = random.randint(0, 6)
            attackName = SuitAttacks.SuitAttackLengths.keys()[attack]
        else:
            if self.head in ['vp']:
                attack = random.randint(0, 6)
                attackName = SuitAttacks.SuitAttackLengths.keys()[attack]
            else:
                attackName = random.choice(SuitAttacks.SuitAttackLengths.keys())
                attack = SuitAttacks.SuitAttackLengths.keys().index(attackName)
        attackTaunt = random.randint(0, len(CIGlobals.SuitAttackTaunts[attackName]) - 1)
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('doAttack', [attack, av.doId, timestamp])
        if av.__class__.__name__ in ["DistributedSuitAI", "DistributedPieTurretAI"]:
            distance = self.getDistance(av)
            speed = 50.0
            if attackName == "glowerpower":
                speed = 100.0
            timeUntilHeal = distance / speed
            if av.__class__.__name__ == "DistributedSuitAI":
                self.d_setChat(CIGlobals.SuitHealTaunt)
            else:
                self.d_setChat(CIGlobals.SuitAttackTaunts[attackName][attackTaunt])
            if attackName != "glowerpower":
                if self.type == "C":
                    timeUntilRelease = 2.2
                else:
                    timeUntilRelease = 3.0
            else:
                timeUntilRelease = 1.0
            currentBossPos = av.getPos(render)
            hp = int(self.maxHealth / SuitAttacks.SuitAttackDamageFactors[attackName])
            self.suitHealTrack = Sequence(
                Wait(timeUntilRelease + timeUntilHeal),
                Func(
                    self.attemptToHealBoss,
                    av,
                    currentBossPos,
                    hp
                )
            )
            self.suitHealTrack.start()
        else:
            self.d_setChat(CIGlobals.SuitAttackTaunts[attackName][attackTaunt])
        time = SuitAttacks.SuitAttackLengths[attackName]
        if self.track:
            self.track.pause()
            self.track = None
        taskMgr.doMethodLater(SuitAttacks.SuitAttackLengths[attackName],
                self.continuePathTask, self.uniqueName('continueSuitRoam'))

    def attemptToHealBoss(self, boss, currBossPos, hp):
        if not boss.isEmpty():
            if (boss.getPos(render) - currBossPos).length() <= 1:
                if not boss.isDead():
                    if boss.__class__.__name__ == "DistributedSuitAI":
                        boss.b_setHealth(boss.getHealth() + hp)
                        boss.d_announceHealth(1, hp)
                    else:
                        # Turret
                        boss.b_setHealth(boss.getHealth() - hp)
                        boss.d_announceHealth(0, hp)
                    self.d_handleWeaponTouch()

    def continuePathTask(self, task):
        self.setAttacking(False)
        if self.head != "vp":
            if self.brain.fsm.getCurrentState().getName() == "followBoss":
                # If we're protecting the boss, don't walk away from him!
                return task.done
            else:
                self.brain.neutral_startLookingForToons()
                self.brain.start()
                return task.done
        self.continuePath()
        return task.done

    def d_handleWeaponTouch(self):
        self.sendUpdate("handleWeaponTouch", [])

    def continuePath(self):
        # Create a new path for the Suit if they are stuck...
        if self.head != "vp":
            if self.walkTrack:
                self.ignore(self.walkTrack.getName())
                self.walkTrack.clearToInitial()
                self.walkTrack = None
            self.brain.end()
            self.brain.start()
        else:
            self.b_setAnimState("neutral")

    def setAttacking(self, value):
        self.attacking = value

    def getAttacking(self):
        return self.attacking

    def monitorHealth(self, task):
        if self.health <= 0:
            taskMgr.remove(self.uniqueName('attackTask'))
            taskMgr.remove(self.uniqueName('continueSuitRoam'))
            if self.suitHealTrack:
                self.suitHealTrack.pause()
                self.suitHealTrack = None
            self.b_setSuitState(3, -1, -1)
            if self.walkTrack:
                self.ignore(self.walkTrack.getName())
                self.walkTrack.clearToInitial()
                self.walkTrack = None
            self.d_interruptAttack()
            self.brain.end()
            if self.head == "vp":
                self.boss.stopBoss()
            if self.track:
                self.track.pause()
                self.track = None

            anim2WaitTime = {
                'pie': 2.0,
                'drop': 6.0,
                'drop-react' : 3.5,
                'squirt-small': 4.0,
                'squirt-large': 4.9,
                'soak' : 6.5,
                'neutral': 0.0,
                'walk': 0.0
            }
            self.track = Sequence(Wait(anim2WaitTime[self.getAnimStateStr()]), Func(self.killSuit))
            self.track.start()

            return task.done
        return task.cont

    def isWalking(self):
        if self.walkTrack:
            return self.walkTrack.isPlaying()
        else:
            return False

    def killSuit(self):
        self.b_setAnimState('die')
        if self.track:
            self.track.pause()
            self.track = None
        self.track = Sequence(Wait(6.0), Func(self.closeSuit))
        self.track.start()

    def closeSuit(self):
        # Drop the jellybeans I stole before I die!
        self.itemDropper.drop()
        self.getManager().deadSuit(self.doId)
        self.disable()
        self.requestDelete()

    def createPath(self, path_key = None, durationFactor = 0.2, fromCurPos = False):
        if path_key == None and not len(self.currentPathQueue):
            path_key_list = CIGlobals.SuitPathData[self.hood][self.currentPath]
            path_key = random.choice(path_key_list)
        elif len(self.currentPathQueue):
            path_key = self.currentPathQueue[0]
            self.currentPathQueue.remove(path_key)
        endIndex = CIGlobals.SuitSpawnPoints[self.hood].keys().index(path_key)
        path = CIGlobals.SuitSpawnPoints[self.hood][path_key]
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.clearToInitial()
            self.walkTrack = None
        if not self.currentPath or fromCurPos:
            startIndex = -1
        else:
            oldPath = self.currentPath
            startIndex = CIGlobals.SuitSpawnPoints[self.hood].keys().index(oldPath)
        self.currentPath = path_key
        pathName = self.uniqueName('suitPath')
        self.walkTrack = NPCWalkInterval(self, path, startPos = self.getPos(render),
            name = pathName, durationFactor = durationFactor, fluid = 1)
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.startFollow()
        self.b_setSuitState(1, startIndex, endIndex)

    def startFollow(self):
        #self.b_setAnimState('walk')
        if self.walkTrack:
            self.acceptOnce(self.walkTrack.getName(), self.walkDone)
            self.walkTrack.start()

    def walkDone(self):
        if self.walkTrack:
            self.walkTrack.finish()
            self.walkTrack = None
        self.b_setAnimState('neutral')
        self.createPath()

    def toonHitByWeapon(self, weaponId, avId):
        sender = self.air.getMsgSender()
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup", "buzzword", "razzledazzle",
                        "jargon", "mumbojumbo", 'doubletalk', 'schmooze', 'fingerwag', 'filibuster']:
            self.d_handleWeaponTouch()
        dmg = int(self.maxHealth / SuitAttacks.SuitAttackDamageFactors[weapon])
        toon = self.air.doId2do.get(avId, None)
        if toon:
            hp = toon.getHealth() - dmg
            if hp < 0:
                hp = 0
            toon.b_setHealth(hp)
            toon.d_announceHealth(0, dmg)
            if toon.isDead():
                self.b_setAnimState('win')
                taskMgr.remove(self.uniqueName('continueSuitRoam'))
                taskMgr.doMethodLater(6.0, self.continuePathTask, self.uniqueName('continueSuitRoam'))

    def turretHitByWeapon(weaponId, avId):
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup"]:
            self.d_handleWeaponTouch()
        dmg = int(self.maxHealth / CIGlobals.SuitAttackDamageFactors[weapon])
        turret = self.air.doId2do.get(avId, None)
        if turret:
            turret.b_setHealth(turret.getHealth() - 1)
            turret.d_announceHealth(0, dmg)

    def setSuit(self, suitType, head, team, skeleton):
        self.type = suitType
        self.head = head
        self.team = team
        self.skeleton = skeleton
        self.health = CIGlobals.getSuitHP(self.level)
        self.maxHealth = self.health
        self.itemDropper.calculate()

    def b_setSuit(self, suitType, head, team, skeleton):
        self.d_setSuit(suitType, head, team, skeleton)
        self.setSuit(suitType, head, team, skeleton)

    def d_setSuit(self, suitType, head, team, skeleton):
        self.sendUpdate("setSuit", [suitType, head, team, skeleton])

    def getSuit(self):
        return tuple((self.type, self.head, self.team, self.skeleton))

    def setAnimState(self, anim):
        self.anim = anim

    def b_setAnimState(self, anim):
        if type(anim) == types.StringType:
            anim = self.animState2animId[anim]
        self.d_setAnimState(anim)
        self.setAnimState(anim)

    def d_setAnimState(self, anim):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate("setAnimState", [anim, timestamp])

    def getAnimState(self):
        return self.anim

    def getAnimStateStr(self):
        return self.animId2animState[self.getAnimState()]

    def d_interruptAttack(self):
        self.sendUpdate("interruptAttack", [])

    def d_setAttack(self, attack):
        self.sendUpdate("setAttack", [attack])

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        if self.track:
            self.track.pause()
            self.track = None
        Sequence(Wait(0.1), Func(self.spawn)).start()

    def generate(self):
        DistributedAvatarAI.generate(self)
        DistributedSmoothNodeAI.generate(self)

    def disable(self):
        try:
            self.DistributedSuitAI_disabled
        except:
            self.DistributedSuitAI_disabled = 1
            if self.track:
                self.track.pause()
                self.track = None
            taskMgr.remove(self.uniqueName('monitorHealth'))
            taskMgr.remove(self.uniqueName('attackTask'))
            taskMgr.remove(self.uniqueName('continueSuitRoam'))
            if self.suitHealTrack:
                self.suitHealTrack.pause()
                self.suitHealTrack = None
            if self.walkTrack:
                self.ignore(self.walkTrack.getName())
                self.walkTrack.clearToInitial()
                self.walkTrack = None
            if self.boss:
                self.boss.stopBoss()
                self.boss = None
            if self.brain:
                self.brain.end()
                self.brain = None
            self.itemDropper.cleanup()
            self.itemDropper = None
            self.aiChar = None
            self.aiBehaviors = None
            self.continuePathId = None
            self.attackId = None
            self.name = None
            self.anim = None
            self.state = None
            self.damage = None
            self.health = None
            self.backup = None
            self.type = None
            self.team = None
            self.head = None
            self.skeleton = 0
            self.dmg_lbl = None
            self.currentPath = None
            self.lbl_int = None
            self.bean = None
            self.avatarType = None
            self.lateX = None
            self.lateY = None
            self.currentPathQueue = None
            DistributedAvatarAI.disable(self)
        return

    def delete(self):
        try:
            self.DistributedSuitAI_deleted
        except:
            self.DistributedSuitAI_deleted = 1
            del self.aiChar
            del self.brain
            del self.aiBehaviors
            del self.boss
            del self.continuePathId
            del self.attackId
            del self.name
            del self.anim
            del self.state
            del self.damage
            del self.health
            del self.type
            del self.team
            del self.head
            del self.skeleton
            del self.dmg_lbl
            del self.lbl_int
            del self.bean
            del self.currentPath
            del self.avatarType
            del self.walkTrack
            del self.suitHealTrack
            del self.backup
            del self.lateX
            del self.lateY
            del self.currentPathQueue
            DistributedAvatarAI.delete(self)
            DistributedSmoothNodeAI.delete(self)
        return
