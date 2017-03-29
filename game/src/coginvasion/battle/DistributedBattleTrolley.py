# Filename: DistributedBattleTrolley.py
# Created by:  blach (25Oct15)
#
# This is a new way to go into the future to battle -- the trolley.

from pandac.PandaModules import Point3, Vec3, TextNode, Fog

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import LerpPosInterval, LerpHprInterval, LerpQuatInterval, ActorInterval, Parallel, Sequence, Wait, Func
from direct.interval.IntervalGlobal import SoundInterval, LerpFunctionInterval

from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil
import math

TROLLEY_ENTER_TIME = 5.0
TROLLEY_EXIT_TIME = 5.0

class DistributedBattleTrolley(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleTrolley')

    STAND_POSITIONS = [
        Point3(-4.75, -5, 1.4),
        Point3(-4.75, -1.6, 1.4),
        Point3(-4.75, 1.6, 1.4),
        Point3(-4.75, 5, 1.4),
        Point3(-4.75, -5, 1.4),
        Point3(-4.75, -1.6, 1.4),
        Point3(-4.75, 1.6, 1.4),
        Point3(-4.75, 5, 1.4)
    ]
    TROLLEY_NEUTRAL_POS = Point3(15, 14, -1)
    TROLLEY_GONE_POS = Point3(50, 14.1588, -0.984615)
    TROLLEY_ARRIVING_START_POS = Point3(-20, 14.1588, -0.984615)
    CAM_POS = Point3(-35, 0, 8)
    CAM_HPR = Vec3(-90, 0, 0)

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedBattleTrolley', [State.State('off', self.enterOff, self.exitOff),
         State.State('wait', self.enterWait, self.exitWait),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('leaving', self.enterLeaving, self.exitLeaving),
         State.State('arriving', self.enterArriving, self.exitArriving)], 'off', 'off')
        self.fsm.enterInitialState()
        self.trolleyStation = None
        self.trolleyCar = None
        self.trolleyKey = None
        self.countdownText = None
        self.trolleyAwaySfx = base.loadSfx('phase_4/audio/sfx/SZ_trolley_away.ogg')

        if self.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.trolleyAwaySfx = base.loadSfx('winter/audio/sfx/SZ_trolley_away.mp3')

        self.trolleyBellSfx = base.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.ogg')
        self.toZone = 0
        self.localAvOnTrolley = False
        self.trolleyEnterTrack = None
        self.trolleyExitTrack = None
        self.hoodAbbr = ""
        self.index = 0
        self.mySlot = -1
        
    def setIndex(self, index):
        self.index = index
        
        hood = self.cr.playGame.hood
        hoodAbbr = None
        
        if self.index == 0:
            hoodAbbr = hood.abbr
        elif self.index == 1:
            hoodAbbr = CIGlobals.ZoneId2HoodAbbr[self.toZone]
        self.hoodAbbr = hoodAbbr
        
        findStr = '**/prop_trolley_station_' + hoodAbbr + '_DNARoot'
        
        self.trolleyStation = hood.loader.geom.find(findStr)
        self.trolleyCar = self.trolleyStation.find('**/trolley_car')
        self.trolleyKey = self.trolleyStation.find('**/key')

        exitFog = Fog('TrolleyExitFog')
        exitFog.setColor(0.0, 0.0, 0.0)
        exitFog.setLinearOnsetPoint(30.0, 14.0, 0.0)
        exitFog.setLinearOpaquePoint(37.0, 14.0, 0.0)
        exitFog.setLinearFallback(70.0, 999.0, 1000.0)
        self.trolleyExitFog = self.trolleyStation.attachNewNode(exitFog)
        self.trolleyExitFogNode = exitFog
        enterFog = Fog('TrolleyEnterFog')
        enterFog.setColor(0.0, 0.0, 0.0)
        enterFog.setLinearOnsetPoint(0.0, 14.0, 0.0)
        enterFog.setLinearOpaquePoint(-7.0, 14.0, 0.0)
        enterFog.setLinearFallback(70.0, 999.0, 1000.0)
        self.trolleyEnterFog = self.trolleyStation.attachNewNode(enterFog)
        self.trolleyEnterFogNode = enterFog
        self.trolleyCar.setFogOff()

        tn = TextNode('trolleycountdowntext')
        tn.setFont(CIGlobals.getMickeyFont())
        tn.setTextColor(1, 0, 0, 1)
        tn.setAlign(TextNode.ACenter)

        self.keys = self.trolleyCar.findAllMatches('**/key')
        self.numKeys = self.keys.getNumPaths()
        self.keyInit = []
        self.keyRef = []
        for i in range(self.numKeys):
            key = self.keys[i]
            key.setTwoSided(1)
            ref = self.trolleyCar.attachNewNode('key' + `i` + 'ref')
            ref.iPosHpr(key)
            self.keyRef.append(ref)
            self.keyInit.append(key.getTransform())

        self.frontWheels = self.trolleyCar.findAllMatches('**/front_wheels')
        self.numFrontWheels = self.frontWheels.getNumPaths()
        self.frontWheelInit = []
        self.frontWheelRef = []
        for i in range(self.numFrontWheels):
            wheel = self.frontWheels[i]
            ref = self.trolleyCar.attachNewNode('frontWheel' + `i` + 'ref')
            ref.iPosHpr(wheel)
            self.frontWheelRef.append(ref)
            self.frontWheelInit.append(wheel.getTransform())

        self.backWheels = self.trolleyCar.findAllMatches('**/back_wheels')
        self.numBackWheels = self.backWheels.getNumPaths()
        self.backWheelInit = []
        self.backWheelRef = []
        for i in range(self.numBackWheels):
            wheel = self.backWheels[i]
            ref = self.trolleyCar.attachNewNode('backWheel' + `i` + 'ref')
            ref.iPosHpr(wheel)
            self.backWheelRef.append(ref)
            self.backWheelInit.append(wheel.getTransform())

        trolleyAnimationReset = Func(self.resetAnimation)
        trolleyEnterStartPos = Point3(-20, 14, -1)
        trolleyEnterEndPos = Point3(15, 14, -1)
        trolleyEnterPos = Sequence(name='TrolleyEnterPos')
        trolleyEnterPos.append(Func(self.trolleyCar.setFog, self.trolleyEnterFogNode))
        trolleyEnterPos.append(self.trolleyCar.posInterval(TROLLEY_ENTER_TIME, trolleyEnterEndPos, startPos=trolleyEnterStartPos, blendType='easeOut'))
        trolleyEnterPos.append(Func(self.trolleyCar.setFogOff))
        trolleyEnterTrack = Sequence(trolleyAnimationReset, trolleyEnterPos, name='trolleyEnter')
        keyAngle = round(TROLLEY_ENTER_TIME) * 360
        dist = Vec3(trolleyEnterEndPos - trolleyEnterStartPos).length()
        wheelAngle = dist / (2.0 * math.pi * 0.95) * 360
        trolleyEnterAnimateInterval = LerpFunctionInterval(self.animateTrolley, duration=TROLLEY_ENTER_TIME, blendType='easeOut', extraArgs=[keyAngle, wheelAngle], name='TrolleyAnimate')
        trolleyEnterSoundTrack = SoundInterval(self.trolleyAwaySfx, node=self.trolleyCar)
        self.trolleyEnterTrack = Parallel(trolleyEnterTrack, trolleyEnterAnimateInterval, trolleyEnterSoundTrack)
        trolleyExitStartPos = Point3(15, 14, -1)
        trolleyExitEndPos = Point3(50, 14, -1)
        trolleyExitPos = Sequence(name='TrolleyExitPos')
        trolleyExitPos.append(Func(self.trolleyCar.setFog, self.trolleyExitFogNode))
        trolleyExitPos.append(self.trolleyCar.posInterval(TROLLEY_EXIT_TIME, trolleyExitEndPos, startPos=trolleyExitStartPos, blendType='easeIn'))
        trolleyExitPos.append(Func(self.trolleyCar.setFogOff))
        trolleyExitStartPos = Point3(15, 14, -1)
        trolleyExitEndPos = Point3(50, 14, -1)
        trolleyExitBellInterval = SoundInterval(self.trolleyBellSfx, node=self.trolleyCar)
        trolleyExitAwayInterval = SoundInterval(self.trolleyAwaySfx, node=self.trolleyCar)
        keyAngle = round(TROLLEY_EXIT_TIME) * 360
        dist = Vec3(trolleyExitEndPos - trolleyExitStartPos).length()
        wheelAngle = dist / (2.0 * math.pi * 0.95) * 360
        trolleyExitAnimateInterval = LerpFunctionInterval(self.animateTrolley, duration=TROLLEY_EXIT_TIME, blendType='easeIn', extraArgs=[keyAngle, wheelAngle], name='TrolleyAnimate')
        self.trolleyExitTrack = Parallel(trolleyExitPos, trolleyExitBellInterval, trolleyExitAwayInterval, trolleyExitAnimateInterval, name=self.uniqueName('trolleyExit'))

        self.countdownText = self.trolleyStation.attachNewNode(tn)
        self.countdownText.setScale(3.0)
        self.countdownText.setPos(14.58, 10.77, 11.17)
        
        try:
            self.trolleyStation.find('**/trolley_sphere').setName('trolley{0}_sphere'.format(hoodAbbr))
        except:
            pass
        
    def getIndex(self):
        return self.index
        
    def putAvatarInTrolley(self, avId, slot):
        av = self.cr.doId2do.get(avId)
        if av:
            av.stopSmooth()
            av.wrtReparentTo(self.trolleyCar)
            av.setAnimState('off')
            slotPos = self.STAND_POSITIONS[slot]
            av.setPos(slotPos)
            if slot <= 3:
                av.loop('sit')
            else:
                av.loop('neutral')
            av.setHpr(90, 0, 0)

    def headOff(self):
        hoodId = ZoneUtil.getHoodId(self.toZone)
        requestStatus = {'zoneId': self.toZone,
                    'hoodId': hoodId,
                    'where': 'playground',
                    'avId': base.localAvatar.doId,
                    'loader': 'safeZoneLoader',
                    'shardId': None,
                    'wantLaffMeter': 1,
                    'how': 'trolleyOut',
                    'prevZoneId': base.localAvatar.zoneId,
                    'slot': self.mySlot}
        self.cr.playGame.getPlace().doneStatus = requestStatus
        messenger.send(self.cr.playGame.getPlace().doneEvent)
        base.localAvatar.reparentTo(render)
        base.localAvatar.setPos(0, 0, 0)
        base.localAvatar.setHpr(0, 0, 0)
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.localAvOnTrolley = False

    def setToZone(self, zone):
        self.toZone = zone

    def getToZone(self):
        return self.toZone

    def enterOff(self, ts = 0):
        pass

    def exitOff(self):
        pass
        
    def __maybeAcceptCollisions(self):
        if self.fsm.getCurrentState().getName() in ['wait', 'waitCountdown'] and not self.localAvOnTrolley:
            self.acceptOnce('entertrolley{0}_sphere'.format(self.hoodAbbr), self.__handleTrolleyTrigger)
            
    def __ignoreCollisions(self):
        self.ignore('entertrolley{0}_sphere'.format(self.hoodAbbr))

    def enterWait(self, ts = 0):
        self.trolleyCar.setPos(self.TROLLEY_NEUTRAL_POS)
        self.__maybeAcceptCollisions()

    def exitWait(self):
        self.__ignoreCollisions()

    def enterWaitCountdown(self, ts = 0):
        self.trolleyCar.setPos(self.TROLLEY_NEUTRAL_POS)
        self.__maybeAcceptCollisions()
        if self.countdownText:
            self.countdownTrack = Sequence()
            for i in range(20):
                self.countdownTrack.append(Func(self.countdownText.node().setText, str(20 - i)))
                self.countdownTrack.append(Wait(1.0))
            self.countdownTrack.start()

    def exitWaitCountdown(self):
        self.__ignoreCollisions()
        if hasattr(self, 'countdownTrack'):
            self.countdownTrack.finish()
            del self.countdownTrack
        if self.countdownText:
            self.countdownText.node().setText('')
        self.disableExitButton()

    def enterArriving(self, ts = 0):
        if self.localAvOnTrolley == True:
            CIGlobals.hideWaitForOthers()
            camera.wrtReparentTo(self.trolleyCar)
            camera.setPos(0, -18.55, 3.75)
            camera.setHpr(0, 0, 0)
            Sequence(Wait(2.0), camera.posHprInterval(3, self.CAM_POS, self.CAM_HPR, startPos = (0, -18.55, 3.75), startHpr = (0, 0, 0), blendType='easeInOut')).start()
        self.trolleyEnterTrack.start(ts)

    def exitArriving(self):
        if self.trolleyEnterTrack:
            self.trolleyEnterTrack.finish()

    def enterLeaving(self, ts = 0):
        base.playSfx(self.trolleyBellSfx, node = self.trolleyCar)
        if self.localAvOnTrolley == True:
            camera.posHprInterval(3, (0, 18.55, 3.75), (-180, 0, 0), blendType='easeInOut').start()
            self.trolleyExitTrack.append(Sequence(Wait(4.0), Func(base.transitions.fadeOut), Wait(1.0), Func(self.headOff)))
        self.trolleyExitTrack.start(ts)
        self.__ignoreCollisions()

    def exitLeaving(self):
        if self.trolleyExitTrack:
            self.trolleyExitTrack.finish()

    def setState(self, stateName, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.fsm.request(stateName, [ts])

    def __handleTrolleyTrigger(self, entry):
        # workaround for a bug that i don't understand why it happens
        if not hasattr(self, 'cr'):
            self.cr = base.cr
            
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.disableGags()
        self.notify.info('Waiting for response from server to enter trolley')
        self.sendUpdate('requestBoard')
        base.localAvatar.walkControls.setCollisionsActive(0)

    def rejectBoard(self):
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')
        self.__maybeAcceptCollisions()

    def fillSlot(self, index, avId):
        if avId == base.localAvatar.doId:
            self.localAvOnTrolley = True
            base.localAvatar.stopSmartCamera()
            base.camera.wrtReparentTo(self.trolleyCar)
            camTrack = Sequence(Parallel(
             LerpPosInterval(
              base.camera,
              duration = 1.5,
              pos = self.CAM_POS,
              startPos = base.camera.getPos(),
              blendType = 'easeOut'
             ),
             LerpQuatInterval(
              base.camera,
              duration = 1.5,
              hpr = self.CAM_HPR,
              startHpr = base.camera.getHpr(),
              blendType = 'easeOut'
             )
            ), Func(self.enableExitButton))
            camTrack.start()
            self.mySlot = index

        toon = self.cr.doId2do.get(avId)
        toon.stopSmooth()
        if toon:
            toon.wrtReparentTo(self.trolleyCar)
            slotPos = self.STAND_POSITIONS[index]
            toon.headsUp(slotPos)
            track = Sequence(
                Func(toon.setAnimState, 'run'),
                LerpPosInterval(toon, 0.75, slotPos),
                LerpHprInterval(toon, 0.25, Point3(90, 0, 0)))
            if index <= 3:
                sitStartDuration = toon.getDuration('start-sit')
                track.append(Parallel(ActorInterval(toon, 'start-sit'),
                                      Sequence(Wait(sitStartDuration * 0.25),
                                               LerpPosInterval(toon, sitStartDuration * 0.25, Point3(-3.9, -4.5 + index * 3, 3.0)))))
                track.append(Func(toon.loop, 'sit'))
            else:
                track.append(Func(toon.loop, 'neutral'))
            track.start()
        

    def enableExitButton(self):
        if self.fsm.getCurrentState().getName() != 'leaving':
            self.exitButton = CIGlobals.getExitButton(cmd = self.__handleExitButton, pos = (0, 0, -0.8))

    def __handleExitButton(self):
        if self.fsm.getCurrentState().getName() == 'waitCountdown' and self.localAvOnTrolley == True:
            self.disableExitButton()
            self.sendUpdate('requestHopOff')

    def disableExitButton(self):
        if hasattr(self, 'exitButton'):
            self.exitButton.destroy()
            del self.exitButton

    def emptySlot(self, index, avId):
        toon = self.cr.doId2do.get(avId)
        toon.stopSmooth()
        currToonPos = toon.getPos(render)
        toon.wrtReparentTo(render)
        slotPos = self.STAND_POSITIONS[index]
        endPos = (-20, slotPos.getY(), 1.4)
        toon.setPos(self.trolleyCar, endPos)
        endPosWrtRender = toon.getPos(render)
        toon.setPos(currToonPos)
        toon.headsUp(self.trolleyCar, endPos)
        if index <= 3:
            track = Sequence(Parallel(
                ActorInterval(toon, 'start-sit', startTime=1, endTime=0.0),
                Sequence(Wait(0.5),
                    LerpPosInterval(toon, 0.25,
                    Point3(-5, -4.5 + index * 3, 1.4), other=self.trolleyCar))),
                    Func(toon.setAnimState, 'run'),
                    LerpPosInterval(toon, 1, Point3(21 - index * 3, -5, 0.02), other=self.trolleyStation),
                    Func(toon.setAnimState, 'neutral'),
                    Func(toon.startSmooth),
                name=toon.uniqueName('emptyTrolley'), autoPause=1)
        else:
            track = Sequence(
             Func(toon.setAnimState, 'run'),
             LerpPosInterval(
              toon,
              duration = 1.0,
              pos = endPosWrtRender,
              startPos = currToonPos
             ),
             Func(toon.setAnimState, 'neutral'),
             Func(toon.startSmooth)
            )
        if avId == base.localAvatar.doId:
            self.localAvOnTrolley = False
            track.append(Func(self.__hoppedOffTrolley))
        track.start()

    def __hoppedOffTrolley(self):
        self.acceptOnce('entertrolley_sphere', self.__handleTrolleyTrigger)
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')

    def resetAnimation(self):
        if self.keys:
            for i in range(self.numKeys):
                self.keys[i].setTransform(self.keyInit[i])

            for i in range(self.numFrontWheels):
                self.frontWheels[i].setTransform(self.frontWheelInit[i])

            for i in range(self.numBackWheels):
                self.backWheels[i].setTransform(self.backWheelInit[i])

    def animateTrolley(self, t, keyAngle, wheelAngle):
        if self.keys:
            for i in range(self.numKeys):
                key = self.keys[i]
                ref = self.keyRef[i]
                key.setH(ref, t * keyAngle)

            for i in range(self.numFrontWheels):
                frontWheel = self.frontWheels[i]
                ref = self.frontWheelRef[i]
                frontWheel.setH(ref, t * wheelAngle)

            for i in range(self.numBackWheels):
                backWheel = self.backWheels[i]
                ref = self.backWheelRef[i]
                backWheel.setH(ref, t * wheelAngle)

    def delete(self):
        self.trolleyStation = None
        self.trolleyKey = None
        self.soundMoving = None
        self.soundBell = None
        self.troleyCar = None
        self.backWheelInit = None
        self.backWheelRef = None
        self.backWheels = None
        self.frontWheelInit = None
        self.frontWheelRef = None
        self.frontWheels = None
        self.keyInit = None
        self.keyRef = None
        self.keys = None
        self.trolleyEnterTrack = None
        self.trolleyExitTrack = None
        self.trolleyExitFog = None
        self.trolleyExitFogNode = None
        self.trolleyEnterFogNode = None
        self.trolleyEnterFog = None

        self.ignore('entertrolley_sphere')
        DistributedObject.delete(self)
