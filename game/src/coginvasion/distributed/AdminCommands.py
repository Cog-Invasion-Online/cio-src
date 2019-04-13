"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdminCommands.py
@author Brian Lach
@date September 09, 2016

@desc Houses methods for admin commands in game.
      The methods are basically like macros but in Python.

"""

from src.coginvasion.gui import Dialog
import __builtin__

NoAccess = 0

Kick = 0
Ban = 1
UnlockAllGags = 2
RefillLaff = 3

PERM_TOGGLE_GHOST = "ADM_TOGGLE_GHOST"
PERM_DIST_MSG = "ADM_DISTRICT_MESSAGE"
PERM_UNLOCK_GAGS = "ADM_UNLOCK_GAGS"
PERM_REFILL_LAFF = "ADM_REFILL_LAFF"
PERM_AWARD_TSA_UNIFORM = "ADM_AWARD_TSA_UNIFORM"
PERM_SET_WORLD_ACCESS = "ADM_SET_WORLD_ACCESS"
PERM_TOGGLE_PLAYER_IDS = "ADM_TOGGLE_PLAYER_IDS"
PERM_SET_ACCESS_LEVEL = "ADM_SET_ACCESS_LEVEL"
PERM_KICK_PLAYER = "ADM_KICK_PLAYER"
PERM_BAN_PLAYER = "ADM_BAN_PLAYER"

NoPermission = "Insufficient permissions!"
FeedbackDoneEvent = 'feedback-done'

class Role:
    """ This represents different staff member roles within the game. """
    
    def __init__(self, name, accessLevel, token, permissions):
        """ Requires the name, access level (int), token instance, and a list of permissions """
        self.name = name
        self.accessLevel = accessLevel
        self.token = token
        self.permissions = permissions
        
    def hasPermission(self, permission):
        return (permission in self.permissions) or ('*' in self.permissions)

class Token:
    """ The circular icon that displays above a staff member """
    
    def __init__(self, color, matName):
        """ Expects an RGBA color and the material name """
        self.color = color
        self.matName = matName
        
    def getColor(self):
        return self.color
        
    def getMaterialPath(self):
        return 'phase_3/maps/{0}'.format(self.matName)

TeamLeadToken = Token((194.0 / 255.0, 9.0 / 255.0, 4.0 / 255.0, 1.0), 'team_lead.mat')
DeveloperToken = Token((0.0 / 255, 134.0 / 255, 254.0 / 255, 1.0), 'developer.mat')
ModeratorToken = Token((241.0 / 255, 183.0 / 255, 48.0 / 255, 1.0), 'moderator.mat')
PublicRelationsToken = Token((231.0 / 255.0, 131.0 / 255.0, 46.0 / 255.0, 1.0), 'public_relations.mat')
CreativeTeamToken = Token((100.0 / 255, 193.0 / 255, 75.0 / 255, 1.0), 'creative.mat')

# Access Level : Role Instance
# Keys should be identical to the actual access level passed into the Role class.
Roles = {
    1000 : Role("Team Lead", 1000, TeamLeadToken, ['*']),
    750 : Role("Developer", 750, DeveloperToken, ['*']),
    500 : Role("Creative", 500, CreativeTeamToken, ['*']),
    250 : Role("Public Relations", 250, PublicRelationsToken, ['*']),
    100 : Role("Moderator", 100, ModeratorToken, ['*'])
}

RoleIdByName = {
    "Developer" : 1000,
    "Creative" : 500,
    "Moderator" : 100
}

########################################
def precommandChecks(permission):
    if not hasattr(__builtin__, "base") and not hasattr(base, "localAvatar"):
        return False
    elif base.localAvatar.getAccessLevel() > NoAccess:
        # Let's see if the local avatar has permission to access the requested command.
        hasPermission = base.localAvatar.role.hasPermission(permission)
        
        if not hasPermission:
            # Let's let them know that they don't have permission to access the requested command.
            showFeedbackDialog(NoPermission)
        return hasPermission

    return False
    
def hasUpdateAuthorityOn():
    pass
########################################

# Command name followed by its 
Commands = {}

def __cleanupFeedbackDialog(dialog):
    if dialog:
        dialog.cleanup()
    return

def showFeedbackDialog(message):
    dialog = Dialog.GlobalDialog(message, FeedbackDoneEvent, Dialog.Ok)
    base.localAvatar.acceptOnce(FeedbackDoneEvent, __cleanupFeedbackDialog, extraArgs = [dialog])
    base.localAvatar.acceptOnce(base.cr.playGame.getPlace().doneEvent, __cleanupFeedbackDialog, extraArgs = [dialog])

def REQ_SET_TSA_UNI(avId, flag):
    if not precommandChecks(PERM_AWARD_TSA_UNIFORM):
        return
        
    toon = base.cr.doId2do.get(avId)
    if toon:
        toon.sendUpdate('reqSetTSAUni', [flag])

__builtin__.REQ_SET_TSA_UNI = REQ_SET_TSA_UNI

def REQ_SET_ACCESS_LEVEL(avId, accessLevel):
    if not precommandChecks(PERM_SET_ACCESS_LEVEL):
        return
    
    toon = base.cr.doId2do.get(avId)
    if toon:
        myAccess = base.localAvatar.getAccessLevel()
        if myAccess > accessLevel:
            showFeedbackDialog(NoPermission)
            return

        toon.sendUpdate('reqSetAccessLevel', [accessLevel])

__builtin__.REQ_SET_ACCESS_LEVEL = REQ_SET_ACCESS_LEVEL

def SEND_KICK_MSG(avId, andBan = 0):
    if (not andBan and not precommandChecks(PERM_KICK_PLAYER)) or (andBan and not precommandChecks(PERM_BAN_PLAYER)):
        return
    
    toon = base.cr.doId2do.get(avId)
    if toon:
        myAccess = base.localAvatar.getAccessLevel()
        if myAccess > toon.getAccessLevel():
            showFeedbackDialog(NoPermission)
            return
    
    
    print "SEND_KICK_MSG({0}, {1})".format(avId, andBan)
    base.localAvatar.sendUpdate("requestEject", [avId, andBan])

__builtin__.SEND_KICK_MSG = SEND_KICK_MSG

def SEND_SUIT_CMD(commandName):
    if not precommandChecks(None):
        return
        
    if base.cr.playGame.suitManager:
        base.cr.playGame.suitManager.sendUpdate('suitAdminCommand', [base.localAvatar.getAccessLevel(),
                                                                     commandName])

__builtin__.SEND_SUIT_CMD = SEND_SUIT_CMD

def SEND_REQ_UNLOCK_GAGS():
    if not precommandChecks(PERM_UNLOCK_GAGS):
        return

    base.localAvatar.sendUpdate('reqUnlockAllGags')

__builtin__.SEND_REQ_UNLOCK_GAGS = SEND_REQ_UNLOCK_GAGS

def SEND_REQ_REFILL_LAFF():
    if not precommandChecks(PERM_REFILL_LAFF):
        return
    
    base.localAvatar.sendUpdate('reqRefillLaff')

__builtin__.SEND_REQ_REFILL_LAFF = SEND_REQ_REFILL_LAFF

def TOGGLE_GHOST():
    if not precommandChecks(PERM_TOGGLE_GHOST):
        return
    
    if base.localAvatar.getGhost():
        base.localAvatar.b_setGhost(0)
    else:
        base.localAvatar.b_setGhost(1)

__builtin__.TOGGLE_GHOST = TOGGLE_GHOST

def TOGGLE_PLAYER_IDS():
    if not precommandChecks(PERM_TOGGLE_PLAYER_IDS):
        return
        
    if base.cr.isShowingPlayerIds:
        base.cr.hidePlayerIds()
    else:
        base.cr.showPlayerIds()
        
__builtin__.TOGGLE_PLAYER_IDS = TOGGLE_PLAYER_IDS

def DISTRICT_WIDE_MSG(msg):
    if not precommandChecks(PERM_DIST_MSG):
        return
        
    base.cr.myDistrict.sendUpdate('systemMessageCommand', [base.localAvatar.getAccessLevel(), msg])

__builtin__.DISTRICT_WIDE_MSG = DISTRICT_WIDE_MSG

def REQ_SET_WORLD_ACCESS(avId, andTP):
    if not precommandChecks(PERM_SET_WORLD_ACCESS):
        return
    
    toon = base.cr.doId2do.get(avId)
    if toon:
        toon.sendUpdate('reqSetWorldAccess', [andTP])
        
__builtin__.REQ_SET_WORLD_ACCESS = REQ_SET_WORLD_ACCESS
    
