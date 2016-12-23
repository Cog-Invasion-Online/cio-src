"""

  Filename: Place.py
  Created by: blach (15Dec14)

  Description: Handles the avatar events that happen while the avatar is
               in a place such as a playground.

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, LerpHprInterval, Sequence, Wait, Func, LerpPosInterval, LerpQuatInterval
from src.coginvasion.globals import CIGlobals
from PublicWalk import PublicWalk
from src.coginvasion.book.ShtickerBook import ShtickerBook
from src.coginvasion.gui.Dialog import GlobalDialog, Ok
from src.coginvasion.minigame.FirstPerson import FirstPerson
from src.coginvasion.nametag import NametagGlobals
import LinkTunnel
import ZoneUtil

class Place(StateData):
    notify = directNotify.newCategory("Place")

    def __init__(self, loader, doneEvent):
        StateData.__init__(self, doneEvent)
        self.loader = loader
        self.zoneId = None
        self.track = None
        self.firstPerson = FirstPerson()
        self.lastBookPage = 2
        self.useFirstPerson = config.GetBool('want-firstperson-battle')
        return

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
        base.localAvatar.disableChatInput()
        del self.lastBookPage
        StateData.exit(self)
        
    def enterTrolleyOut(self, requestStatus):
        print "enterTrolleyOut"
        base.localAvatar.walkControls.setCollisionsActive(0)
        base.transitions.fadeScreen(1.0)
        
        prevZone = requestStatus['prevZoneId']
        slot = requestStatus['slot']
        for trolley in base.cr.doFindAll("DistributedBattleTrolley"):
            if trolley.toZone == prevZone:
                print "Found the trolley"
                trolley.localAvOnTrolley = True
                trolley.sendUpdate('arrivedInTrolley', [slot])
                    
    def exitTrolleyOut(self):
        pass

    def enterDoorIn(self, distDoor):
        base.localAvatar.attachCamera()
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

    def exitDoorIn(self):
        base.localAvatar.detachCamera()
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
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
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
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        self.ignore('DistributedDoor_localAvatarCameOutOfDoor')

    def handleDoorOutDone(self):
        base.transitions.irisIn()
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.fsm.request(self.nextState)

    def enterShtickerBook(self):
        base.localAvatar.attachCamera()
        base.localAvatar.createLaffMeter()
        base.localAvatar.startSmartCamera()
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setAnimState('openBook', self.enterShtickerBookGui)

    def enterShtickerBookGui(self):
        doneEvent = 'shtickerBookDone'
        self.shtickerBookStateData = ShtickerBook(doneEvent)
        self.acceptOnce(doneEvent, self.__shtickerBookDone)
        self.shtickerBookStateData.load()
        self.shtickerBookStateData.enter(self.lastBookPage)
        base.localAvatar.showBookButton(1)
        base.localAvatar.b_setAnimState('readBook')
        self.acceptOnce('escape-up', base.localAvatar.bookButtonClicked, [0])

    def __shtickerBookDone(self):
        self.ignore('escape-up')
        doneStatus = self.shtickerBookStateData.getDoneStatus()
        base.localAvatar.hideBookButton()
        self.shtickerBookStateData.exit()
        if doneStatus['mode'] == 'exit':
            base.localAvatar.b_setAnimState('closeBook', self.__handleBookCloseExit)
        elif doneStatus['mode'] == 'teleport':
            base.localAvatar.b_setAnimState('closeBook', self.__handleBookCloseTeleport, [doneStatus])
        elif doneStatus['mode'] == 'resume':
            base.localAvatar.b_setAnimState('closeBook', self.__handleBookCloseResume, [doneStatus])
        elif doneStatus['mode'] == 'switchShard':
            base.localAvatar.b_setAnimState('closeBook', self.__handleBookCloseSwitchShard, [doneStatus])

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
            
        self.fsm.request('walk')

    def __handleBookCloseTeleport(self, requestStatus):
        self.fsm.request('teleportOut', [requestStatus])

    def __teleportOutDone(self, requestStatus):
        if base.localAvatar.getMyBattle() is not None:
            base.localAvatar.getMyBattle().d_left()
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def __handleBookCloseExit(self):
        base.localAvatar.b_setAnimState('teleportOut', self.__handleBookExitTeleport)

    def __handleBookExitTeleport(self):
        base.transitions.fadeOut(0.0)
        base.cr.gameFSM.request('closeShard')

    def exitShtickerBook(self):
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.disableLaffMeter()
        self.ignore(self.shtickerBookStateData.doneEvent)
        self.shtickerBookStateData.exit()
        self.shtickerBookStateData.unload()
        del self.shtickerBookStateData
        base.localAvatar.hideBookButton()
        self.ignore('escape-up')

    def enterStop(self, doNeutral = 1):
        if doNeutral:
            base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.createLaffMeter()
        base.localAvatar.createMoney()
        #base.localAvatar.showBookButton()
        base.localAvatar.enableGags(0)

    def exitStop(self):
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        base.localAvatar.disableLaffMeter()
        base.localAvatar.disableMoney()
        base.localAvatar.disableGags()
        #base.localAvatar.hideBookButton()

    def load(self):
        StateData.load(self)
        self.walkDoneEvent = "walkDone"
        self.walkStateData = PublicWalk(self.fsm, self.walkDoneEvent)
        self.walkStateData.load()

    def unload(self):
        StateData.unload(self)
        del self.walkDoneEvent
        self.walkStateData.unload()
        del self.walkStateData
        del self.loader

    def enterTeleportIn(self, requestStatus):
        base.transitions.irisIn()
        self.nextState = requestStatus.get('nextState', 'walk')
        if requestStatus['avId'] != base.localAvatar.doId:
            av = base.cr.doId2do.get(requestStatus['avId'])
            if av:
                base.localAvatar.gotoNode(av)
                base.localAvatar.b_setChat("Hi, %s." % av.getName())
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.startPosHprBroadcast()
        globalClock.tick()
        base.localAvatar.b_setAnimState('teleportIn', callback = self.teleportInDone)
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setParent(CIGlobals.SPRender)
        return

    def exitTeleportIn(self):
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        base.localAvatar.stopPosHprBroadcast()
        return

    def teleportInDone(self):
        if hasattr(self, 'fsm'):
            self.fsm.request(self.nextState, [1])

    def enterAcknowledgeDeath(self, foo = 0):
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
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
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()

    def enterDied(self, requestStatus, callback = None):
        if callback == None:
            callback = self.__diedDone
        base.localAvatar.createLaffMeter()
        base.localAvatar.attachCamera()
        base.localAvatar.b_setAnimState('died', callback, [requestStatus])

    def __diedDone(self, requestStatus):
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def exitDied(self):
        base.localAvatar.disableLaffMeter()
        base.localAvatar.detachCamera()

    def enterWalk(self, teleportIn = 0):
        self.walkStateData.enter()
        if teleportIn == 0:
            self.walkStateData.fsm.request('walking')
        self.acceptOnce(self.walkDoneEvent, self.handleWalkDone)
        self.walkStateData.fsm.request('walking')
        self.watchTunnelSeq = Sequence(Wait(1.0), Func(LinkTunnel.globalAcceptCollisions))
        self.watchTunnelSeq.start()
        base.localAvatar.setBusy(0)
        base.localAvatar.enablePicking()
        base.localAvatar.showFriendButton()
        NametagGlobals.setWantActiveNametags(True)
        NametagGlobals.makeTagsReady()
        if self.useFirstPerson:
            if base.localAvatar.getMyBattle():
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
                base.localAvatar.chatInput.disableKeyboardShortcuts()

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
        base.localAvatar.hideFriendButton()
        if base.localAvatar.friendsList:
            base.localAvatar.friendsList.fsm.requestFinalState()
        if base.localAvatar.panel:
            base.localAvatar.panel.fsm.requestFinalState()
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
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.b_setAnimState('teleportOut', callback, [requestStatus])

    def exitTeleportOut(self):
        base.localAvatar.disableLaffMeter()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        base.localAvatar.stopPosHprBroadcast()

    def enterTunnelIn(self, linkTunnel):
        zoneId = linkTunnel.data['zoneId']
        base.localAvatar.sendUpdate('goThroughTunnel', [zoneId, 0])
        base.localAvatar.attachCamera()
        base.localAvatar.playMovementSfx("run")

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
        base.localAvatar.reparentTo(render)
        base.localAvatar.detachCamera()
        base.localAvatar.walkControls.setCollisionsActive(1)

    def enterTunnelOut(self, requestStatus):
        zone = requestStatus['fromZone']
        base.localAvatar.sendUpdate('goThroughTunnel', [zone, 1])
        base.localAvatar.playMovementSfx("run")
        base.transitions.irisIn()
        self.nextState = requestStatus.get('nextState', 'walk')
        base.localAvatar.goThroughTunnel(zone, 1)

    def exitTunnelOut(self):
        base.localAvatar.playMovementSfx(None)
        base.localAvatar.walkControls.setCollisionsActive(1)
        base.localAvatar.detachCamera()
        del self.nextState

    def enterNoAccessFA(self):
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.createLaffMeter()
        base.localAvatar.createMoney()

        noAccess = "Watch out!\n\nThis neighborhood is too dangerous for your Toon. Complete Quests to unlock this neighborhood."
        self.dialog = GlobalDialog(noAccess, 'noAccessAck', Ok)
        self.acceptOnce('noAccessAck', self.__handleNoAccessAck)
        self.dialog.show()

    def __handleNoAccessAck(self):
        self.fsm.request('walk')

    def exitNoAccessFA(self):
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        base.localAvatar.disableLaffMeter()
        base.localAvatar.disableMoney()

        if hasattr(self, 'dialog'):
            self.dialog.cleanup()
            del self.dialog
