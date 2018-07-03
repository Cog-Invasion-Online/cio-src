"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Place.py
@author Brian Lach
@date December 15, 2014

@desc Handles avatar events that happen while the avatar is
      in a place such as a playground.

"""

from panda3d.core import VBase4

from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from src.coginvasion.globals import CIGlobals
from PublicWalk import PublicWalk
from src.coginvasion.book.ShtickerBook import ShtickerBook
from src.coginvasion.gui.Dialog import GlobalDialog, Ok
from src.coginvasion.gui.ChatInput import CHAT_WINDOW_OPENED_EVENT, CHAT_WINDOW_CLOSED_EVENT
from src.coginvasion.minigame.FirstPerson import FirstPerson
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
from SnowEffect import SnowEffect
import LinkTunnel
import ZoneUtil

class Place(StateData):
    notify = directNotify.newCategory("Place")

    def __init__(self, loader, doneEvent):
        StateData.__init__(self, doneEvent)
        self.loader = loader
        self.zoneId = None
        self.track = None
        self.interior = False
        self.firstPerson = FirstPerson()
        self.snowEffect = SnowEffect(self)
        self.lastBookPage = 2
        self.useFirstPerson = config.GetBool('want-firstperson-battle')
        self.lampLights = []
        self.lampLightColor = VBase4(255 / 255.0, 255 / 255.0, 218 / 255.0, 1.0)
        return
    
    def __handleChatInputOpened(self):
        if base.localAvatarReachable():
            if self.fsm.getCurrentState().getName() == 'walk':
                base.localAvatar.disableAvatarControls(True)
            
    def __handleChatInputClosed(self):
        if base.localAvatarReachable():
            if self.fsm.getCurrentState().getName() == 'walk':
                base.localAvatar.enableAvatarControls(True)
    
    def __acceptEvents(self):
        self.accept(CHAT_WINDOW_OPENED_EVENT, self.__handleChatInputOpened)
        self.accept(CHAT_WINDOW_CLOSED_EVENT, self.__handleChatInputClosed)
        
    def __ignoreEvents(self):
        self.ignore(CHAT_WINDOW_OPENED_EVENT)
        self.ignore(CHAT_WINDOW_CLOSED_EVENT)

    def maybeUpdateAdminPage(self):
        if self.fsm:
            if self.fsm.getCurrentState():
                if self.fsm.getCurrentState().getName() == 'shtickerBook':
                    if hasattr(self, 'shtickerBookStateData'):
                        if self.shtickerBookStateData.getCurrentPage() and self.shtickerBookStateData.getCurrentPage().title == 'Admin Page':
                            if base.cr.playGame.suitManager:
                                text2Change2 = 'Turn Suit Spawner '
                                if base.cr.playGame.suitManager.getSpawner():
                                    text2Change2 += 'Off'
                                else:
                                    text2Change2 += 'On'
                                self.shtickerBookStateData.getCurrentPage().suitSpawnerBtn['text'] = text2Change2
    
    # Used to disable all GUI interaction.   
    def __disableInteraction(self):
        if base.localAvatar.invGui:
            base.localAvatar.invGui.disable()
        base.localAvatar.disableLaffMeter()
        

    def enterStart(self):
        pass

    def exitStart(self):
        pass

    def enterFinal(self):
        pass

    def exitFinal(self):
        pass

    def enter(self):
        StateData.enter(self)

        base.localAvatar.createChatInput()

    def exit(self):
        self.__disableInteraction()
        del self.lastBookPage
        
        base.localAvatar.disableChatInput()

        StateData.exit(self)
        
    def enterTrolleyOut(self, requestStatus):
        base.localAvatar.walkControls.setCollisionsActive(0)
        base.transitions.fadeScreen(1.0)
        
        prevZone = requestStatus['prevZoneId']
        slot = requestStatus['slot']
        for trolley in base.cr.doFindAll("DistributedBattleTrolley"):
            if trolley.toZone == prevZone:
                trolley.localAvOnTrolley = True
                CIGlobals.showWaitForOthers()
                trolley.sendUpdate('arrivedInTrolley', [slot])
                    
    def exitTrolleyOut(self):
        pass

    def enterDoorIn(self, distDoor):
        requestStatus = {}
        requestStatus['zoneId'] = distDoor.getToZone()
        requestStatus['hoodId'] = base.cr.playGame.hood.id
        requestStatus['how'] = 'doorOut'
        requestStatus['shardId'] = None
        requestStatus['doorIndex'] = distDoor.getDoorIndex()
        foundBlock = False
        for interior in base.cr.doFindAll("DistributedToonInterior"):
            if interior.zoneId == base.localAvatar.zoneId:
                foundBlock = True
                requestStatus['block'] = interior.getBlock()
                break
        if not foundBlock:
            requestStatus['block'] = distDoor.getBlock()
        requestStatus['where'] = ZoneUtil.getWhereName(requestStatus['zoneId'])
        requestStatus['loader'] = base.cr.playGame.hood.fsm.getCurrentState().getName()
        requestStatus['avId'] = base.localAvatar.doId
        self.acceptOnce('DistributedDoor_localAvatarWentInDoor', self.handleDoorInDone, [requestStatus])
        self.acceptOnce('DistributedDoor_localAvatarGoingInDoor', base.transitions.irisOut)

        base.localAvatar.doFirstPersonCameraTransition()

    def exitDoorIn(self):
        self.ignore('DistributedDoor_localAvatarWentInDoor')
        self.ignore('DistributedDoor_localAvatarGoingInDoor')

    def handleDoorInDone(self, requestStatus):
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def __waitOnDoor(self, door, task):
        if door.ready:
            self.__doorReady(door)
            return task.done
        return task.cont

    def enterDoorOut(self, requestStatus):
        base.localAvatar.d_clearSmoothing()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.walkControls.setCollisionsActive(0)
        block = requestStatus['block']
        zoneId = requestStatus['zoneId']
        doorIndex = requestStatus['doorIndex']
        doorToExitFrom = None
        for door in base.cr.doFindAll("DistributedDoor"):
            if door.zoneId == zoneId:
                if door.getBlock() == block:
                    if door.getDoorIndex() == doorIndex:
                        doorToExitFrom = door
                        break
        if not doorToExitFrom:
            self.notify.error('Could not find a DistributedDoor to exit from!')
        elif not doorToExitFrom.ready:
            base.taskMgr.add(self.__waitOnDoor, "Place.waitOnDoor",
                extraArgs = [doorToExitFrom], appendTask = True)
            return
        self.__doorReady(doorToExitFrom)

    def __doorReady(self, door):
        door.sendUpdate('requestExit', [])
        self.nextState = 'walk'
        self.acceptOnce('DistributedDoor_localAvatarCameOutOfDoor', self.handleDoorOutDone)

    def exitDoorOut(self):
        base.taskMgr.remove("Place.waitOnDoor")
        self.ignore('DistributedDoor_localAvatarCameOutOfDoor')

    def handleDoorOutDone(self):
        base.transitions.irisIn()
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.fsm.request(self.nextState)

    def enterShtickerBook(self):
        base.localAvatar.createLaffMeter()
        base.localAvatar.startSmartCamera()
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        if base.localAvatar.isFirstPerson():
            # Don't wait for an animation we can't see, open the book now.
            self.enterShtickerBookGui()
        else:
            base.localAvatar.b_setAnimState('openBook', self.enterShtickerBookGui)

    def enterShtickerBookGui(self):
        doneEvent = 'shtickerBookDone'
        self.shtickerBookStateData = ShtickerBook(doneEvent)
        self.acceptOnce(doneEvent, self.__shtickerBookDone)
        self.shtickerBookStateData.load()
        self.shtickerBookStateData.enter(self.lastBookPage)
        base.localAvatar.showBookButton(1)
        base.localAvatar.b_setAnimState('readBook')
        base.localAvatar.showFriendButton()
        NametagGlobals.setWantActiveNametags(True)
        NametagGlobals.makeTagsReady()
        self.acceptOnce('escape-up', base.localAvatar.bookButtonClicked, [0])

    def __shtickerBookDone(self):
        self.hideFriendsStuff()
        NametagGlobals.setWantActiveNametags(False)
        NametagGlobals.makeTagsInactive()
        self.ignore('escape-up')
        doneStatus = self.shtickerBookStateData.getDoneStatus()
        base.localAvatar.hideBookButton()
        self.shtickerBookStateData.exit()

        data = []
        if doneStatus['mode'] == 'exit':
            data = [self.__handleBookCloseExit, []]
        elif doneStatus['mode'] == 'teleport':
            data = [self.__handleBookCloseTeleport, [doneStatus]]
        elif doneStatus['mode'] == 'resume':
            data = [self.__handleBookCloseResume, [doneStatus]]
        elif doneStatus['mode'] == 'switchShard':
            data = [self.__handleBookCloseSwitchShard, [doneStatus]]

        if base.localAvatar.isFirstPerson():
            # Don't wait for an animation we can't see.
            data[0](*data[1])
        else:
            base.localAvatar.b_setAnimState('closeBook', data[0], data[1])

    def __handleBookCloseSwitchShard(self, requestStatus):
        base.localAvatar.b_setAnimState('teleportOut', self.__handleBookSwitchShard, [requestStatus])

    def __handleBookSwitchShard(self, requestStatus):
        params = []
        params.append(requestStatus['shardId'])
        params.append(base.cr.playGame.hood.id)
        params.append(ZoneUtil.getZoneId(base.cr.playGame.hood.id))
        params.append(base.localAvatar.doId)
        base.cr.gameFSM.request('switchShards', params)

    def __handleBookCloseResume(self, doneStatus):
        if doneStatus.get('callback'):
            doneStatus['callback'](*doneStatus.get("extraArgs", []))
            
        if base.localAvatar.isFirstPerson():
            base.localAvatar.getGeomNode().hide()
        self.fsm.request('walk', [0, 0])

    def __handleBookCloseTeleport(self, requestStatus):
        self.fsm.request('teleportOut', [requestStatus])

    def __teleportOutDone(self, requestStatus):
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def __handleBookCloseExit(self):
        base.localAvatar.b_setAnimState('teleportOut', self.__handleBookExitTeleport)

    def __handleBookExitTeleport(self):
        base.transitions.fadeOut(0.0)
        base.cr.gameFSM.request('closeShard')

    def exitShtickerBook(self):
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.disableLaffMeter()
        self.ignore(self.shtickerBookStateData.doneEvent)
        self.shtickerBookStateData.exit()
        self.shtickerBookStateData.unload()
        del self.shtickerBookStateData
        base.localAvatar.hideBookButton()
        self.hideFriendsStuff()
        NametagGlobals.setWantActiveNametags(False)
        NametagGlobals.makeTagsInactive()
        self.ignore('escape-up')

    def enterStop(self, doNeutral = 1):
        if doNeutral:
            base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.createLaffMeter()
        if base.localAvatar.inBattle:
            base.localAvatar.enableGags(andKeys = 0)

    def exitStop(self):
        self.__disableInteraction()
        if base.localAvatar.inBattle:
            base.localAvatar.disableGags()

    def load(self):
        StateData.load(self)
        self.walkDoneEvent = "walkDone"
        self.walkStateData = PublicWalk(self.fsm, self.walkDoneEvent)
        self.walkStateData.load()
        if not self.interior and (base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS
                                  or base.cr.playGame.getCurrentWorldName() == 'BRHood'):
            self.snowEffect.load()
        self.__acceptEvents()

    def unload(self):
        StateData.unload(self)
        if not self.interior and (base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS
                                  or base.cr.playGame.getCurrentWorldName() == 'BRHood'):
            self.snowEffect.unload()
        del self.walkDoneEvent
        self.walkStateData.unload()
        del self.walkStateData
        del self.loader
        del self.snowEffect
        
        self.__ignoreEvents()

    def enterTeleportIn(self, requestStatus):
        self.nextState = requestStatus.get('nextState', 'walk')
        if requestStatus['avId'] != base.localAvatar.doId:
            av = base.cr.doId2do.get(requestStatus['avId'])
            if av:
                base.localAvatar.gotoNode(av)
                base.localAvatar.b_setChat("Hi, %s." % av.getName())

        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.b_setAnimState('teleportIn', callback = self.teleportInDone)
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setParent(CIGlobals.SPRender)

        base.transitions.irisIn()

    def exitTeleportIn(self):
        base.localAvatar.stopPosHprBroadcast()
        return

    def teleportInDone(self):
        if hasattr(self, 'fsm'):
            self.fsm.request(self.nextState, [1])

    def enterAcknowledgeDeath(self, foo = 0):
        message = "You were defeated by the Cogs! Collect treasures in the Playground to refill your Laff meter."
        self.dialog = GlobalDialog(message = message, style = 3, doneEvent = 'ackDeathDone')
        self.dialog.show()
        self.acceptOnce('ackDeathDone', self.handleAckDeathDone)

    def handleAckDeathDone(self):
        self.fsm.request('walk', [1])

    def exitAcknowledgeDeath(self):
        self.ignore('ackDeathDone')
        self.dialog.cleanup()
        del self.dialog

    def enterDied(self, requestStatus, callback = None):
        if callback is None:
            callback = self.__diedDone
        base.localAvatar.createLaffMeter()
        base.localAvatar.b_setAnimState('died', callback, [requestStatus])

    def __diedDone(self, requestStatus):
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def exitDied(self):
        base.localAvatar.disableLaffMeter()

    def enterWalk(self, teleportIn = 0, wantMouse = 1):
        self.walkStateData.enter(wantMouse)
        if teleportIn == 0:
            self.walkStateData.fsm.request('walking')
        self.acceptOnce(self.walkDoneEvent, self.handleWalkDone)
        self.walkStateData.fsm.request('walking')
        self.watchTunnelSeq = Sequence(Wait(1.0), Func(LinkTunnel.globalAcceptCollisions))
        self.watchTunnelSeq.start()
        NametagGlobals.setWantActiveNametags(True)
        NametagGlobals.makeTagsReady()
        
        if base.localAvatar.getMyBattle():
            if self.useFirstPerson:
                base.localAvatar.stopSmartCamera()
                camera.setPos(base.localAvatar.smartCamera.firstPersonCamPos)
                self.firstPerson.start()
                self.firstPerson.reallyStart()
                self.firstPerson.disableMouse()
                base.localAvatar.getGeomNode().show()
                base.localAvatar.getShadow().hide()
                base.localAvatar.find('**/torso-top').hide()
                base.localAvatar.find('**/torso-bot').hide()
                base.localAvatar.getPart('head').hide()
            base.localAvatar.setBusy(1)
        else:
            base.localAvatar.setBusy(0)
            base.localAvatar.enablePicking()
            base.localAvatar.showFriendButton()
            base.localAvatar.questManager.enableShowQuestsHotkey()

    def hideFriendsStuff(self):
        base.localAvatar.hideFriendButton()
        if base.localAvatar.friendsList:
            base.localAvatar.friendsList.fsm.requestFinalState()
        if base.localAvatar.panel:
            base.localAvatar.panel.fsm.requestFinalState()

    def exitWalk(self):
        self.walkStateData.exit()
        self.ignore(self.walkDoneEvent)
        if base.cr.playGame.hood.titleText != None:
            base.cr.playGame.hood.hideTitleText()
        if hasattr(self, 'watchTunnelSeq'):
            self.watchTunnelSeq.pause()
            del self.watchTunnelSeq
        NametagGlobals.setWantActiveNametags(False)
        NametagGlobals.makeTagsInactive()
        base.localAvatar.setBusy(1)
        base.localAvatar.disablePicking()
        self.hideFriendsStuff()
        if base.localAvatar.invGui:
            base.localAvatar.invGui.disable()
        if base.localAvatar.questManager:
            base.localAvatar.questManager.disableShowQuestsHotkey()
        if self.useFirstPerson:
            if base.localAvatar.getMyBattle():
                self.firstPerson.enableMouse()
                self.firstPerson.end()
                self.firstPerson.reallyEnd()
                base.localAvatar.getShadow().show()
                base.localAvatar.find('**/torso-top').show()
                base.localAvatar.find('**/torso-bot').show()
                base.localAvatar.getPart('head').show()
        return

    def handleWalkDone(self, doneStatus):
        pass

    def enterTeleportOut(self, requestStatus, callback = None):
        if not callback:
            callback = self.__teleportOutDone
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setAnimState('teleportOut', callback, [requestStatus])

    def exitTeleportOut(self):
        base.localAvatar.disableLaffMeter()
        base.localAvatar.stopPosHprBroadcast()

    def enterTunnelIn(self, linkTunnel):
        zoneId = linkTunnel.data['zoneId']
        base.localAvatar.sendUpdate('goThroughTunnel', [zoneId, 0])
        base.localAvatar.playMovementSfx('run')

        requestStatus = {}
        requestStatus['zoneId'] = linkTunnel.data['zoneId']

        # Goes from safe zone to street.
        if linkTunnel.__class__.__name__ == "SafeZoneLinkTunnel":
            requestStatus['where'] = 'street'
            requestStatus['loader'] = 'townLoader'
            requestStatus['hoodId'] = base.cr.playGame.hood.id
            requestStatus['shardId'] = None
            requestStatus['avId'] = base.localAvatar.doId
            requestStatus['how'] = 'tunnelOut'
            requestStatus['fromZone'] = base.localAvatar.zoneId
        # Goes from street to safe zone.
        elif linkTunnel.__class__.__name__ == "StreetLinkTunnel":
            requestStatus['where'] = 'playground'
            requestStatus['loader'] = 'safeZoneLoader'
            requestStatus['hoodId'] = base.cr.playGame.hood.id
            requestStatus['shardId'] = None
            requestStatus['avId'] = base.localAvatar.doId
            requestStatus['how'] = 'tunnelOut'
            requestStatus['fromZone'] = base.localAvatar.zoneId
        # Goes from street to street.
        elif linkTunnel.__class__.__name__ == "NeighborhoodLinkTunnel":
            requestStatus['where'] = 'street'
            requestStatus['loader'] = 'townLoader'
            hoodId = ZoneUtil.getHoodId(linkTunnel.data['zoneId'], 1)
            requestStatus['hoodId'] = hoodId
            requestStatus['shardId'] = None
            requestStatus['avId'] = base.localAvatar.doId
            requestStatus['how'] = 'tunnelOut'
            requestStatus['fromZone'] = base.localAvatar.zoneId

        base.localAvatar.goThroughTunnel(zoneId, 0, requestStatus)

    def exitTunnelIn(self):
        base.localAvatar.playMovementSfx(None)
        base.localAvatar.wrtReparentTo(render)
        base.localAvatar.walkControls.setCollisionsActive(1)

    def enterTunnelOut(self, requestStatus):
        zone = requestStatus['fromZone']
        base.localAvatar.sendUpdate('goThroughTunnel', [zone, 1])
        base.localAvatar.playMovementSfx('run')

        self.nextState = requestStatus.get('nextState', 'walk')
        base.localAvatar.goThroughTunnel(zone, 1)

    def exitTunnelOut(self):
        base.localAvatar.playMovementSfx(None)
        del self.nextState

    def enterNoAccessFA(self):
        base.localAvatar.startSmartCamera()
        base.localAvatar.createLaffMeter()

        noAccess = "Watch out!\n\nThis neighborhood is too dangerous for your Toon. Complete Quests to unlock this neighborhood."
        self.dialog = GlobalDialog(noAccess, 'noAccessAck', Ok)
        self.acceptOnce('noAccessAck', self.__handleNoAccessAck)
        self.dialog.show()

    def __handleNoAccessAck(self):
        self.fsm.request('walk')

    def exitNoAccessFA(self):
        base.localAvatar.disableLaffMeter()

        if hasattr(self, 'dialog'):
            self.dialog.cleanup()
            del self.dialog
