"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSuit.py
@author Maverick Liberty
@date September 01, 2015

"""

from panda3d.core import VBase4

from direct.distributed.DelayDeletable import DelayDeletable
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import SoundInterval, LerpPosInterval
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Func, Wait
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar

from SuitBank import SuitPlan
from Suit import Suit
from SuitUtils import getMoveIvalFromPath
import SuitBank
import SuitGlobals
import Voice
import Variant

class DistributedSuit(Suit, DistributedAvatar, DelayDeletable):
    notify = directNotify.newCategory('DistributedSuit')

    def __init__(self, cr):
        Suit.__init__(self)
        DistributedAvatar.__init__(self, cr)

        self.anim = None
        self.dept = None
        self.variant = None
        self.suitPlan = None
        self.level = None
        self.moveIval = None
        self.hpFlash = None

        self.chaseTarget = 0

    def setChaseTarget(self, avId):
        self.chaseTarget = avId

    def setWalkPath(self, path, timestamp):
        elapsedT = globalClockDelta.localElapsedTime(timestamp)
        self.suitFSM.request('walking', [path, elapsedT])

    def showAvId(self):
        self.setDisplayName(self.getName() + "\n" + str(self.doId))

    def showName(self):
        self.setDisplayName(self.getName())

    def setDisplayName(self, name):
        self.setupNameTag(tempName = name)

    def enterWalking(self, path, elapsedT):
        # path: A list of point2s.
        #
        # We will make a sequence of NPCWalkIntervals for each point2 in the path.

        self.clearMoveTrack()
        self.moveIval = getMoveIvalFromPath(self, path, elapsedT, True, 'suitMoveIval')
        self.moveIval.start()#elapsedT) # don't do the timestamp for now

    def clearMoveTrack(self):
        if self.moveIval:
            self.ignore(self.moveIval.getDoneEvent())
            self.moveIval.pause()
            self.moveIval = None
        if not self.isDead():
            self.animFSM.request('neutral')
        self.stopFootsteps()

    def exitWalking(self):
        self.clearMoveTrack()
        if not self.isDead():
            self.animFSM.request('neutral')

    def enterFlyingDown(self, startIndex, endIndex, ts = 0.0):
        if self.getHood() != '' and startIndex != -1 and endIndex != -1:
            duration = 3.5
            startPoint = CogBattleGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
            startPos = CogBattleGlobals.SuitSpawnPoints[self.getHood()][startPoint] + (0, 0, 6.5 * 4.8)
            endPoint = CogBattleGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
            endPos = CogBattleGlobals.SuitSpawnPoints[self.getHood()][endPoint]
            self.stopMoving(finish = 1)
            groundF = 28
            dur = self.getDuration('land')
            fr = self.getFrameRate('land')
            if fr:
                animTimeInAir = groundF / fr
            else:
                animTimeInAir = groundF
            impactLength = dur - animTimeInAir
            timeTillLanding = 6.5 - impactLength
            self.moveIval = LerpPosInterval(self, duration = timeTillLanding, pos = endPos, startPos = startPos, fluid = 1)
            self.moveIval.start(ts)
        self.animFSM.request('flyDown', [ts])

    def exitFlyingDown(self):
        self.stopMoving(finish = 1)
        self.animFSM.request('neutral')

    def enterFlyingUp(self, startIndex, endIndex, ts = 0.0):
        if self.getHood() != '':
            duration = 3
            if startIndex > -1:
                startPoint = CogBattleGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
                startPos = CogBattleGlobals.SuitSpawnPoints[self.getHood()][startPoint]
            else:
                startPos = self.getPos(render)
            if endIndex > -1:
                endPoint = CogBattleGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
                endPos = CogBattleGlobals.SuitSpawnPoints[self.getHood()][endPoint] + (0, 0, 6.5 * 4.8)
            else:
                endPos = self.getPos(render) + (0, 0, 6.5 * 4.8)

            self.stopMoving(finish = 1)
            groundF = 28
            dur = self.getDuration('land')
            fr = self.getFrameRate('land')
            if fr:
                animTimeInAir = groundF / fr
            else:
                animTimeInAir = groundF
            impactLength = dur - animTimeInAir
            timeTillLanding = 6.5 - impactLength
            self.moveIval = Sequence(Wait(impactLength), LerpPosInterval(self, duration = timeTillLanding, pos = endPos, startPos = startPos, fluid = 1))
            self.moveIval.start(ts)
        self.animFSM.request('flyAway', [ts, 1])

    def exitFlyingUp(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.animFSM.request('neutral')

    def enterLured(self, _, __, ___):
        self.loop('lured')

    def exitLured(self):
        self.stop()

    def enterSuitOff(self, foo1 = None, foo2 = None, foo3 = None):
        pass

    def exitSuitOff(self):
        pass

    def setName(self, name):
        Suit.setName(self, name, self.suitPlan.getName())

    def setLevel(self, level):
        self.level = level

    def getLevel(self):
        return self.level

    def toggleRay(self, ray = 1):
        if ray:
            self.enableRay()
        else:
            self.disableRay()
        pass

    def startRay(self):
        self.enableRay()

    def setHealth(self, health):
        if health > self.health:
            # We got an hp boost. Flash green.
            flashColor = VBase4(0, 1, 0, 1)
        elif health < self.health:
            # We got an hp loss. Flash red.
            flashColor = VBase4(1, 0, 0, 1)
        DistributedAvatar.setHealth(self, health)

        def doBossFlash():
            if not self.isEmpty():
                LerpColorScaleInterval(self, 0.2, flashColor).start()

        def clearBossFlash():
            if not self.isEmpty():
                self.clearColorScale()

        if self.isDead():
            self.setChaseTarget(0)
            base.taskMgr.remove(self.uniqueName('monitorLocalAvDistance'))
            #if self.isInRange:
            #    self.isInRange = False
            #self.gruntSound.play()

        if self.getLevel() > 12:
            if self.hpFlash:
                self.hpFlash.finish()
                self.hpFlash = None
            self.hpFlash = Sequence(
                Func(doBossFlash),
                Wait(0.2),
                Func(clearBossFlash)
            )
            self.hpFlash.start()
        self.updateHealthBar(health)

    def announceHealth(self, level, hp, extraId = -1):
        DistributedAvatar.announceHealth(self, level, hp, extraId)
        if level == 1:
            healthSfx = base.audio3d.loadSfx(SuitGlobals.healedSfx)
            base.audio3d.attachSoundToObject(healthSfx, self)
            SoundInterval(healthSfx, node = self).start()
            del healthSfx
        if hp < 0:
            self.doDamageFade()

    #
    #    'setSuit' sets the suit type and generates it.
    #    'arg' is an id for a SuitPlan as defined in SuitBank or
    #        an instance of SuitPlan.
    #    'variant' is an optional argument that sets the variant.
    #        It takes an id for the variant or an instance of Variant.
    #        Default is Variant.NORMAL.

    def setSuit(self, arg, variant = 0):
        if isinstance(arg, SuitPlan):
            plan = arg
        else:
            plan = SuitBank.getSuitById(arg)

        voice = Voice.NORMAL
        if variant:
            if isinstance(variant, (int, long, float, complex)):
                variant = Variant.getVariantById(variant)

        if plan.getForcedVoice():
            voice = plan.getForcedVoice()

        self.generateSuit(
            plan,
            variant,
            voice = voice
        )
        self.suitPlan = plan
        self.variant = Variant.getVariantById(variant)

    def getSuit(self):
        return tuple((self.suitPlan, self.variant))

    def stun(self, animB4Stun):
        self.animFSM.request('stunned', [animB4Stun])

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)

        # Picked up by DistributedBattleZone:
        messenger.send('suitCreate', [self])

        self.activateSmoothing(True, False)
        self.startSmooth()
        self.reparentTo(render)

    def generate(self):
        DistributedAvatar.generate(self)

    def disable(self):
        self.stopSmooth()

        # Picked up by DistributedBattleZone:
        messenger.send('suitDelete', [self])

        self.anim = None
        self._state = None
        self.dept = None
        self.variant = None
        self.suitPlan = None
        if self.hpFlash:
            self.hpFlash.finish()
            self.hpFlash = None
        if self.moveIval:
            self.moveIval.pause()
            self.moveIval = None
        Suit.disable(self)
        DistributedAvatar.disable(self)

    def delete(self):
        Suit.delete(self)
        del self.anim
        del self._state
        del self.dept
        del self.variant
        del self.suitPlan
        del self.moveIval
        DistributedAvatar.delete(self)
