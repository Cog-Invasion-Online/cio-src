########################################
# Filename: Variant.py
# Created by: DecodedLogic (31Jul15)
########################################

NORMAL = 0
SKELETON = 1
WAITER = 2
MINIGAME = 3
ZOMBIE = 4

def getVariantById(index):
    variants = [NORMAL, SKELETON, WAITER, MINIGAME, ZOMBIE]
    return variants[index]
