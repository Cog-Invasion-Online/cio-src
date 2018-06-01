"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Variant.py
@author Maverick Liberty
@date July 31, 2015

"""

from panda3d.core import VBase4

NORMAL = 0
SKELETON = 1
WAITER = 2
MINIGAME = 3
ZOMBIE = 4
CORRODED = 5

CORRODED_HAND_COLOR = VBase4(102.0 / 255.0, 75.0 / 255.0, 28.0 / 255.0, 1.0)#VBase4(146.0 / 255.0, 88.0 / 255.0, 36.0 / 255.0, 1.0)

VariantToName = {
    NORMAL : 'Suit',
    SKELETON : 'Skelecog',
    WAITER : 'Waiter',
    MINIGAME : 'MG Bot',
    ZOMBIE : 'Zombie',
    CORRODED : 'Corroded'
}

def getVariantById(index):
    variants = [NORMAL, SKELETON, WAITER, MINIGAME, ZOMBIE, CORRODED]
    return variants[index]
