"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BattleGlobals.py
@author Brian Lach
@date January 2, 2018

"""

from src.coginvasion.hood.ZoneUtil import BattleTTC, TheBrrrgh

ArcadeModeBadCode = 'Sorry, that code is not associated with any rooms.'
ArcadeModeFriendsOnlyRoom = 'Sorry, you must be a friend of that room\'s host to join.'
ArcadeModeFullRoom = 'Sorry, that room is full.'
ArcadeModeRoomJoinFailure = 'An unexpected error occurred while trying to place you into that room.'
ArcadeModeRoomLeaveConf = 'Are you sure you want to leave this room?'
ArcadeModeRoomDeleteConf = 'Are you sure you want to delete your room? This action is not reversible.'
ArcadeModeKickedByHost = 'You have been kicked from that room by the host.'
ArcadeModeConfCancelQueue = 'You are already in the matchmaking queue and a match will be found shortly. Are you sure you want to join this room instead?'
ArcadeModeConfCancelExistingRoom = 'The match you created will be canceled if you join this room. Join this room anyway?'
ArcadeModeMatchMakingStarted = 'You\'ve entered the matchmaking queue. You will be notified when an available room is found.'
ArcadeModeMatchMakingQuitConf = 'Are you sure you want to exit the matchmaking queue? You will not be notified of available matches anymore.'
ArcadeModeMatchMakingDisabled = 'Sorry, matchmaking is not available at this time. Try again later.'

ArcadeId2Arena = {
    0 : BattleTTC,
    1 : TheBrrrgh
}

ArcadeArena2Id = {}

def getArcadeArenaIdByName(arenaName):
    """ Fetches the id of an arena from its name. Returns None if the name passed is not a valid arena. """
    global ArcadeArena2Id

    if len(ArcadeArena2Id.keys()) == 0:
        # If the 'ArcadeArena2Id' dictionary has not been setup, we need
        # to set it up now.
        for key, value in ArcadeId2Arena.iteritems():
            ArcadeArena2Id[value] = key
    
    return ArcadeArena2Id.get(arenaName, None)
            

# Battle type
BTBattle = 0
BTOffice = 1
BTStreet = 2
BTTutorial = 3
BTArcade = 4
BTSewer = 5

# 20% chance of a cog taunting when attacking (it gets annoying if they taunt every time).
AttackTauntChance = [0, 4]

VictoryCamFov = 80.0