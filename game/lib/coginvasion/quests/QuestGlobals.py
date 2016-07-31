# Filename: QuestGlobals.py
# Created by:  blach (29Jul15)

from lib.coginvasion.suit import CogBattleGlobals
from lib.coginvasion.globals.CIGlobals import *

Any = 0
Anywhere = 0

class Tiers:
    TT = 13
    DD = 14
    DG = 15
    ML = 16
    BR = 17
    DL = 18

class NPCDialogue:
    Goodbyes = ["Have a great day!", "Have fun in Toontown!", "Goodbye!", "See you soon!"]
    QuestAssignGoodbyes = Goodbyes + ["Good luck!", "I believe in you!", "You can do it!"]

    QuestCompletedIntros = ["Say there, %s!", "Hello, %s!", "Hi there, %s.", "Thank you, %s!", "Hey, %s!"]
    QuestCompletedCongrats = ["Great job, %s!", "Great job completing that Quest!", "Nice job, %s.",
                                "Nice job completing that Quest.", "Amazing job, %s!", "Good job, %s!"]

    FindNPC = ["You can find %s at %s...", "%s is located at %s..."]
    WhichIs = "...which is %s"

    Reward = ["Enjoy having %s!", "You have earned %s.", "You now have %s."]

def makePastTense(text):
    if text.endswith('e'):
        return text + 'd'
    else:
        return text + 'ed'

def makeSingular(text):
    if text.endswith('s'):
        return text[:-1]

def makePlural(text):
    if text.endswith('y'):
        text = text[:-1]
        return text + 'ies'
    elif text.endswith('s'):
        return text
    else:
        return text + 's'


def getOrdinal(number):
    """Returns number as a string with an ordinal. Ex: 1st, 2nd, 3rd"""

    return "%d%s" % (number,"tsnrhtdd"[(number / 10 % 10 != 1) * (number % 10 < 4) * number % 10::4])
