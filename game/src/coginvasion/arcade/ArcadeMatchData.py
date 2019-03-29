"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ArcadeMatchData.py
@author Maverick Liberty
@date June 15, 2018

A class containing data about an individual Arcade Mode match.

"""

from src.coginvasion.battle import BattleGlobals

class ArcadeMatchData:
    
    def __init__(self, hostId):
        """ Requires the avatar id of the host of the match as the first argument. """
        
        # This is the avatar id of the host of this match.
        self.hostId = hostId
        
        # This is the district id of where the match will be hosted.
        self.districtId = -1
        
        # Let's default to the very first arcade arena.
        self.arena = BattleGlobals.ArcadeId2Arena.values()[0]
        
        # Whether or not the battle shop should be generated. (If this is disabled, powerups cannot be purchased).
        self.wantPowerups = True
        
        # This is the minimum amount of laff a player needs to join this match.
        self.minimumLaff = -1
        
        # This is the maximum amount of laff a player can have before being denied entry into this match.
        self.maximumLaff = -1
        
        # This is whether or not this match is open to the public. If this is false, only friends of the host can join.
        self.isPublic = True
    
        # This is a list of avatar ids currently associated with this match. (This excludes the host id)
        self.party = []
