"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendRequestManager.py
@author Brian Lach
@date August 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from src.coginvasion.gui.Dialog import GlobalDialog

class FriendRequestManager(DirectObject):
    notify = directNotify.newCategory("FriendRequestManager")

    MessageFriendRequest = "%s would like to be your friend. Do you want to be friends with %s?"

    def __init__(self):
        DirectObject.__init__(self)
        self.friendRequests = {}

    def cleanup(self):
        self.friendRequests = None

    def iAcceptedRequest(self, requestId):
        self.cleanupRequest(requestId)
        base.cr.friendsManager.d_iAcceptedFriendRequest(requestId)

    def iRejectedRequest(self, requestId):
        self.cleanupRequest(requestId)
        base.cr.friendsManager.d_iRejectedFriendRequest(requestId)

    def watch(self):
        self.accept('newFriendRequest', self.__newFriendRequest)
        self.accept('friendRequestCancelled', self.cleanupRequest)

    def __newFriendRequest(self, requester, name, dna):
        request = GlobalDialog(message = self.MessageFriendRequest % (name, name), style = 1,
            text_wordwrap = 12, doneEvent = 'friendRequestDone-%d' % requester, extraArgs = [requester])
        self.friendRequests[requester] = request
        self.acceptOnce('friendRequestDone-%d' % requester, self.handleFriendRequestChoice)

    def handleFriendRequestChoice(self, requester):
        value = self.friendRequests[requester].getValue()
        if value:
            self.iAcceptedRequest(requester)
        else:
            self.iRejectedRequest(requester)

    def cleanupRequest(self, requester):
        request = self.friendRequests.get(requester)
        if request:
            request.cleanup()
            del self.friendRequests[requester]
