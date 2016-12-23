"""

  Filename: UnoGameGlobals.py
  Created by: blach (14Oct14)
  Updated by: mliberty (01Apr15)

"""

from src.coginvasion.holiday.HolidayManager import HolidayType
import random

# These are the difficulties for NPC games.
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2

# These are ID numbers for the different card types.
CARD_0 = 11
CARD_1 = 12
CARD_2 = 13
CARD_3 = 14
CARD_4 = 15
CARD_5 = 16
CARD_6 = 17
CARD_7 = 18
CARD_8 = 19
CARD_9 = 21
CARD_REVERSE = 10
CARD_SKIP = 20
CARD_DRAW_TWO = 30
CARD_WILD = 40
CARD_WILD_DRAW_FOUR = 50
CARD_BLUE = 60
CARD_RED = 70
CARD_YELLOW = 80
CARD_GREEN = 90

colorId2colorName = {str(CARD_BLUE): "Blue",
                    str(CARD_GREEN): "Green",
                    str(CARD_RED): "Red",
                    str(CARD_YELLOW): "Yellow"}
colorName2colorId = {v: k for k, v in colorId2colorName.items()}

def addRandomColorToCardType(card_type):
    wildCards = [str(CARD_WILD), str(CARD_WILD_DRAW_FOUR)]
    colors = [str(CARD_BLUE), str(CARD_RED), str(CARD_YELLOW), str(CARD_GREEN)]
    new_card = str(card_type)
    if card_type not in wildCards:
        color = random.choice(colors)
        new_card.join(color)
    return new_card

# Now these are card combination IDs.
# Ex: a draw two card that is blue
cardId = [str(CARD_DRAW_TWO) + str(CARD_BLUE),
    str(CARD_DRAW_TWO) + str(CARD_GREEN),
    str(CARD_DRAW_TWO) + str(CARD_RED),
    str(CARD_DRAW_TWO) + str(CARD_YELLOW),
    str(CARD_WILD),
    str(CARD_WILD_DRAW_FOUR),
    str(CARD_SKIP) + str(CARD_GREEN),
    str(CARD_SKIP) + str(CARD_BLUE),
    str(CARD_SKIP) + str(CARD_RED),
    str(CARD_SKIP) + str(CARD_YELLOW),
    str(CARD_REVERSE) + str(CARD_GREEN),
    str(CARD_REVERSE) + str(CARD_BLUE),    
    str(CARD_REVERSE) + str(CARD_RED),
    str(CARD_REVERSE) + str(CARD_YELLOW),
    str(CARD_0) + str(CARD_BLUE),
    str(CARD_1) + str(CARD_BLUE),
    str(CARD_2) + str(CARD_BLUE),
    str(CARD_3) + str(CARD_BLUE),
    str(CARD_4) + str(CARD_BLUE),
    str(CARD_5) + str(CARD_BLUE),
    str(CARD_6) + str(CARD_BLUE),
    str(CARD_7) + str(CARD_BLUE),
    str(CARD_8) + str(CARD_BLUE),
    str(CARD_9) + str(CARD_BLUE),
    str(CARD_0) + str(CARD_GREEN),
    str(CARD_1) + str(CARD_GREEN),
    str(CARD_2) + str(CARD_GREEN),
    str(CARD_3) + str(CARD_GREEN),
    str(CARD_4) + str(CARD_GREEN),
    str(CARD_5) + str(CARD_GREEN),
    str(CARD_6) + str(CARD_GREEN),
    str(CARD_7) + str(CARD_GREEN),
    str(CARD_8) + str(CARD_GREEN),
    str(CARD_9) + str(CARD_GREEN),
    str(CARD_0) + str(CARD_RED),
    str(CARD_1) + str(CARD_RED),
    str(CARD_2) + str(CARD_RED),
    str(CARD_3) + str(CARD_RED),
    str(CARD_4) + str(CARD_RED),
    str(CARD_5) + str(CARD_RED),
    str(CARD_6) + str(CARD_RED),
    str(CARD_7) + str(CARD_RED),
    str(CARD_8) + str(CARD_RED),
    str(CARD_9) + str(CARD_RED),
    str(CARD_0) + str(CARD_YELLOW),
    str(CARD_1) + str(CARD_YELLOW),
    str(CARD_2) + str(CARD_YELLOW),
    str(CARD_3) + str(CARD_YELLOW),
    str(CARD_4) + str(CARD_YELLOW),
    str(CARD_5) + str(CARD_YELLOW),
    str(CARD_6) + str(CARD_YELLOW),
    str(CARD_7) + str(CARD_YELLOW),
    str(CARD_8) + str(CARD_YELLOW),
    str(CARD_9) + str(CARD_YELLOW)]

# This is data for card draw decks. It says how many of each card there is.
DRAW_CARD_DECK_DATA = {
    cardId[0]: 2,
    cardId[1]: 2,
    cardId[2]: 2,
    cardId[3]: 2,
    cardId[4]: 4,
    cardId[5]: 4,
    cardId[6]: 2,
    cardId[7]: 2,
    cardId[8]: 2,
    cardId[9]: 2,
    cardId[10]: 2,
    cardId[11]: 2,
    cardId[12]: 2,
    cardId[13]: 2,
    cardId[14]: 1,
    cardId[15]: 2,
    cardId[16]: 2,
    cardId[17]: 2,
    cardId[18]: 2,
    cardId[19]: 2,
    cardId[20]: 2,
    cardId[21]: 2,
    cardId[22]: 2,
    cardId[23]: 2,
    cardId[24]: 1,
    cardId[25]: 2,
    cardId[26]: 2,
    cardId[27]: 2,
    cardId[28]: 2,
    cardId[29]: 2,
    cardId[30]: 2,
    cardId[31]: 2,
    cardId[32]: 2,
    cardId[33]: 2,
    cardId[34]: 1,
    cardId[35]: 2,
    cardId[36]: 2,
    cardId[37]: 2,
    cardId[38]: 2,
    cardId[39]: 2,
    cardId[40]: 2,
    cardId[41]: 2,
    cardId[42]: 2,
    cardId[43]: 2,
    cardId[44]: 1,
    cardId[45]: 2,
    cardId[46]: 2,
    cardId[47]: 2,
    cardId[48]: 2,
    cardId[49]: 2,
    cardId[50]: 2,
    cardId[51]: 2,
    cardId[52]: 2,
    cardId[53]: 2,
}
        
cardTex2cardId = {"mg_uno_actioncards_blue_drawtwo": cardId[0],
            "mg_uno_actioncards_green_drawtwo": cardId[1],
            "mg_uno_actioncards_red_drawtwo": cardId[2],
            "mg_uno_actioncards_yellow_drawtwo": cardId[3],
            "mg_uno_actioncards_wild": cardId[4],
            "mg_uno_actioncards_wild_drawfour": cardId[5],
            "mg_uno_actioncards_green_skip": cardId[6],
            "mg_uno_actioncards_blue_skip": cardId[7],
            "mg_uno_actioncards_red_skip": cardId[8],
            "mg_uno_actioncards_yellow_skip": cardId[9],
            "mg_uno_actioncards_green_reverse": cardId[10],
            "mg_uno_actioncards_blue_reverse": cardId[11],    
            "mg_uno_actioncards_red_reverse": cardId[12],
            "mg_uno_actioncards_yellow_reverse": cardId[13],
            "mg_uno_numcards_blue_0": cardId[14],
            "mg_uno_numcards_blue_1": cardId[15],
            "mg_uno_numcards_blue_2": cardId[16],
            "mg_uno_numcards_blue_3": cardId[17],
            "mg_uno_numcards_blue_4": cardId[18],
            "mg_uno_numcards_blue_5": cardId[19],
            "mg_uno_numcards_blue_6": cardId[20],
            "mg_uno_numcards_blue_7": cardId[21],
            "mg_uno_numcards_blue_8": cardId[22],
            "mg_uno_numcards_blue_9": cardId[23],
            "mg_uno_numcards_green_0": cardId[24],
            "mg_uno_numcards_green_1": cardId[25],
            "mg_uno_numcards_green_2": cardId[26],
            "mg_uno_numcards_green_3": cardId[27],
            "mg_uno_numcards_green_4": cardId[28],
            "mg_uno_numcards_green_5": cardId[29],
            "mg_uno_numcards_green_6": cardId[30],
            "mg_uno_numcards_green_7": cardId[31],
            "mg_uno_numcards_green_8": cardId[32],
            "mg_uno_numcards_green_9": cardId[33],
            "mg_uno_numcards_red_0": cardId[34],
            "mg_uno_numcards_red_1": cardId[35],
            "mg_uno_numcards_red_2": cardId[36],
            "mg_uno_numcards_red_3": cardId[37],
            "mg_uno_numcards_red_4": cardId[38],
            "mg_uno_numcards_red_5": cardId[39],
            "mg_uno_numcards_red_6": cardId[40],
            "mg_uno_numcards_red_7": cardId[41],
            "mg_uno_numcards_red_8": cardId[42],
            "mg_uno_numcards_red_9": cardId[43],
            "mg_uno_numcards_yellow_0": cardId[44],
            "mg_uno_numcards_yellow_1": cardId[45],
            "mg_uno_numcards_yellow_2": cardId[46],
            "mg_uno_numcards_yellow_3": cardId[47],
            "mg_uno_numcards_yellow_4": cardId[48],
            "mg_uno_numcards_yellow_5": cardId[49],
            "mg_uno_numcards_yellow_6": cardId[50],
            "mg_uno_numcards_yellow_7": cardId[51],
            "mg_uno_numcards_yellow_8": cardId[52],
            "mg_uno_numcards_yellow_9": cardId[53]}
cardId2cardTex = {v: k for k, v in cardTex2cardId.items()}

def getCard(cardType):
    gui = loader.loadModel("phase_4/models/minigames/mg_uno_game_cards.egg")
    card = gui.find('**/%s' % (cardType))
    if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
        card.setTexture(loader.loadTexture('winter/maps/uno/%s.png' % (card.getName())), 1)
    return card

# Play-by-play event messages.
EVENT_DEALING_CARDS = "Dealing cards to players..."
EVENT_CARD_PLACED = "%s placed a %s card!"
EVENT_UNO_CALLED = "%s has called UNO!"
EVENT_WINNER = "%s has won the game!"
EVENT_NEW_TURN = "It's %s turn!"
EVENT_DRAWING_TWO = "%s is drawing two cards!"
EVENT_DRAWING_FOUR = "%s is drawing four cards!"
EVENT_NEW_COLOR = "%s has picked the color %s!"
EVENT_CHOOSING_NEW_COLOR = "%s is choosing a new color..."
EVENT_SKIPPED_TURN = "%s's turn was skipped!"
EVENT_REVERSE = "The turns have been reversed!"
EVENT_SHUFFLING = "Shuffling the cards..."