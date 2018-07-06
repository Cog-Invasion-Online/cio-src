"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ClientServicesManagerUD.py
@author Brian Lach
@date December 3, 2014

"""

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.MsgTypes import *
from src.coginvasion.distributed.CogInvasionErrorCodes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.gags import GagGlobals
from src.coginvasion.distributed import AdminCommands
from src.coginvasion.hood import ZoneUtil
from panda3d.core import NetDatagram
import anydbm
import os

class CreateToonProcess:
    notify = directNotify.newCategory("CreateToonProcess")

    def __init__(self, choice, accountId, sender, csm):
        self.choice = choice
        self.accountId = accountId
        self.sender = sender
        self.csm = csm
        self.air = self.csm.air
        self.accFields = None
        self.newToonId = 0
        self.avList = None
        self.csm.queryAccount(accountId, self.accountResp)

    def cleanup(self):
        del self.choice
        del self.accountId
        del self.sender
        del self.air
        del self.accFields
        del self.newToonId
        del self.avList
        del self.csm

    def avatarCreateDone(self):
        self.notify.info("Avatar creation done.")
        self.csm.sendUpdateToAccountId(self.accountId, 'toonCreated', [self.newToonId])
        self.cleanup()

    def accountResp(self, dclass, fields):
        if dclass != self.air.dclassesByName['AccountUD']:
            self.cleanup()
            return
        if fields['AVATAR_IDS'][self.choice[1]] != 0:
            self.notify.warning("Client tried to create a toon on an occupied slot!")
            self.air.eject(self.sender, EC_OCCUPIED_SLOT_CREATION_ATTEMPT, "Client tried to create a toon on an occupied slot!")
            self.cleanup()
            return

        self.accFields = fields

        # We can create the new toon now!
        self.createToon()

    def createToon(self):
        fields = {"ACCOUNT": self.accountId,
                "setDNAStrand": (str(self.choice[0]),),
                "setName": (str(self.choice[2]),),
                "setHealth": (100,),
                "setMaxHealth": (100,),
                "setMoney": (5000,),
                "setBackpackAmmo": (GagGlobals.getDefaultBackpack().toNetString(),),
                "setLoadout": (GagGlobals.InitLoadout,), # Start with cupcake and squirting flower.
                "setTrackExperience": (GagGlobals.trackExperienceToNetString(GagGlobals.DefaultTrackExperiences),),
                "setAdminToken": (AdminCommands.NoToken,),
                "setQuests": ("",),
                "setQuestHistory": ([],),
                "setTier": (13,),
                "setFriendsList": ([],),
                "setTutorialCompleted": (1,),#self.choice[3],),
                "setHoodsDiscovered": ([ZoneUtil.ToontownCentralId],),
                "setTeleportAccess": ([],),
                "setLastHood": (ZoneUtil.ToontownCentralId,),
                "setDefaultShard": (0,)}
        self.notify.info("Creating new toon!")
        self.avList = self.accFields["AVATAR_IDS"]
        self.avList = self.avList[:6]
        self.avList += [0] * (6 - len(self.avList))

        self.air.dbInterface.createObject(
                    self.air.dbId,
                    self.air.dclassesByName['DistributedPlayerToonUD'],
                    fields,
                    self.createDone)

    def storeToonDone(self, fields):
        if fields:
            self.cleanup()
            return
        self.avatarCreateDone()

    def storeToonID(self):
        self.notify.info("STORING ID!")
        self.avList[self.choice[1]] = self.newToonId
        self.air.dbInterface.updateObject(
                self.air.dbId,
                self.accountId,
                self.air.dclassesByName['AccountUD'],
                {"AVATAR_IDS": self.avList},
                {"AVATAR_IDS": self.accFields["AVATAR_IDS"]},
                self.storeToonDone)

    def createDone(self, newId):
        if not newId:
            self.notify.warning("Failed to create a new toon object!")
            self.cleanup()
            return
        self.notify.info("create finished, storing toon id...")
        self.newToonId = newId
        self.storeToonID()

class ClientServicesManagerUD(DistributedObjectGlobalUD):

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        filename = base.config.GetString('account-bridge-filename',
                    'astron/databases/account-bridge.db')
        self.dbm = anydbm.open(filename, 'c')
        self.private__dg = PyDatagram()
        return

    def giveClientOwnershipOfObject(self, context, accId, doId, dclassNum):
        print "CSM: giveClientOwnershipOfObject:", context, accId, doId
        sender = self.air.getMsgSender()

        # Activate the object on the db stateserver.
        self.air.sendActivate(doId, 0, 0)

        # Grant the client ownership of the object.
        dg = PyDatagram()
        dg.addServerHeader(doId, self.air.ourChannel, STATESERVER_OBJECT_SET_OWNER)
        dg.addChannel(accId << 32 | doId)
        self.air.send(dg)

        self.sendUpdateToChannel(sender, 'clientObjectOwnershipGranted', [context, accId, doId])

    def unsandboxClient(self, sender):
        dg = PyDatagram()
        dg.addServerHeader(sender, self.air.ourChannel, CLIENTAGENT_SET_STATE)
        dg.addUint16(2) # 2 = established
        self.air.send(dg)

    def createAccount(self, username, accountId, sender):
        fields = {"ACCOUNT_ID": str(username),
                "AVATAR_IDS": [0, 0, 0, 0, 0, 0],
                "BANNED": 0}
        self.notify.info("Fields %s" % fields)

        def storeAccountID(accountId):
            self.dbm[str(username)] = str(accountId)
            self.notify.info("storing id...")
            if getattr(self.dbm, 'sync', None):
                self.dbm.sync()
                self.notify.info("synced db file.")
            else:
                self.notify.warning("failed to store an account id in the database.")
                return
            self.setAccount(sender, accountId)

        def handleCreate(accountId):
            if not accountId:
                self.notify.warning("failed to create an account object in the database.")
                return
            self.notify.info("created account, storing id...")
            storeAccountID(accountId)

        self.air.dbInterface.createObject(
                    self.air.dbId,
                    self.air.dclassesByName['AccountUD'],
                    fields,
                    handleCreate)

    def setAccount(self, sender, accountId):
        # Check if this account is already logged in.
        print "setAccount: accountId = %s" % accountId
        dg = PyDatagram()
        dg.addServerHeader(self.GetAccountConnectionChannel(accountId),
                    self.air.ourChannel,
                    CLIENTAGENT_EJECT)
        dg.addUint16(EC_MULTIPLE_LOGINS)
        dg.addString('This account is already logged in.')
        self.air.send(dg)

        # Add this connection to the account channel.
        dg = PyDatagram()
        dg.addServerHeader(sender, self.air.ourChannel,
                    CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.GetAccountConnectionChannel(accountId))
        self.air.send(dg)

        # Set the sender channel to represent their account affiliation.
        dg = PyDatagram()
        dg.addServerHeader(sender, self.air.ourChannel,
                    CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(accountId << 32)
        self.air.send(dg)

        # Unsandbox the client.
        self.unsandboxClient(sender)
        self.d_loginAccepted(sender)
        self.notify.info("Successfully created a new account object.")

    def setAvatar(self, fields, avId, sender):
        accId = self.GetAccountConnectionChannel(sender)

        # Give a POST_REMOVE to unload the avatar just
        # in case we lose connection while working.
        dgc = PyDatagram()
        dgc.addServerHeader(avId, accId,
                STATESERVER_OBJECT_DELETE_RAM)
        dgc.addUint32(avId)
        dg = PyDatagram()
        dg.addServerHeader(accId,
                self.air.ourChannel,
                CLIENTAGENT_ADD_POST_REMOVE)
        dg.addString(dgc.getMessage())
        self.air.send(dg)

        # Activate the avatar on the db stateserver.
        self.air.sendActivate(avId, 0, 0, self.air.dclassesByName['DistributedPlayerToonUD'])

        # Add the connection to the avatar channel.
        dg = PyDatagram()
        dg.addServerHeader(accId, self.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.GetPuppetConnectionChannel(avId))
        self.air.send(dg)

        # Set the sender channel to represent their account affiliation.
        dg = PyDatagram()
        dg.addServerHeader(accId, self.air.ourChannel,
                    CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(sender << 32 | avId)
        self.air.send(dg)

        # Grant the client ownership of the avatar.
        dg = PyDatagram()
        dg.addServerHeader(avId, self.air.ourChannel, STATESERVER_OBJECT_SET_OWNER)
        dg.addChannel(sender << 32 | avId)
        self.air.send(dg)

        # The avatar should stay around for the entire client session.
        self.air.clientAddSessionObject(accId, avId)

        # OLD WAY: Tell the friends manager a toon has gone online.
        # self.__handleToonOnline(avId)
        
        # NEW WAY: Tell the FriendsManagerUD that a toon is online.
        # Let's use the netMessenger.
        self.air.netMessenger.send('avatarOnline', [avId])
        
        # Let's prepare the avatarOffline message if the avatar disconnects unexpectedly.
        cleanupDatagram = self.air.netMessenger.prepare('avatarOffline', [avId])
        dg = PyDatagram()
        dg.addServerHeader(accId, self.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        dg.addString(cleanupDatagram.getMessage())
        self.air.send(dg)

    def __handleToonOnline(self, avId):

        print "toon online " + str(avId)

        def toonResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedPlayerToonUD']:
                return

            name = fields['setName'][0]
            fl = fields['setFriendsList'][0]

            # Now tell them.
            self.air.friendsManager.d_toonOnline(avId, fl, name)

        # We need to query this toon to get their name and friends list.
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avId,
            toonResponse
        )

    def unloadAvatar(self, target, doId):
        channel = self.GetAccountConnectionChannel(target)

        print "unloadAvatar"

        # Allow the avatar to be deleted now.
        self.air.clientRemoveSessionObject(target, doId)

        # Clear the postremove
        dg = PyDatagram()
        dg.addServerHeader(
            channel,
            self.air.ourChannel,
            CLIENTAGENT_CLEAR_POST_REMOVES
        )
        self.air.send(dg)

        # Remove avatar channel
        dg = PyDatagram()
        dg.addServerHeader(
            channel,
            self.air.ourChannel,
            CLIENTAGENT_CLOSE_CHANNEL)
        dg.addChannel(self.GetPuppetConnectionChannel(doId))
        self.air.send(dg)

        # Reset sender channel
        dg = PyDatagram()
        dg.addServerHeader(
            channel,
            self.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID
        )
        dg.addChannel(doId<<32)
        self.air.send(dg)

        # Delete avatar object
        dg = PyDatagram()
        dg.addServerHeader(
            doId,
            channel,
            STATESERVER_OBJECT_DELETE_RAM
        )
        dg.addUint32(doId)
        self.air.send(dg)

        # Tell the friends manager a toon has gone offline.
        #self.__handleToonOffline(doId)

    def __handleToonOffline(self, avId):

        print "toon offline " + str(avId)

        def toonResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedPlayerToonUD']:
                return

            name = fields['setName'][0]
            fl = fields['setFriendsList'][0]

            # Now tell them.
            self.air.friendsManager.d_toonOffline(avId, fl, name)

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avId,
            toonResponse
        )

    def requestLogin(self, token, username):
        username = username.lower()
        sender = self.air.getMsgSender()
        print sender
        self.air.getDatagram(self.private__dg)
        ip = str(NetDatagram(self.private__dg).getAddress())
        if sender >> 32:
            self.air.eject(sender, EC_MULTIPLE_LOGINS, 'You are already logged in.')
            return

        if not self.air.isValidToken(token, ip):
            self.air.eject(sender, EC_BAD_TOKEN, 'I have rejected your token.')
            return

        accountId = int(self.dbm.get(str(username), 0))

        if str(username) not in self.dbm:
            self.createAccount(username, accountId, sender)
            self.notify.info("Creating a new account...")
        else:
            self.setAccount(sender, accountId)
            self.notify.info("Account already exists!")

    def d_loginAccepted(self, sender):
        self.sendUpdateToChannel(sender, 'loginAccepted', [])

    def requestAvatars(self):
        accountId = self.air.getAccountIdFromSender()
        sender = self.air.getMsgSender()
        if not accountId:
            self.air.eject(sender, EC_INVALID_ACCOUNT, 'You do not have a valid account.')
            return
        self.queryAccount(accountId)

    def queryAccount(self, accountId, callback = None):

        def accountResp(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return
            self.queryToons(fields, accountId)

        if callback:
            self.air.dbInterface.queryObject(
                self.air.dbId, accountId,
                callback)
        else:
            self.air.dbInterface.queryObject(
                    self.air.dbId, accountId,
                    accountResp)

    def queryToons(self, accFields, accId):
        collectedAvatars = []
        pendingAvatars = set()
        avId = 0

        for avId in accFields['AVATAR_IDS']:
            if avId != 0:
                pendingAvatars.add(avId)

                def toonResponse(dclass, fields, avId=avId):
                    if dclass != self.air.dclassesByName['DistributedPlayerToonUD']:
                        return
                    if fields.get('ACCOUNT', None) is None:
                        print "No field ACCOUNT in this toon, I'll add it for you."
                        self.air.dbInterface.updateObject(
                            self.air.dbId,
                            avId,
                            self.air.dclassesByName['DistributedPlayerToonUD'],
                            {"ACCOUNT": accId}
                        )
                    collectedAvatars.append([avId, fields['setDNAStrand'][0],
                            fields['setName'][0],
                            accFields['AVATAR_IDS'].index(avId),
                            fields['setLastHood'][0]])
                    pendingAvatars.remove(avId)
                    if not pendingAvatars:
                        self.sendToons(collectedAvatars, accId)

                self.air.dbInterface.queryObject(
                        self.air.dbId, avId,
                        toonResponse)

        if not pendingAvatars:
            self.sendToons(collectedAvatars, accId)

        sender = self.GetAccountConnectionChannel(accId)

        def checkAccountBanStatus(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return
            if fields.get("BANNED") == 1:
                self.air.eject(sender, 0, 'You are banned.')
            elif fields.get("BANNED", None) is None:
                self.air.dbInterface.updateObject(
                    self.air.dbId,
                    accId,
                    self.air.dclassesByName['AccountUD'],
                    {"BANNED": 0})

        self.queryAccount(accId, checkAccountBanStatus)

    def sendToons(self, avs, accId):
        print avs
        self.sendUpdateToAccountId(accId, 'setAvatars', [avs])



    def deleteToon(self, accountId, avId, accFields, callback):
        self.notify.info("Deleting toon with dbId %s on account %s" % (avId, accountId))

        # First, remove the avId from the account field AVATAR_IDS and change it to 0.
        avList = accFields["AVATAR_IDS"]
        avList = avList[:6]
        avList += [0] * (6 - len(avList))
        avPos = avList.index(avId)
        avList[avPos] = 0

        def deleteToonDone(fields):
            if fields:
                self.notify.warning("Failed to delete toon on the account database!")
                return
            self.notify.info("account fields update finished, deleting toon database file...")
            # Finally, delete the toon database file.
            os.remove("astron/databases/astrondb/" + str(avId) + ".yaml")
            callback()

        # Then, update the account object fields on the database.
        self.air.dbInterface.updateObject(
                    self.air.dbId,
                    accountId,
                    self.air.dclassesByName['AccountUD'],
                    {"AVATAR_IDS": avList},
                    {"AVATAR_IDS": accFields["AVATAR_IDS"]},
                    deleteToonDone)

    def requestDeleteAvatar(self, avId):
        accountId = self.air.getAccountIdFromSender()
        sender = self.air.getMsgSender()

        def avatarDeleteDone():
            self.notify.info("DONE DELETING TOON!")
            self.sendUpdateToAccountId(accountId, 'toonDeleted', [])

        def accountResp(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return
            if not avId in fields["AVATAR_IDS"]:
                self.notify.warning("Client tried to delete a non-existent avatar!")
                self.air.eject(sender, EC_NON_EXISTENT_AV, "Client tried to delete a non-existent avatar!")
                return

            # We can delete the toon now!
            self.deleteToon(accountId, avId, fields, avatarDeleteDone)

        self.queryAccount(accountId, accountResp)

    def requestNewAvatar(self, dna, slot, name, skipTutorial = 1):
        choice = [dna, slot, name, skipTutorial]
        accountId = self.air.getAccountIdFromSender()
        sender = self.air.getMsgSender()

        CreateToonProcess(choice, accountId, sender, self)

    def requestSetAvatar(self, avId):
        currentAvId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        sender = self.air.getMsgSender()

        if not avId:
            self.unloadAvatar(sender, currentAvId)

        def __handleAvatar(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedPlayerToonUD']:
                return
            self.setAvatar(fields, avId, accountId)

        def accountResp(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return
            if not avId in fields['AVATAR_IDS']:
                self.notify.warning("Client tried to play an avatar that doesn't belong to them or doesn't exist!")
                self.air.eject(sender, EC_NON_EXISTENT_AV, "Client tried to play an avatar that doesn't belong to them or doesn't exist!")
                return

            self.air.dbInterface.queryObject(
                                self.air.dbId,
                                avId,
                                __handleAvatar)

        self.queryAccount(accountId, accountResp)
