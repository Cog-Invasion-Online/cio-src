"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendsManager.py
@author Brian Lach
@date August 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

from src.coginvasion.globals import CIGlobals, ChatGlobals
from src.coginvasion.gui.Whisper import Whisper
from src.coginvasion.gui.WhisperPopup import WhisperPopup

class FriendsManager(DistributedObjectGlobal):
    notify = directNotify.newCategory("FriendsManager")

    ComingOnlineMessage = "%s is coming online!"
    GoingOfflineMessage = "%s has logged out."
    LeftListMessage = "%s left your friends list."
    TeleportNotify = "%s is coming to visit you."

    def d_sendWhisper(self, target, message):
        self.sendUpdate('sendWhisper', [target, message])

    def whisper(self, sender, message, name):
        whisper = WhisperPopup(name + ': ' + message, CIGlobals.getToonFont(), ChatGlobals.WTNormal)
        whisper.setClickable(name, sender, isPlayer = 1)
        whisper.manage(base.marginManager)

    def getAvatarName(self, avId):
        av = self.cr.doId2do.get(avId)
        if av:
            return av.getName()

    def d_requestFriendsList(self):
        self.sendUpdate('requestFriendsList', [])

    def friendsList(self, idArray, nameArray, flags, adminTokens):
        messenger.send('gotFriendsList', [idArray, nameArray, flags, adminTokens])

    def teleportNotify(self, name):
        whisper = WhisperPopup(self.TeleportNotify % name, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)

    def friendLeftYourList(self, avatarId):
        whisper = WhisperPopup(self.LeftListMessage % self.getAvatarName(avatarId), CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)
        base.localAvatar.panel.maybeUpdateFriendButton()
        self.d_requestFriendsList()

    def toonOnline(self, avatarId, name):
        if avatarId in base.localAvatar.friends:
            whisper = WhisperPopup(self.ComingOnlineMessage % name, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
            whisper.setClickable(name, avatarId, isPlayer = 1)
            whisper.manage(base.marginManager)
            self.d_requestFriendsList()

    def toonOffline(self, avatarId, name):
        print "toon offline"
        if avatarId in base.localAvatar.friends:
            print "they are in my friends list"
            whisper = WhisperPopup(self.GoingOfflineMessage % name, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
            whisper.manage(base.marginManager)
            self.d_requestFriendsList()

    def avatarInfo(self, name, dna, maxHP, hp, zoneId, shardId, isOnline, adminToken):
        messenger.send('avatarInfoResponse', [name, dna, maxHP, hp, zoneId, shardId, isOnline, adminToken])

    def friendRequest(self, sender, name, dna):
        messenger.send('newFriendRequest', [sender, name, dna])

    def avatarLocation(self, avatarId, shardId, zoneId):
        messenger.send('gotAvatarTeleportResponse', [avatarId, shardId, zoneId])

    def d_myAvatarLocation(self, avatarId, shardId, zoneId):
        self.sendUpdate('myAvatarLocation', [avatarId, shardId, zoneId])

    def avatarWantsYourLocation(self, avatarId):
        self.d_myAvatarLocation(avatarId, base.localAvatar.parentId, base.localAvatar.zoneId)

    def d_requestAvatarInfo(self, avatarId):
        self.sendUpdate('requestAvatarInfo', [avatarId])

    def d_iWantToTeleportToAvatar(self, avatarId):
        self.sendUpdate('iWantToTeleportToAvatar', [avatarId])

    def d_iRemovedFriend(self, avatarId):
        self.sendUpdate('iRemovedFriend', [avatarId])

    def d_iAcceptedFriendRequest(self, avatarId):
        self.sendUpdate('iAcceptedFriendRequest', [avatarId])

    def d_iRejectedFriendRequest(self, avatarId):
        self.sendUpdate('iRejectedFriendRequest', [avatarId])

    def d_iCancelledFriendRequest(self, avatarId):
        self.sendUpdate('iCancelledFriendRequest', [avatarId])

    def d_requestAvatarStatus(self, avatarId):
        self.sendUpdate('requestAvatarStatus', [avatarId])

    def d_myAvatarStatus(self, avatarId):
        busy = base.localAvatar.getBusy()
        if base.localAvatar.getMyBattle():
            busy = 1
        self.sendUpdate('myAvatarStatus', [avatarId, busy])

    def d_askAvatarToBeFriends(self, avatarId):
        self.sendUpdate('askAvatarToBeFriends', [avatarId])

    def avatarStatus(self, avatarId, status):
        messenger.send('gotAvatarStatus', [avatarId, status])

    def someoneWantsYourStatus(self, avatarId):
        self.d_myAvatarStatus(avatarId)

    def acceptedFriendRequest(self):
        messenger.send('friendRequestAccepted')

    def rejectedFriendRequest(self):
        messenger.send('friendRequestRejected')

    def cancelFriendRequest(self, requester):
        messenger.send('friendRequestCancelled', [requester])
