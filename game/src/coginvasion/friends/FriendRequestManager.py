"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendRequestManager.py
@author Brian Lach
@date August 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from direct.interval.IntervalGlobal import LerpScaleInterval, Sequence, Func

from src.coginvasion.gui.Dialog import GlobalDialog
from src.coginvasion.toon import ToonGlobals
from src.coginvasion.globals import ChatGlobals

class FriendRequestManager(DirectObject):
    notify = directNotify.newCategory("FriendRequestManager")

    MessageFriendRequest = "Do you want to befriend {avatarName}?"

    def __init__(self):
        DirectObject.__init__(self)
        self.friendRequests = {}
        self.popUpSfx = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')
        self.popUpSfx.setVolume(2.25)
        self.requestIval = None

    def cleanup(self):
        self.stopWatching()
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

    def stopWatching(self):
        self.ignore('newFriendRequest')
        self.ignore('friendRequestCancelled')

    def __newFriendRequest(self, requester, name, dna):
        head = ToonGlobals.generateGuiHead(dna)
        size = (0.55 * 1.5, 0.55 * 1.5, 0.35 * 1.5)
        
        request = GlobalDialog(message = ChatGlobals.mentionAvatar(self.MessageFriendRequest, name), style = 1,
            text_wordwrap = 12, doneEvent = 'friendRequestDone-%d' % requester, extraArgs = [requester],
            text_scale = 0.065, pos = (-0.85, 0, -0.275), 
            geom = head, geom_scale = (0.125*1.25, 0.125*1.25, 0.1625*1.25), 
            scale = size, image_scale = size, 
        text_pos = (0.15, 0.075, 0), relief = None)
        request.reparentTo(base.a2dTopRight)
        
        text = request.component('text0') 
        text.setScale(0.065, 0.1)
        
        for cmpt in request.components():
            if 'Button' in cmpt:
                btn = request.component(cmpt)
                btn.setScale(btn, btn.getSx(), btn.getSy() + 0.1, btn.getSz() + 0.2)
        
        self.friendRequests[requester] = request
        self.acceptOnce('friendRequestDone-%d' % requester, self.handleFriendRequestChoice)
        
        self.requestIval = Sequence(
            Func(self.popUpSfx.play),
            LerpScaleInterval(request, 0.35, size, startScale = 0.01, blendType = 'easeOut')
        )
        
        self.requestIval.start()

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
        
        if self.requestIval:
            self.requestIval.pause()
            self.requestIval = None
