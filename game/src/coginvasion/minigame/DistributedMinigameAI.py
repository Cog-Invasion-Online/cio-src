"""

  Filename: DistributedMinigameAI.py
  Created by: blach (06Oct14)

"""

from direct.distributed import DistributedObjectAI
import TimerAI

class DistributedMinigameAI(DistributedObjectAI.DistributedObjectAI, TimerAI.TimerAI):

    def __init__(self, air):
        try:
            self.DistributedMinigameAI_initialized
            return
        except:
            self.DistributedMinigameAI_initialized = 1
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        TimerAI.TimerAI.__init__(self)
        self.gameName = None
        self.air = air
        self.readyAvatars = 0
        self.numPlayers = 0
        self.avatars = []
        self.zone = 0
        self.round = 0
        self.finalScores = []
        self.finalScoreAvIds = []
        return


    def setGameName(self, game):
        self.gameName = game

    def setRound(self, round):
        self.round = round

    def b_setRound(self, round):
        self.sendUpdate('setRound', [round])
        self.setRound(round)

    def getRound(self):
        return self.round

    def myFinalScore(self, score):
        avId = self.air.getAvatarIdFromSender()
        self.finalScoreAvIds.append(avId)
        self.finalScores.append(score)
        if len(self.finalScores) == self.numPlayers:
            self.sendUpdate('finalScores', [self.finalScoreAvIds, self.finalScores])

    def sendHeadPanels(self):
        gender = None
        head = None
        for avatar in self.avatars:
            gender = avatar.getGender()
            animal = avatar.getAnimal()
            head, color = avatar.getHeadStyle()
            r, g, b, _ = color
            self.d_generateHeadPanel(gender, animal, head, [r, g, b], avatar.doId, avatar.getName())

    def d_generateHeadPanel(self, gender, head, headtype, color, doId, name):
        self.sendUpdate("generateHeadPanel", [gender, head, headtype, color, doId, name])

    def d_updateHeadPanelValue(self, doId, direction):
        self.sendUpdate("updateHeadPanelValue", [doId, direction])

    def appendAvatar(self, avatar):
        self.avatars.append(avatar)

    def clearAvatar(self, avatar=None, doId=None):
        if (avatar != None and doId != None or
            avatar == None and doId == None):
            return
        if avatar != None:
            self.avatars.remove(avatar)
        elif doId != None:
            for avatar in self.avatars:
                if avatar.doId == doId:
                    self.avatars.remove(avatar)

    def isAvatarPresent(self, doId):
        for avatar in self.avatars:
            if avatar.doId == doId:
                return True
        return False

    def setNumPlayers(self, players):
        self.numPlayers = players

    def d_setNumPlayers(self, players):
        self.sendUpdate('setNumPlayers', [players])

    def b_setNumPlayers(self, players):
        self.d_setNumPlayers(players)
        self.setNumPlayers(players)

    def getNumPlayers(self):
        return self.numPlayers

    def getAvatarName(self, doId):
        for avatar in self.avatars:
            if avatar.doId == doId:
                return avatar.getName()
        return None

    def ready(self):
        if self.readyAvatars == None:
            return
        self.readyAvatars += 1
        if self.areAllAvatarsReady():
            self.allAvatarsReady()
            self.readyAvatars = 0

    def areAllAvatarsReady(self):
        return (self.getNumPlayers() == self.readyAvatars)

    def allAvatarsReady(self):
        self.d_startGame()

    def leaving(self):
        doId = self.air.getAvatarIdFromSender()
        if self.isAvatarPresent(doId):
            self.clearAvatar(doId=doId)

    def d_startGame(self):
        self.sendUpdate('allPlayersReady', [])

    def d_gameOver(self, winner=0, winnerDoId=[]):
        self.givePrizes(winnerDoId)

        for avatar in self.avatars:
            # Let this avatar's quest manager know that they have played a minigame.
            print "Letting questManager know"
            avatar.questManager.minigamePlayed(self.gameName)

        self.sendUpdate('gameOver', [winner, winnerDoId, 0])

    def d_abort(self):
        self.sendUpdate("abort", [])

    def givePrizes(self, winnerAvId):
        for avatar in self.avatars:

            if avatar.doId in winnerAvId:
                avatar.b_setMoney(avatar.getMoney() + self.winnerPrize)
            else:
                avatar.b_setMoney(avatar.getMoney() + self.loserPrize)

    def d_setTimerTime(self, time):
        self.sendUpdate("setTimerTime", [time])

    def delete(self):
        try:
            self.DistributedMinigameGameAI_deleted
            return
        except:
            self.DistributedMinigameGameAI_deleted = 1
        DistributedObjectAI.DistributedObjectAI.delete(self)
        TimerAI.TimerAI.disable(self)
        self.readyAvatars = None
        self.numPlayers = None
        self.avatars = None
        self.zone = None
        self.round = None
        self.gameName = None
        return
