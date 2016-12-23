# Filename: DistributedSuitManagerAI.py
# Created by:  blach (22Dec14)

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from src.coginvasion.cog import Variant
from src.coginvasion.cog import SuitBank
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.suit.SuitTournament import SuitTournament
from src.coginvasion.globals import CIGlobals
import CogBattleGlobals
import random

class DistributedSuitManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory("DistributedSuitManagerAI")

    chances = {'invasion': range(56, 100 + 1), 'cog': range(8, 55 + 1), 'tournament': range(1, 7 + 1)}
    # The delays after a certain spawn type has ended
    delayRangeBySpawn = {'invasion': [20, 40], 'cog': [5, 20], 'tournament': [20, 40]}
    suitsRequestBySize = {'small': 7, 'medium': 14, 'large': 21}

    def __init__(self, air):
        try:
            self.DistributedSuitManagerAI_initialized
            return
        except:
            self.DistributedSuitManagerAI_initialized = 1
        DistributedObjectAI.__init__(self, air)
        self.tournament = SuitTournament(self)
        self.suits = {}
        self.numSuits = 0
        self.activeInvasion = False
        self.suitsSpawnedThisInvasion = 0
        self.suitsRequest = -1
        self.lastChoice = None
        self.totalSuitsThisShift = 0
        self.maxSuitsThisShift = 0
        self.spawnerStatus = 0
        self.battle = None
        self.drops = []
        self.currInvasionSize = None
        return

    def addDrop(self, drop):
        self.drops.append(drop)

    def removeDrop(self, drop):
        self.drops.remove(drop)

    def getDrops(self):
        return self.drops

    def setBattle(self, battle):
        self.battle = battle

    def getBattle(self):
        return self.battle

    def spawner(self, onOrOff):
        self.spawnerStatus = onOrOff

    def b_spawner(self, onOrOff):
        self.d_spawner(onOrOff)
        self.spawner(onOrOff)

    def d_spawner(self, onOrOff):
        self.sendUpdate('spawner', [onOrOff])

    def getSpawner(self):
        return self.spawnerStatus

    def suitAdminCommand(self, adminToken, commandName):
        avId = self.air.getAvatarIdFromSender()
        tokens = [CIGlobals.DevToken, CIGlobals.UndercoverToken, CIGlobals.ModToken]
        av = self.air.doId2do.get(avId, None)
        if av:
            if (adminToken in tokens and
            av.getAdminToken() in tokens and
            av.getAdminToken() == adminToken):
                if commandName in ['invasion', 'suit', 'tournament']:
                    self.createAutoSuit(commandName)
                elif commandName == 'suitSpawner':
                    if self.getSpawner():
                        self.stopSpawner()
                    else:
                        self.startSpawner()
                elif commandName == 'killCogs':
                    self.killAllSuits(1)

    def newShift(self):
        self.maxSuitsThisShift = random.randint(35, 50)
        self.totalSuitsThisShift = 0

    def setActiveInvasion(self, value):
        self.activeInvasion = value

    def getActiveInvasion(self):
        return self.activeInvasion

    def killAllSuits(self, andVP = 0):
        for suit in self.suits.values():
            if not andVP:
                if not suit.isDead() and not suit.suitPlan in [SuitBank.VicePresident,
                                                               SuitBank.LucyCrossbill]:
                    suit.b_setHealth(0)
            else:
                if not suit.isDead():
                    suit.b_setHealth(0)

    def flyAwayAllSuits(self):
        for suit in self.suits.values():
            if not suit.isDead() and not suit.suitPlan in [SuitBank.VicePresident,
                                                           SuitBank.LucyCrossbill]:
                base.taskMgr.remove(suit.uniqueName('monitorHealth'))
                if hasattr(suit, 'brain'):
                    suit.brain.stopThinking()
                    suit.brain.unloadBehaviors()
                    suit.brain = None
                suit.clearTrack()
                suit.b_setSuitState(3, -1, -1)
                base.taskMgr.doMethodLater(7.0, self.__suitFlyAwayDone, suit.uniqueName('flyawayDone'), extraArgs = [suit], appendTask = True)

    def __suitFlyAwayDone(self, suit, task):
        suit.closeSuit(False)
        return task.done

    def deadSuit(self, avId):
        if avId in self.suits:
            del self.suits[avId]
        self.numSuits -= 1
        self.battle.b_setCogsRemaining(self.battle.getCogsRemaining() - 1)
        if self.numSuits < 0:
            self.numSuits = 0
        if self.tournament.inTournament:
            self.tournament.handleDeadSuit()
            if not self.tournament.inTournament:
                for avId in self.battle.avIds:
                    avatar = self.air.doId2do.get(avId)
                    if avatar:
                        avatar.questManager.tournamentDefeated(CogBattleGlobals.HoodIndex2HoodName[self.battle.getHoodIndex()])
            return
        if self.numSuits == 0:
            if self.getActiveInvasion() and self.isFullInvasion():
                for avId in self.battle.avIds:
                    avatar = self.air.doId2do.get(avId)
                    if avatar:
                        avatar.questManager.invasionDefeated(CogBattleGlobals.HoodIndex2HoodName[self.battle.getHoodIndex()])
                self.setActiveInvasion(0)
                self.suitsSpawnedThisInvasion = 0
                self.suitsRequest = -1
                self.currInvasionSize = None
            #if self.totalSuitsThisShift >= self.maxSuitsThisShift:
            #	self.sendSysMessage(random.choice(CIGlobals.SuitBreakMsgArray))
            #	if self.getSpawner():
            #		self.stopSpawner()
            #	self.startBreak()
            self.sendUpdate('noSuits', [])

    def sendSysMessage(self, message):
        self.sendUpdate('systemMessage', [message])

    def createSuit(self, anySuit = 0, levelRange = None, variant = Variant.NORMAL, plan = None):
        if self.isCogCountFull():
            return
        if anySuit:
            if not levelRange:
                levelRange = CogBattleGlobals.HoodIndex2LevelRange[self.battle.getHoodIndex()]
            availableSuits = []
            level = random.choice(levelRange)
            for suit in SuitBank.getSuits():
                if level >= suit.getLevelRange()[0] and level <= suit.getLevelRange()[1]:
                    availableSuits.append(suit)
            plan = random.choice(availableSuits)
        else:
            if not plan:
                return
            level = random.randint(plan.getLevelRange()[0], plan.getLevelRange()[1])
        if self.battle.getHoodIndex() == CogBattleGlobals.SkeletonHoodIndex and variant == Variant.NORMAL:
            variant = Variant.SKELETON
        elif self.battle.getHoodIndex() == CogBattleGlobals.WaiterHoodIndex and variant == Variant.NORMAL:
            variant = Variant.WAITER
        suit = DistributedSuitAI(self.air)
        suit.setManager(self)
        suit.generateWithRequired(self.zoneId)
        suit.d_setHood(suit.hood)
        suit.b_setLevel(level)
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        if variant == Variant.SKELETON:
            suit.b_setName(CIGlobals.Skelesuit)
        else:
            suit.b_setName(plan.getName())
        #suit.startPosHprBroadcast()
        #suit.d_clearSmoothing()
        #suit.d_broadcastPosHpr()
        suit.b_setParent(CIGlobals.SPHidden)
        self.suits[suit.doId] = suit
        self.numSuits += 1
        if self.numSuits == 1:
            if (self.tournament.inTournament and self.tournament.getRound() == 1
            or not self.tournament.inTournament):
                self.sendUpdate('newSuit', [])
                if self.tournament.inTournament and self.tournament.getRound() == 1:
                    self.sendUpdate('tournamentSpawned', [])
        if self.getActiveInvasion():
            self.suitsSpawnedThisInvasion += 1
            if self.suitsSpawnedThisInvasion == 1:
                if not self.tournament.inTournament:
                    self.sendUpdate('invasionSpawned', [])
        if plan in [SuitBank.VicePresident, SuitBank.LucyCrossbill]:
            self.sendUpdate('bossSpawned', [])
        return suit

    def requestSuitInfo(self):
        avId = self.air.getAvatarIdFromSender()
        if self.numSuits > 0:
            self.sendUpdateToAvatarId(avId, 'newSuit', [])
        else:
            self.sendUpdateToAvatarId(avId, 'noSuits', [])
        if self.getActiveInvasion() and not self.tournament.inTournament:
            self.sendUpdateToAvatarId(avId, 'invasionSpawned', [])
            self.sendUpdateToAvatarId(avId, 'invasionInProgress', [])
        elif self.tournament.inTournament:
            self.sendUpdateToAvatarId(avId, 'invasionSpawned', [])
            self.sendUpdateToAvatarId(avId, 'tournamentInProgress', [])
            if self.tournament.getRound() == 4:
                self.sendUpdateToAvatarId(avId, 'bossSpawned', [])

    def suitSpawner(self, task):
        configData = [
            base.config.GetBool('want-suit'),
            base.config.GetBool('want-suit-invasion'),
            base.config.GetBool('want-suit-tournament')
        ]
        random_choice = random.randint(1, 100)

        if random_choice in self.chances['invasion']:
            if configData[2]:
                random_delay = random.randint(20, 40)
                choice = "invasion"
            else:
                self.suitSpawner(task)
                return task.done
        elif random_choice in self.chances['cog']:
            if configData[0]:
                random_delay = random.randint(5, 20)
                choice = "suit"
            else:
                self.suitSpawner(task)
                return task.done
        elif random_choice in self.chances['tournament']:
            if configData[1]:
                choice = "tournament"
                random_delay = random.randint(360, 700)
            else:
                self.suitSpawner(task)
                return task.done
        if random_choice in self.chances['tournament'] and self.getActiveInvasion() or self.numSuits > 0:
            random_delay = random.randint(5, 20)
        if self.air.toonsAreInZone(self.zoneId):
            self.createAutoSuit(choice)
        else:
            random_delay = random.randint(20, 40)
        task.delayTime = random_delay
        return task.again

    def createAutoSuit(self, choice):
        self.lastChoice = choice
        if choice == "invasion":
            if not self.isFullInvasion() and not self.tournament.inTournament and not self.getActiveInvasion() and self.numSuits == 0:
                # Spawn invasion
                difficulty = CogBattleGlobals.HoodIndex2LevelRange[self.battle.getHoodIndex()]
                size = random.choice(["small", "medium", "large"])
                self.suitsRequest = self.suitsRequestBySize[size]
                suit = "ABC"
                if self.battle.getHoodIndex() == CogBattleGlobals.SkeletonHoodIndex:
                    skeleton = 1
                else:
                    skeleton = 0
                self.startInvasion(suit, difficulty, skeleton)
        elif choice == "suit":
            if not self.isCogCountFull() and not self.tournament.inTournament:
                # Spawn suit
                self.createSuit(anySuit = 1)
        elif choice == "tournament":
            if self.numSuits == 0 and not self.tournament.inTournament and not self.getActiveInvasion():
                # Spawn tournament
                self.tournament.initiateTournament()

    def isCogCountFull(self):
        return self.numSuits >= 25

    def isFullInvasion(self):
        isFull = self.suitsSpawnedThisInvasion >= self.suitsRequest and self.suitsRequest > -1
        return isFull

    def startInvasion(self, suit, difficulty, skeleton, backup = 0):
        if not self.getActiveInvasion() and not self.tournament.inTournament:
            self.sendSysMessage(CIGlobals.SuitInvasionMsg)
        self.setActiveInvasion(1)
        if self.isFullInvasion() or self.isCogCountFull() or self.suitsRequest < 0:
            return
        self.suitsSpawnedThisInvasion = 0
        taskMgr.add(
            self.__doInvasion, self.uniqueName('doInvasion'),
            extraArgs = [suit, difficulty, skeleton, backup], appendTask = True
        )

    def __doInvasion(self, suitType, difficulty, skeleton, backup, task):
        if self.isFullInvasion() or self.suits == None:
            return task.done
        suitsNow = random.randint(0, 7)
        for suit in range(suitsNow):
            if self.isFullInvasion() or self.isCogCountFull():
                break
            if suitType == "ABC":
                suitType = random.choice(["A", "B", "C"])
            self.createSuit(levelRange = difficulty, anySuit = 1)
        task.delayTime = 4
        return task.again

    def start(self):
        self.startSpawner()

    def stop(self):
        self.stopSpawner()
        self.stopBreak()
        taskMgr.remove(self.uniqueName('doInvasion'))
        for suit in self.suits.values():
            self.deadSuit(suit.doId)
            suit.disable()
            suit.requestDelete()
        for drop in self.getDrops():
            if hasattr(drop, 'disable'):
                drop.disable()
            drop.requestDelete()

    def startSpawner(self):
        taskMgr.add(self.suitSpawner, self.uniqueName('suitSpawner'))
        self.b_spawner(1)

    def stopSpawner(self):
        taskMgr.remove(self.uniqueName('suitSpawner'))
        self.suitSpawnerOn = False
        self.b_spawner(0)

    def startBreak(self):
        breakTime = random.randint(135, 210)
        self.notify.info("The Suits are taking a break for %s seconds." % str(breakTime))
        taskMgr.doMethodLater(breakTime, self._breakOver, self.uniqueName('suitBreak'))

    def _breakOver(self, task):
        self.newShift()
        if not self.getSpawner():
            self.startSpawner()
        self.notify.info("The Suits are back from break.")
        return task.done

    def stopBreak(self):
        taskMgr.remove(self.uniqueName('suitBreak'))

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.start()

    def disable(self):
        self.stop()
        self.tournament.cleanup()
        self.tournament = None
        self.suits = None
        self.drops = None
        self.numSuits = None
        self.activeInvasion = None
        self.suitsSpawnedThisInvasion = None
        self.lastChoice = None
        self.totalSuitsThisShift = None
        self.maxSuitsThisShift = None
        self.spawnerStatus = None
        self.battle = None
        self.currInvasionSize = None

    def delete(self):
        del self.suits
        del self.spawnerStatus
        DistributedObjectAI.delete(self)
