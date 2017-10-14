"""

  Filename: SuitTournament.py
  Created by: blach (??Aug14)

"""

from src.coginvasion.globals import CIGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.cog import SuitBank
import random

class SuitTournament:
    notify = directNotify.newCategory("SuitTournament")
    round_difficulties = [range(1, 4 + 1),
                        range(5, 8 + 1),
                        range(9, 12 + 1)]
    round_sizes = [25,
                25,
                25]
    round_dialogue = {1: {"end": "That's all the " + CIGlobals.Suits + " of round one. The " + CIGlobals.Suits + " are recharging and upgrading their parts..."},
                    2: {"start": "This is the second round of the " + CIGlobals.Suit + " Tournament, the more advanced " + CIGlobals.Suits + " are arriving.",
                        "end": "That's all for round two, prepare for the most advanced " + CIGlobals.Suits + " to arrive."},
                    3: {"start": "This is the third and deciding round! Defeat all the " + CIGlobals.Suits + " to stop them!",
                        "end": "You fought off all of the " + CIGlobals.Suits + "! Good job!"},
                    4: {"start": "You've fought off all of the " + CIGlobals.Suits + ". However, the " + CIGlobals.Suit + " who defeated the most Toons won the prize of Vice President of " + CIGlobals.Suits + "!",
                            "end": "Wow, great job fighting off the Vice President! I don't think we'll be seeing him again."}}
    BACKUP_INTERVAL = 150.0
    INITIAL_BACKUP_INTERVAL = 40.0
    backup_levels = {1: range(1, 4 + 1),
                    2: range(5, 8 + 1),
                    3: range(9, 12 + 1)}

    def __init__(self, suitMgr):
        self.suitMgr = suitMgr
        self.inTournament = False
        self.round = 0
        self.totalTournaments = 0 # Total tournaments played in this session
        self.backupLevel = 0

    def initiateTournament(self):
        self.suitMgr.setActiveInvasion(1)
        self.totalTournaments += 1
        if self.inTournament:
            self.notify.warning("cannot start a tournament when there already is one happening!")
            return
        self.inTournament = True
        self.suitMgr.sendSysMessage("The Cogs have planned a tournament of multiple rounds to see who can defeat the most Toons. You have to stop them!")
        random_waitTime = random.randint(15, 20)
        taskMgr.doMethodLater(random_waitTime, self.startTournament, self.suitMgr.uniqueName("startTournament"))

    def startTournament(self, task):
        if not self.suitMgr:
            self.cleanup()
            return task.done
        self.suitMgr.sendSysMessage("This is it, the Tournament has started! Good luck!")
        self.startRound(None, 1)

    def startRound(self, task, round):
        self.setRound(round)
        if self.getRound() != 1:
            self.suitMgr.sendSysMessage(self.round_dialogue[self.getRound()]["start"])
            self.suitMgr.sendUpdate('newTournamentRound')
        if self.getRound() == 4:
            self.suitMgr.createSuit(plan = SuitBank.VicePresident)
            return
        taskMgr.add(self.startInvasion, self.suitMgr.uniqueName("startTournamentInvasion"), appendTask=True)

    def startInvasion(self, task):
        suit = "ABC"
        levelRange = self.round_difficulties[self.getRound() - 1]
        size = self.round_sizes[self.getRound() - 1]
        self.suitMgr.suitsRequest = size
        skeleton = 0
        if self.getRound() == 4:
            skeleton = 1
        self.suitMgr.startInvasion(suit, levelRange, skeleton)
        return task.done

    def endRound(self):
        self.suitMgr.sendSysMessage(self.round_dialogue[self.getRound()]["end"])
        if self.getRound() > 3:
            self.suitMgr.sendUpdate('tournamentRoundEnded')
        elif self.getRound() == 3:
            self.suitMgr.sendUpdate('normalRoundsEnded')
        random_waitTime = random.randint(15, 20)
        if self.getRound() == 4:
            self.stopBackup()
            self.endTournament()
            self.suitMgr.deadSuit(None)
            return
        taskMgr.doMethodLater(random_waitTime, self.startRound, self.suitMgr.uniqueName("startRoundTask"), extraArgs=[None, self.getRound() + 1])

    def cleanup(self):
        taskMgr.remove(self.suitMgr.uniqueName("startTournament"))
        taskMgr.remove(self.suitMgr.uniqueName("startRoundTask"))
        taskMgr.remove(self.suitMgr.uniqueName("callBackup"))
        taskMgr.remove(self.suitMgr.uniqueName("sendInBackup"))
        self.inTournament = None
        self.round = None
        self.backupLevel = None
        self.suitMgr = None
        self.inTournament = None
        self.totalTournaments = None

    def endTournament(self):
        self.inTournament = False
        self.round = 0
        self.backupLevel = 0

    def startBackup(self):
        taskMgr.doMethodLater(self.INITIAL_BACKUP_INTERVAL, self.callBackupTask, self.suitMgr.uniqueName("callBackup"))

    def callBackupTask(self, task):
        bosses = 0
        self.backupLevel += 1
        if self.backupLevel == 4:
            return task.done
        for suit in self.suitMgr.suits.values():
            if suit.head == "vp":
                bosses += 1
        if bosses == 0:
            return task.done
        self.suitMgr.sendSysMessage("The Vice President is calling in backup level %s!" % self.backupLevel)
        self.__doBackup(self.backup_levels[self.backupLevel])
        taskMgr.doMethodLater(8, self.sendBackup, self.suitMgr.uniqueName("sendInBackup"))
        task.delayTime = self.BACKUP_INTERVAL
        return task.again

    def __doBackup(self, difficulty):
        suit = "ABC"
        size = "medium"
        self.suitMgr.killAllSuits()

    def sendBackup(self, task):
        self.suitMgr.sendSysMessage("The backup has arrived!")
        difficulty = self.backup_levels[self.backupLevel]
        self.suitMgr.startInvasion("ABC", difficulty, "medium", 1, backup = 1)
        return task.done

    def stopBackup(self):
        taskMgr.remove(self.suitMgr.uniqueName("callBackup"))
        taskMgr.remove(self.suitMgr.uniqueName("sendInBackup"))

    def setRound(self, round):
        self.round = round

    def getRound(self):
        return self.round

    def handleDeadSuit(self):
        if self.suitMgr.numSuits == 0 and self.suitMgr.isFullInvasion():
            self.suitMgr.suitsSpawnedThisInvasion = 0
            self.endRound()
