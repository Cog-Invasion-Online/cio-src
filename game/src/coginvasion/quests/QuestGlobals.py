# Filename: QuestGlobals.py
# Created by:  blach (29Jul15)

from pandac.PandaModules import Vec4, Point3

from src.coginvasion.suit import CogBattleGlobals
from src.coginvasion.globals.CIGlobals import *

#####################################################################
# Quest posters

JUST_FOR_FUN = 'Just for fun!'
SIDE_QUEST = 'Side Quest'
ANYWHERE = 'Anywhere'
PLAYGROUND = 'The Playground'
DEFEAT = 'Defeat'
VISIT = 'Visit'
RECOVER = 'Recover'
DELIVER = 'Deliver'
TO = 'to:'
FROM = 'from:'

QPauxText = 0.04
QPtextScale = 0.045
QPtextWordwrap = 15.6

IMAGE_SCALE_LARGE = 0.2
IMAGE_SCALE_SMALL = 0.15

# Constants for the reward frame on posters.
JB_JAR_SCALE = 0.225
LEFT_JB_JAR_POS = Point3(-0.275, 0, 0.05)
RIGHT_JB_JAR_POS = Point3(0.2825, 0, 0.05)

LAFF_METER_SCALE = 0.035
LEFT_LAFF_METER_POS = Point3(-0.2875, 0, 0.0475)
RIGHT_LAFF_METER_POS = Point3(0.25, 0, 0.0275)

TP_ACCESS_SCALE = 0.1
LEFT_TP_ACCESS_POS = Point3(-0.2725, 0, 0.05)
RIGHT_TP_ACCESS_POS = Point3(0.285, 0, 0.05)

# Default positions for elements on posters.
DEFAULT_INFO_POS = Point3(0, 0, -0.02)
RECOVER_INFO_POS = Point3(-0.2, 0, -0.02)

DEFAULT_INFO2_POS = Point3(0, 0, -0.02)
RECOVER_INFO2_POS = Point3(0.18, 0, -0.02)

DEFAULT_LEFT_PICTURE_POS = Point3(0, 0, 0.09)
RECOVER_LEFT_PICTURE_POS = Point3(-0.2, 0, 0.09)
DEFAULT_RIGHT_PICTURE_POS = Point3(0.18, 0, 0.09)

# The text at the top that says something like Defeat, Recover, Take, etc
DEFAULT_AUX_POS = Point3(0, 0, 0.18)
RECOVER_AUX_POS = Point3(-0.2, 0, 0.18)

DEFAULT_MIDDLE_POS = Point3(-0.01, 0, 0.0725)

RED = Vec4(0.8, 0.45, 0.45, 1)
BRIGHT_RED = Vec4(1.0, 0.16, 0.16, 1)
REWARD_RED = Vec4(0.8, 0.3, 0.3, 1)
BLUE = Vec4(0.45, 0.45, 0.8, 1)
LIGHT_BLUE = Vec4(0.42, 0.671, 1, 1)
GREEN = Vec4(0.45, 0.8, 0.45, 1)
LIGHT_GREEN = Vec4(0.784, 1, 0.863, 1)
BROWN = Vec4(0.52, 0.42, 0.22, 1)
WHITE = Vec4(1, 1, 1, 1)

TEXT_COLOR = Vec4(0.3, 0.25, 0.2, 1)

def getTPAccessIcon():
    geom = loader.loadModel('phase_3.5/models/gui/sos_textures.bam').find('**/teleportIcon')
    return geom

def getFilmIcon():
    return loader.loadModel('phase_3.5/models/gui/filmstrip.bam')

def getPackageIcon():
    geom = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
    geom = geom.find('**/package')
    geom.setScale(0.12)
    return geom

def getCogIcon():
    geom = loader.loadModel('phase_3/models/gui/cog_icons.bam')
    geom = geom.find('**/cog')
    #geom.setScale(IMAGE_SCALE_SMALL)
    return geom

def getJBIcon():
    geom = loader.loadModel('phase_3.5/models/gui/jar_gui.bam')
    return geom

###########################################################################

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

    QuestCompletedIntros = ["Say there, %s!", "Hello, %s!", "Hi there, %s.", "Thank you, %s!", "Hey, %s!", "Howdy, %s!"]
    QuestCompletedCongrats = ["Great job, %s!", "Great job completing that ToonTask!", "Nice job, %s.",
                                "Nice job completing that ToonTask.", "Amazing job, %s!", "Good job, %s!"]

    FindNPC = ["You can find %s at %s...", "%s is located at %s..."]
    WhichIs = "...which is %s"

    Reward = ["Enjoy having %s!", "You have earned %s.", "You now have %s."]

    PickQuestTimeOut = "Need more time to think?"
    PickQuest = "Choose a ToonTask."
    CancelQuestPicker = "Come back later if you need a ToonTask, bye!"

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

def getNumName(number):
    if number == 1:
        return "One"
    elif number == 2:
        return "Two"
    elif number == 3:
        return "Three"
    elif number == 4:
        return "Four"
    elif number == 5:
        return "Five"
