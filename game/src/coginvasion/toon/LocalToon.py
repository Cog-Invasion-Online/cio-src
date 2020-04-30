"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LocalToon.py
@author Brian Lach
@date November 30, 2014
"""

from panda3d.core import Point3, ConfigVariableBool
from src.coginvasion.globals import CIGlobals
from direct.task import Task
from DistributedPlayerToon import DistributedPlayerToon
from SmartCamera import SmartCamera
from src.coginvasion.gui.ChatInput import ChatInput
from src.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, LerpPosHprInterval
from direct.gui.DirectGui import DirectButton, OnscreenText
from direct.showbase.InputStateGlobal import inputState
from direct.gui.DirectGui import DGG
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.gui.ToonPanel import ToonPanel
from src.coginvasion.friends.FriendRequestManager import FriendRequestManager
from src.coginvasion.base.PositionExaminer import PositionExaminer
from src.coginvasion.friends.FriendsList import FriendsList
from src.coginvasion.quest.QuestManager import QuestManager
from src.coginvasion.quest.QuestGlobals import QUEST_DATA_UPDATE_EVENT
from src.coginvasion.gui.Crosshair import Crosshair
from src.coginvasion.gui.QuestUpdateGUI import QuestUpdateGUI
from src.coginvasion.toon.TPMouseMovement import TPMouseMovement
from src.coginvasion.phys.CILocalControls import CILocalControls
from src.coginvasion.avatar.BaseLocalAvatar import BaseLocalAvatar

from src.coginvasion.nametag import NametagGlobals

import random
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.minigame import GunGameGlobals

lightwarps = ["phase_3/maps/toon_lightwarp.jpg", "phase_3/maps/toon_lightwarp_2.jpg", "test_lightwarp.png",
              "phase_3/maps/toon_lightwarp_cartoon.jpg", "phase_3/maps/toon_lightwarp_dramatic.jpg",
              "phase_3/maps/toon_lightwarp_bright.jpg"]

NO_TRANSITION = 1

class LocalToon(DistributedPlayerToon, BaseLocalAvatar):
    neverDisable = 1

    GTAControls = ConfigVariableBool('want-gta-controls', False)

    def __init__(self, cr):
        try:
            self.LocalToon_initialized
            return
        except:
            self.LocalToon_initialized = 1
        DistributedPlayerToon.__init__(self, cr)
        BaseLocalAvatar.__init__(self)
        self.chatInputState = False
        self.avatarChoice = cr.localAvChoice
        self.chatInput = ChatInput()
        self.positionExaminer = PositionExaminer()
        self.friendRequestManager = FriendRequestManager()
        self.friendsList = FriendsList()
        self.questManager = QuestManager(self)
        self.questUpdateGUI = QuestUpdateGUI()
        self.panel = ToonPanel()
        self.firstTimeGenerating = True
        friendsgui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        self.friendButton = DirectButton(geom = (friendsgui.find('**/FriendsBox_Closed'),
            friendsgui.find('**/FriendsBox_Rollover'), friendsgui.find('**/FriendsBox_Rollover')),
            text = ("", "Friends", "Friends", ""),
            text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1), text_scale = 0.09,
            text_pos = (0, -0.18), relief = None, parent = base.a2dTopRight,
            pos = (-0.141, 0, -0.125), command = self.friendsButtonClicked, scale = 0.8)
        friendsgui.removeNode()
        del friendsgui
        self.hideFriendButton()
        self.runSfx = base.loadSfx("phase_3.5/audio/sfx/AV_footstep_runloop.ogg")
        self.runSfx.setLoop(True)
        self.walkSfx = base.loadSfx("phase_3.5/audio/sfx/AV_footstep_walkloop.ogg")
        self.walkSfx.setLoop(True)
        self.offset = 3.2375
        self.firstPersonCamPos = None
        self.movementKeymap = {
            "forward": 0, "backward": 0,
            "left": 0, "right": 0, "jump": 0
        }
        self.avatarMovementEnabled = False
        self.isMoving_forward = False
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_jump = False
        self.gagThrowBtn = None

        self.pickerTrav = None
        self.pickerRay = None
        self.pickerRayNode = None
        self.pickerHandler = None
        self.rolledOverTag = None
        
        self.clickToonCallback = None

        self.inTutorial = False
        self.hasDoneJump = False
        self.lastState = None
        self.lastAction = None

        self.jumpHardLandIval = None
        
        # This is used by CutsceneGUI
        self.allowA2dToggle = True
        
        # This is used by the animation traverser.
        self.__traverseGUI = None
            
    def primaryFirePress(self):
        if not self.canUseGag():
            return

        DistributedPlayerToon.primaryFirePress(self)

    def primaryFireRelease(self):
        if not self.canUseGag():
            return

        DistributedPlayerToon.primaryFireRelease(self)

    def secondaryFirePress(self):
        if not self.canUseGag():
            return
        
        DistributedPlayerToon.secondaryFirePress(self)

    def secondaryFireRelease(self):
        if not self.canUseGag():
            return

        DistributedPlayerToon.secondaryFireRelease(self)

    def stopPlay(self):
        if not self.playState:
            self.notify.warning("Redundant call to stopPlay()")
            return

        self.hideBookButton()
        self.hideFriendButton()

        BaseLocalAvatar.stopPlay(self)
        
        self.stopTrackAnimToSpeed()

    def startPlay(self, gags = False, book = False, friends = False, laff = False, chat = False, wantMouse = 1):
        if self.playState:
            self.notify.warning("Redundant call to startPlay()")
            return

        if book:
            self.showBookButton()
        if friends:
            self.showFriendButton()
        if chat:
            self.createChatInput()

        self.startTrackAnimToSpeed()
        
        BaseLocalAvatar.startPlay(self, gags, laff, wantMouse)

    def handleSuitAttack(self, attack):
        if self.isFirstPerson():
            self.getFPSCam().handleSuitAttack(attack)
            
    def areGagsAllowed(self):
        return (
            BaseLocalAvatar.areGagsAllowed(self) and
            (self.chatInput is not None and self.chatInput.fsm.getCurrentState().getName() == 'idle')
        )

    def setEquippedAttack(self, gagId):
        DistributedPlayerToon.setEquippedAttack(self, gagId)
        BaseLocalAvatar.setEquippedAttack(self, gagId)

    def updateAttackAmmo(self, attackId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip):
        DistributedPlayerToon.updateAttackAmmo(self, attackId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip)
        BaseLocalAvatar.updateAttackAmmo(self, attackId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip)

    def setupAttacks(self):
        DistributedPlayerToon.setupAttacks(self)
        BaseLocalAvatar.setupAttacks(self)

    def _handleWentInTunnel(self, requestStatus):
        self.cr.playGame.getPlace().doneStatus = requestStatus
        messenger.send(self.cr.playGame.getPlace().doneEvent)

    def _handleCameOutTunnel(self):
        self.wrtReparentTo(render)
        
        self.cr.playGame.getPlace().fsm.request(self.cr.playGame.getPlace().nextState)

    def handleClickedWhisper(self, senderName, fromId, isPlayer, openPanel = False):
        place = self.cr.playGame.getPlace()
        if place is None or not hasattr(place, 'fsm') or place.fsm is None:
            return

        if openPanel and place.fsm.getCurrentState().getName() in ['walk', 'shtickerBook']:
            self.panel.makePanel(fromId)

        self.chatInput.disableKeyboardShortcuts()
        self.chatInput.fsm.request('input', ["", fromId])

    def handleClickedSentWhisper(self, senderName, fromId, isPlayer):
        self.handleClickedWhisper(senderName, fromId, isPlayer, True)

    def hasDiscoveredHood(self, zoneId):
        return zoneId in self.hoodsDiscovered

    def hasTeleportAccess(self, zoneId):
        return zoneId in self.teleportAccess

    def tutorialCreated(self, zoneId):
        self.cr.tutorialCreated(zoneId)

    def friendsButtonClicked(self):
        self.hideFriendButton()
        self.friendsList.fsm.request('onlineFriendsList')

    def destroyFriendButton(self):
        if CIGlobals.isNodePathOk(self.friendButton):
            self.friendButton.destroy()
            self.friendButton = None

    def hideFriendButton(self):
        self.friendButton.hide()

    def showFriendButton(self):
        self.friendButton.show()

    def gotoNode(self, node, eyeHeight = 3):
        possiblePoints = (
            Point3(0, 0, 0),
            Point3(3, 6, 0),
            Point3(-3, 6, 0),
            Point3(6, 6, 0),
            Point3(-6, 6, 0),
            Point3(3, 9, 0),
            Point3(-3, 9, 0),
            Point3(6, 9, 0),
            Point3(-6, 9, 0),
            Point3(9, 9, 0),
            Point3(-9, 9, 0),
            Point3(6, 0, 0),
            Point3(-6, 0, 0),
            Point3(6, 3, 0),
            Point3(-6, 3, 0),
            Point3(9, 9, 0),
            Point3(-9, 9, 0),
            Point3(0, 12, 0),
            Point3(3, 12, 0),
            Point3(-3, 12, 0),
            Point3(6, 12, 0),
            Point3(-6, 12, 0),
            Point3(9, 12, 0),
            Point3(-9, 12, 0),
            Point3(0, -6, 0),
            Point3(-3, -6, 0),
            Point3(0, -9, 0),
            Point3(-6, -9, 0)
        )
        for point in possiblePoints:
            pos = self.positionExaminer.consider(node, point, eyeHeight)
            if pos:
                self.setPos(node, pos)
                self.lookAt(node)
                self.setHpr(self.getH() + random.choice((-10, 10)), 0, 0)
                return

        self.setPos(node, 0, 0, 0)

    def setFriendsList(self, friends):
        DistributedPlayerToon.setFriendsList(self, friends)
        self.cr.friendsManager.d_requestFriendsList()
        self.panel.maybeUpdateFriendButton()

    def d_requestAddFriend(self, avId):
        self.sendUpdate('requestAddFriend', [avId])

    def enablePicking(self):
        self.accept('toonClicked', self.toonClicked)

    def disablePicking(self):
        self.ignore('toonClicked')

    def toonClicked(self, avId):
        if not self.clickToonCallback:
            self.panel.makePanel(avId)
        else:
            self.clickToonCallback(avId)
            self.clickToonCallback = None

    def prepareToSwitchControlType(self):
        # Hack fix for getting stuck moving in one direction without pressing the movement keys.
        inputs = [
            "run",
            "forward",
            "reverse",
            "turnLeft",
            "turnRight",
            "slideLeft",
            "slideRight",
            "jump"
        ]
        for inputName in inputs:
            try:
                inputState.releaseInputs(inputName)
            except:
                pass

    def getBackpack(self):
        return DistributedPlayerToon.getBackpack(self)

    def enterReadBook(self, ts = 0, callback = None, extraArgs = []):
        self.stopLookAround()
        self.b_lookAtObject(0, -45, 0)
        DistributedPlayerToon.enterReadBook(self, ts, callback, extraArgs)

    def exitReadBook(self):
        DistributedPlayerToon.exitReadBook(self)
        self.startLookAround()

    def getAirborneHeight(self):
        return self.offset + 0.025000000000000001

    def setupControls(self):
        self.walkControls = CILocalControls()
        self.walkControls.setupControls()
        self.walkControls.setMode(CIGlobals.getSettingsMgr().getSetting("bpov").getValue())

    def setWalkSpeedNormal(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
            CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
        )

    def setWalkSpeedNormalNoJump(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, 0.0,
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonRotateSpeed
        )

    def setWalkSpeedSlow(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSlowSpeed, CIGlobals.ToonJumpSlowForce,
            CIGlobals.ToonReverseSlowSpeed, CIGlobals.ToonRotateSlowSpeed
        )

    def setDNAStrand(self, dnaStrand):
        DistributedPlayerToon.setDNAStrand(self, dnaStrand)
        if self.firstTimeGenerating:
            self.setupCamera()
            self.firstTimeGenerating = False

    def setMoney(self, money):
        DistributedPlayerToon.setMoney(self, money)

    def setupNameTag(self, tempName = None):
        DistributedPlayerToon.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCLocal])
        self.nametag.unmanage(base.marginManager)
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def b_setAnimState(self, anim, callback = None, extraArgs = []):
        if self.anim != anim:
            self.d_setAnimState(anim)
            DistributedPlayerToon.setAnimState(self, anim, callback = callback, extraArgs = extraArgs)
            
            camTransitionStates = ['teleportIn', 'teleportOut', 'died']
            if anim in camTransitionStates and not NO_TRANSITION in extraArgs:
                self.doFirstPersonCameraTransition()

    def enableAvatarControls(self, wantMouse = 0):
        BaseLocalAvatar.enableAvatarControls(self, wantMouse)
        self.accept('jumpStart', self.__jump)

    def handleJumpLand(self):
        if self.jumpHardLandIval:
            self.jumpHardLandIval.finish()
            self.jumpHardLandIval = None
        if self.getHealth() > 0:
            self.b_setAnimState('Happy')

    def handleJumpHardLand(self):
        if self.jumpHardLandIval:
            self.jumpHardLandIval.finish()
            self.jumpHardLandIval = None
        self.jumpHardLandIval = ActorInterval(self, 'zend')
        self.jumpHardLandIval.setDoneEvent('LT::zend-done')
        self.acceptOnce('LT::zend-done', self.handleJumpLand)
        self.jumpHardLandIval.start()

    def disableAvatarControls(self, chat = False):
        BaseLocalAvatar.disableAvatarControls(self, chat)
        self.ignore('jumpStart')
        for k, _ in self.movementKeymap.items():
            self.updateMovementKeymap(k, 0)
        self.resetTorsoRotation()
        self.resetHeadHpr()

    def updateMovementKeymap(self, key, value):
        self.movementKeymap[key] = value

    def getMovementKeyValue(self, key):
        return self.movementKeymap[key]

    def playMovementSfx(self, movement):
        """ This previously was the main method of playing movement sfxs, but now this is only used for tunnels """

        if movement == 'run':
            self.walkSfx.stop()
            self.runSfx.play()
        elif movement == 'walk':
            self.runSfx.stop()
            self.walkSfx.play()
        else:
            self.runSfx.stop()
            self.walkSfx.stop()

    def __forward(self):
        self.resetHeadHpr()
        self.stopLookAround()
        if self.getHealth() < 1:
            self.setPlayRate(1.2, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.setAnimState('run')
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_forward = True
        self.isMoving_jump = False

    def __turn(self):
        self.resetHeadHpr()
        self.stopLookAround()
        if self.getHealth() < 1:
            self.setPlayRate(1.2, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.setPlayRate(1.0, "walk")
            self.setAnimState("walk")
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_side = True
        self.isMoving_jump = False

    def __reverse(self):
        self.resetHeadHpr()
        self.stopLookAround()
        if self.getHealth() < 1:
            self.setPlayRate(-1.0, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.setAnimState("walkBack")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = True
        self.isMoving_jump = False

    def __jump(self):
        if self.getHealth() > 0:
            if self.playingAnim in ['run', 'walk']:
                self.b_setAnimState("leap")
            else:
                self.b_setAnimState("jump")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_jump = True

    def __neutral(self):
        self.resetHeadHpr()
        self.startLookAround()
        if self.getHealth() > 0:
            self.setAnimState("neutral")
        else:
            self.setPlayRate(1.0, 'dneutral')
            self.setAnimState("deadNeutral")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_jump = False

    def movementTask(self, task):
        if self.getMovementKeyValue("jump") == 1:
            if not self.walkControls.isAirborne:
                if self.walkControls.mayJump:
                    self.__jump()
                    self.hasDoneJump = True
                else:
                    if self.hasDoneJump:
                        if self.getHealth() > 0:
                            self.b_setAnimState('Happy')
                        self.hasDoneJump = False
        else:
            if not self.walkControls.isAirborne:
                if self.hasDoneJump:
                    if self.getHealth() > 0:
                        self.b_setAnimState('Happy')
                    self.hasDoneJump = False
        return task.cont

    def startTrackAnimToSpeed(self):
        if not base.taskMgr.hasTaskNamed(self.uniqueName('trackAnimToSpeed')):
            base.taskMgr.add(self.trackAnimToSpeed, self.uniqueName('trackAnimToSpeed'))

    def stopTrackAnimToSpeed(self):
        base.taskMgr.remove(self.uniqueName('trackAnimToSpeed'))

    def trackAnimToSpeed(self, task):
        slideSpeed, speed, rotSpeed = self.walkControls.getSpeeds()
        state = None
        if self.isSwimming:
            state = 'swim'
        else:
            if self.getHealth() > 0:
                state = 'Happy'
            else:
                state = 'Sad'
        if state != self.lastState:
            self.lastState = state
            self.b_setAnimState(state)
            if base.minigame is None and not self.battleControls:
                if state == 'Sad' and not self.isSwimming:
                    self.setWalkSpeedSlow()
                else:
                    self.setWalkSpeedNormal()
        action = self.setSpeed(speed, rotSpeed, slideSpeed)
        if action != self.lastAction:
            self.lastAction = action
            if action == CIGlobals.WALK_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
            elif action == CIGlobals.RUN_INDEX or action in [CIGlobals.STRAFE_LEFT_INDEX, CIGlobals.STRAFE_RIGHT_INDEX] or action == CIGlobals.REVERSE_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
            else:
                self.resetHeadHpr()
                self.stopLookAround()
                if self.walkControls.mode == self.walkControls.MThirdPerson:
                    if state == 'Happy':
                        self.startLookAround()
        return task.cont

    def setLoadout(self, gagIds):
        DistributedPlayerToon.setLoadout(self, gagIds)
        place = base.cr.playGame.getPlace()
        if place and place.fsm.getCurrentState().getName() == 'shtickerBook':
            if hasattr(place, 'shtickerBookStateData'):
                stateData = place.shtickerBookStateData
                if stateData.getCurrentPage() is not None:
                    if stateData.getCurrentPage().title == 'Gags':
                        stateData.getCurrentPage().gui.fsm.request('idle')

    def resetHeadHpr(self, override = False):
        if self.lookMode == self.LMOff or not self.walkControls.controlsEnabled or override:
            self.b_lookAtObject(0, 0, 0, blink = 0)

    def checkSuitHealth(self, suit):
        pass

    def handleLookSpot(self, hpr):
        h, p, r = hpr
        self.d_lookAtObject(h, p, r, blink = 1)

    def showBookButton(self, inBook = 0):
        self.book_gui = loader.loadModel("phase_3.5/models/gui/stickerbook_gui.bam")
        self.book_btn = DirectButton(
            image=(
                self.book_gui.find('**/BookIcon_CLSD'),
                self.book_gui.find('**/BookIcon_OPEN'),
                self.book_gui.find('**/BookIcon_RLVR')
            ),
            relief=None,
            pos=(-0.158, 0, 0.17),
            command=self.bookButtonClicked,
            scale=0.305,
            parent=base.a2dBottomRight
        )
        self.book_btn.setBin('gui-popup', 60)
        if inBook:
            self.book_btn["image"] = (
                self.book_gui.find('**/BookIcon_OPEN'),
                self.book_gui.find('**/BookIcon_CLSD'),
                self.book_gui.find('**/BookIcon_RLVR2')
            )
            self.book_btn["command"] = self.bookButtonClicked
            self.book_btn["extraArgs"] = [0]

    def hideBookButton(self):
        if hasattr(self, 'book_gui'):
            self.book_gui.removeNode()
            del self.book_gui
        if hasattr(self, 'book_btn'):
            self.book_btn.destroy()
            del self.book_btn

    def bookButtonClicked(self, openIt = 1):
        if openIt:
            base.cr.playGame.getPlace().fsm.request('shtickerBook')
        else:
            base.cr.playGame.getPlace().shtickerBookStateData.finishedResume()

    def handleHealthChange(self, hp, oldHp):
        if hp > 0 and oldHp < 1:
            if self.cr.playGame and self.cr.playGame.getPlace():
                if self.cr.playGame.getPlace().fsm.getCurrentState().getName() == 'walk':
                    if self.cr.playGame.getPlace().walkStateData.fsm.getCurrentState().getName() == 'deadWalking':
                        self.cr.playGame.getPlace().walkStateData.fsm.request('walking')
            if self.animFSM.getCurrentState().getName() == 'deadNeutral':
                self.b_setAnimState("neutral")
            elif self.animFSM.getCurrentState().getName() == 'deadWalk':
                self.b_setAnimState("run")
        
        BaseLocalAvatar.handleHealthChange(self, hp, oldHp)

        DistributedPlayerToon.handleHealthChange(self, hp, oldHp)

    def setSessionHealth(self, hp):
        currHp = self.getSessionHealth()

        self.handleHealthChange(hp, currHp)

        DistributedPlayerToon.setSessionHealth(self, hp)

    def reparentTo(self, parent):
        self.notify.debug("Local toon reparent to {0}".format(parent.node().getName()))
        DistributedPlayerToon.reparentTo(self, parent)

    def wrtReparentTo(self, parent):
        self.notify.debug("Local toon wrtReparent to {0}".format(parent.node().getName()))
        DistributedPlayerToon.wrtReparentTo(self, parent)
        
    def loadAvatar(self):
        DistributedPlayerToon.loadAvatar(self)
        base.avatars.remove(self)

    def diedStateDone(self, requestStatus):
        hood = self.cr.playGame.hood.id
        if hood == ZoneUtil.BattleTTC:
            hood = ZoneUtil.ToontownCentral
        toZone = ZoneUtil.getZoneId(hood)
        if self.zoneId != toZone:
            requestStatus = {'zoneId': toZone,
                        'hoodId': hood,
                        'where': ZoneUtil.getWhereName(toZone),
                        'avId': self.doId,
                        'loader': ZoneUtil.getLoaderName(toZone),
                        'shardId': None,
                        'wantLaffMeter': 1,
                        'how': 'teleportIn'}
            self.cr.playGame.getPlace().doneStatus = requestStatus
            messenger.send(self.cr.playGame.getPlace().doneEvent)
        else:
            return

    def teleportToCT(self):
        toZone = ZoneUtil.CogTropolisId
        hood = ZoneUtil.CogTropolis
        requestStatus = {'zoneId': toZone,
                'hoodId': hood,
                'where': ZoneUtil.getWhereName(toZone),
                'avId': self.doId,
                'loader': ZoneUtil.getLoaderName(toZone),
                'shardId': None,
                'wantLaffMeter': 1,
                'how': 'teleportIn'}
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])
        
    def setQuests(self, dataStr):
        oldDataStr = self.quests
        DistributedPlayerToon.setQuests(self, dataStr)
        self.questManager.makeQuestsFromData()
    
        # Let's send our quest data update event.
        messenger.send(QUEST_DATA_UPDATE_EVENT, [oldDataStr, dataStr])

    def createChatInput(self):
        if not self.chatInputState:
            self.chatInput.load()
            self.chatInput.enter()
            self.chatInputState = True

    def disableChatInput(self):
        if self.chatInputState:
            self.chatInput.exit()
            self.chatInput.unload()
            self.chatInputState = False

    def toggleAspect2d(self):
        if self.allowA2dToggle:
            if base.aspect2d.isHidden():
                base.aspect2d.show()
            else:
                base.aspect2d.hide()
                
    def startTraverseAnimationControls(self, animName):
        if not self.__traverseGUI:
            if not self.getNumFrames(animName) is None:
                frame = self.getCurrentFrame(animName)
                
                if frame is None:
                    frame = 0
                    self.pose(animName, 0)
                
                self.accept('h', self.__traverseAnimation, extraArgs = [animName, -1])
                self.accept('j', self.__traverseAnimation, extraArgs = [animName, 1])
                
                self.__traverseGUI = OnscreenText(text = 'Current Frame: {0}\n\'H\' Decrease Frame, \'J\' Increase Frame'.format(str(frame)),
                    pos = (0, -0.75), font = CIGlobals.getToonFont(), fg = (1, 1, 1, 1),
                    shadow = (0, 0, 0, 1))
            else:
                self.notify.info('Tried to traverse unknown animation: {0}'.format(animName))
            
    def __traverseAnimation(self, animName, delta):
        frame = self.getCurrentFrame(animName)
        if frame is None: 
            frame = 0

        if (frame + delta) < 0:
            frame = self.getNumFrames(animName) - 1
        elif (frame + delta) > (self.getNumFrames(animName) - 1):
            frame = self.getNumFrames(animName) - 1
        else:
            frame += delta
        self.pose(animName, frame)
        self.__traverseGUI.setText('Current Frame: {0}\n\'H\' Decrease Frame, \'J\' Increase Frame'.format(str(frame)))
            
    def endTraverseAnimationControls(self):
        self.ignore('h')
        self.ignore('j')
        
        if self.__traverseGUI:
            self.__traverseGUI.destroy()
            self.__traverseGUI = None

    def generate(self):
        DistributedPlayerToon.generate(self)

    def delete(self):
        DistributedPlayerToon.delete(self)
        self.deleteLaffMeter()
        return

    def disable(self):
        DistributedPlayerToon.disable(self)

        self.stopTrackAnimToSpeed()
        base.camLens.setMinFov(CIGlobals.OriginalCameraFov / (4./3.))
        if self.jumpHardLandIval:
            self.ignore('LT::zend-done')
            self.jumpHardLandIval.finish()
            self.jumpHardLandIval = None
        if self.friendsList:
            self.friendsList.destroy()
            self.friendsList = None
        if self.panel:
            self.panel.cleanup()
            self.panel = None
        if self.positionExaminer:
            self.positionExaminer.delete()
            self.positionExaminer = None
        self.disablePicking()
        self.destroyFriendButton()
        self.stopLookAround()
        self.disableAvatarControls()
        self.destroyControls()
        if self.smartCamera:
            self.smartCamera.stopUpdateSmartCamera()
            self.smartCamera.deleteSmartCameraCollisions()
            self.smartCamera = None
        if self.questManager:
            self.questManager.cleanup()
            self.questManager = None
        if self.questUpdateGUI:
            self.questUpdateGUI.cleanup()
            self.questUpdateGUI = None
        if self.friendRequestManager:
            self.friendRequestManager.cleanup()
            self.friendRequestManager = None
        self.destroyInvGui()
        if self.crosshair:
            self.crosshair.destroy()
            self.crosshair = None
        self.disableLaffMeter()
        self.disableGags()
        self.disableChatInput()
        self.hideBookButton()
        self.weaponType = None
        self.runSfx = None
        self.walkSfx = None
        self.offset = None
        self.movementKeymap = None
        self.minigame = None
        self.inTutorial = None
        self.avatarChoice = None
        self.chatInputState = None
        self.playState = None
        self.endTraverseAnimationControls()
        self.ignore("gotLookSpot")
        self.ignore("clickedWhisper")
        self.ignore('/')
        self.ignore(base.inputStore.ToggleAspect2D)
        return

    def delete(self):
        DistributedPlayerToon.delete(self)
        del base.localAvatar
        del __builtins__['localAvatar']
        print "Local avatar finally deleted"

    def sewerHeadOff(self, zoneId):
        # TEMPORARY
        requestStatus = {'zoneId': zoneId,
                    'hoodId': 0,
                    'where': 'sewer',
                    'avId': self.doId,
                    'loader': 'sewer',
                    'shardId': None,
                    'wantLaffMeter': 1}
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])

    def announceGenerate(self):
        DistributedPlayerToon.announceGenerate(self)
        self.setupControls()
        self.startLookAround()
        self.friendRequestManager.watch()
        self.accept("gotLookSpot", self.handleLookSpot)
        self.accept("clickedWhisper", self.handleClickedSentWhisper)
        self.accept(base.inputStore.ToggleAspect2D, self.toggleAspect2d)
        
        if not metadata.IS_PRODUCTION:
            self.acceptOnce('m', self.sendUpdate, ['reqMakeSewer'])
            self.accept('l', render.ls)
            self.accept('/', self.printPos)
            self.accept('\\', self.printPos_cam)

        #self.accept('c', self.walkControls.setCollisionsActive, [0])

        self.createInvGui()

        # Unused developer methods.
        #self.accept('p', self.enterPictureMode)
        self.accept('c', self.teleportToCT)
        #posBtn = DirectButton(text = "Get Pos", scale = 0.08, pos = (0.3, 0, 0), parent = base.a2dLeftCenter, command = self.printAvPos)

    def enterHiddenToonMode(self):
        self.laffMeter.stop()
        self.laffMeter.disable()
        self.laffMeter.destroy()
        self.getGeomNode().hide()
        self.deleteNameTag()
        self.invGui.disable()
        self.hideFriendButton()
        self.hideBookButton()
        self.removeAdminToken()
