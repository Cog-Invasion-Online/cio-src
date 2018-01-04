"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendsList.py
@author Brian Lach
@date August 04, 2015

"""

from panda3d.core import TextNode, Vec4
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import DirectButton, OnscreenText, DirectFrame, DirectScrolledList, DGG
from direct.fsm import ClassicFSM, State

from src.coginvasion.globals import CIGlobals

textRolloverColor = Vec4(1, 1, 0, 1)
textDownColor = Vec4(0.5, 0.9, 1, 1)

class FriendsList(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory("FriendsList")

    def __init__(self):
        DirectFrame.__init__(self, parent = base.a2dTopRight, pos = (-0.2235, 0.0, -0.457))
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        self['image'] = gui.find('**/FriendsBox_Open')

        self.headingText = OnscreenText(text = "", parent = self, pos = (0.01, 0.2), fg = (0.1, 0.1, 0.4, 1.0), scale = 0.04)

        self.frameForNames = DirectScrolledList(frameSize = (0.0, 0.35, 0, 0.35),
            incButton_geom = (gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            incButton_relief = None,
            incButton_hpr = (0, 0, 180),
            incButton_pos = (0.17, 0, -0.04),
            decButton_geom = (gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            decButton_relief = None,
            decButton_pos = (0.17, 0, 0.395),
            pos = (-0.1625, 0.0, -0.27),
            parent = self,
            numItemsVisible = 9,
            forceHeight = 0.04,
            itemFrame_frameSize = (-0.15, 0.15, 0, -0.35),
            itemFrame_pos = (0, 0, 0.3275),
            itemFrame_relief = None,
            relief = None)
        
        self.fwdBtn = CIGlobals.makeDirectionalBtn(1, self, (0.17, 0.0, -0.38), command = self.doState)
        self.backBtn = CIGlobals.makeDirectionalBtn(0, self, (-0.15, 0.0, -0.38), command = self.doState)

        self.closeBtn = DirectButton(geom = CIGlobals.getCancelBtnGeom(), relief = None,
            parent = self, command = self.exitClicked)
        self.closeBtn.setPos(0.015, 0.0, -0.375)

        gui.removeNode()
        del gui

        self.hide()

        self.friends = {}
        self.onlineFriends = {}

        self.fsm = ClassicFSM.ClassicFSM('FriendsList', [State.State('off', self.enterOff, self.exitOff),
            State.State('onlineFriendsList', self.enterOnlineFriendsList, self.exitOnlineFriendsList),
            State.State('allFriendsList', self.enterAllFriendsList, self.exitAllFriendsList)],
            'off', 'off')
        self.fsm.enterInitialState()
        self.accept('gotFriendsList', self.handleFriendsList)

    def destroy(self):
        self.ignore('gotFriendsList')
        self.fsm.requestFinalState()
        del self.fsm
        self.headingText.destroy()
        del self.headingText
        self.frameForNames.destroy()
        del self.frameForNames
        self.fwdBtn.destroy()
        del self.fwdBtn
        self.backBtn.destroy()
        del self.backBtn
        self.closeBtn.destroy()
        del self.closeBtn
        del self.friends
        del self.onlineFriends
        DirectFrame.destroy(self)

    def doState(self, state):
        self.fsm.request(state)

    def exitClicked(self):
        self.fsm.request('off')
        base.localAvatar.showFriendButton()

    def setButtons(self, fwd = None, back = None):
        if fwd:
            self.fwdBtn['extraArgs'] = [fwd]
            self.fwdBtn['state'] = DGG.NORMAL
        else:
            self.fwdBtn['extraArgs'] = []
            self.fwdBtn['state'] = DGG.DISABLED

        if back:
            self.backBtn['extraArgs'] = [back]
            self.backBtn['state'] = DGG.NORMAL
        else:
            self.backBtn['extraArgs'] = []
            self.backBtn['state'] = DGG.DISABLED


    def handleFriendsList(self, friendIdArray, nameArray, flags, adminTokens):
        self.friends = {}
        self.onlineFriends = {}
        for i in xrange(len(friendIdArray)):
            avatarId = friendIdArray[i]
            name = nameArray[i]
            adminToken = adminTokens[i]
            self.friends[avatarId] = [name, adminToken]
            if flags[i] == 1:
                # This friend is online
                self.onlineFriends[avatarId] = [name, adminToken]

    def enterOff(self):
        self.hide()

    def exitOff(self):
        self.show()

    def addFriend(self, name, avatarId, adminToken):
        text_fg = CIGlobals.TextColorByAdminToken[adminToken]
        self.frameForNames.addItem(
            DirectButton(
                text = name,
                extraArgs = [avatarId],
                command = self.friendClicked,
                scale = 0.035,
                relief = None,
                text_fg = text_fg,
                text1_bg = textDownColor,
                text2_bg = textRolloverColor,
                text_align = TextNode.ALeft
            )
        )

    def friendClicked(self, avatarId):
        base.localAvatar.panel.makePanel(avatarId)

    def maybeShowList(self):
        if self.isHidden() and self.fsm.getCurrentState().getName() != 'off':
            base.localAvatar.hideFriendButton()
            self.show()

    def resetAll(self):
        self.headingText.setText("")
        self.frameForNames.removeAndDestroyAllItems()
        self.setButtons(None, None)

    def sortListItems(self):
        self.frameForNames['items'].sort(key = lambda x: x['text'])
        self.frameForNames.refresh()

    def enterAllFriendsList(self):
        self.headingText.setText("ALL\nFRIENDS")
        for friendId, data in self.friends.items():
            name = data[0]
            adminToken = data[1]
            self.addFriend(name, friendId, adminToken)
        self.sortListItems()
        self.setButtons(None, 'onlineFriendsList')

    def exitAllFriendsList(self):
        self.resetAll()

    def enterOnlineFriendsList(self):
        self.headingText.setText("ONLINE\nFRIENDS")
        for friendId, data in self.onlineFriends.items():
            name = data[0]
            adminToken = data[1]
            self.addFriend(name, friendId, adminToken)
        self.sortListItems()
        self.setButtons('allFriendsList', None)

    def exitOnlineFriendsList(self):
        self.resetAll()
