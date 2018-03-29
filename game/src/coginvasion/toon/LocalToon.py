"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LocalToon.py
@author Brian Lach
@date November 30, 2014
"""

from panda3d.core import Point3, ConfigVariableBool
from src.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from src.coginvasion.toon.CIGravityWalker import GravityWalker
from direct.task import Task
from DistributedToon import DistributedToon
from SmartCamera import SmartCamera
from src.coginvasion.gui.ChatInput import ChatInput
from src.coginvasion.gui.LaffOMeter import LaffOMeter
from src.coginvasion.gui.InventoryGui import InventoryGui
from src.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval
from direct.gui.DirectGui import DirectButton, OnscreenText
from direct.showbase.InputStateGlobal import inputState
from direct.gui.DirectGui import DGG
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.gui.ToonPanel import ToonPanel
from src.coginvasion.friends.FriendRequestManager import FriendRequestManager
from src.coginvasion.base.PositionExaminer import PositionExaminer
from src.coginvasion.friends.FriendsList import FriendsList
from src.coginvasion.cog import SuitAttacks
from src.coginvasion.quests.QuestManager import QuestManager
from src.coginvasion.gui.Crosshair import Crosshair

from src.coginvasion.nametag import NametagGlobals

import random
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.minigame import GunGameGlobals

lightwarps = ["phase_3/maps/toon_lightwarp.jpg", "phase_3/maps/toon_lightwarp_2.jpg", "test_lightwarp.png",
              "phase_3/maps/toon_lightwarp_cartoon.jpg", "phase_3/maps/toon_lightwarp_dramatic.jpg",
              "phase_3/maps/toon_lightwarp_bright.jpg"]

class LocalToon(DistributedToon):
    neverDisable = 1

    GTAControls = ConfigVariableBool('want-gta-controls', False)

    def __init__(self, cr):
        try:
            self.LocalToon_initialized
            return
        except:
            self.LocalToon_initialized = 1
        DistributedToon.__init__(self, cr)
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
        self.controlManager = ControlManager.ControlManager(True, False)
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

        self.jumpHardLandIval = None

        # Modified by DistributedBattleZone.
        self.inBattle = False
        
        # This is used by CutsceneGUI
        self.allowA2dToggle = True
        
        # This is used by the animation traverser.
        self.__traverseGUI = None
        
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
        self.walkControls.setCollisionsActive(1)
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
        DistributedToon.setFriendsList(self, friends)
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
        return DistributedToon.getBackpack(self)

    def setMyBattle(self, battle):
        self.myBattle = battle
        self.inBattle = (not battle is None)

    def getMyBattle(self):
        return self.myBattle

    def ghostOn(self):
        self.getGeomNode().setTransparency(1)
        self.getGeomNode().setColorScale(1, 1, 1, 0.25)

    def ghostOff(self):
        self.getGeomNode().setColorScale(1, 1, 1, 1)
        self.getGeomNode().setTransparency(0)

    def enterReadBook(self, ts = 0, callback = None, extraArgs = []):
        self.stopLookAround()
        self.b_lookAtObject(0, -45, 0)
        DistributedToon.enterReadBook(self, ts, callback, extraArgs)

    def exitReadBook(self):
        DistributedToon.exitReadBook(self)
        self.startLookAround()

    def getAirborneHeight(self):
        return self.offset + 0.025000000000000001

    def isMoving(self):
        fwd, rot, sli = self.walkControls.getSpeeds()
        return fwd != 0.0 or rot != 0.0 or sli != 0.0

    def setupControls(self):
        if self.GTAControls:
            self.prepareToSwitchControlType()
            self.controlManager.wantWASD = True
            self.controlManager.disable()
            self.controlManager.enable()
            self.controlManager.setWASDTurn(False)

        self.walkControls = GravityWalker(legacyLifter=False)
        self.walkControls.setWallBitMask(CIGlobals.WallBitmask)
        self.walkControls.setFloorBitMask(CIGlobals.FloorBitmask)
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
            CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
        )
        self.walkControls.initializeCollisions(base.cTrav, self, floorOffset=0.025, reach=4.0)
        self.walkControls.cEventSphereNodePath.node().setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.WeaponBitmask
            | GunGameGlobals.HILL_BITMASK)
        self.walkControls.setAirborneHeightFunc(self.getAirborneHeight)

    def destroyControls(self):
        self.walkControls.disableAvatarControls()
        self.walkControls.setCollisionsActive(0)
        self.walkControls.deleteCollisions()
        self.walkControls = None

    def setWalkSpeedNormal(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonRotateSpeed
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
        DistributedToon.setDNAStrand(self, dnaStrand)
        if self.firstTimeGenerating:
            self.setupCamera()
            self.firstTimeGenerating = False

    def setMoney(self, money):
        DistributedToon.setMoney(self, money)

    def setupNameTag(self, tempName = None):
        DistributedToon.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCLocal])
        self.nametag.unmanage(base.marginManager)
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def d_broadcastPositionNow(self):
        self.d_clearSmoothing()
        self.d_broadcastPosHpr()

    def b_setAnimState(self, anim, callback = None, extraArgs = []):
        if self.anim != anim:
            self.d_setAnimState(anim)
            DistributedToon.setAnimState(self, anim, callback = callback, extraArgs = extraArgs)

    def attachCamera(self):
        #self.notify.info("Attaching camera...")
        camera.reparentTo(self)
        camera.setPos(self.smartCamera.getIdealCameraPos())
        camera.lookAt(self.smartCamera.getLookAtPoint())

    def startSmartCamera(self):
        #self.notify.info("Starting camera...")
        self.smartCamera.startUpdateSmartCamera()

    def resetSmartCamera(self):
        #self.notify.info("Resetting camera...")
        self.stopSmartCamera()
        self.startSmartCamera()

    def stopSmartCamera(self):
        #self.notify.info("Stopping camera...")
        self.smartCamera.stopUpdateSmartCamera()

    def detachCamera(self):
        #self.notify.info("Detaching camera...")
        camera.reparentTo(render)
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)

    def handleSuitAttack(self, attack_id, suit_id):
        DistributedToon.handleSuitAttack(self, attack_id, suit_id)

        if not self.isDead() and base.config.GetBool('want-sa-reactions'):
            base.taskMgr.remove('LT.attackReactionDone')
            attack = SuitAttacks.SuitAttackLengths.keys()[attack_id]
            suit = self.cr.doId2do.get(suit_id)
            animToPlay = None
            timeToWait = 3.0
            if not attack in ["pickpocket", "fountainpen"]:
                suitH = suit.getH(render) % 360
                myH = self.getH(render) % 360
                if -90.0 <= (suitH - myH) <= 90.0:
                    animToPlay = "fallFWD"
                else:
                    animToPlay = "fallBCK"
            elif attack in ["pickpocket"]:
                animToPlay = "cringe"
            elif attack in ["fountainpen"]:
                animToPlay = "conked"
                timeToWait = 5.0
            self.cr.playGame.getPlace().fsm.request('stop')
            self.b_setAnimState(animToPlay)
            base.taskMgr.doMethodLater(timeToWait, self.__attackReactionDone, 'LT.attackReactionDone')

    def __attackReactionDone(self, task):
        self.cr.playGame.hood.loader.place.fsm.request('walk')
        self.b_setAnimState('neutral')
        return Task.done

    def printPos(self):
        x, y, z = self.getPos(render)
        h, p, r = self.getHpr(render)
        print "Pos: (%s, %s, %s), Hpr: (%s, %s, %s)" % (x, y, z, h, p, r)

    def enableAvatarControls(self):
        self.walkControls.enableAvatarControls()
        self.accept("control", self.updateMovementKeymap, ["jump", 1])
        self.accept("control-up", self.updateMovementKeymap, ["jump", 0])
        self.accept(base.inputStore.NextCameraPosition, self.smartCamera.nextCameraPos, [1])
        self.accept(base.inputStore.PreviousCameraPosition, self.smartCamera.nextCameraPos, [0])
        self.accept(base.inputStore.LookUp, self.smartCamera.pageUp)
        self.accept(base.inputStore.LookDown, self.smartCamera.pageDown)
        self.accept('jumpStart', self.__jump)
        self.accept('jumpLand', self.__handleJumpLand)
        self.accept('jumpHardLand', self.__handleJumpHardLand)
        self.avatarMovementEnabled = True
        self.playMovementSfx(None)
        if self.smartCamera.isOverTheShoulder():
            self.crosshair.show()

    def __handleJumpLand(self):
        if self.jumpHardLandIval:
            self.jumpHardLandIval.finish()
            self.jumpHardLandIval = None
        if self.getHealth() > 0:
            self.b_setAnimState('Happy')

    def __handleJumpHardLand(self):
        if self.jumpHardLandIval:
            self.jumpHardLandIval.finish()
            self.jumpHardLandIval = None
        self.jumpHardLandIval = ActorInterval(self, 'zend')
        self.jumpHardLandIval.setDoneEvent('LT::zend-done')
        self.acceptOnce('LT::zend-done', self.__handleJumpLand)
        self.jumpHardLandIval.start()

    def disableAvatarControls(self):
        self.walkControls.disableAvatarControls()
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
        self.playMovementSfx(None)
        for k, _ in self.movementKeymap.items():
            self.updateMovementKeymap(k, 0)
        self.resetSpeeds()
        self.resetTorsoRotation()
        self.crosshair.hide()

    def updateMovementKeymap(self, key, value):
        self.movementKeymap[key] = value

    def getMovementKeyValue(self, key):
        return self.movementKeymap[key]

    def playMovementSfx(self, movement):
        if movement == "run":
            self.walkSfx.stop()
            self.runSfx.play()
        elif movement == "walk":
            self.runSfx.stop()
            self.walkSfx.play()
        else:
            self.runSfx.stop()
            self.walkSfx.stop()

    def __forward(self):
        self.resetHeadHpr()
        self.stopLookAround()
        if self.getHealth() < 1:
            self.playMovementSfx("walk")
            self.setPlayRate(1.2, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.playMovementSfx("run")
            self.setAnimState('run')
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_forward = True
        self.isMoving_jump = False

    def __turn(self):
        self.resetHeadHpr()
        self.stopLookAround()
        self.playMovementSfx("walk")
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
            self.playMovementSfx("walk")
        else:
            self.setAnimState("walkBack")
            self.playMovementSfx("run")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = True
        self.isMoving_jump = False

    def __jump(self):
        self.playMovementSfx(None)
        if base.localAvatar.getHealth() > 0:
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
        self.playMovementSfx(None)
        if base.localAvatar.getHealth() > 0:
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
        speed, rotSpeed, slideSpeed = self.walkControls.getSpeeds()
        state = None
        if self.getHealth() > 0:
            state = 'Happy'
        else:
            state = 'Sad'
        if state != self.lastState:
            self.lastState = state
            self.b_setAnimState(state)
            if base.minigame is None:
                if state == 'Sad':
                    self.setWalkSpeedSlow()
                else:
                    self.setWalkSpeedNormal()
        action = self.setSpeed(speed, rotSpeed, slideSpeed)
        if action != self.lastAction:
            self.lastAction = action
            if action == CIGlobals.WALK_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
                self.playMovementSfx("walk")
            elif action == CIGlobals.RUN_INDEX or action in [CIGlobals.STRAFE_LEFT_INDEX, CIGlobals.STRAFE_RIGHT_INDEX] or action == CIGlobals.REVERSE_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
                self.playMovementSfx("run")
            else:
                self.resetHeadHpr()
                self.stopLookAround()
                if state == 'Happy' and not self.smartCamera.isOverTheShoulder():
                    self.startLookAround()
                self.playMovementSfx(None)
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
        DistributedToon.setLoadout(self, gagIds)
        place = base.cr.playGame.getPlace()
        if place and place.fsm.getCurrentState().getName() == 'shtickerBook':
            if hasattr(place, 'shtickerBookStateData'):
                stateData = place.shtickerBookStateData
                if stateData.getCurrentPage() is not None:
                    if stateData.getCurrentPage().title == 'Gags':
                        stateData.getCurrentPage().gui.fsm.request('idle')

    def enableGags(self, andKeys = 0):
        if self.avatarMovementEnabled and andKeys:
            self.enableGagKeys()
        self.invGui.enable()
        if self.backpack.getCurrentGag():
            slot = self.invGui.getSlotOfGag(self.backpack.getCurrentGag())
            self.invGui.setWeapon(slot, playSound = False)

    def enableGagKeys(self):
        if self.gagThrowBtn:
            self.gagThrowBtn.bind(DGG.B1PRESS, self.startGag)
            self.gagThrowBtn.bind(DGG.B1RELEASE, self.throwGag)
        key = CIGlobals.getSettingsMgr().getSetting("gagkey")
        self.accept(key, self.startGag)
        self.accept(key + "-up", self.throwGag)
        self.gagsEnabled = True

    def disableGagKeys(self):
        self.gagsEnabled = False
        if self.gagThrowBtn:
            self.gagThrowBtn.unbind(DGG.B1PRESS)
            self.gagThrowBtn.unbind(DGG.B1RELEASE)
        key = CIGlobals.getSettingsMgr().getSetting("gagkey")
        self.ignore(key)
        self.ignore(key + "-up")

    def disableGags(self):
        self.disableGagKeys()
        if self.invGui:
            self.invGui.disable()
        if hasattr(self, 'backpack'):
            if self.backpack:
                self.backpack.setCurrentGag()

    def setWeaponType(self, weaponType):
        enableKeysAgain = 0
        if weaponType != self.weaponType:
            enableKeysAgain = 1
        self.weaponType = weaponType
        if enableKeysAgain:
            self.disableGagKeys()
            self.enableGagKeys()

    def resetHeadHpr(self):
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

        self.ignore(CIGlobals.getSettingsMgr().getSetting("gagkey"))
        self.resetHeadHpr()
        self.b_gagStart(self.backpack.getCurrentGag().getID())

    def throwGag(self, start = True):
        if not self.canUseGag(False):
            return

        if self.gagThrowBtn:
            self.gagThrowBtn.unbind(DGG.B1RELEASE)

        self.ignore(CIGlobals.getSettingsMgr().getSetting("gagkey") + "-up")

        if self.backpack.getActiveGag().getType() == GagType.SQUIRT and self.backpack.getActiveGag().getName() in [CIGlobals.SeltzerBottle]:
            self.b_gagRelease(self.backpack.getActiveGag().getID())
        else:
            self.b_gagThrow(self.backpack.getActiveGag().getID())

        activeGag = self.backpack.getActiveGag()
        if not activeGag:
            activeGag = self.backpack.getCurrentGag()

        if not activeGag.doesAutoRelease():
            Sequence(Wait(0.75), Func(self.releaseGag)).start()

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
                self.playMovementSfx(None)
                self.b_setAnimState("neutral")
            elif self.animFSM.getCurrentState().getName() == 'deadWalk':
                self.playMovementSfx("run")
                self.b_setAnimState("run")
        DistributedToon.setHealth(self, hp)


    def diedStateDone(self, requestStatus):
        hood = self.cr.playGame.hood.id
        if hood == CIGlobals.BattleTTC:
            hood = CIGlobals.ToontownCentral
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
        toZone = CIGlobals.CogTropolisId
        hood = CIGlobals.CogTropolis
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
        self.controlManager.collisionsOn()

    def collisionsOff(self):
        self.controlManager.collisionsOff()

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
        DistributedToon.generate(self)

    def delete(self):
        DistributedToon.delete(self)
        self.deleteLaffMeter()
        return

    def disable(self):
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
        if self.controlManager:
            self.controlManager.delete()
            self.controlManager = None
        DistributedToon.disable(self)
        if self.smartCamera:
            self.smartCamera.deleteSmartCameraCollisions()
            self.smartCamera = None
        if self.questManager:
            self.questManager.cleanup()
            self.questManager = None
        if self.friendRequestManager:
            self.friendRequestManager.cleanup()
            self.friendRequestManager = None
        if self.invGui:
            self.invGui.deleteGui()
            self.invGui = None
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
        self.endTraverseAnimationControls()
        self.ignore("gotLookSpot")
        self.ignore("clickedWhisper")
        self.ignore('/')
        self.ignore(base.inputStore.ToggleAspect2D)
        return

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        self.setupControls()
        self.startLookAround()
        self.friendRequestManager.watch()
        self.accept("gotLookSpot", self.handleLookSpot)
        self.accept("clickedWhisper", self.handleClickedSentWhisper)
        self.accept(base.inputStore.ToggleAspect2D, self.toggleAspect2d)

        #self.accept('c', self.walkControls.setCollisionsActive, [0])

        self.invGui = InventoryGui()
        self.invGui.createGui()
        self.backpack.loadoutGUI = self.invGui

        # Unused developer methods.
        self.accept('/', self.printPos)
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
