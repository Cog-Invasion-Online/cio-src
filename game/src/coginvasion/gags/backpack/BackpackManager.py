########################################
# Filename: BackpackManager.py
# Created by: DecodedLogic (08Jul15)
########################################

from src.coginvasion.gags.backpack.SmallPouch import SmallPouch
from src.coginvasion.gags.backpack.AdminPouch import AdminPouch
import copy

backpacks = [SmallPouch, AdminPouch]
clientPacks = []

def getBackpack(index):
    backpack = None
    if index < len(backpacks) and index >= 0:
        backpack = backpacks[index]
    if backpack:
        backpack = copy.copy(backpack)
        if game.process == 'client':
            clientPacks.append(backpack)
    return backpack()

def getIndex(backpack):
    if not backpack: return
    for pack in backpacks:
        if pack == backpack:
            return backpacks.index(pack)

def getClientPack(backpack):
    if not backpack: return
    return clientPacks[backpack]

def getClientPackIndex(backpack):
    return clientPacks.index(backpack)

def getBackpacks():
    packs = []
    for pack in backpacks:
        packs.append(pack())
    return packs
