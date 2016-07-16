# Filename: DistributedDodgeballGameAI.py
# Created by:  blach (18Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State

from DistributedToonFPSGameAI import DistributedToonFPSGameAI
from DistributedDodgeballGame import BLUE, RED
from TeamMinigameAI import TeamMinigameAI

import random

class DistributedDodgeballGameAI(DistributedToonFPSGameAI, TeamMinigameAI):
    """The winter dodgeball game (AI/server side)"""

    notify = directNotify.newCategory("DistributedDodgeballGameAI")

    GameOverTime = 15.0
    GameTime = 120

    def __init__(self, air):
        DistributedToonFPSGameAI.__init__(self, air)
        TeamMinigameAI.__init__(self)
        self.setZeroCommand(self.__gameOver)
        self.setInitialTime(self.GameTime)
        self.fsm = ClassicFSM.ClassicFSM('DDodgeballGameAI', [
            State.State('off', self.enterOff, self.exitOff),
            State.State('waitForChooseTeam', self.enterWaitForChooseTeam, self.exitWaitForChooseTeam),
            State.State('play', self.enterPlay, self.exitPlay)], 'off', 'off')
        self.fsm.enterInitialState()
        self.playersReadyToStart = 0
        self.numFrozenByTeam = {RED: 0, BLUE: 0}
        self.availableSpawnsByTeam = {
            BLUE: [0, 1, 2, 3],
            RED: [0, 1, 2, 3]}
        self.announcedWinner = False
        self.winnerPrize = 200
        self.loserPrize = 0
        self.round = 1

    def __gameOver(self):
        teams = [BLUE, RED]
        teams.sort(key = lambda team: self.scoreByTeam[team], reverse = True)
        self.winnerTeam = teams[0]
        self.sendUpdate('teamWon', [self.winnerTeam])
        self.stopTiming()

    def enemyFrozeMe(self, myTeam, enemyTeam):
        self.scoreByTeam[enemyTeam] += 1
        self.numFrozenByTeam[myTeam] += 1
        self.sendUpdate('incrementTeamScore', [enemyTeam])
        if self.numFrozenByTeam[myTeam] >= len(self.playerListByTeam[myTeam]) and not self.announcedWinner:
            # All of the players on this team are frozen! The enemy team wins!
            self.announcedWinner = True
            self.winnerTeam = enemyTeam
            self.sendUpdate('teamWon', [enemyTeam])
            self.stopTiming()
            taskMgr.doMethodLater(self.GameOverTime, self.__gameOverTask, self.uniqueName("gameOverTask"))

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
        self.d_startGame()
        base.taskMgr.doMethodLater(15.0, self.__actuallyStarted, self.uniqueName('actuallyStarted'))

    def __actuallyStarted(self, task):
        self.startTiming()
        return task.done

    def exitPlay(self):
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
