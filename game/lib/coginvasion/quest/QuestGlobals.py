"""

  Filename: QuestGlobals.py
  Created by: DecodedLogic (13Nov15)

"""

from lib.coginvasion.quest import RewardType
from panda3d.core import Vec4

REWARD_DESCRIPTION = {
    RewardType.JELLYBEANS : 'For %s jellybeans',
    RewardType.LAFF_POINTS : 'For a %s point Laff boost',
    RewardType.TELEPORT_ACCESS : 'For teleport access to %s.'
}

JUST_FOR_FUN = 'Just for fun!'
QPauxText = 0.04
QPtextScale = 0.045
QPtextWordwrap = 15.6

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