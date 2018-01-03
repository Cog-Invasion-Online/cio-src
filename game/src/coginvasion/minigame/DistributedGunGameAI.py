"""

  Filename: DistributedGunGameAI.py
  Created by: blach (26Oct14)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.fsm import ClassicFSM, State

from src.coginvasion.minigame.DistributedToonFPSGameAI import DistributedToonFPSGameAI
import GunGameGlobals as GGG
import GunGameLevelLoaderAI
from DistributedGunGameFlagAI import DistributedGunGameFlagAI
from DistributedGunGameCapturePointAI import DistributedGunGameCapturePointAI
from TeamMinigameAI import TeamMinigameAI

class DistributedGunGameAI(DistributedToonFPSGameAI, TeamMinigameAI):
    notify = directNotify.newCategory("DistributedGunGameAI")

    def __init__(self, air):
        try:
            self.DistributedGunGameAI_initialized
            return
        except:
            self.DistributedGunGameAI_initialized = 1
        DistributedToonFPSGameAI.__init__(self, air)
        TeamMinigameAI.__init__(self)
        self.fsm = ClassicFSM.ClassicFSM('DGunGameAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('voteGM', self.enterVoteGameMode, self.exitVoteGameMode),
         State.State('wait4ChoseTeam', self.enterWaitForChoseTeam, self.exitWaitForChoseTeam),
         State.State('play', self.enterPlay, self.exitPlay)], 'off', 'off')
        self.fsm.enterInitialState()
        self.loader = GunGameLevelLoaderAI.GunGameLevelLoaderAI(self)
        self.setZeroCommand(self.timeUp)
        self.setInitialTime(305) # 5 minutes + the time it takes to countdown
        self.winnerPrize = 200
        self.loserPrize = 15
        self.gameMode = 0
        self.votes = {GGG.GameModes.CTF: 0, GGG.GameModes.CASUAL: 0, GGG.GameModes.KOTH : 0}
        self.playersReadyToStart = 0
        self.flags = []
        self.points = []

        self.kothCapturePoints = {}
        return

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterPlay(self):
        DistributedToonFPSGameAI.allAvatarsReady(self)
        for flag in self.flags:
            flag.sendUpdate('placeAtMainPoint')
        for point in self.points:
            point.sendUpdate('startListening')
        self.startTiming()

    def exitPlay(self):
        self.stopTiming()

    def enterVoteGameMode(self):
        self.sendUpdate('startGameModeVote')

    def exitVoteGameMode(self):
        pass

    def enterWaitForChoseTeam(self):
        for avatar in self.avatars:
            self.sendUpdate('setupRemoteAvatar', [avatar.doId])

    def teamScored(self, team):
        self.scoreByTeam[team] += 1
        self.sendUpdate('incrementTeamScore', [team])
        if self.scoreByTeam[team] >= GGG.CTF_SCORE_CAP:
            self.sendUpdate('teamWon', [team, 0])
            Sequence(Wait(10.0), Func(self.d_gameOver)).start()

    def exitWaitForChoseTeam(self):
        pass

    def setGameMode(self, mode):
        self.gameMode = mode

    def d_setGameMode(self, mode):
        self.sendUpdate('setGameMode', [mode])

    def b_setGameMode(self, mode):
        self.d_setGameMode(mode)
        self.setGameMode(mode)

    def getGameMode(self):
        return self.gameMode

    def timeUp(self):
        self.sendUpdate('timeUp', [])
        Sequence(Wait(10.0), Func(self.d_gameOver)).start()

    def d_gameOver(self):
        winnerAvIds = []
        if self.gameMode == GGG.GameModes.CASUAL:
            for avId in self.finalScoreAvIds:
                score = self.finalScores[self.finalScoreAvIds.index(avId)]
                if score == max(self.finalScores):
                    winnerAvIds.append(avId)
        elif self.gameMode == GGG.GameModes.CTF:
            highestScore = max(self.scoreByTeam.values())
            for team, score in self.scoreByTeam.items():
                if score == highestScore:
                    # This team won. Make all the players that are on the winning team be winners.
                    for avId in self.playerListByTeam[team]:
                        winnerAvIds.append(avId)
        elif self.gameMode == GGG.GameModes.KOTH:
            hill = self.points[0]
            if hill.getKing():
                winnerAvIds.append(hill.getKingId())

        DistributedToonFPSGameAI.d_gameOver(self, 1, winnerAvIds)

    def allAvatarsReady(self):
        self.fsm.request('voteGM')

    def readyToStart(self):
        self.playersReadyToStart += 1
        if self.playersReadyToStart == len(self.avatars):
            self.fsm.request('play')

    def myGameModeVote(self, mode):
        self.votes[mode] += 1
        self.sendUpdate('incrementGameModeVote', [mode])
        totalVotes = 0
        for numVotes in self.votes.values():
            totalVotes += numVotes
        if totalVotes >= len(self.avatars):
            v = list(self.votes.values())
            k = list(self.votes.keys())
            gameMode = k[v.index(max(v))]
            self.b_setGameMode(gameMode)
            self.sendUpdate('gameModeDecided', [gameMode, 0])
            self.fsm.request('wait4ChoseTeam')
            self.setupGameMode()

    def setupGameMode(self):
        self.loader.makeLevel()
        self.setInitialTime(self.loader.getGameTimeOfCurrentLevel())
        if self.gameMode == GGG.GameModes.CTF:
            blueFlag = DistributedGunGameFlagAI(self.air, self, GGG.Teams.BLUE)
            blueFlag.generateWithRequired(self.zoneId)
            redFlag = DistributedGunGameFlagAI(self.air, self, GGG.Teams.RED)
            redFlag.generateWithRequired(self.zoneId)
            self.flags.append(blueFlag)
            self.flags.append(redFlag)
        elif self.gameMode == GGG.GameModes.KOTH:
            capPoint = DistributedGunGameCapturePointAI(self.air, self)
            capPoint.generateWithRequired(self.zoneId)
            self.points.append(capPoint)

            # Let's initialize the kothCapturePoints dict.
            for avatar in self.avatars:
                self.kothCapturePoints.update({avatar.doId : 0})

    def b_setKOTHPoints(self, avId, points):
        if avId in self.kothCapturePoints.keys():
            self.kothCapturePoints.update({avId : points})
        self.sendUpdateToAvatarId(avId, 'setKOTHPoints', [points])

    def d_setKOTHKing(self, avId):
        self.sendUpdate('setKOTHKing', [avId])

    def getKOTHPoints(self, avId):
        if avId in self.kothCapturePoints.keys():
            return self.kothCapturePoints[avId]

    def deadAvatar(self, avId, timestamp):
        sender = self.air.getAvatarIdFromSender()

    def dead(self, killerId):
        self.sendUpdateToAvatarId(killerId, 'incrementKills', [])

    def d_setLevelName(self, level):
        self.sendUpdate('setLevelName', [level])

    def getLevelName(self):
        return self.loader.getLevel()

    def delete(self):
        try:
            self.DistributedGunGameAI_deleted
            return
        except:
            self.DistributedGunGameAI_deleted = 1
        for flag in self.flags:
            flag.requestDelete()
        for point in self.points:
            point.requestDelete()
        self.flags = None
        self.points = None
        self.stopTiming()
        self.loader.cleanup()
        DistributedToonFPSGameAI.delete(self)
