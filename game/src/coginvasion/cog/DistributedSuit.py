"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSuit.py
@author Maverick Liberty
@date September 01, 2015

"""

from panda3d.core import Point3, VBase4

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.distributed.DelayDeletable import DelayDeletable
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import SoundInterval, LerpPosInterval, ProjectileInterval, LerpHprInterval
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Func, Wait, Parallel
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from src.coginvasion.globals import CIGlobals
from src.coginvasion.npc.NPCWalker import NPCWalkInterval
from src.coginvasion.battle import BattleGlobals

from SuitState import SuitState
from SuitBank import SuitPlan
from Suit import Suit
from SpawnMode import SpawnMode
from SuitUtils import getMoveIvalFromPath
import SuitBank
import SuitGlobals
import Voice
import Variant
import SuitAttacks

import types, random

class DistributedSuit(Suit, DistributedAvatar, DistributedSmoothNode, DelayDeletable):
    notify = directNotify.newCategory('DistributedSuit')

    def __init__(self, cr):
        Suit.__init__(self)
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)

        self.anim = None
        self._state = SuitState.ALIVE
        self.dept = None
        self.variant = None
        self.suitPlan = None
        self.level = None
        self.moveIval = None
        self.hpFlash = None

        # For PythonCTMusicManager:
        # Are we in range of the localAvatar?
        self.isInRange = False

        self.chaseTarget = 0

        self.suitFSM = ClassicFSM('DistributedSuit',
            [
                State('off', self.enterSuitOff, self.exitSuitOff),
                State('walking', self.enterWalking, self.exitWalking),
                State('flyingDown', self.enterFlyingDown, self.exitFlyingDown),
                State('flyingUp', self.enterFlyingUp, self.exitFlyingUp),
                State('lured', self.enterLured, self.exitLured)
            ],
            'off', 'off'
        )
        self.stateIndex2suitState = {}
        self.suitFSM.enterInitialState()
        self.makeStateDict()

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
        self.moveIval.start(elapsedT)

    def clearMoveTrack(self):
        if self.moveIval:
            self.ignore(self.moveIval.getDoneEvent())
            self.moveIval.pause()
            self.moveIval = None
        if not self.isDead():
            self.animFSM.request('neutral')

    def exitWalking(self):
        self.clearMoveTrack()
        if not self.isDead():
            self.animFSM.request('neutral')

    def enterFlyingDown(self, startIndex, endIndex, ts = 0.0):
        if self.getHood() != '' and startIndex != -1 and endIndex != -1:
            duration = 3.5
            startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
            startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint] + (0, 0, 6.5 * 4.8)
            endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
            endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint]
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
                startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
                startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint]
            else:
                startPos = self.getPos(render)
            if endIndex > -1:
                endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
                endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint] + (0, 0, 6.5 * 4.8)
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
        if self.level == 12:
            self.maxHealth = 200
        elif self.level > 0:
            self.maxHealth = (self.level + 1) * (self.level + 2)
        else:
            self.maxHealth = 1
        self.health = self.maxHealth
        self.updateHealthBar(self.health)

    def getLevel(self):
        return self.level

    def startMoveInterval(self, startX, startY, startZ, endX, endY, endZ, duration):
        self.stopMoving()
        endPos = Point3(endX, endY, endZ)
        self.moveIval = NPCWalkInterval(self, endPos,
            durationFactor = duration, fluid = 1)
        self.moveIval.start()

    def stopMoveInterval(self, andTurnAround = 0):
        if self.moveIval:
            self.moveIval.pause()
            self.moveIval = None
        if andTurnAround == 1:
            if self.health > 0:
                self.animFSM.request('neutral')
            self.setH(self.getH() - 180)

    def toggleRay(self, ray = 1):
        if ray:
            Suit.initializeRay(self, self.avatarType, 2)
        else:
            Suit.disableRay(self)

    def startProjInterval(self, startX, startY, startZ, endX, endY, endZ, duration, gravityMult, ts = 0):
        if isinstance(ts, int) and ts != 0:
            ts = globalClockDelta.localElapsedTime(ts)

        self.disableRay()
        self.stopMoveInterval()
        startPos = Point3(startX, startY, startZ)
        endPos = Point3(endX, endY, endZ)
        oldHpr = self.getHpr(render)
        self.headsUp(endPos)
        newHpr = self.getHpr(render)
        self.setHpr(oldHpr)
        self.moveIval = Parallel(
            LerpHprInterval(self, duration = 0.5, hpr = newHpr, startHpr = oldHpr, blendType = 'easeInOut'),
            Sequence(
                Func(self.animFSM.request, 'flyAway', [ts]),
                Wait(3.5),
                Func(self.animFSM.request, 'flyDown', [1.0])
            ),
            Sequence(
                Wait(2.0),
                Func(self.headsUp, endPos),
                ProjectileInterval(self,
                    startPos = startPos,
                    endPos = endPos,
                    gravityMult = gravityMult,
                    duration = duration)
            )
        )
        self.moveIval.start(ts)

    def startPosInterval(self, startX, startY, startZ, endX, endY, endZ, duration, blendType, ts = 0.0):
        if ts != 0.0:
            ts = globalClockDelta.localElapsedTime(ts)
        self.stopMoveInterval()
        startPos = Point3(startX, startY, startZ)
        endPos = Point3(endX, endY, endZ)
        self.moveIval = LerpPosInterval(self,
            duration = duration,
            pos = endPos,
            startPos = startPos,
            blendType = blendType
        )
        self.moveIval.start(ts)

    def stopMoving(self, finish = 0):
        if self.moveIval:
            if finish:
                self.moveIval.finish()
            else:
                self.moveIval.pause()
            self.moveIval = None

    def d_disableMovement(self, wantRay = False):
        self.sendUpdate('disableMovement', [])
        self.interruptAttack()
        self.stopMoving()
        if not wantRay:
            Suit.disableRay(self)

    def d_enableMovement(self):
        self.sendUpdate('enableMovement', [])
        Suit.initializeRay(self, self.avatarType, 2)

    def startRay(self):
        Suit.initializeRay(self, self.avatarType, 2)

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
            if self.isInRange:
                self.isInRange = False
            self.interruptAttack()

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

        Suit.generate(self,
            plan,
            variant,
            voice = voice
        )
        self.suitPlan = plan
        self.variant = Variant.getVariantById(variant)

    def getSuit(self):
        return tuple((self.suitPlan, self.variant))

    def spawn(self, startIndex, endIndex, spawnMode = SpawnMode.FLYDOWN):
        if spawnMode == SpawnMode.FLYDOWN:
            startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
            startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint] + (0, 0, 50)
            endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
            endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint]
            if self.moveIval:
                self.moveIval.finish()
                self.moveIval = None
            self.moveIval = LerpPosInterval(self, duration = 3, pos = endPos, startPos = startPos, fluid = 1)

    def makeStateDict(self):
        self.stateIndex2suitState = {
            0 : self.suitFSM.getStateNamed('off'),
            1 : self.suitFSM.getStateNamed('walking'),
            2 : self.suitFSM.getStateNamed('flyingDown'),
            3 : self.suitFSM.getStateNamed('flyingUp'),
            4 : self.suitFSM.getStateNamed('lured')
        }
        self.suitState2stateIndex = {}
        for stateId, state in self.stateIndex2suitState.items():
            self.suitState2stateIndex[state.getName()] = stateId

    def setSuitState(self, index, startPoint, endPoint, timestamp = None):
        if timestamp != None:
            ts = globalClockDelta.localElapsedTime(timestamp)
        else:
            ts = 0.0

        self.suitState = self.stateIndex2suitState[index]
        self.startPoint = startPoint
        self.endPoint = endPoint

        self.suitFSM.request(self.suitState, [startPoint, endPoint, ts])

    def getSuitState(self):
        return self.suitState

    def setAnimState(self, anim, loop = 1, timestamp = None):
        prevAnim = self.anim
        self.anim = anim

        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        if type(anim) == types.IntType:
            if anim != 44 and anim != 45:
                anim = SuitGlobals.getAnimById(anim)
                animName = anim.getName()
            elif anim == 44:
                animName = 'die'
            elif anim == 45:
                animName = 'flyNeutral'
        elif type(anim) == types.StringType:
            animName = anim

        if self.animFSM.hasStateNamed(animName):
            self.animFSM.request(animName, [ts])
        else:
            if loop:
                self.loop(animName)
            else:
                self.play(animName)
        messenger.send(SuitGlobals.animStateChangeEvent % (self.uniqueName), [anim, prevAnim])

    def doAttack(self, attackId, avId, timestamp = None):
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        attackName = SuitAttacks.SuitAttackLengths.keys()[attackId]
        attackTaunt = CIGlobals.SuitAttackTaunts[attackName][random.randint(0, len(CIGlobals.SuitAttackTaunts[attackName]) - 1)]
        avatar = self.cr.doId2do.get(avId)

        shouldChat = random.randint(*BattleGlobals.AttackTauntChance) == BattleGlobals.AttackTauntChance[0]
        if shouldChat:
            self.setChat(attackTaunt)

        self.animFSM.request('attack', [attackName, avatar, 0.0])

    def throwObject(self):
        self.acceptOnce('enter' + self.wsnp.node().getName(), self.__handleWeaponCollision)
        Suit.throwObject(self)

    def __handleWeaponCollision(self, entry):
        self.sendUpdate('toonHitByWeapon', [self.attack, base.localAvatar.doId])
        base.localAvatar.handleHitByWeapon(self.attack, self)
        self.b_handleWeaponTouch()

    def b_handleWeaponTouch(self):
        self.sendUpdate('handleWeaponTouch', [])
        self.handleWeaponTouch()

    def __monitorLocalAvDistance(self, task):
        if not hasattr(base, 'localAvatar'):
            return task.done

        return task.cont

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        self.setAnimState('neutral')

        # Picked up by DistributedBattleZone:
        messenger.send('suitCreate', [self])

        base.taskMgr.add(self.__monitorLocalAvDistance, self.uniqueName('monitorLocalAvDistance'))

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)

    def disable(self):
        # Picked up by DistributedBattleZone:
        messenger.send('suitDelete', [self])

        base.taskMgr.remove(self.uniqueName('monitorLocalAvDistance'))
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
        DistributedSmoothNode.delete(self)
