"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdminCommands.py
@author Brian Lach
@date September 09, 2016

@desc Houses methods for admin commands in game.
      The methods are basically like macros but in Python.

"""

import __builtin__

NoToken = -1
DevToken = 0
UndercoverToken = 1
ModToken = 2
CreativeToken = 3

Kick = 0
Ban = 1
UnlockAllGags = 2

Permissions = {
    NoToken : 0,
    ModToken : []
}

TextByAdminToken = {NoToken:         "Nothing",
                    UndercoverToken: "Undercover",
                    DevToken:        "Developer",
                    ModToken:        "Moderator",
                    CreativeToken: "Creative"}

TextColorByAdminToken = {NoToken : (0, 0, 0, 1),
                         UndercoverToken : (0, 0, 0, 1),
                         DevToken : (255.0 / 255, 154.0 / 255, 0.0 / 255, 1),
                         ModToken : (0.0 / 255, 85.0 / 255, 255.0 / 255, 1),
                         CreativeToken: (99.0 / 255, 192.0 / 255, 74.0 / 255, 1)}

# These are the admin tokens
# Key is token id, value is the actual model id.
STAFF_TOKENS = {DevToken : 500, ModToken : 300, CreativeToken : 600}

########################################
def precommandChecks():
    if not hasattr(__builtin__, "base") and not hasattr(base, "localAvatar"):
        return False
    else:
        return base.localAvatar.getAdminToken() > NoToken
    
def hasUpdateAuthorityOn():
    pass
########################################

# Command name followed by its 
Commands = {}

def REGISTER_COMMAND(cmdName, cmdPerms = []):
    if not cmdName in Commands.keys():
        pass

def REQ_SET_TSA_UNI(avId, flag):
    if not precommandChecks():
        return
        
    toon = base.cr.doId2do.get(avId)
    if toon:
        toon.sendUpdate('reqSetTSAUni', [flag])

__builtin__.REQ_SET_TSA_UNI = REQ_SET_TSA_UNI

def REQ_SET_ADMIN_TOKEN(avId, token):
    if not precommandChecks():
        return
    
    toon = base.cr.doId2do.get(avId)
    if toon:
        myToken = base.localAvatar.getAdminToken()
        if myToken > token:
            pass
    
        # Restrict people from changing the token of a dev.
        if toon.getAdminToken() != DevToken:
            toon.sendUpdate('reqSetAdminToken', [token])

__builtin__.REQ_SET_ADMIN_TOKEN = REQ_SET_ADMIN_TOKEN

def SEND_KICK_MSG(avId, andBan = 0):
    if not precommandChecks():
        return
    
    print "SEND_KICK_MSG({0}, {1})".format(avId, andBan)
    base.localAvatar.sendUpdate("requestEject", [avId, andBan])

__builtin__.SEND_KICK_MSG = SEND_KICK_MSG

def SEND_SUIT_CMD(commandName):
    if not precommandChecks():
        return
        
    if base.cr.playGame.suitManager:
        base.cr.playGame.suitManager.sendUpdate('suitAdminCommand', [base.localAvatar.getAdminToken(),
                                                                     commandName])

__builtin__.SEND_SUIT_CMD = SEND_SUIT_CMD

def SEND_REQ_UNLOCK_GAGS():
    if not precommandChecks():
        return

    base.localAvatar.sendUpdate('reqUnlockAllGags')

__builtin__.SEND_REQ_UNLOCK_GAGS = SEND_REQ_UNLOCK_GAGS

def SEND_REQ_GAG_SLOTS():
    if not precommandChecks():
        return

    base.localAvatar.sendUpdate('reqAllGagSlots')

__builtin__.SEND_REQ_GAG_SLOTS = SEND_REQ_GAG_SLOTS

def TOGGLE_GHOST():
    if not precommandChecks():
        return
    
    if base.localAvatar.getGhost():
        base.localAvatar.setGhost(0)
    else:
        base.localAvatar.setGhost(1)

__builtin__.TOGGLE_GHOST = TOGGLE_GHOST

def TOGGLE_PLAYER_IDS():
    if not precommandChecks():
        return
        
    if base.cr.isShowingPlayerIds:
        base.cr.hidePlayerIds()
    else:
        base.cr.showPlayerIds()
        
__builtin__.TOGGLE_PLAYER_IDS = TOGGLE_PLAYER_IDS

def DISTRICT_WIDE_MSG(msg):
    if not precommandChecks():
        return
        
    base.cr.myDistrict.sendUpdate('systemMessageCommand', [base.localAvatar.getAdminToken(), msg])

__builtin__.DISTRICT_WIDE_MSG = DISTRICT_WIDE_MSG

def REQ_SET_WORLD_ACCESS(avId, andTP):
    if not precommandChecks():
        return
    
    toon = base.cr.doId2do.get(avId)
    if toon:
        toon.sendUpdate('reqSetWorldAccess', [andTP])
        
__builtin__.REQ_SET_WORLD_ACCESS = REQ_SET_WORLD_ACCESS
