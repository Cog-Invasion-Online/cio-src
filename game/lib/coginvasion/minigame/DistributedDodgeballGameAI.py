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

    def __init__(self, air):
        DistributedToonFPSGameAI.__init__(self, air)
        TeamMinigameAI.__init__(self)
        self.fsm = ClassicFSM.ClassicFSM('DDodgeballGameAI', [
            State.State('off', self.enterOff, self.exitOff),
            State.State('waitForChooseTeam', self.enterWaitForChooseTeam, self.exitWaitForChooseTeam),
            State.State('play', self.enterPlay, self.exitPlay)], 'off', 'off')
        self.fsm.enterInitialState()
        self.playersReadyToStart = 0
        self.availableSpawnsByTeam = {
            BLUE: [0, 1, 2, 3],
            RED: [0, 1, 2, 3]}

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

    def exitPlay(self):
        pass

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
        self.fsm.requestFinalState()
        del self.fsm
        del self.playersReadyToStart
        del self.availableSpawnsByTeam
        TeamMinigameAI.cleanup(self)
        DistributedToonFPSGameAI.delete(self)


