"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestGlobals.py
@author Brian Lach
@date July 29, 2015

"""

from panda3d.core import Vec4, Point3
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.hood import ZoneUtil

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
PLAY = 'Play'
INSPECT = 'Inspect'
RETURN = 'Return'
TO = 'to:'
FROM = 'from:'

# The event that is fired by the messenger when quest data is updated.
QUEST_DATA_UPDATE_EVENT = 'questDataUpdate'

QPauxText = 0.04
QPtextScale = 0.045
QPtextWordwrap = 15.6

SIMPLE_IMAGE_SCALE = 0.12
IMAGE_SCALE_LARGE = 0.2 # 0.2
IMAGE_SCALE_SMALL = 0.15 #0.15

GAG_SLOT_ICON_SCALE = 0.035
LEFT_GAG_SLOT_POS = Point3(-0.275, 0, -0.2425)
RIGHT_GAG_SLOT_POS = Point3(0.2825, 0, -0.2425)

# Constants for the reward frame on posters.
JB_JAR_SCALE = 0.225
LEFT_JB_JAR_POS = Point3(-0.275, 0, -0.18)
RIGHT_JB_JAR_POS = Point3(0.2825, 0, -0.18)

LAFF_METER_SCALE = 0.035
LEFT_LAFF_METER_POS = Point3(-0.2875, 0, -0.19)
RIGHT_LAFF_METER_POS = Point3(0.25, 0, -0.19)

TP_ACCESS_SCALE = 0.1125
LEFT_TP_ACCESS_POS = Point3(-0.275, 0, -0.2)
RIGHT_TP_ACCESS_POS = Point3(0.285, 0, -0.2)

# Default positions for elements on posters.
DEFAULT_INFO_POS = Point3(0, 0, -0.03) # -0.02
RECOVER_INFO_POS = Point3(-0.2, 0, -0.03)

DEFAULT_INFO2_POS = Point3(0, 0, -0.03)
RECOVER_INFO2_POS = Point3(0.18, 0, -0.03)

DEFAULT_LEFT_PICTURE_POS = Point3(0, 0, 0.09)
RECOVER_LEFT_PICTURE_POS = Point3(-0.2, 0, 0.09)
DEFAULT_RIGHT_PICTURE_POS = Point3(0.18, 0, 0.09)

# The text at the top that says something like Defeat, Recover, Take, etc
DEFAULT_AUX_POS = Point3(0, 0, 0.185)
RECOVER_AUX_POS = Point3(-0.2, 0, 0.185)

DEFAULT_MIDDLE_POS = Point3(-0.01, 0, 0.0725)

DEFAULT_LEFT_ARROW_POS = Point3(-0.15, 0, 0)
DEFAULT_RIGHT_ARROW_POS = Point3(0.15, 0, 0)
SECONDARY_LEFT_ARROW_POS = Point3(-0.13, 0, 0)
SECONDARY_RIGHT_ARROW_POS = Point3(0.515, 0, 0)

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
    'flunky' : [-0.04, 0.3],
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
    geom.setScale(0.12)
    return geom

def getTrolleyIcon():
    geom = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
    geom = geom.find('**/trolley')
    return geom

def getCogBuildingIcon():
    geom = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
    geom = geom.find('**/COG_building')
    return geom

def getCogIcon():
    geom = loader.loadModel('phase_3/models/gui/cog_icons.bam')
    geom = geom.find('**/cog')
    return geom

def getJBIcon():
    geom = loader.loadModel('phase_3.5/models/gui/jar_gui.bam')
    return geom

def getHQIcon():
    icons = loader.loadModel('phase_4/models/gui/tfa_images.bam')
    geom = icons.find('**/hq-dialog-image')
    icons.removeNode()
    return geom

def getGagSlotIcon(slot):
    return loader.loadTexture('phase_3.5/maps/slot_%s_%s.png' % (str(slot), 'selected'))

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

    FindNPC = ["You can find %s at %s...", "%s is located at %s...", "%s[p] building is called %s..."]
    WhichIs = "...which is %s"

    Reward = ["Enjoy having %s!", "You have earned %s.", "You now have %s."]
    Rewards = ["These rewards should come in handy!", "You've earned these rewards!"]

    PickQuestTimeOut = "Need more time to think?"
    PickQuest = "Choose a ToonTask."
    CancelQuestPicker = "Come back later if you need a ToonTask, bye!"

def getLocationText(location, objective = None):
    # Let's handle when the location is None, this means we want to go
    # to the objective's assigner. OR if we're looking for an HQ officer.
    if location == 0 or not location and objective:
        # Let's figure out where the assigner is at, fam.
        if location == 0 or objective.assigner == 0:
            return 'Any Street\nAny Neighborhood'
        else:
            return getLocationText(NPCGlobals.NPCToonDict[objective.assigner][0])
    
    if location in ZoneUtil.ZoneId2Hood.keys():
        if location == ZoneUtil.MinigameAreaId:
            return ZoneUtil.ZoneId2Hood.get(location)
        return '%s\n%s' % ('Any Street', ZoneUtil.ZoneId2Hood.get(location))
    elif location in ZoneUtil.BranchZone2StreetName.keys():
        streetName = ZoneUtil.BranchZone2StreetName.get(location)
        playground = ZoneUtil.ZoneId2Hood.get(location - (location % 1000))
        return '%s\n%s' % (streetName, playground)
    elif location in ZoneUtil.zone2TitleDict.keys():
        shop = ZoneUtil.zone2TitleDict.get(location)[0]
        streetZone = ZoneUtil.getBranchZone(location)
        if streetZone % 1000 >= 100:
            streetName = ZoneUtil.BranchZone2StreetName[streetZone]
        else:
            streetName = PLAYGROUND
        hoodName = ZoneUtil.getHoodId(streetZone, 1)
        return '%s\n%s\n%s' % (shop, streetName, hoodName)
    elif not location:
        return 'Any Street\nAny Playground'
    
def generatePoster(quest, parent, **kw):
    # We have to seek to the first objective if the seeker isn't on the first one yet.
    if quest and quest.accessibleObjectives.seeker == -1:
        quest.accessibleObjectives.nextObjective()
            
    from src.coginvasion.quest.poster.DoubleFrameQuestPoster import DoubleFrameQuestPoster
    poster = DoubleFrameQuestPoster(quest, parent = parent, **kw)
    poster.setup()
    return poster
    
def isShopLocation(location):
    return location in ZoneUtil.zone2TitleDict.keys() or location == 0

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
