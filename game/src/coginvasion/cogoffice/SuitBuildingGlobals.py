"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitBuildingGlobals.py
@author Brian Lach
@date December 13, 2015

"""

from ElevatorConstants import *
from src.coginvasion.globals import CIGlobals

VICTORY_RUN_TIME = ElevatorData[ELEVATOR_NORMAL]['openTime'] + TOON_VICTORY_EXIT_TIME
TO_TOON_BLDG_TIME = 8
VICTORY_SEQUENCE_TIME = VICTORY_RUN_TIME + TO_TOON_BLDG_TIME
CLEAR_OUT_TOON_BLDG_TIME = 4
TO_SUIT_BLDG_TIME = 8

SPAWN_TIME_RANGE = (300, 600)

# Range of guards per section.
GUARDS_PER_SECTION = 0
# Cog level range on the bottom floors.
LEVEL_RANGE = 1
# Cog level range on the top floor.
BOSS_LEVEL_RANGE = 2

buildingInfo = {
    CIGlobals.ToontownCentral:   {GUARDS_PER_SECTION: (0, 2),
                                  LEVEL_RANGE:        (1, 4),
                                  BOSS_LEVEL_RANGE:   (2, 4)},

    CIGlobals.DonaldsDock:       {GUARDS_PER_SECTION: (1, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (3, 6)},

    CIGlobals.DaisyGardens:      {GUARDS_PER_SECTION: (2, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6)},

    CIGlobals.MinniesMelodyland: {GUARDS_PER_SECTION: (2, 4),
                                  LEVEL_RANGE:        (3, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6)},

    CIGlobals.TheBrrrgh:         {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (6, 11),
                                  BOSS_LEVEL_RANGE:   (8, 11)},

    CIGlobals.DonaldsDreamland:  {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (8, 11),
                                  BOSS_LEVEL_RANGE:   (8, 12)}
}

# The minimum and maximum number of cog buildings that can be present on each street.
buildingMinMax = {
    CIGlobals.SillyStreet: (1, 3),
    CIGlobals.PunchlinePlace: (0, 3),
    CIGlobals.LoopyLane: (0, 3),
    CIGlobals.BarnacleBoulevard: (1, 5),
    CIGlobals.SeaweedStreet: (1, 5),
    CIGlobals.LighthouseLane: (1, 5),
    CIGlobals.ElmStreet: (2, 6),
    CIGlobals.MapleStreet: (2, 6),
    CIGlobals.OakStreet: (2, 6),
    CIGlobals.AltoAvenue: (3, 7),
    CIGlobals.BaritoneBoulevard: (3, 7),
    CIGlobals.TenorTerrace: (3, 7),
    CIGlobals.WalrusWay: (5, 10),
    CIGlobals.SleetStreet: (5, 10),
    CIGlobals.PolarPlace: (5, 10),
    CIGlobals.LullabyLane: (6, 12),
    CIGlobals.PajamaPlace: (6, 12)
}

# The chance a cog building will be spawned each interval.
buildingChances = {
    CIGlobals.SillyStreet: 2.0,
    CIGlobals.LoopyLane: 2.0,
    CIGlobals.PunchlinePlace: 2.0,
    CIGlobals.BarnacleBoulevard: 75.0,
    CIGlobals.SeaweedStreet: 75.0,
    CIGlobals.LighthouseLane: 75.0,
    CIGlobals.ElmStreet: 90.0,
    CIGlobals.MapleStreet: 90.0,
    CIGlobals.OakStreet: 90.0,
    CIGlobals.AltoAvenue: 95.0,
    CIGlobals.BaritoneBoulevard: 95.0,
    CIGlobals.TenorTerrace: 95.0,
    CIGlobals.WalrusWay: 100.0,
    CIGlobals.SleetStreet: 100.0,
    CIGlobals.PolarPlace: 100.0,
    CIGlobals.LullabyLane: 100.0,
    CIGlobals.PajamaPlace: 100.0,
}

# The chances a cog level has of spawning a building with a certain number of floors.
floorNumberChances = {
    1: [range(1, 100 + 1), [], [], [], []],
    2: [range(26, 100 + 1), range(1, 25 + 1), [], [], []],
    3: [range(1, 50 + 1), range(51, 100 + 1), [], [], []],
    4: [range(51, 75 + 1), range(1, 50 + 1), range(75, 100 + 1), [], []],
    5: [range(91, 95 + 1), range(76, 90 + 1), range(1, 75 + 1), range(96, 100 + 1), []],
    6: [[], range(96, 100 + 1), range(1, 50 + 1), range(51, 95 + 1), []],
    7: [[], [], range(1, 25 + 1), range(26, 75 + 1), range(76, 100 + 1)],
    8: [[], [], range(66, 100 + 1), range(1, 50 + 1), range(51, 65 + 1)],
    9: [[], [], range(96, 100 + 1), range(1, 30 + 1), range(31, 95 + 1)],
    10: [[], [], range(86, 100 + 1), range(56, 85 + 1), range(1, 55 + 1)],
    11: [[], [], range(91, 100 + 1), range(61, 90 + 1), range(1, 60 + 1)],
    12: [[], [], [], range(81, 100 + 1), range(1, 80 + 1)]
}
