# Filename: DistributedSuit.py
# Created by:  blach (02Nov14)

from panda3d.core import *
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from direct.distributed import DelayDelete
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.Suit import Suit
from direct.interval.IntervalGlobal import SoundInterval, LerpPosInterval, ProjectileInterval, Sequence, Wait, Func
from direct.distributed.DelayDeletable import DelayDeletable
from direct.distributed.ClockDelta import globalClockDelta
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from lib.coginvasion.hood import ZoneUtil
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
import random
import types
import SuitAttacks

class DistributedSuit(Suit, DistributedAvatar, DistributedSmoothNode, DelayDeletable):
    notify = directNotify.newCategory("DistributedSuit")

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1
        Suit.__init__(self)
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)

        self.suitFSM = ClassicFSM('DistributedSuit',
            [
                State('off', self.enterSuitOff, self.exitSuitOff),
                State('walking', self.enterWalking, self.exitWalking),
                State('flyingDown', self.enterFlyingDown, self.exitFlyingDown),
                State('flyingUp', self.enterFlyingUp, self.exitFlyingUp),
                State('bossFlying', self.enterBossFlying, self.exitBossFlying)
            ],
            'off', 'off'
        )
        self.suitFSM.enterInitialState()
        self.makeStateDict()
        self.makeAnimStateDict()

        # These are just default values, we'll set them later on.
        self.anim = None
        self.state = "alive"
        self.health = None
        self.type = None
        self.team = None
        self.head = None
        self.skeleton = 0
        self.battle = None
        self.suitState = None
        self.startPoint = None
        self.endPoint = None
        self.moveIval = None
        self.walkPaused = None
        self.animIval = None
        self.level = None
        return

    def d_disableMovement(self, wantRay = False):
        self.sendUpdate('disableMovement', [])
        self.interruptAttack()
        if not wantRay:
            Suit.disableRay(self)

    def d_enableMovement(self):
        self.sendUpdate('enableMovement', [])
        Suit.initializeRay(self, self.avatarType, 2)

    def startRay(self):
        Suit.initializeRay(self, self.avatarType, 2)

    def setLevel(self, level):
        self.level = level

    def getLevel(self):
        return self.level

    def makeStateDict(self):
        self.suitState2stateIndex = {}
        for state in self.suitFSM.getStates():
            self.suitState2stateIndex[state.getName()] = self.suitFSM.getStates().index(state)
        self.stateIndex2suitState = {v: k for k, v in self.suitState2stateIndex.items()}

    def makeAnimStateDict(self):
        self.animState2animId = {}
        for index in range(len(self.animFSM.getStates())):
            self.animState2animId[self.animFSM.getStates()[index].getName()] = index
        self.animId2animState = {v: k for k, v in self.animState2animId.items()}

    def setLatePos(self, x, y):
        self.setX(x)
        self.setY(y)

    def enterAttack(self, attack, target, ts = 0):
        Suit.enterAttack(self, attack, target, ts)
        if target:
            self.headsUp(target)

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

    def enterWalking(self, startIndex, endIndex, ts = 0.0):
        durationFactor = 0.2
        if startIndex > -1:
            startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
            startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint]
        else:
            startPos = self.getPos(render)
        endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
        endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint]

        if self.moveIval:
            self.moveIval.pause()
            self.moveIval = None

        self.moveIval = NPCWalkInterval(self, endPos, durationFactor, startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('walk')

    def exitWalking(self):
        if self.moveIval:
            self.moveIval.pause()
            self.moveIval = None
        if not self.isDead():
            self.animFSM.request('off')

    def enterFlyingDown(self, startIndex, endIndex, ts = 0.0):
        duration = 3
        startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
        startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint] + (0, 0, 50)
        endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
        endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint]
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.moveIval = LerpPosInterval(self, duration = duration, pos = endPos, startPos = startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('flydown', [ts])
        yaw = random.uniform(0.0, 360.0)
        self.setH(yaw)

    def exitFlyingDown(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.animFSM.request('off')

    def enterFlyingUp(self, startIndex, endIndex, ts = 0.0):
        duration = 3
        startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
        endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
        startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint]
        endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint] + (0, 0, 50)

        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None

        self.moveIval = LerpPosInterval(self, duration = duration, pos = endPos, startPos = startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('flyaway', [ts])

    def exitFlyingUp(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.animFSM.request('off')

    def enterBossFlying(self, startIndex, endIndex, ts = 0.0):
        duration = 3.5
        startPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[startIndex]
        endPoint = CIGlobals.SuitSpawnPoints[self.getHood()].keys()[endIndex]
        startPos = CIGlobals.SuitSpawnPoints[self.getHood()][startPoint]
        endPos = CIGlobals.SuitSpawnPoints[self.getHood()][endPoint]

        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None

        self.animIval = Sequence(
            Func(self.animFSM.request, 'flyaway', [ts]),
            Wait(1.0),
            Func(self.animFSM.request, 'flydown', [ts])
        )

        self.moveIval = Sequence(
            Wait(0.5),
            Func(self.headsUp, endPos),
            ProjectileInterval(
                self,
                startPos = startPos,
                endPos = endPos,
                gravityMult = 0.25,
                duration = duration
            )
        )
        self.moveIval.start(ts)
        self.animIval.start(ts)

    def exitBossFlying(self):
        if self.animIval:
            self.animIval.finish()
            self.animIval = None
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.animFSM.request('off')

    def enterSuitOff(self, foo1 = None, foo2 = None, foo3 = None):
        pass

    def exitSuitOff(self):
        pass

    #def setWalking(self, value, startPos, endPath, timestamp = None):
    #
    #
    #	self.value = value
    #	self.startPath = startPath
    #	self.endPath = endPath
    #
    #	if self.walkIval:
    #		self.walkIval.finish()
    #		self.walkIval = None
    #
    #	if value:
    #		durationFactor = 0.2
    #		path = CIGlobals.SuitSpawnPoints.values()[endPath]
    #		self.walkIval = NPCWalkInterval(self, path, startPos = self.getPos(render), name = pathName, durationFactor = durationFactor, fluid = 1)

    def setBattle(self, battle):
        self.battle = battle

    def getBattle(self):
        return self.battle

    def printPos(self, task):
        print self.getPos(render)
        print self.getHpr(render)
        return task.cont

    def announceHealth(self, level, hp):
        DistributedAvatar.announceHealth(self, level, hp)
        if level == 1:
            healthSfx = base.audio3d.loadSfx("phase_3/audio/sfx/health.mp3")
            base.audio3d.attachSoundToObject(healthSfx, self)
            SoundInterval(healthSfx).start()
            del healthSfx

    def setSuit(self, suitType, head, team, skeleton):
        for obj in self.cr.doId2do.values():
            if obj.zoneId == self.zoneId:
                if obj.__class__.__name__ == "DistributedCogBattle":
                    # This has to be the Cog Battle we're in because it's in the same zone.
                    self.setBattle(obj)
        hp = CIGlobals.SuitHealthAmounts[head]
        Suit.generateSuit(self, suitType, head, team, hp, skeleton)

    def getSuit(self):
        return tuple((self.type, self.head, self.team, self.skeleton))

    def setName(self, name):
        Suit.setName(self, name, self.head)

    def setHealth(self, health):
        DistributedAvatar.setHealth(self, health)
        self.updateHealthBar(health)

    def setAnimState(self, anim, timestamp = None):
        self.anim = anim

        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        if type(anim) == types.IntType:
            anim = self.animId2animState[anim]

        if self.animFSM.getStateNamed(anim):
            self.animFSM.request(anim, [ts])

    def doAttack(self, attackId, avId, timestamp = None):
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        attackName = SuitAttacks.SuitAttackLengths.keys()[attackId]
        avatar = self.cr.doId2do.get(avId)
        self.animFSM.request('attack', [attackName, avatar, ts])

    def throwObject(self):
        self.acceptOnce("enter" + self.wsnp.node().getName(), self.__handleWeaponCollision)
        Suit.throwObject(self)

    def __handleWeaponCollision(self, entry):
        self.sendUpdate('toonHitByWeapon', [self.attack, base.localAvatar.doId])
        base.localAvatar.handleHitByWeapon(self.attack, self)
        self.b_handleWeaponTouch()

    def b_handleWeaponTouch(self):
        self.sendUpdate('handleWeaponTouch', [])
        self.handleWeaponTouch()

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        if self.animFSM.getCurrentState().getName() == 'off':
            self.setAnimState('neutral')

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)
        self.startSmooth()

    def disable(self):
        if self.suitTrack != None:
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        self.stopSmooth()
        self.suitFSM.requestFinalState()
        self.suitFSM = None
        self.suitState2stateIndex = None
        self.stateIndex2suitState = None
        self.anim = None
        self.state = None
        self.health = None
        self.type = None
        self.team = None
        self.head = None
        self.skeleton = None
        self.battle = None
        Suit.disable(self)
        DistributedAvatar.disable(self)

    def delete(self):
        Suit.delete(self)
        DistributedAvatar.delete(self)
        DistributedSmoothNode.delete(self)
