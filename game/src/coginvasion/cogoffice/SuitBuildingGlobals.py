"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitBuildingGlobals.py
@author Brian Lach
@date December 13, 2015

"""

from ElevatorConstants import ElevatorData, ELEVATOR_NORMAL, TOON_VICTORY_EXIT_TIME
from src.coginvasion.hood import ZoneUtil

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
# The chance (in percent) of a heal barrel spawning.
HEAL_BARREL_CHANCE = 3

buildingInfo = {
    ZoneUtil.ToontownCentral:   {GUARDS_PER_SECTION: (0, 2),
                                  LEVEL_RANGE:        (1, 4),
                                  BOSS_LEVEL_RANGE:   (2, 4),
                                  HEAL_BARREL_CHANCE:  10},

    ZoneUtil.DonaldsDock:       {GUARDS_PER_SECTION: (1, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (3, 6),
                                  HEAL_BARREL_CHANCE:  15},

    ZoneUtil.DaisyGardens:      {GUARDS_PER_SECTION: (2, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6),
                                  HEAL_BARREL_CHANCE:  20},

    ZoneUtil.MinniesMelodyland: {GUARDS_PER_SECTION: (2, 4),
                                  LEVEL_RANGE:        (3, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6),
                                  HEAL_BARREL_CHANCE:  25},

    ZoneUtil.TheBrrrgh:         {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (6, 11),
                                  BOSS_LEVEL_RANGE:   (8, 11),
                                  HEAL_BARREL_CHANCE:  30},

    ZoneUtil.DonaldsDreamland:  {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (8, 11),
                                  BOSS_LEVEL_RANGE:   (8, 12),
                                  HEAL_BARREL_CHANCE:  35}
}

# The minimum and maximum number of cog buildings that can be present on each street.
buildingMinMax = {
    ZoneUtil.SillyStreet: (1, 3),
    ZoneUtil.PunchlinePlace: (1, 3),
    ZoneUtil.LoopyLane: (1, 3),
    ZoneUtil.BarnacleBoulevard: (1, 5),
    ZoneUtil.SeaweedStreet: (1, 5),
    ZoneUtil.LighthouseLane: (1, 5),
    ZoneUtil.ElmStreet: (2, 6),
    ZoneUtil.MapleStreet: (2, 6),
    ZoneUtil.OakStreet: (2, 6),
    ZoneUtil.AltoAvenue: (3, 7),
    ZoneUtil.BaritoneBoulevard: (3, 7),
    ZoneUtil.TenorTerrace: (3, 7),
    ZoneUtil.WalrusWay: (5, 10),
    ZoneUtil.SleetStreet: (5, 10),
    ZoneUtil.PolarPlace: (5, 10),
    ZoneUtil.LullabyLane: (6, 12),
    ZoneUtil.PajamaPlace: (6, 12)
}

# The chance a cog building will be spawned each interval.
# Temporarily buffed TTC spawning rate from 2% to 20%
buildingChances = {
    ZoneUtil.SillyStreet: 20.0,
    ZoneUtil.LoopyLane: 20.0,
    ZoneUtil.PunchlinePlace: 20.0,
    ZoneUtil.BarnacleBoulevard: 75.0,
    ZoneUtil.SeaweedStreet: 75.0,
    ZoneUtil.LighthouseLane: 75.0,
    ZoneUtil.ElmStreet: 90.0,
    ZoneUtil.MapleStreet: 90.0,
    ZoneUtil.OakStreet: 90.0,
    ZoneUtil.AltoAvenue: 95.0,
    ZoneUtil.BaritoneBoulevard: 95.0,
    ZoneUtil.TenorTerrace: 95.0,
    ZoneUtil.WalrusWay: 100.0,
    ZoneUtil.SleetStreet: 100.0,
    ZoneUtil.PolarPlace: 100.0,
    ZoneUtil.LullabyLane: 100.0,
    ZoneUtil.PajamaPlace: 100.0,
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
