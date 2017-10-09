"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Variant.py
@author Maverick Liberty
@date July 31, 2015

"""

NORMAL = 0
SKELETON = 1
WAITER = 2
MINIGAME = 3
ZOMBIE = 4

VariantToName = {
    NORMAL : 'Suit',
    SKELETON : 'Skelecog',
    WAITER : 'Waiter',
    MINIGAME : 'MG Bot',
    ZOMBIE : 'Zombie'
}

def getVariantById(index):
    variants = [NORMAL, SKELETON, WAITER, MINIGAME, ZOMBIE]
    return variants[index]
