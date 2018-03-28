"""

  Filename: DistributedUnoGameAI.py
  Created by: blach (15Oct14)
  Modified and upgraded by: mliberty (01Apr15)

"""

from direct.interval.IntervalGlobal import Sequence, Func, Wait
from src.coginvasion.minigame.UnoGameAIPlayerMgr import UnoGameAIPlayerMgr
from collections import Counter
import DistributedMinigameAI
import UnoGameGlobals as UGG
import random

class DistributedUnoGameAI(DistributedMinigameAI.DistributedMinigameAI):

    def __init__(self, air):
        try:
            self.DistributedUnoGameAI_initialized
            return
        except:
            self.DistributedUnoGameAI_initialized = 1
        DistributedMinigameAI.DistributedMinigameAI.__init__(self, air)
        self.setZeroCommand(self.doNextPlayerTurn)
        self.setInitialTime(10)
        self.winnerPrize = 135
        self.loserPrize = 10
        self.playersDealed = 0 # The number of players who have been dealed cards.
        self.turnOrder = []
        self.turnsReversed = False
        self.currentTurn = None
        self.turnSeq = None
        self.aiTrack = None
        self.drawDeck = []
        self.availableCards = []
        self.singlePlayer = False
        self.playerMgr = None
        self.currentCard = None
        self.ais = 0
        self.load()
        self.newColor = None
        self.winnerAnnounced = False
        self.maxDrawsPerTurn = 4
        self.gameStarted = False
        self.cardsToDeal = 7
        return

    def load(self):
        self.loadCards()

    def makeCardDeck(self, announceShuffling = False):
        # brian 4/18/15:
        #
        # Make an array of card ids that the ai can give out to players.
        # The data for how many cards are in a deck of each card is located at
        # UGG.DRAW_CARD_DECK_DATA
        # This is to be realistic to real uno so the cards that are given out
        # are affected by what the other players have drawn.

        if announceShuffling:
            self.d_setPlayByPlay(UGG.EVENT_SHUFFLING)
        newDeck = []
        for cardId in UGG.DRAW_CARD_DECK_DATA.keys():
            cardCount = UGG.DRAW_CARD_DECK_DATA[cardId]
            for _ in range(cardCount):
                newDeck.append(cardId)
        # Okay, now that the array has been made, shuffle it.
        self.drawDeck = random.sample(newDeck, len(newDeck))

    def loadCards(self):
        for card in UGG.cardId:
            self.availableCards.append(card)

    def banCard(self, cardId):
        self.availableCards.remove(cardId)

    def allAvatarsReady(self):
        DistributedMinigameAI.DistributedMinigameAI.allAvatarsReady(self)
        # Is it a single-player game?
        if len(self.avatars) == 1:
            self.singlePlayer = True
            self.playerMgr = UnoGameAIPlayerMgr(self)
            players = random.randint(1, 3)
            for _ in xrange(1):
                self.playerMgr.createPlayer()
            self.ais = len(self.playerMgr.getPlayers())
            self.playerMgr.generateHeadPanels()
        self.dealCards()

    def dealCards(self):
        """ Deal cards to all avatars. """
        self.d_setPlayByPlay(UGG.EVENT_DEALING_CARDS)
        if hasattr(self, 'avatars') and self.avatars != None:
            for avatar in self.avatars:
                for _ in range(self.cardsToDeal):
                    self.d_takeNewCard(avatar.doId, self.pickNewCard())
        # Let's also deal cards to NPCs
        if self.playerMgr:
            for player in self.playerMgr.getPlayers():
                neededCards = self.cardsToDeal
                startingCards = player.getStartingCards()
                if len(startingCards) > 0:
                    for startingCard in startingCards:
                        player.addCard(startingCard)
                        neededCards = neededCards - 1
                for _ in range(neededCards):
                    card = self.pickNewCard()
                    player.addCard(card)
        self.startCountdown()

    def startCountdown(self):
        def setGameStarted():
            self.gameStarted = True
        Sequence(Func(self.d_setPlayByPlay, "3"), Wait(1.0), Func(self.d_setPlayByPlay, "2"),
            Wait(1.0), Func(self.d_setPlayByPlay, "1"), Wait(1.0), Func(self.startTurns), Func(setGameStarted)).start()

    def startTurns(self):
        if hasattr(self, 'avatars') and self.avatars != None:
            for avatar in self.avatars:
                self.turnOrder.append(avatar.doId)
        if self.ais > 0 and self.playerMgr:
            for player in self.playerMgr.getPlayers():
                self.turnOrder.append(player.getID())
        self.placeStartingCard()
        self.doNextPlayerTurn()

    def placeStartingCard(self):
        card = self.pickNewCard()
        if (card == str(UGG.CARD_WILD_DRAW_FOUR) or
        card == str(UGG.CARD_WILD) or
        card[:2] == str(UGG.CARD_DRAW_TWO) or
        card[:2] == str(UGG.CARD_SKIP) or
        card[:2] == str(UGG.CARD_REVERSE)):
            self.placeStartingCard()
            return
        self.d_placeCard(0, card)

    def d_placeCard(self, doId, cardId):
        self.currentCard = cardId
        if doId != 0:
            if self.playerMgr:
                aiPlayer = self.playerMgr.getPlayerByID(doId)
                if not aiPlayer:
                    self.d_updateHeadPanelValue(doId, 0)
                else: aiPlayer.removeCard(cardId)
            else: self.d_updateHeadPanelValue(doId, 0)
        self.sendUpdate("placeCard", [doId, cardId])


    def takeNewCardColor(self, origId, id, doId = None):
        if doId is None:
            doId = self.air.getAvatarIdFromSender()
        self.newColor = id
        self.d_setNewCardColor(id)
        shouldDraw = 0
        if origId == str(UGG.CARD_WILD_DRAW_FOUR):
            shouldDraw = 4
        seq = Sequence()
        seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_NEW_COLOR %
                (self.getAvatarName(doId), UGG.colorId2colorName[id])))
        seq.append(Wait(1.5))
        seq.append(Func(self.doNextPlayerTurn, draw=shouldDraw))
        seq.start()
        self.turnSeq = seq

    def d_setNewCardColor(self, id):
        self.sendUpdate("setNewCardColor", [id])

    def requestPlaceCard(self, id, doId = None):
        if self.gameStarted:
            if doId is None:
                doId = self.air.getAvatarIdFromSender()
            if (self.isAvatarPresent(doId) and self.turnOrder[self.currentTurn] == doId and not self.winnerAnnounced):
                self.currentCard = id
                self.d_placeCard(doId, id)
                self.stopTiming()
                seq = Sequence()
                seq.append(Wait(1.2))
                shouldSkip = 0
                shouldDraw = 0
                reversedNow = 0
                isWild = 0
                ai = None
                if self.ais > 0 and self.playerMgr:
                    for player in self.playerMgr.getPlayers():
                        if player.getID() == doId:
                            ai = player
                            break
                if ai:
                    ai.setDrawsThisTurn(0)
                    if len(ai.getCards()) == 0:
                        self.__handleAIWin(ai)
                        return
                if (id[:2] == str(UGG.CARD_SKIP)):
                    shouldSkip = 1
                elif (id[:2] == str(UGG.CARD_REVERSE)):
                    reversedNow = 1
                    if self.turnsReversed:
                        self.turnsReversed = False
                    else:
                        self.turnsReversed = True
                elif (id[:2] == str(UGG.CARD_DRAW_TWO)):
                    shouldDraw = 2
                elif (id == str(UGG.CARD_WILD_DRAW_FOUR)):
                    shouldDraw = 4
                    isWild = 1
                elif (id == str(UGG.CARD_WILD)):
                    isWild = 1
                if isWild == 1:
                    if not ai:
                        seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_CHOOSING_NEW_COLOR % self.getAvatarName(self.turnOrder[self.currentTurn])))
                        seq.append(Func(self.d_requestNewCardColor, doId))
                    else:
                        seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_CHOOSING_NEW_COLOR % ai.getName()))
                        waitTime = random.uniform(2, 4)
                        track = Sequence()
                        track.append(Wait(waitTime))
                        track.append(Func(self.__handleWildCard, ai, id))
                        track.start()
                        self.aiTrack = track
                else:
                    seq.append(Func(self.doNextPlayerTurn, shouldSkip, shouldDraw, reversedNow))
                self.turnSeq = seq
                seq.start()
            elif (self.isAvatarPresent(doId) and self.turnOrder[self.currentTurn] != doId and not self.winnerAnnounced):
                # Oops, the avatar must have selected their card at the last second,
                # and we missed it! Give them back the card they selected.
                self.d_takeNewCard(doId, id)

    def d_requestNewCardColor(self, doId):
        self.sendUpdateToAvatarId(doId, "requestNewCardColor", [])

    def doNextPlayerTurn(self, skip=0, draw=0, reversedNow=0):
        if self.turnOrder is None:
            return
        turns = 1
        if self.currentTurn is None:
            self.currentTurn = 0
        else:
            if skip:
                turns = 2
            if self.turnsReversed:
                for _ in range(turns):
                    self.__prevPlayerTurn()
            else:
                for _ in range(turns):
                    self.__nextPlayerTurn()
        if draw:
            for _ in range(draw):
                ai = None
                if self.ais > 0 and self.playerMgr:
                    ai = self.playerMgr.getPlayerByID(self.turnOrder[self.currentTurn])
                if not ai:
                    self.d_takeNewCard(self.turnOrder[self.currentTurn], self.pickNewCard())
                else:
                    card = self.pickNewCard()
                    ai.addCard(card)
        self.stopTiming()
        seq = Sequence()
        if draw == 2:
            seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_DRAWING_TWO % self.getAvatarName(self.turnOrder[self.currentTurn])))
            seq.append(Wait(1.5))
            if self.turnsReversed:
                self.__prevPlayerTurn()
            else:
                self.__nextPlayerTurn()
        elif draw == 4:
            seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_DRAWING_FOUR % self.getAvatarName(self.turnOrder[self.currentTurn])))
            seq.append(Wait(1.5))
        elif skip:
            seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_SKIPPED_TURN % self.getPrevAvatarName()))
            seq.append(Wait(1.5))
        elif reversedNow:
            seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_REVERSE))
            seq.append(Wait(1.5))
        seq.append(Func(self.d_setPlayByPlay, UGG.EVENT_NEW_TURN % self.getAvatarNamePossesive(self.turnOrder[self.currentTurn])))
        seq.append(Func(self.d_setPlayerTurn, self.turnOrder[self.currentTurn]))
        seq.append(Func(self.startTiming))
        seq.start()
        self.turnSeq = seq

    def getAvatarNamePossesive(self, doId):
        if hasattr(self, 'avatars') and self.avatars != None:
            for avatar in self.avatars:
                if avatar.doId == doId:
                    name = avatar.getName()
                    if not name:
                        return "Toon"
                    if name.endswith("s"):
                        return name + "'"
                    else:
                        return name + "'s"
        if self.playerMgr:
            for player in self.playerMgr.getPlayers():
                if player.getID() == doId:
                    name = player.getName()
                    if name.endswith("s"):
                        return name + "'"
                    else:
                        return name + "'s"

    def getPrevAvatarName(self):
        if self.turnsReversed:
            self.__nextPlayerTurn()
            name = self.getAvatarName(self.turnOrder[self.currentTurn])
            self.__prevPlayerTurn()
        else:
            self.__prevPlayerTurn()
            name = self.getAvatarName(self.turnOrder[self.currentTurn])
            self.__nextPlayerTurn()
        return name

    def __nextPlayerTurn(self):
        self.currentTurn += 1
        if self.currentTurn >= len(self.turnOrder):
            self.currentTurn = 0

    def __prevPlayerTurn(self):
        self.currentTurn -= 1
        if self.currentTurn < 0:
            self.currentTurn = len(self.turnOrder) - 1

    def d_setPlayerTurn(self, doId):
        if self.playerMgr:
            ai = self.playerMgr.getPlayerByID(doId)
            if ai:
                self.__handleAITurn(ai)
        self.sendUpdate("setPlayerTurn", [doId])

    def __handleWildCard(self, player, wild_card):
        colors = []
        for card in player.getCards():
            if not card in [UGG.CARD_WILD, UGG.CARD_WILD_DRAW_FOUR]:
                colors.append(card[-2:])
        counter = Counter(colors)
        set_color = counter.keys()[0]
        self.takeNewCardColor(origId = wild_card, id = set_color, doId = player.getID())

    def __handleAIWin(self, player):
        self.stopTiming()
        self.d_setPlayByPlay(UGG.EVENT_WINNER % self.getAvatarName(player.getID()))
        self.d_gameOver(winner = 1, winnerDoId = [player.getID()])
        self.winnerAnnounced = True

    def __handleAITurn(self, player):
        if len(player.getCards()) > 0:
            currentColor = self.currentCard[-2:]
            currentId = self.currentCard[:2]
            def hasPlaceableCardBeingDealt():
                placeable = False
                for card in player.getDealingCards():
                    if (card[:2] == currentId or card[:2] == UGG.CARD_WILD or
                        card[:2] == UGG.CARD_WILD_DRAW_FOUR or card[-2:] == currentColor or
                        card[-2:] == self.newColor):
                        placeable = True
                        break
                return placeable
            for card in player.getCards():
                if card[:2] == UGG.CARD_WILD or card[:2] == UGG.CARD_WILD_DRAW_FOUR or card[:2] == currentId or card[-2:] == currentColor or card[-2:] == self.newColor:
                    if self.time >= 4:
                        if player.getDrawsThisTurn() > 0:
                            # It takes some time for the brain to realize that this is a good card to use
                            # after drawing it.
                            waitTime = random.uniform(0.6, 0.9)
                        else:
                            # We already have a good card to use in the deck, it takes some time
                            # for a regular player to look through the deck and decide if it's a
                            # good card or not.
                            waitTime = random.uniform(0.45, self.time - 2.0)
                        track = Sequence()
                        track.append(Wait(waitTime))
                        track.append(Func(self.requestPlaceCard, card, player.getID()))
                        track.start()
                        self.turnSeq = track
                    else:
                        self.requestPlaceCard(card, doId = player.getID())
                    return
            placeableCard = hasPlaceableCardBeingDealt()
            if not placeableCard and player.getMaxDrawsPerTurn() == -1 or not placeableCard and player.getDrawsThisTurn() < player.getMaxDrawsPerTurn():
                new_card = self.pickNewCard()
                player.addDealingCard(new_card)
                player.setDrawsThisTurn(player.getDrawsThisTurn() + 1)
                if self.time >= 2:
                    waitTime = random.uniform(0.5, 1.5)
                    track = Sequence()
                    track.append(Wait(waitTime))
                    track.append(Func(player.addCard, new_card))
                    track.append(Func(player.removeDealingCard, new_card))
                    track.start()
                    self.turnSeq = track
                else:
                    waitTime = random.uniform(0.15, 0.45)
                    track = Sequence()
                    track.append(Wait(waitTime))
                    track.append(Func(player.addCard, new_card))
                    track.start()
                    self.turnSeq = track
                placeable = hasPlaceableCardBeingDealt()
                self.__handleAITurn(player)
            elif player.getDrawsThisTurn() == self.maxDrawsPerTurn:
                # Wait out the clock, can't draw anymore.
                seq = Sequence()
                seq.append(Wait(self.time))
                seq.append(Func(player.setDrawsThisTurn, 0))
                seq.start()
                self.turnSeq = seq
                return
            elif hasPlaceableCardBeingDealt():
                seq = Sequence()
                seq.append(Wait(0.75))
                seq.append(Func(self.__handleAITurn, player))
                seq.start()
                self.turnSeq = seq

    def callUno(self):
        doId = self.air.getAvatarIdFromSender()
        if self.isAvatarPresent(doId):
            self.d_setPlayByPlay(UGG.EVENT_UNO_CALLED % self.getAvatarName(doId))

    def noCards(self):
        doId = self.air.getAvatarIdFromSender()
        if self.isAvatarPresent(doId):
            self.stopTiming()
            self.d_setPlayByPlay(UGG.EVENT_WINNER % self.getAvatarName(doId))
            self.d_gameOver(winner=1, winnerDoId=[doId])
            self.winnerAnnounced = True

    def wasDealed(self):
        """ This is a message sent by the client telling us that they
        have been dealed their cards and are ready to start. """
        doId = self.air.getAvatarIdFromSender()
        if self.isAvatarPresent(doId):
            self.playersDealed += 1
        if self.playersDealed == self.numPlayers:
            self.allPlayersDealed()

    def allPlayersDealed(self):
        """ All players have been dealed their cards, start playing the game. """
        pass

    def requestNewCard(self):
        """ A client requested that we pick a new card for them. """
        doId = self.air.getAvatarIdFromSender()
        if self.isAvatarPresent(doId):
            self.d_takeNewCard(doId, self.pickNewCard())

    def d_takeNewCard(self, doId, cardId):
        """ Send the ID of the new card we are sending to the client. """
        self.d_updateHeadPanelValue(doId, 1)
        self.sendUpdateToAvatarId(doId, "takeNewCard", [cardId])

    def d_setPlayByPlay(self, pbp):
        self.sendUpdate("setPlayByPlay", [pbp])

    def d_startGame(self):
        self.sendHeadPanels()
        DistributedMinigameAI.DistributedMinigameAI.d_startGame(self)

    def pickNewCard(self):
        """ Pick a new card for the client who requested one. """
        try:
            newCardId = self.drawDeck[0]
        except:
            self.makeCardDeck()
            newCardId = self.drawDeck[0]
        self.drawDeck.remove(self.drawDeck[0])
        return newCardId

    def isAvatarPresent(self, doId):
        if hasattr(self, 'avatars') and self.avatars != None:
            for avatar in self.avatars:
                if avatar.doId == doId:
                    return True
        if self.ais > 0 and self.playerMgr:
            for player in self.playerMgr.getPlayers():
                if player.getID() == doId:
                    return True
        return False

    def getAvatarName(self, doId):
        if hasattr(self, 'avatars') and self.avatars != None:
            for avatar in self.avatars:
                if avatar.doId == doId:
                    return avatar.getName()
        if self.playerMgr:
            for player in self.playerMgr.getPlayers():
                if player.getID() == doId:
                    return player.getName()

    def givePrizes(self, winnerAvId):
        avatarLoser = False
        if self.ais > 0 and self.playerMgr:
            for player in self.playerMgr.getPlayers():
                if player.getID() in winnerAvId:
                    self.avatarLoser = True
            addMoney = self.loserPrize
            if not avatarLoser: addMoney = self.winnerPrize
            if hasattr(self, 'avatars') and self.avatars != None:
                for avatar in self.avatars:
                    avatar.b_setMoney(avatar.getMoney() + addMoney)
        else:
            DistributedMinigameAI.DistributedMinigameAI.givePrizes(self, winnerAvId)

    def delete(self):
        try:
            self.DistributedUnoGameAI_deleted
            return
        except:
            self.DistributedUnoGameAI_deleted = 1
        DistributedMinigameAI.DistributedMinigameAI.delete(self)
        if self.aiTrack:
            self.aiTrack.pause()
            self.aiTrack = None
        if self.turnSeq:
            self.turnSeq.pause()
            self.turnSeq = None
        self.stopTiming()
        self.playerMgr = None
        self.drawDeck = None
        self.currentCard = None
        self.playersDealed = None
        self.turnOrder = None
        self.turnsReversed = None
        self.currentTurn = None
        return
