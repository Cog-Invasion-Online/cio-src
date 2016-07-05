# Filename: ElevatorConstants.py
# Created by:  blach (13Dec15)

from panda3d.core import Vec4, Point3

ELEVATOR_NORMAL = 0
ELEVATOR_INT = 1
REJECT_NOREASON = 0
REJECT_SHUFFLE = 1
REJECT_NOSEAT = 2
MAX_GROUP_BOARDING_TIME = 6.0

ElevatorData = {ELEVATOR_NORMAL: {'openTime': 2.0,
    'closeTime': 2.0,
    'width': 3.5,
    'countdown': 15.0,
    'sfxVolume': 1.0,
    'collRadius': 5},
    ELEVATOR_INT: {'openTime': 2.0,
    'closeTime': 2.0,
    'width': 3.5,
    'countdown': 65.0,
    'sfxVolume': 1.0,
    'collRadius': 5}}

TOON_BOARD_ELEVATOR_TIME = 1.0
TOON_EXIT_ELEVATOR_TIME = 1.0
TOON_VICTORY_EXIT_TIME = 1.0
SUIT_HOLD_ELEVATOR_TIME = 1.0
SUIT_LEAVE_ELEVATOR_TIME = 2.0
INTERIOR_ELEVATOR_COUNTDOWN_TIME = 90
LIGHT_OFF_COLOR = Vec4(0.5, 0.5, 0.5, 1.0)
LIGHT_ON_COLOR = Vec4(1.0, 1.0, 1.0, 1.0)

ElevatorPoints = [Point3(-1.5, 5, 0.1), Point3(1.5, 5, 0.1),
                  Point3(-2.5, 3, 0.1), Point3(2.5, 3, 0.1)]

ElevatorOutPoints = [Point3(-1.5, -5, 0), Point3(1.5, -5, 0),
                     Point3(-2.5, -7, 0), Point3(2.5, -7, 0)]

ElevatorOutPointsFar = [Point3(-1.5, -5, 0), Point3(1.5, -5, 0),
                     Point3(-2.5, -7, 0), Point3(2.5, -7, 0)]
