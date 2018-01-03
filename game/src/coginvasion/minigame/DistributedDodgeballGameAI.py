# Filename: DistributedDodgeballGameAI.py
# Created by:  blach (18Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State

from DistributedToonFPSGameAI import DistributedToonFPSGameAI
from TeamMinigameAI import TeamMinigameAI

from DodgeballGlobals import *

import random

class DistributedDodgeballGameAI(DistributedToonFPSGameAI, TeamMinigameAI):
    """The winter dodgeball game (AI/server side)"""

    notify = directNotify.newCategory("DistributedDodgeballGameAI")

    GameOverTime = 15.0
    GameTime = 120

    def __init__(self, air):
        DistributedToonFPSGameAI.__init__(self, air)
        TeamMinigameAI.__init__(self)
        self.setZeroCommand(self.__gameOver_time)
        self.setInitialTime(self.GameTime)
        self.fsm = ClassicFSM.ClassicFSM('DDodgeballGameAI', [
            State.State('off', self.enterOff, self.exitOff),
            State.State('waitForChooseTeam', self.enterWaitForChooseTeam, self.exitWaitForChooseTeam),
            State.State('play', self.enterPlay, self.exitPlay),
            State.State('roundIntermission', self.enterRoundIntermission, self.exitRoundIntermission)], 'off', 'off')
        self.fsm.enterInitialState()
        self.playersReadyToStart = 0
        self.resetNumFrozen()
        self.availableSpawnsByTeam = {
            BLUE: [0, 1, 2, 3],
            RED: [0, 1, 2, 3]}
        self.announcedWinner = False
        self.winnerPrize = 200
        self.loserPrize = 0

    def resetNumFrozen(self):
        self.numFrozenByTeam = {RED: 0, BLUE: 0}

    def enterRoundIntermission(self):
        pass

    def exitRoundIntermission(self):
        pass

    def __gameOver_time(self):
        self.__gameOver(1)

    def __decideWinner(self):
        teams = [BLUE, RED]
        teams.sort(key = lambda team: self.scoreByTeam[team], reverse = True)
        self.winnerTeam = teams[0]

    def __gameOver(self, timeRanOut = 0):
        self.timeRanOutLastRound = timeRanOut
        self.fsm.request('off')
        if self.round == MaxRounds:
            self.__decideWinner()
            self.sendUpdate('teamWon', [self.winnerTeam, timeRanOut])
        else:
            self.sendUpdate('roundOver', [timeRanOut])
            self.fsm.request('play')

    def enemyFrozeMe(self, myTeam, enemyTeam):
        self.scoreByTeam[enemyTeam] += 1
        self.numFrozenByTeam[myTeam] += 1
        self.sendUpdate('incrementTeamScore', [enemyTeam])
        if self.numFrozenByTeam[myTeam] >= len(self.playerListByTeam[myTeam]) and not self.announcedWinner:
            # All of the players on this team are frozen! The enemy team wins!
            self.announcedWinner = True
            self.timeRanOutLastRound = 0
            self.fsm.request('off')
            self.resetNumFrozen()
            if self.round == MaxRounds:
                self.__decideWinner()
                self.sendUpdate('teamWon', [self.winnerTeam, 0])
                taskMgr.doMethodLater(self.GameOverTime, self.__gameOverTask, self.uniqueName("gameOverTask"))
            else:
                self.sendUpdate('roundOver', [0])
                self.fsm.request('play')

    def __gameOverTask(self, task):
        winners = list(self.playerListByTeam[self.winnerTeam])
        self.d_gameOver(1, winners)
        return task.done

    def teamMateUnfrozeMe(self, myTeam):
        self.numFrozenByTeam[myTeam] -= 1

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWaitForChooseTeam(self):
        for avatar in self.avatars:
            self.sendUpdate('setupRemoteAvatar', [avatar.doId])
        self.sendUpdate('chooseUrTeam')

    def exitWaitForChooseTeam(self):
        pass

    def enterPlay(self):
        self.announcedWinner = False
        self.setRound(self.getRound() + 1)
        if self.getRound() == 1:
            self.d_startGame()
            time = 18.0
        else:
            mult = 2
            if self.timeRanOutLastRound:
                mult = 3
            time = (2.05 * mult) + 8.0

        base.taskMgr.doMethodLater(time, self.__actuallyStarted, self.uniqueName('actuallyStarted'))

    def __actuallyStarted(self, task):
        self.setInitialTime(self.GameTime)
        self.startTiming()
        return task.done

    def exitPlay(self):
        self.stopTiming()
        base.taskMgr.remove(self.uniqueName('actuallyStarted'))

    def allAvatarsReady(self):
        self.fsm.request('waitForChooseTeam')

    def choseTeam(self, team):
        avId = self.air.getAvatarIdFromSender()

        # We'll send our own accepted message.
        isOnTeam = TeamMinigameAI.choseTeam(self, team, avId, sendAcceptedMsg = False)

        if isOnTeam:
            # Pick a spawn point for them
            spawnIndex = random.choice(self.availableSpawnsByTeam[team])
            self.availableSpawnsByTeam[team].remove(spawnIndex)

            self.sendUpdateToAvatarId(avId, 'acceptedIntoTeam', [spawnIndex])

    def readyToStart(self):
        self.playersReadyToStart += 1
        if self.playersReadyToStart == len(self.avatars):
            self.fsm.request('play')

    def delete(self):
        taskMgr.remove(self.uniqueName('gameOverTask'))
        self.fsm.requestFinalState()
        del self.fsm
        del self.playersReadyToStart
        del self.availableSpawnsByTeam
        TeamMinigameAI.cleanup(self)
        DistributedToonFPSGameAI.delete(self)
