########################################
# Filename: Variant.py
# Created by: DecodedLogic (31Jul15)
########################################

NORMAL, SKELETON, WAITER, MINIGAME, ZOMBIE = range(5)

def getVariantById(index):
    variants = [NORMAL, SKELETON, WAITER, MINIGAME, ZOMBIE]
    return variants[index]