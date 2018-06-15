"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file UnoGameAIPlayer.py
@author Maverick Liberty
@date April 1, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.ToonDNA import ToonDNA
from src.coginvasion.minigame import UnoGameGlobals as UGG
import random

class UnoGameAIPlayer(ToonDNA):

    def __init__(self, npc_id, doId, uno_ai):
        ToonDNA.__init__(self)
        self.game = uno_ai
        self.npc_id = npc_id
        self.name = CIGlobals.NPCToonDict[npc_id][1]
        self.dna = CIGlobals.NPCToonDict[npc_id][2]
        self.cards = []
        self.dealingCards = []
        self.strategicCards = []
        self.startingCards = []
        self.doId = doId
        self.drawsThisTurn = 0
        self.maxDrawsPerTurn = -1

    def generate(self):
        self.setDNAStrand(self.dna)

    def organizeStrategicCards(self):
        strategyCards = [str(UGG.CARD_DRAW_TWO), str(UGG.CARD_SKIP), str(UGG.CARD_WILD), str(UGG.CARD_WILD_DRAW_FOUR)]
        self.strategicCards = []
        for card in self.cards:
            if card[:2] in strategyCards:
                self.strategicCards.append(card)

    def hasStrategicCard(self):
        if len(self.strategicCards) > 0:
            return True
        else:
            return False

    def getRandomStrategicCard(self):
        card = None
        if self.hasStrategicCard():
            card = self.strategicCards[random.randint(0, (len(self.strategicCards) - 1))]
        return card

    def addStartingCard(self, card):
        self.startingCards.append(card)

    def getStartingCards(self):
        return self.startingCards

    def addCard(self, card):
        self.cards.append(card)
        self.game.d_updateHeadPanelValue(self.doId, 1)
        self.organizeStrategicCards()

    def removeCard(self, card):
        if card in self.cards:
            self.cards.remove(card)
            self.game.d_updateHeadPanelValue(self.doId, 0)
            self.drawsThisTurn = 0
            self.organizeStrategicCards()

    def getCards(self):
        return self.cards

    def addDealingCard(self, card):
        self.dealingCards.append(card)

    def removeDealingCard(self, card):
        self.dealingCards.remove(card)

    def getDealingCards(self):
        return self.dealingCards

    def setDrawsThisTurn(self, draws):
        self.drawsThisTurn = draws

    def getDrawsThisTurn(self):
        return self.drawsThisTurn

    def setMaxDrawsPerTurn(self, maxDraws):
        self.maxDrawsPerTurn = maxDraws

    def getMaxDrawsPerTurn(self):
        return self.maxDrawsPerTurn

    def getName(self):
        return self.name

    def getID(self):
        return self.doId
