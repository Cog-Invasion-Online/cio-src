"""

  Filename: QuestGlobals.py
  Created by: DecodedLogic (13Nov15)

"""

from pandac.PandaModules import Vec4, Point3

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil

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
NOBODY = -1

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

Suit2PosterZNDScale = {
    'bigcheese' : [-0.05, 0.18],
    'tightwad' : [-0.035, 0.3],
    'headhunter' : [-0.04, 0.3],
    'beancounter' : [-0.05, 0.2],
    'micromanager' : [-0.04, 0.25],
    'yesman' : [-0.045, 0.2],
    'pencilpusher' : [-0.05, IMAGE_SCALE_SMALL],
    'flunky' : [-0.04, 0.3], # GLASSES AREN'T SCALING CORRECTLY
    'bigwig' : [-0.05, 0.25],
    'legaleagle' : [-0.04, 0.3],
    'telemarketer' : [-0.05, 0.18],
    'backstabber' : [-0.0575, 0.14],
    'ambulancechaser' : [-0.055, 0.16],
    'twoface' : [-0.05, 0.18],
    'movershaker' : [-0.055, 0.18],
    'loanshark' : [-0.06, 0.25],
    'moneybags' : [-0.04, 0.2],
    'numbercruncher' : [-0.055, 0.17],
    'pennypincher' : [-0.05, 0.12],
    'coldcaller' : [-0.045, 0.25],
    'gladhander' : [-0.0425, 0.225]
}

def getTPAccessIcon():
    geom = loader.loadModel('phase_3.5/models/gui/sos_textures.bam').find('**/teleportIcon')
    return geom

def getFilmIcon():
    return loader.loadModel('phase_3.5/models/gui/filmstrip.bam')

def getPackageIcon():
    geom = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
    geom = geom.find('**/package')
    return geom

def getCogIcon():
    geom = loader.loadModel('phase_3/models/gui/cog_icons.bam')
    geom = geom.find('**/cog')
    return geom

def getJBIcon():
    geom = loader.loadModel('phase_3.5/models/gui/jar_gui.bam')
    return geom

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

# Gets the location text for a location.

def getLocationText(location):
    if location in CIGlobals.ZoneId2Hood.keys():
        return '%s\n%s' % ('Any Street', CIGlobals.ZoneId2Hood.get(location))
    elif location in CIGlobals.BranchZone2StreetName.keys():
        streetName = CIGlobals.BranchZone2StreetName.get(location)
        playground = CIGlobals.ZoneId2Hood.get(location - (location % 1000))
        return '%s\n%s' % (streetName, playground)
    elif location in CIGlobals.zone2TitleDict.keys():
        shop = CIGlobals.zone2TitleDict.get(location)[0]
        streetZone = ZoneUtil.getBranchZone(location)
        if streetZone % 1000 >= 100:
            streetName = CIGlobals.BranchZone2StreetName[streetZone]
        else:
            streetName = PLAYGROUND
        hoodName = ZoneUtil.getHoodId(streetZone, 1)
        return '%s\n%s\n%s' % (shop, streetName, hoodName)
    elif not location:
        return 'Any Street\nAny Playground'
    
def isShopLocation(location):
    return location in CIGlobals.zone2TitleDict.keys()

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

def getPossessive(word):
    lastLetter = word[len(word) - 1]
    if lastLetter != 's':
        word += "'s"
    else:
        word += "'"
    return word