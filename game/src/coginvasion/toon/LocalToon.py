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
from src.coginvasion.gui.LaffOMeter import LaffOMeter
from src.coginvasion.gui.GagSelectionGui import GagSelectionGui
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
from src.coginvasion.gui.Crosshair import Crosshair
from src.coginvasion.toon.TPMouseMovement import TPMouseMovement
from src.coginvasion.phys.LocalControls import LocalControls

from src.coginvasion.nametag import NametagGlobals

import random
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.minigame import GunGameGlobals

lightwarps = ["phase_3/maps/toon_lightwarp.jpg", "phase_3/maps/toon_lightwarp_2.jpg", "test_lightwarp.png",
              "phase_3/maps/toon_lightwarp_cartoon.jpg", "phase_3/maps/toon_lightwarp_dramatic.jpg",
              "phase_3/maps/toon_lightwarp_bright.jpg"]

NO_TRANSITION = 1

class LocalToon(DistributedPlayerToon):
    neverDisable = 1

    GTAControls = ConfigVariableBool('want-gta-controls', False)

    def __init__(self, cr):
        try:
            self.LocalToon_initialized
            return
        except:
            self.LocalToon_initialized = 1
        DistributedPlayerToon.__init__(self, cr)
        self.chatInputState = False
        self.avatarChoice = cr.localAvChoice
        self.smartCamera = SmartCamera()
        self.chatInput = ChatInput()
        self.laffMeter = LaffOMeter()
        self.positionExaminer = PositionExaminer()
        self.friendRequestManager = FriendRequestManager()
        self.friendsList = FriendsList()
        self.questManager = QuestManager(self)
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
        self.myBattle = None
        self.gagsTimedOut = False
        self.needsToSwitchToGag = None
        self.gagsEnabled = False
        
        self.crosshair = Crosshair()
        self.crosshair.hide()

        self.pickerTrav = None
        self.pickerRay = None
        self.pickerRayNode = None
        self.pickerHandler = None
        self.rolledOverTag = None
        
        self.clickToonCallback = None

        self.walkControls = None

        self.inTutorial = False
        self.hasDoneJump = False
        self.lastState = None
        self.lastAction = None

        self.invGui = None

        self.isSwimming = False
        self.touchingWater = False

        self.jumpHardLandIval = None

        # Modified by DistributedBattleZone.
        self.inBattle = False
        
        # This is used by CutsceneGUI
        self.allowA2dToggle = True
        
        # This is used by the animation traverser.
        self.__traverseGUI = None

        self.playState = False
        self.battleControls = True
        
        self.selectedGag = -1
        self.lastSelectedGag = -1
        
    def selectGag(self, gagId, record = True):
        if record:
            self.lastSelectedGag = self.selectedGag
        self.selectedGag = gagId
        self.needsToSwitchToGag = gagId
        self.b_setCurrentGag(gagId)
        
    def setBattleControls(self, flag):
        self.battleControls = flag
        if self.playState:
            self.disableAvatarControls()
            self.enableAvatarControls(1)

    def stopPlay(self):
        if not self.playState:
            self.notify.warning("Redundant call to stopPlay()")
            return

        self.disableLaffMeter()
        self.disableGags()
        self.hideBookButton()
        self.hideFriendButton()
        self.disableChatInput()

        self.collisionsOff()
        if self.walkControls.getCollisionsActive():
            self.walkControls.setCollisionsActive(0, andPlaceOnGround=1)
        self.disableAvatarControls()
        self.stopTrackAnimToSpeed()
        self.stopPosHprBroadcast()

        self.playState = False

    def startPlay(self, gags = False, book = False, friends = False, laff = False, chat = False, wantMouse = 1):
        if self.playState:
            self.notify.warning("Redundant call to startPlay()")
            return

        if laff:
            self.createLaffMeter()
        if book:
            self.showBookButton()
        if friends:
            self.showFriendButton()
        if chat:
            self.createChatInput()

        self.collisionsOn()
        if not self.walkControls.getCollisionsActive():
            self.walkControls.setCollisionsActive(1)
        self.enableAvatarControls(wantMouse)
        
        if gags:
            self.enableGags(1)
        
        self.startPosHprBroadcast()
        self.d_broadcastPositionNow()
        self.startTrackAnimToSpeed()

        self.playState = True
        
    def startSmooth(self):
        self.notify.warning("Tried to call startSmooth() on LocalToon!")

    def handleSuitAttack(self, attack):
        if self.isFirstPerson():
            self.getFPSCam().handleSuitAttack(attack)

    def doFirstPersonCameraTransition(self):
        if self.isFirstPerson():
            # Fancy little camera transition for first person
            camHeight = max(self.getHeight(), 3.0)
            heightScaleFactor = camHeight * 0.3333333333

            LerpPosHprInterval(nodePath = camera, other = self, duration = 1.0,
                               pos = (0, -9.0 * heightScaleFactor, camHeight), hpr = (0, 0, 0),
                               blendType = 'easeInOut').start()

    def areGagsAllowed(self):
        state = (self.isFirstPerson() and self.getFPSCam().mouseEnabled) or (self.isThirdPerson() and base.localAvatar.battleControls)
        return (self.avatarMovementEnabled and self.walkControls.controlsEnabled and
                (self.chatInput is not None and self.chatInput.fsm.getCurrentState().getName() == 'idle') and
                (self.invGui is not None and self.invGui.getCurrentOrNextState() != 'Select') and state)

    def isFirstPerson(self):
        return self.walkControls.mode == self.walkControls.MFirstPerson and base.localAvatar.battleControls

    def isThirdPerson(self):
        return self.walkControls.mode == self.walkControls.MThirdPerson or not base.localAvatar.battleControls

    def getViewModel(self):
        return self.walkControls.fpsCam.viewModel

    def getFPSCam(self):
        return self.walkControls.fpsCam

    def b_setCurrentGag(self, gagId):
        self.setCurrentGag(gagId)
        self.sendUpdate('setCurrentGag', [gagId])

    def b_unEquipGag(self):
        self.b_setCurrentGag(-1)
        
    def switchToLastSelectedGag(self):
        self.selectGag(self.lastSelectedGag)

    def setCurrentGag(self, gagId):
        DistributedPlayerToon.setCurrentGag(self, gagId)
        if gagId != -1:
            if self.battleControls:
                self.crosshair.setCrosshair(self.backpack.getGagByID(gagId).crosshair)
                self.crosshair.show()
                self.b_setLookMode(self.LMCage)
        else:
            # We've unequipped
            if not self.walkControls:
                return
            if self.battleControls:
                self.crosshair.hide()
                self.b_setLookMode(self.LMHead)
            else:
                self.b_setLookMode(self.LMOff)
        
    def showCrosshair(self):
        self.crosshair.show()
        
    def hideCrosshair(self):
        self.crosshair.hide()
        
    def resetSpeeds(self):
        self.walkControls.speed = 0.0
        self.walkControls.rotationSpeed = 0.0
        self.walkControls.slideSpeed = 0.0

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
        possiblePoints = (Point3(3, 6, 0),
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
         Point3(-6, -9, 0))
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

    def setMyBattle(self, battle):
        self.myBattle = battle
        self.inBattle = (not battle is None)

    def getMyBattle(self):
        return self.myBattle

    def enterReadBook(self, ts = 0, callback = None, extraArgs = []):
        self.stopLookAround()
        self.b_lookAtObject(0, -45, 0)
        DistributedPlayerToon.enterReadBook(self, ts, callback, extraArgs)

    def exitReadBook(self):
        DistributedPlayerToon.exitReadBook(self)
        self.startLookAround()

    def getAirborneHeight(self):
        return self.offset + 0.025000000000000001

    def isMoving(self):
        return self.walkControls.isMoving()

    def setupControls(self):
        self.walkControls = LocalControls()
        self.walkControls.setupControls()
        self.walkControls.setMode(CIGlobals.getSettingsMgr().getSetting("bpov").getValue())

    def destroyControls(self):
        self.walkControls.disableControls()
        self.walkControls.stopControllerUpdate()
        self.walkControls = None

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

    def setupCamera(self):
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
        self.smartCamera.initializeSmartCamera()
        self.smartCamera.initCameraPositions()
        self.smartCamera.setCameraPositionByIndex(0)

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

    def d_broadcastPositionNow(self):
        self.d_clearSmoothing()
        if self.d_broadcastPosHpr:
            self.d_broadcastPosHpr()

    def b_setAnimState(self, anim, callback = None, extraArgs = []):
        if self.anim != anim:
            self.d_setAnimState(anim)
            DistributedPlayerToon.setAnimState(self, anim, callback = callback, extraArgs = extraArgs)
            
            camTransitionStates = ['teleportIn', 'teleportOut']
            if anim in camTransitionStates and not NO_TRANSITION in extraArgs:
                self.doFirstPersonCameraTransition()

    def attachCamera(self):
        self.walkControls.attachCamera()

    def startSmartCamera(self):
        #self.notify.info("Starting camera...")
        self.smartCamera.startUpdateSmartCamera()
        pass

    def resetSmartCamera(self):
        #self.notify.info("Resetting camera...")
        self.stopSmartCamera()
        self.startSmartCamera()
        pass

    def stopSmartCamera(self):
        #self.notify.info("Stopping camera...")
        self.smartCamera.stopUpdateSmartCamera()
        pass

    def detachCamera(self):
        camera.reparentTo(render)
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)

    def printPos(self):
        x, y, z = self.getPos(render)
        h, p, r = self.getHpr(render)
        print "Pos: (%s, %s, %s), Hpr: (%s, %s, %s)" % (x, y, z, h, p, r)
        
    def printPos_cam(self):
        x, y, z = camera.getPos(render)
        h, p, r = camera.getHpr(render)
        print "Pos: (%s, %s, %s), Hpr: (%s, %s, %s)" % (x, y, z, h, p, r)

    def enableAvatarControls(self, wantMouse = 0):
        self.walkControls.enableControls(wantMouse)
        #self.accept("control", self.updateMovementKeymap, ["jump", 1])
        #self.accept("control-up", self.updateMovementKeymap, ["jump", 0])
        #self.accept(base.inputStore.NextCameraPosition, self.smartCamera.nextCameraPos, [1])
        #self.accept(base.inputStore.PreviousCameraPosition, self.smartCamera.nextCameraPos, [0])
        #self.accept(base.inputStore.LookUp, self.smartCamera.pageUp)
        #self.accept(base.inputStore.LookDown, self.smartCamera.pageDown)
        self.accept('jumpStart', self.__jump)
        self.avatarMovementEnabled = True
        #self.mouseMov.enableMovement()
        #if self.smartCamera.isOverTheShoulder():
        #    self.crosshair.show()

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
        #self.mouseMov.disableMovement(False)
        self.walkControls.disableControls(chat)
        self.ignore('tab')
        self.ignore('shift-tab')
        self.ignore('page_up')
        self.ignore('page_down')
        self.ignore("arrow_up")
        self.ignore("arrow_up-up")
        self.ignore("arrow_down")
        self.ignore("arrow_down-up")
        self.ignore("arrow_left")
        self.ignore("arrow_left-up")
        self.ignore("arrow_right")
        self.ignore("arrow_right-up")
        self.ignore("control")
        self.ignore("control-up")
        self.ignore('jumpStart')
        self.ignore('jumpLand')
        self.ignore('jumpHardLand')
        taskMgr.remove("avatarMovementTask")
        self.isMoving_forward = False
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_jump = False
        self.avatarMovementEnabled = False
        for k, _ in self.movementKeymap.items():
            self.updateMovementKeymap(k, 0)
        self.resetSpeeds()
        self.resetTorsoRotation()
        self.resetHeadHpr()
        #self.crosshair.hide()

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

    def createLaffMeter(self):
        r, g, b, _ = self.getHeadColor()
        animal = self.getAnimal()
        maxHp = self.getMaxHealth()
        hp = self.getHealth()
        self.laffMeter.generate(r, g, b, animal, maxHP = maxHp, initialHP = hp)
        self.laffMeter.start()

    def disableLaffMeter(self):
        self.laffMeter.stop()
        self.laffMeter.disable()

    def deleteLaffMeter(self):
        self.laffMeter.delete()

    def setLoadout(self, gagIds):
        DistributedPlayerToon.setLoadout(self, gagIds)
        place = base.cr.playGame.getPlace()
        if place and place.fsm.getCurrentState().getName() == 'shtickerBook':
            if hasattr(place, 'shtickerBookStateData'):
                stateData = place.shtickerBookStateData
                if stateData.getCurrentPage() is not None:
                    if stateData.getCurrentPage().title == 'Gags':
                        stateData.getCurrentPage().gui.fsm.request('idle')

    def b_setLookMode(self, mode):
        self.setLookMode(mode)
        self.sendUpdate('setLookMode', [mode])

    def b_setLookPitch(self, pitch):
        self.setLookPitch(pitch)
        self.sendUpdate('setLookPitch', [pitch])

    def enableGags(self, andKeys = 0):
        if self.avatarMovementEnabled and andKeys:
            self.enableGagKeys()
            self.selectGag(self.selectedGag, False)
        self.invGui.show()
        self.invGui.enableControls()

    def enableGagKeys(self):
        if not self.areGagsAllowed():
            return

        if self.gagThrowBtn:
            self.gagThrowBtn.bind(DGG.B1PRESS, self.startGag)
            self.gagThrowBtn.bind(DGG.B1RELEASE, self.throwGag)
            
        key = CIGlobals.getSettingsMgr().getSetting("gagkey").getValue()
        CIGlobals.acceptWithModifiers(self, key, self.startGag)
        CIGlobals.acceptWithModifiers(self, key + "-up", self.throwGag)
        
        self.gagsEnabled = True

    def disableGagKeys(self):
        self.gagsEnabled = False
        
        if self.gagThrowBtn:
            self.gagThrowBtn.unbind(DGG.B1PRESS)
            self.gagThrowBtn.unbind(DGG.B1RELEASE)
        key = CIGlobals.getSettingsMgr().getSetting("gagkey").getValue()
        CIGlobals.ignoreWithModifiers(self, key)
        CIGlobals.ignoreWithModifiers(self, key + "-up")

    def disableGags(self):
        self.disableGagKeys()
        if self.invGui:
            self.invGui.hide()
            self.invGui.disableControls()
        self.b_setCurrentGag(-1)

    def resetHeadHpr(self, override = False):
        if self.lookMode == self.LMOff or not self.walkControls.controlsEnabled or override:
            self.b_lookAtObject(0, 0, 0, blink = 0)

    def canUseGag(self, preActive):
        if preActive:

            # We're checking if we can call `startGag` (before the gag gets activated)
            return (self.backpack is not None
                    and self.backpack.getCurrentGag() is not None
                    and self.backpack.getSupply() > 0
                    and self.gagsEnabled)

        else:

            # We're checking if we can call `throwGag` or `releaseGag` (after the gag gets activated)
            return (self.backpack is not None
                    and self.backpack.getCurrentGag() is not None
                    and self.backpack.getActiveGag() is not None
                    and self.backpack.getSupply() > 0
                    and self.gagsEnabled)

    def startGag(self, start = True):
        if not self.canUseGag(True) or self.backpack.getCurrentGag().__class__.__name__ == 'BananaPeel':
            return

        if self.gagThrowBtn:
            self.gagThrowBtn.unbind(DGG.B1PRESS)

        CIGlobals.ignoreWithModifiers(self, CIGlobals.getSettingsMgr().getSetting("gagkey").getValue())
        self.resetHeadHpr()
        self.b_gagStart(self.backpack.getCurrentGag().getID())

    def throwGag(self, start = True):
        if not self.canUseGag(False):
            return

        if self.gagThrowBtn:
            self.gagThrowBtn.unbind(DGG.B1RELEASE)

        CIGlobals.ignoreWithModifiers(self, CIGlobals.getSettingsMgr().getSetting("gagkey").getValue() + "-up")

        self.b_gagThrow(self.backpack.getActiveGag().getID())

        activeGag = self.backpack.getActiveGag()
        if not activeGag:
            activeGag = self.backpack.getCurrentGag()

    def releaseGag(self):
        if not self.canUseGag(False) or self.backpack.getCurrentGag().__class__.__name__ == 'BananaPeel':
            return
        gag = self.backpack.getActiveGag()
        if not gag:
            gag = self.backpack.getCurrentGag()
        if gag.getState() != GagState.RELEASED:
            gagName = gag.getName()
            self.b_gagRelease(GagGlobals.getIDByName(gagName))

    def checkSuitHealth(self, suit):
        pass

    def handleLookSpot(self, hpr):
        h, p, r = hpr
        self.d_lookAtObject(h, p, r, blink = 1)

    def showGagButton(self):
        geom = CIGlobals.getDefaultBtnGeom()
        self.gagThrowBtn = DirectButton(
            geom = geom,
            geom_scale = (0.75, 1, 1),
            text = "Throw Gag",
            text_scale = 0.05,
            text_pos = (0, -0.01),
            relief = None,
            parent = base.a2dTopCenter,
            pos = (0, 0, -0.1)
        )
        self.gagThrowBtn.setBin('gui-popup', 60)
        self.gagThrowBtn.hide()

    def hideGagButton(self):
        if self.gagThrowBtn:
            self.gagThrowBtn.removeNode()
            self.gagThrowBtn = None

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

    def startMonitoringHP(self):
        taskMgr.add(self.monitorHealth, "localToon-monitorHealth")

    def monitorHealth(self, task):
        if self.isDead():
            base.taskMgr.remove("LT.attackReactionDone")
            if (self.cr.playGame.hood.id != ZoneUtil.getHoodId(self.zoneId)):
                self.cr.playGame.getPlace().fsm.request('died', [{}, self.diedStateDone])
            return task.done
        return task.cont

    def stopMonitoringHP(self):
        taskMgr.remove("localToon-monitorHealth")

    def setHealth(self, hp):
        if hp > 0 and self.getHealth() < 1:
            if self.cr.playGame and self.cr.playGame.getPlace():
                if self.cr.playGame.getPlace().fsm.getCurrentState().getName() == 'walk':
                    if self.cr.playGame.getPlace().walkStateData.fsm.getCurrentState().getName() == 'deadWalking':
                        self.cr.playGame.getPlace().walkStateData.fsm.request('walking')
            if self.animFSM.getCurrentState().getName() == 'deadNeutral':
                self.b_setAnimState("neutral")
            elif self.animFSM.getCurrentState().getName() == 'deadWalk':
                self.b_setAnimState("run")
        
        if self.walkControls:
            if hp < self.getHealth() and self.isFirstPerson():
                self.getFPSCam().doDamageFade(1, 0, 0, (self.getHealth() - hp) / 30.0)
        DistributedPlayerToon.setHealth(self, hp)

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

    def collisionsOn(self):
        pass
        #self.controlManager.collisionsOn()

    def collisionsOff(self):
        pass
        #self.controlManager.collisionsOff()

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
        self.stopMonitoringHP()
        taskMgr.remove("resetHeadColorAfterFountainPen")
        taskMgr.remove("LT.attackReactionDone")
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
        self.stopMonitoringHP()
        self.hideBookButton()
        self.hideGagButton()
        self.weaponType = None
        self.myBattle = None
        self.runSfx = None
        self.walkSfx = None
        self.offset = None
        self.movementKeymap = None
        self.inBattle = None
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

    def createInvGui(self):
        self.invGui = GagSelectionGui()
        self.invGui.load()
        self.invGui.hide()
        self.backpack.loadoutGUI = self.invGui

    def reloadInvGui(self):
        self.destroyInvGui()
        self.createInvGui()

    def destroyInvGui(self):
        if self.invGui:
            self.invGui.cleanup()
            self.invGui = None

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
        #self.accept('c', self.teleportToCT)
        #posBtn = DirectButton(text = "Get Pos", scale = 0.08, pos = (0.3, 0, 0), parent = base.a2dLeftCenter, command = self.printAvPos)

    def enterHiddenToonMode(self):
        self.laffMeter.stop()
        self.laffMeter.disable()
        self.laffMeter.destroy()
        self.getGeomNode().hide()
        self.deleteNameTag()
        self.invGui.disable()
        self.hideGagButton()
        self.hideFriendButton()
        self.hideBookButton()
        self.removeAdminToken()
