"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendsManagerUD.py
@author Brian Lach
@date August 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

from src.coginvasion.hood import ZoneUtil

class RequestFriendsListProcess:
    notify = directNotify.newCategory('RequestFriendsListProcess')

    def __init__(self, csm, air, sender):
        self.csm = csm
        self.air = air
        self.sender = sender
        self.realFriendsList = [[], [], [], []]
        self.avatarFriendsList = []
        self.friendIndex = 0
        self.senderDclass = None

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            self.senderRetrieved
        )

    def __updatedFriendsListDeletedToonDone(self, foo = None):
        self.csm.requestFriendsList(self.sender)
        self.cleanup()

    def friendRetrieved(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.notify.warning("Toon on friends list was deleted.")
            self.avatarFriendsList.remove(self.avatarFriendsList[self.friendIndex])
            dg = self.senderDclass.aiFormatUpdate('setFriendsList', self.sender, self.sender, self.air.ourChannel, [self.avatarFriendsList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, self.sender, self.senderDclass, {'setFriendsList': [self.avatarFriendsList]}, callback = self.__updatedFriendsListDeletedToonDone)
            return

        name = fields['setName'][0]
        adminToken = fields['setAdminToken'][0]
        avatarId = self.avatarFriendsList[self.friendIndex]
        self.realFriendsList[0].append(avatarId)
        self.realFriendsList[1].append(name)
        isOnline = int(avatarId in self.csm.toonsOnline)
        self.realFriendsList[2].append(isOnline)
        self.realFriendsList[3].append(adminToken)
        if self.friendIndex >= len(self.avatarFriendsList) - 1:
            # Done, send it out
            self.csm.sendUpdateToAvatarId(self.sender, 'friendsList', self.realFriendsList)
            self.cleanup()
            return
        self.friendIndex += 1

        self.air.dbInterface.queryObject(
            self.air.dbId,
            self.avatarFriendsList[self.friendIndex],
            self.friendRetrieved
        )

    def senderRetrieved(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.notify.warning("Queried a non toon object?!")
            return

        self.senderDclass = dclass

        self.avatarFriendsList = fields['setFriendsList'][0]

        if len(self.avatarFriendsList) == 0:
            self.csm.sendUpdateToAvatarId(self.sender, 'friendsList', [[], [], [], []])
            return

        self.air.dbInterface.queryObject(
            self.air.dbId,
            self.avatarFriendsList[self.friendIndex],
            self.friendRetrieved
        )

    def cleanup(self):
        del self.air
        del self.csm
        del self.sender
        del self.realFriendsList
        del self.avatarFriendsList
        del self.friendIndex
        del self.senderDclass

class FriendsManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory("FriendsManagerUD")

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.toonsOnline = []
        self.air.netMessenger.accept('avatarOnline', self, self.toonOnline)
        self.air.netMessenger.accept('avatarOffline', self, self.toonOffline)

    def sendWhisper(self, target, message):
        sender = self.air.getAvatarIdFromSender()

        def senderAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            name = fields['setName'][0]
            self.sendUpdateToAvatarId(target, 'whisper', [sender, message, name])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            senderAvatarResponse
        )

    def requestFriendsList(self, sender = None):
        if sender is None:
            sender = self.air.getAvatarIdFromSender()
        RequestFriendsListProcess(self, self.air, sender)
        
    def toonOnline(self, avatarId):

        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                self.notify.warning('toonOnline: avatarResponse: Attempted to get name of a newly online Toon and retrieved non-toon.')
                return

            name = fields['setName'][0]
            friendsList = fields['setFriendsList'][0]
            self.d_toonOnline(avatarId, friendsList, name)
        
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            avatarResponse
        )
        
    def toonOffline(self, avatarId):
        
        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                self.notify.warning('toonOffline: avatarResponse: Attempted to get name of an offline Toon and retrieved non-toon.')
                return

            name = fields['setName'][0]
            friendsList = fields['setFriendsList'][0]
            self.d_toonOffline(avatarId, friendsList, name)
        
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            avatarResponse
        )

    def d_toonOnline(self, avatarId, friendsList, name):
        if not avatarId in self.toonsOnline:
            self.toonsOnline.append(avatarId)

        for friendId in friendsList:
            if friendId in self.toonsOnline:
                self.sendUpdateToAvatarId(friendId, 'toonOnline', [avatarId, name])

    def d_toonOffline(self, avatarId, friendsList, name):
        if avatarId in self.toonsOnline:
            self.toonsOnline.remove(avatarId)

        for friendId in friendsList:
            if friendId in self.toonsOnline:
                self.sendUpdateToAvatarId(friendId, 'toonOffline', [avatarId, name])

    def requestAvatarInfo(self, avId):
        sender = self.air.getAvatarIdFromSender()

        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("requestAvatarInfo: avatarResponse: It's not a toon.")
                return

            name = fields['setName'][0]
            dna = fields['setDNAStrand'][0]
            maxHP = fields['setMaxHealth'][0]
            hp = fields['setHealth'][0]
            zoneId = fields['setLastHood'][0]
            try:
                shardId = fields['setDefaultShard'][0]
            except:
                shardId = 0
            adminToken = fields['setAdminToken'][0]
            isOnline = int(avId in self.toonsOnline)

            self.sendUpdateToAvatarId(sender, 'avatarInfo', [name, dna, maxHP, hp, zoneId, shardId, isOnline, adminToken])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avId,
            avatarResponse
        )

    def askAvatarToBeFriends(self, avId):
        sender = self.air.getAvatarIdFromSender()

        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("requestAvatarInfo: avatarResponse: It's not a toon.")
                return

            name = fields['setName'][0]
            dna = fields['setDNAStrand'][0]

            self.sendUpdateToAvatarId(avId, 'friendRequest', [sender, name, dna])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            avatarResponse
        )

    def iRemovedFriend(self, friendId):
        sender = self.air.getAvatarIdFromSender()

        def removerAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iRemovedFriend: removerAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.remove(friendId)
            dg = dclass.aiFormatUpdate('setFriendsList', sender, sender, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, sender, dclass, {'setFriendsList': [newList]})

        def removeeAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iRemovedFriend: removeeAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.remove(sender)
            dg = dclass.aiFormatUpdate('setFriendsList', friendId, friendId, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, friendId, dclass, {'setFriendsList': [newList]})

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            removerAvatarResponse
        )
        self.air.dbInterface.queryObject(
            self.air.dbId,
            friendId,
            removeeAvatarResponse
        )

        self.sendUpdateToAvatarId(friendId, 'friendLeftYourList', [sender])

    def iAcceptedFriendRequest(self, avatarId):
        sender = self.air.getAvatarIdFromSender()

        def accepterAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iAcceptedFriendRequest: accepterAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.append(avatarId)
            dg = dclass.aiFormatUpdate('setFriendsList', sender, sender, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, sender, dclass, {'setFriendsList': [newList]})

        def requesterAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iAcceptedFriendRequest: requesterAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.append(sender)
            dg = dclass.aiFormatUpdate('setFriendsList', avatarId, avatarId, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, avatarId, dclass, {'setFriendsList': [newList]})

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            accepterAvatarResponse
        )
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            requesterAvatarResponse
        )

        self.sendUpdateToAvatarId(avatarId, 'acceptedFriendRequest', [])

    def iRejectedFriendRequest(self, avatarId):
        self.sendUpdateToAvatarId(avatarId, 'rejectedFriendRequest', [])

    def iCancelledFriendRequest(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'cancelFriendRequest', [sender])

    def requestAvatarStatus(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'someoneWantsYourStatus', [sender])

    def myAvatarStatus(self, avatarId, status):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'avatarStatus', [sender, status])

    def iWantToTeleportToAvatar(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'avatarWantsYourLocation', [sender])

    def myAvatarLocation(self, avatarId, shardId, zoneId):
        sender = self.air.getAvatarIdFromSender()

        def teleportingAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return

            name = fields['setName'][0]
            self.sendUpdateToAvatarId(sender, 'teleportNotify', [name])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            teleportingAvatarResponse
        )
        self.sendUpdateToAvatarId(avatarId, 'avatarLocation', [sender, shardId, zoneId])
