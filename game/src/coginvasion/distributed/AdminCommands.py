# COG INVASION ONLINE
# Copyright (c) Brian Lach       <brianlach72@gmail.com>
#               Maverick Liberty <maverick.liberty29@gmail.com>
#
# file:    AdminCommands.py
# author:  Brian Lach
# date:    2016-09-05
#
# purpose: Houses methods for admin commands in game.
#          The methods are basically like preprocessor #defines but in Python.

import __builtin__

from src.coginvasion.globals.CIGlobals import NoToken, DevToken

########################################
def precommandChecks():
    if not hasattr(__builtin__, "base") and not hasattr(base, "localAvatar"):
        return False
    else:
        return base.localAvatar.getAdminToken() > NoToken
########################################

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

def TOGGLE_GHOST():
    if not precommandChecks():
        return
    
    if base.localAvatar.getGhost():
        print "Ghost off"
        base.localAvatar.setGhost(0)
    else:
        print "Ghost on"
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
