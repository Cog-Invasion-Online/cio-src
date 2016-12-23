# Filename: EagleGameGlobals.py
# Created by:  blach (08Jul15)

from pandac.PandaModules import Point3

EAGLE_HIT_EVENT = 'DEagleSuit-hitByLocalToon'

EAGLE_FLY_POINTS = [
    Point3(0.0, 80.0, 15.0),
    Point3(-30.0, 65.58, 15.0),
    Point3(30.0, 65.58, 15.0),
    Point3(0.0, 50.09, 15.0),
    Point3(15.0, 50.09, 5.0),
    Point3(-15.0, 50.09, 5.0),
    Point3(-15.0, 100.0, 5.0),
    Point3(15.0, 100.0, 5.0),
    Point3(30.0, 100.0, 25.0),
    Point3(-30.0, 100.0, 25.0),
    Point3(0.0, 124.03, 25.0),
    Point3(0.0, 101.72, 25.0),
    Point3(25.53, 192.04, 5.0)
]

ROUND_2_EAGLE_SPEED = {
    1: 0.35,
    2: 0.15,
    3: 0.05
}
