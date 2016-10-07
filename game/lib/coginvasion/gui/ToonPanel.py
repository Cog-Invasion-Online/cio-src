# Filename: ToonPanel.py
# Created by:  blach (03Aug15)

from pandac.PandaModules import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectButton, OnscreenText, DGG
from direct.fsm import ClassicFSM, State

from lib.coginvasion.gui.LaffOMeter import LaffOMeter
from lib.coginvasion.toon import ToonHead, ToonDNA
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil

class ToonPanel(DirectFrame):
    notify = directNotify.newCategory("ToonPanel")

    animal2HeadData = {'dog': (0.125, 0.04), 'duck': (0.1, 0.025), 'cat': (0.115, 0.04),
        'rabbit': (0.115, 0.04), 'horse': (0.115, 0.06), 'monkey': (0.115, 0.06), 'pig': (0.115, 0.07),
        'mouse': (0.09, 0.02), 'bear': (0.125, 0.05)}

    State2Text = {'status': ('Seeing if %s is available...', '%s is busy right now; try again later.'),
        'teleport': ('Trying to go to %s...', 'Could not go to %s.'),
        'friend': ('Asking %s to be your friend...', '%s said no, thank you.', 'You are now friends with %s!'),
        'remove': ('Are you sure you want to remove %s from your friends list?', '%s left your friends list.')}

    def __init__(self):
        DirectFrame.__init__(self, scale = 1.2)
        self['image'] = DGG.getDefaultDialogGeom()
        self['image_hpr'] = (0, 0, -90)
        self['image_scale'] = (0.67, 0.9, 0.325)
        self['image_color'] = (1, 1, 0.75, 1)
        self['image_pos'] = (0, 0, -0.09)
        self['relief'] = None
        self.reparentTo(base.a2dTopRight)
        self.setPos(-0.235, 0.0, -0.325)
        self.hide()
        self.head = None
        self.laffMeter = None
        self.exitButton = None
        self.friendButton = None
        self.teleportButton = None
        self.whisperButton = None
        self.nameText = None
        self.actionFrame = None
        self.actionFrameText = None
        self.actionFrameButton = None
        self.actionFrameButton2 = None
        self.avatarInfo = None
        self.action = None
        self.locationText = None
        self.shardText = None
        self.detailsExitBtn = None

        self.fsm = ClassicFSM.ClassicFSM('ToonPanel', [State.State('off', self.enterOff, self.exitOff),
            State.State('waitOnAvatarInfoResponse', self.enterWaitOnAvatarInfoResponse,
                self.exitWaitOnAvatarInfoResponse, ['panel']),
            State.State('panel', self.enterPanel, self.exitPanel, ['off'])],
            'off', 'off')
        self.fsm.enterInitialState()

        self.actionFSM = ClassicFSM.ClassicFSM('ToonPanelActionFSM', [State.State('off', self.enterOff, self.exitOff),
            State.State('waitOnAvatarStatusResponse', self.enterWaitOnAvatarStatusResponse,
                self.exitWaitOnAvatarStatusResponse, ['waitOnAvatarTeleportResponse', 'waitOnAvatarFriendListResponse',
                'avatarBusy', 'off']),
            State.State('avatarBusy', self.enterAvatarBusy, self.exitAvatarBusy, ['off']),
            State.State('waitOnAvatarTeleportResponse', self.enterWaitOnAvatarTeleportResponse,
                self.exitWaitOnAvatarTeleportResponse, ['unableToTP']),
            State.State('unableToTP', self.enterUnableToTP, self.exitUnableToTP, ['off']),
            State.State('waitOnAvatarFriendListResponse', self.enterWaitOnAvatarFriendListResponse,
                self.exitWaitOnAvatarFriendListResponse, ['fRequestA', 'fRequestR']),
            State.State('fRequestA', self.enterFriendRequestAccepted, self.exitFriendRequestAccepted, ['off']),
            State.State('fRequestR', self.enterFriendRequestRejected, self.exitFriendRequestRejected, ['off']),
            State.State('removeFriendConfirm', self.enterRemoveFriendConfirm, self.exitRemoveFriendConfirm, ['off', 'removedFriend']),
            State.State('removedFriend', self.enterRemovedFriend, self.exitRemovedFriend, ['off'])],
            'off', 'off')
        self.actionFSM.enterInitialState()

    def makeMoreDetailsPanel(self):
        self.actionFSM.request('off')
        self.removeMoreDetailsPanel()
        self.removeActionPanel()
        self.makeActionPanel()
        zoneId = self.avatarInfo[5]
        shardId = self.avatarInfo[6]
        isOnline = self.avatarInfo[7]
        shardName = 'Unknown District'
        hoodName = ZoneUtil.getHoodId(zoneId, 1)
        for district in base.cr.activeDistricts.values():
            if district.doId == shardId:
                shardName = district.getDistrictName()
                break
        if not isOnline:
            hoodName = 'Offline'
            shardName = 'Offline'
        self.locationText = OnscreenText('Location: {0}'.format(hoodName), parent = self.actionFrame, pos = (-0.3, 0.05, 0), align = TextNode.ALeft, scale = 0.04)
        self.shardText = OnscreenText('District: {0}'.format(shardName), parent = self.actionFrame, pos = (-0.3, 0.0, 0), align = TextNode.ALeft, scale = 0.04)
        self.detailsExitBtn = DirectButton(geom = CIGlobals.getCancelBtnGeom(), parent = self.actionFrame,
            relief = None, scale = 0.8, pos = (-0.3, 0.0, -0.175), command = self.removeMoreDetailsPanel)

    def removeMoreDetailsPanel(self):
        if self.locationText:
            self.locationText.destroy()
            self.locationText = None
        if self.shardText:
            self.shardText.destroy()
            self.shardText = None
        if self.detailsExitBtn:
            self.detailsExitBtn.destroy()
            self.detailsExitBtn = None
        self.removeActionPanel()

    def maybeUpdateFriendButton(self):
        if self.friendButton:
            if self.avatarInfo:
                if not self.avatarInfo[0] in base.localAvatar.friends:
                    self.friendButton['text'] = 'Add Friend'
                    self.friendButton['extraArgs'] = ['waitOnAvatarFriendListResponse']
                else:
                    self.friendButton['text'] = 'Remove Friend'
                    self.friendButton['extraArgs'] = ['removeFriendConfirm']

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterUnableToTP(self):
        pass

    def exitUnableToTP(self):
        pass

    def enterWaitOnAvatarTeleportResponse(self):
        self.setActionText(self.State2Text['teleport'][0] % self.getAvatarName())
        self.makeButtons('Cancel')
        self.acceptOnce('gotAvatarTeleportResponse', self.handleTeleportResponse)
        base.cr.friendsManager.d_iWantToTeleportToAvatar(self.avatarInfo[0])

    def handleTeleportResponse(self, avatarId, shardId, zoneId):
        if self.avatarInfo[0] == avatarId:
            requestStatus = {}
            whereName = ZoneUtil.getWhereName(zoneId)
            loaderName = ZoneUtil.getLoaderName(zoneId)
            requestStatus['zoneId'] = zoneId
            if base.localAvatar.parentId == shardId:
                requestStatus['shardId'] = None
            else:
                requestStatus['shardId'] = shardId
            requestStatus['hoodId'] = ZoneUtil.getHoodId(zoneId, 1)
            requestStatus['where'] = whereName
            requestStatus['loader'] = loaderName
            requestStatus['how'] = 'teleportIn'
            requestStatus['avId'] = avatarId
            base.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])
            self.cleanup()

    def exitWaitOnAvatarTeleportResponse(self):
        self.ignore('gotAvatarTeleportResponse')
        self.clearActionText()
        self.clearActionButtons()

    def setActionText(self, text):
        self.actionFrameText.setText(text)

    def clearActionText(self):
        self.actionFrameText.setText("")

    def makeButtons(self, button1, button2 = None):
        button2GeomFunc = {'Cancel': CIGlobals.getCancelBtnGeom, 'No': CIGlobals.getCancelBtnGeom,
            'Okay': CIGlobals.getOkayBtnGeom, 'Yes': CIGlobals.getOkayBtnGeom}
        if button1 and not button2:
            button1Pos = (0, 0, -0.1)
        elif button1 and button2:
            button1Pos = (-0.1, 0, -0.1)
        button2Pos = (0.1, 0, -0.1)
        if button1:
            self.actionFrameButton = DirectButton(text = button1, geom = button2GeomFunc[button1](),
                parent = self.actionFrame, pos = button1Pos, text_scale = 0.045, text_pos = (0, -0.08),
                command = self.actionButtonPressed, extraArgs = [1], relief = None, geom_scale = 0.75)
        if button2:
            self.actionFrameButton2 = DirectButton(text = button2, geom = button2GeomFunc[button2](),
                parent = self.actionFrame, pos = button2Pos, text_scale = 0.045, text_pos = (0, -0.08),
                command = self.actionButtonPressed, extraArgs = [2], relief = None, geom_scale = 0.75)

    def actionButtonPressed(self, buttonNum):
        currentState = self.actionFSM.getCurrentState().getName()
        if buttonNum == 1:
            if currentState in ['waitOnAvatarStatusResponse', 'waitOnAvatarTeleportResponse',
            'waitOnAvatarFriendListResponse', 'avatarBusy', 'unableToTP', 'fRequestA', 'fRequestR',
            'removeFriendConfirm', 'removedFriend']:
                if currentState == 'waitOnAvatarFriendListResponse':
                    base.cr.friendsManager.d_iCancelledFriendRequest(self.avatarInfo[0])
                elif currentState == 'removeFriendConfirm':
                    self.actionFSM.request('removedFriend')
                    return
                self.actionFSM.request('off')
                self.removeActionPanel()
                self.action = None
        elif buttonNum == 2:
            self.actionFSM.request('off')
            self.removeActionPanel()
            self.action = None

    def clearActionButtons(self):
        if self.actionFrameButton2:
            self.actionFrameButton2.destroy()
            self.actionFrameButton2 = None
        if self.actionFrameButton:
            self.actionFrameButton.destroy()
            self.actionFrameButton = None

    def enterAvatarBusy(self):
        self.setActionText(self.State2Text['status'][1] % self.getAvatarName())
        self.makeButtons('Okay')

    def exitAvatarBusy(self):
        self.clearActionText()
        self.clearActionButtons()

    def getAvatarName(self):
        if self.avatarInfo:
            return self.avatarInfo[1]

    def enterWaitOnAvatarStatusResponse(self):
        self.acceptOnce('gotAvatarStatus', self.handleAvatarStatusResponse)
        base.cr.friendsManager.d_requestAvatarStatus(self.avatarInfo[0])
        self.setActionText(self.State2Text['status'][0] % self.getAvatarName())
        self.makeButtons('Cancel')

    def handleAvatarStatusResponse(self, avatarId, status):
        if avatarId == self.avatarInfo[0]:

            # Busy
            if status == 1:
                self.actionFSM.request('avatarBusy')

            # Not busy
            else:
                self.actionFSM.request(self.action)
        else:
            self.acceptOnce('gotAvatarStatus', self.handleAvatarStatusResponse)

    def exitWaitOnAvatarStatusResponse(self):
        self.ignore('gotAvatarStatus')
        self.clearActionText()
        self.clearActionButtons()

    def enterWaitOnAvatarFriendListResponse(self):
        self.acceptOnce('friendRequestAccepted', self.handleFriendRequestAccepted)
        self.acceptOnce('friendRequestRejected', self.handleFriendRequestRejected)
        base.cr.friendsManager.d_askAvatarToBeFriends(self.avatarInfo[0])
        self.setActionText(self.State2Text['friend'][0] % self.getAvatarName())
        self.makeButtons('Cancel')

    def handleFriendRequestAccepted(self):
        self.actionFSM.request('fRequestA')

    def handleFriendRequestRejected(self):
        self.actionFSM.request('fRequestR')

    def exitWaitOnAvatarFriendListResponse(self):
        self.ignore('friendRequestAccepted')
        self.ignore('friendRequestRejected')
        self.clearActionText()
        self.clearActionButtons()

    def enterFriendRequestAccepted(self):
        self.setActionText(self.State2Text['friend'][2] % self.getAvatarName())
        self.makeButtons('Okay')

    def exitFriendRequestAccepted(self):
        self.clearActionText()
        self.clearActionButtons()

    def enterFriendRequestRejected(self):
        self.setActionText(self.State2Text['friend'][1] % self.getAvatarName())
        self.makeButtons('Okay')

    def exitFriendRequestRejected(self):
        self.clearActionText()
        self.clearActionButtons()

    def enterRemoveFriendConfirm(self):
        self.setActionText(self.State2Text['remove'][0] % self.getAvatarName())
        self.makeButtons('Yes', 'No')

    def exitRemoveFriendConfirm(self):
        self.clearActionText()
        self.clearActionButtons()

    def enterRemovedFriend(self):
        base.cr.friendsManager.d_iRemovedFriend(self.avatarInfo[0])
        self.setActionText(self.State2Text['remove'][1] % self.getAvatarName())
        self.makeButtons('Okay')

    def exitRemovedFriend(self):
        self.clearActionText()
        self.clearActionButtons()

    def makeActionPanel(self):
        self.actionFrame = DirectFrame(image = DGG.getDefaultDialogGeom(), image_scale = (0.7, 0.5, 0.45),
            image_color = (1, 1, 0.75, 1), relief = None)
        self.actionFrame.reparentTo(base.a2dTopRight)
        self.actionFrame.setPos(-0.815, 0, -0.31)
        self.actionFrameText = OnscreenText(text = "",
            parent = self.actionFrame, scale = 0.05, wordwrap = 12, pos = (0, 0.1))

    def removeActionPanel(self):
        self.clearActionButtons()
        if self.actionFrameText:
            self.actionFrameText.destroy()
            self.actionFrameText = None
        if self.actionFrame:
            self.actionFrame.destroy()
            self.actionFrame = None

    def doAction(self, action):
        self.action = action
        self.actionFSM.requestFinalState()
        self.removeMoreDetailsPanel()
        self.removeActionPanel()
        self.makeActionPanel()
        if action != 'removeFriendConfirm':
            self.actionFSM.request('waitOnAvatarStatusResponse')
        else:
            self.actionFSM.request(action)

    def enterWaitOnAvatarInfoResponse(self):
        self.label = OnscreenText(text = 'Retrieving Toon\ndetails...', parent = self, scale = 0.04)
        self.acceptOnce('avatarInfoResponse', self.handleAvatarInfoResponse)
        base.cr.friendsManager.d_requestAvatarInfo(self.avatarInfo[0])

    def handleAvatarInfoResponse(self, name, dna, maxHealth, health, zoneId, shardId, isOnline, adminToken):
        if self.avatarInfo:
            self.avatarInfo.append(name)
            self.avatarInfo.append(dna)
            self.avatarInfo.append(maxHealth)
            self.avatarInfo.append(health)
            self.avatarInfo.append(zoneId)
            self.avatarInfo.append(shardId)
            self.avatarInfo.append(isOnline)
            self.avatarInfo.append(adminToken)
            self.fsm.request('panel')

    def exitWaitOnAvatarInfoResponse(self):
        self.label.destroy()
        del self.label
        self.ignore('avatarInfoResponse')

    def makePanel(self, avId):
        if self.avatarInfo:
            if self.avatarInfo[0] == avId:
                # They clicked on the same toon without closing the
                # previous panel, maybe they're spamming?
                return

        self.cleanup()

        base.localAvatar.hideFriendButton()

        self.show()
        self.avatarInfo = []
        self.avatarInfo.append(avId)
        self.fsm.request('waitOnAvatarInfoResponse')

    def exitClicked(self):
        self.cleanup()
        base.localAvatar.showFriendButton()

    def cleanup(self):
        self.actionFSM.requestFinalState()
        self.fsm.requestFinalState()
        self.avatarInfo = None

    def enterPanel(self):
        adminToken = self.avatarInfo[8]
        text_color = CIGlobals.TextColorByAdminToken[adminToken]
        self.nameText = OnscreenText(text = self.avatarInfo[1], parent = self,
            pos = (0, 0.2), scale = 0.035, wordwrap = 8, fg = text_color)
        self.nameText.setBin('gui-popup', 60)

        dna = ToonDNA.ToonDNA()
        dna.setDNAStrand(self.avatarInfo[2])

        self.head = ToonHead.ToonHead(base.cr)
        self.head.generateHead(dna.gender, dna.animal, dna.head, 1)
        self.head.setHeadColor(dna.headcolor)
        self.head.reparentTo(self)
        self.head.setDepthWrite(1)
        self.head.setDepthTest(1)
        self.head.setH(180)
        self.head.setScale(self.animal2HeadData[dna.animal][0])
        self.head.setZ(self.animal2HeadData[dna.animal][1])

        self.laffMeter = LaffOMeter()
        r, g, b, _ = dna.headcolor
        self.laffMeter.generate(r, g, b, dna.animal, self.avatarInfo[3], self.avatarInfo[4])
        self.laffMeter.reparentTo(self)
        self.laffMeter.setBin('gui-popup', 60)
        self.laffMeter.setScale(0.045)
        self.laffMeter.setPos(0, 0, -0.1)

        self.friendButton = DirectButton(geom = CIGlobals.getDefaultBtnGeom(), text = "Add Friend", scale = 0.58,
            relief = None, text_scale = 0.058, geom_scale = (1.25, 0, 0.9), text_pos = (0, -0.0125), parent = self, pos = (0, 0, -0.12),
            command = self.doAction, extraArgs = ['waitOnAvatarFriendListResponse'])
        self.friendButton.setPos(0, 0.0, -0.225)
        self.maybeUpdateFriendButton()

        self.teleportButton = DirectButton(geom = CIGlobals.getDefaultBtnGeom(), text = "Teleport", scale = 0.58,
	       relief = None, text_scale = 0.058, geom_scale = (1.25, 0, 0.9), text_pos = (0, -0.0125),
           parent = self, pos = (0, 0, -0.12), command = self.doAction, extraArgs = ['waitOnAvatarTeleportResponse'])
        self.teleportButton.setPos(0, 0, -0.275)

        self.whisperButton = DirectButton(geom = CIGlobals.getDefaultBtnGeom(), text = "Whisper", scale = 0.58,
	       relief = None, text_scale = 0.058, geom_scale = (1.25, 0, 0.9), text_pos = (0, -0.0125),
           parent = self, pos = (0, 0, -0.12), command = base.localAvatar.handleClickedWhisper, extraArgs = [self.avatarInfo[1], self.avatarInfo[0], 1])
        self.whisperButton.setPos(0, 0, -0.325)

        self.exitButton = DirectButton(geom = CIGlobals.getCancelBtnGeom(), parent = self,
            relief = None, scale = 0.6, pos = (0, 0.0, -0.39), command = self.exitClicked)
        gui = loader.loadModel("phase_3.5/models/gui/friendslist_gui.bam")
        self.moreDetailsBtn = DirectButton(geom = (gui.find('**/Horiz_Arrow_UP'),
            gui.find('**/Horiz_Arrow_DN'),
            gui.find('**/Horiz_Arrow_Rllvr'),
            gui.find('**/Horiz_Arrow_UP')),
            relief = None,
            parent = self,
            pos = (-0.127, 0.0, -0.39),
            geom_hpr = (180, 0, 0),
            command = self.makeMoreDetailsPanel,
            scale = 0.77,
            text = ('', 'More Details', 'More Details', ''),
            text_scale = 0.045,
            text_fg = (1, 1, 1, 1),
            text_shadow = (0, 0, 0, 1),
            text_pos = (-0.08, -0.01),
            text_align = TextNode.ARight)

    def exitPanel(self):
        if self.actionFSM.getCurrentState().getName() == 'waitOnAvatarFriendListResponse':
            if self.avatarInfo:
                base.cr.friendsManager.d_iCancelledFriendRequest(self.avatarInfo[0])
        self.actionFSM.requestFinalState()
        self.action = None
        self.avatarInfo = None
        self.removeActionPanel()
        self.removeMoreDetailsPanel()
        self.hide()
        if self.nameText:
            self.nameText.destroy()
            self.nameText = None
        if self.head:
            self.head.removeNode()
            self.head.delete()
            self.head = None
        if self.laffMeter:
            self.laffMeter.disable()
            self.laffMeter.delete()
            self.laffMeter = None
        if self.friendButton:
            self.friendButton.destroy()
            self.friendButton = None
        if self.teleportButton:
            self.teleportButton.destroy()
            self.teleportButton = None
        if self.whisperButton:
            self.whisperButton.destroy()
            self.whisperButton = None
        if self.exitButton:
            self.exitButton.destroy()
            self.exitButton = None
        if self.moreDetailsBtn:
            self.moreDetailsBtn.destroy()
            self.moreDetailsBtn = None
