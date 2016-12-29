# Filename: SuitFollowBossBehaviorAI.py
# Created by:  DecodedLogic (02Sep15)
# Updated by:  blach (09Dec15) - Fixed backup cogs having no functionality at all.

from src.coginvasion.cog.SuitPathBehaviorAI import SuitPathBehaviorAI
from src.coginvasion.cog.SuitHabitualBehaviorAI import SuitHabitualBehaviorAI
from src.coginvasion.cog import SuitAttacks
from src.coginvasion.globals import CIGlobals
from SuitFlyToRandomSpotBehaviorAI import SuitFlyToRandomSpotBehaviorAI
from SuitAttackBehaviorAI import SuitAttackBehaviorAI
import SuitPathDataAI
import SuitUtils

from direct.fsm import ClassicFSM, State
from direct.task.Task import Task
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.distributed.ClockDelta import globalClockDelta

import random

class SuitFollowBossBehaviorAI(SuitPathBehaviorAI, SuitHabitualBehaviorAI):

    LEEWAY_DISTANCE = 4
    MAX_BOSS_HELPERS = 5
    HEAL_SPEED = 50.0

    def __init__(self, suit, boss):
        SuitPathBehaviorAI.__init__(self, suit, exitOnWalkFinish = False)
        self.fsm = ClassicFSM.ClassicFSM('SuitFollowBossBehaviorAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('follow', self.enterFollow, self.exitFollow),
         State.State('protect', self.enterProtect, self.exitProtect)], 'off', 'off')
        self.fsm.enterInitialState()
        self.boss = boss
        self.bossSpotKey = None
        self.healInProgress = False
        self.suitHealTrack = None
        self.followBossTaskName = self.suit.uniqueName('followBoss')
        self.pathFinder = SuitPathDataAI.getPathFinder(self.suit.hood)

    def isHealing(self):
        return self.healInProgress

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enter(self):
        SuitPathBehaviorAI.enter(self)

        # Let's start following the boss.
        self.fsm.request('follow')

    def exit(self):
        SuitPathBehaviorAI.exit(self)
        self.fsm.requestFinalState()
        taskMgr.remove(self.followBossTaskName)

    def unload(self):
        SuitPathBehaviorAI.unload(self)
        del self.boss
        del self.followBossTaskName
        del self.bossSpotKey
        del self.fsm
        del self.suitHealTrack
        del self.healInProgress

    def enterProtect(self):
        base.taskMgr.add(self.__protectTick, self.suit.uniqueName('protectBossTick'))

    def __protectTick(self, task):
        if self.boss.isDead():
            # No! He died on us!
            self.suit.b_setAnimState('neutral')
            self.exit()
            return task.done

        # Check if the boss has flown somewhere else.
        if self.bossSpotKey != self.boss.getCurrentPath():
            # Yep, walk over to him. We're still following him.
            self.fsm.request('follow')
            return task.done

        # Hmm, let's figure out what we should do while protecting this boss.
        if self.isHealing():
            # We're already busy healing, don't do anything until we're done.
            return task.cont
        if self.boss.brain.currentBehavior.__class__ == SuitAttackBehaviorAI:
            # Our boss is attacking toons! Should we heal him, or continue protecting?
            choice = random.randint(0, 1)
            if choice == 0:
                # Alright, let's just continue protecting the boss.
                return task.cont
            elif choice == 1:
                # Let's heal him!
                self.doHeal()
        return task.cont

    def __attemptToHealBoss(self, hp, currBossPos):
        if self.isBossAvailable():
            if (self.boss.getPos(render) - currBossPos).length() <= 1:
                self.boss.b_setHealth(self.boss.getHealth() + hp)
                self.boss.d_announceHealth(1, hp)
                self.suit.d_handleWeaponTouch()

    def isBossAvailable(self):
        if not self.boss.isEmpty() and not hasattr(self.boss, 'DELETED') and not self.boss.isDead():
            return True
        return False

    def __disableBoss(self):
        if self.isBossAvailable():
            self.boss.getBrain().stopThinking()
            self.boss.b_setAnimState('neutral')

    def __enableBoss(self):
        if self.isBossAvailable():
            self.boss.getBrain().startThinking()

    def __toggleHeal(self):
        if self.healInProgress:
            self.healInProgress = False
        else:
            self.healInProgress = True

    def doHeal(self):
        self.__toggleHeal()
        # Let's choose one of the heal attacks and send it.
        attack = random.randint(0, 6)
        attackName = SuitAttacks.SuitAttackLengths.keys()[attack]
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.suit.sendUpdate('doAttack', [attack, self.boss.doId, timestamp])

        # Let's setup the variables we need.
        distance = self.suit.getDistance(self.boss)
        timeUntilHeal = distance / self.HEAL_SPEED
        timeUntilRelease = 1.0

        # Let's send the heal taunt message and set the heal amount.
        self.suit.d_setChat(CIGlobals.SuitHealTaunt)
        hp = int(self.suit.maxHealth / SuitAttacks.SuitAttackDamageFactors[attackName])
        if hp == 0:
            hp = 1

        # Let's adjust the heal amount if it's greater than the boss's max health.
        if (self.boss.getHealth() + hp) > self.boss.getMaxHealth():
            hp = (self.boss.getMaxHealth() - self.boss.getHealth())

        # Let's adjust the release time.
        if attackName != 'glowerpower':
            timeUntilRelease = 2.2

        self.suitHealTrack = Sequence(
            Wait(timeUntilRelease + timeUntilHeal),
            Func(self.__attemptToHealBoss, hp, self.boss.getPos(render)),
            Func(self.faceOtherDirection),
            Wait(3.0),
            Func(self.__toggleHeal)
        )
        self.suitHealTrack.start()

    def faceOtherDirection(self):
        self.suit.b_setAnimState('neutral')
        self.suit.setH(self.suit.getH() - 180)
        self.suit.d_setH(self.suit.getH())

    def exitProtect(self):
        base.taskMgr.remove(self.suit.uniqueName('protectBossTick'))
        if self.suitHealTrack:
            self.suitHealTrack.pause()
            self.suitHealTrack = None

    def enterFollow(self):
        self.__updatePath()

        # Let's begin waiting for the suit to get in front of the boss.
        taskMgr.add(self.__followBoss, self.followBossTaskName)

    def exitFollow(self):
        taskMgr.remove(self.followBossTaskName)

    def __updatePath(self):
        # Let's handle abandoning follow, boss deletion, etc.
        if self.boss.isDead():
            self.suit.b_setAnimState('neutral')
            self.exit()
            return task.done

        self.clearWalkTrack()

        if hasattr(self.boss, 'currentPath'):
            bossSpot = self.boss.getCurrentPath()
            self.bossSpotKey = bossSpot

            # Let's create a path.
            pos = self.boss.getPosFromCurrentPath()
            self.createPath(pos = (pos[0], pos[1]))
        else:
            self.exit()

    def __followBoss(self, task):
        # Let's cancel the task if the behavior was unloaded
        # or the boss was killed.
        if not hasattr(self, 'suit') or self.boss.isEmpty() or not self.boss.isEmpty() and self.boss.isDead():
            return Task.done

        # Let's find out if the boss we want to help has flown somewhere else.
        if self.boss.getCurrentPath() != self.bossSpotKey:
            # Sure did! We need to update our path so we can get to where he is.
            self.__updatePath()

        # We need to stop in front of the boss to protect him. Make sure that he's not flying when we're close enough.
        if self.suit.getDistance(self.boss) <= self.LEEWAY_DISTANCE and self.boss.brain.currentBehavior.__class__ != SuitFlyToRandomSpotBehaviorAI:
            self.clearWalkTrack(andTurnAround = 1)
            self.suit.b_setAnimState('neutral')
            self.suit.setH(self.suit.getH() - 180)
            self.suit.d_setH(self.suit.getH())
            # Now, let's protect him.
            self.fsm.request('protect')
            return Task.done
        return Task.cont

    def shouldAbandonFollow(self):
        suitsByBoss = self.getSuitsByBoss()
        backupCalledIn = self.getBackupCalledIn()
        if backupCalledIn == 0:
            backupCalledIn = 1
        return float(len(suitsByBoss)) / float(backupCalledIn) >= 0.4

    def getSuitsByBoss(self):
        suits = []
        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if className == 'DistributedSuitAI':
                if obj.zoneId == self.suit.zoneId:
                    if not obj.isDead() and not obj == self.boss and not obj == self.suit:
                        if obj.getDistance(self.boss) <= (self.LEEWAY_DISTANCE * 3):
                            suits.append(obj)
        return suits

    def getBackupCalledIn(self):
        from src.coginvasion.cog.SuitCallInBackupBehaviorAI import SuitCallInBackupBehaviorAI
        behaviorClass = SuitCallInBackupBehaviorAI
        if hasattr(self.boss, 'DELETED') or not self.boss.getBrain():
            return 0
        behavior = self.boss.getBrain().getBehavior(behaviorClass)
        return behavior.getCalledInBackup()

    def isBossInManager(self):
        return self.boss in self.suit.getManager().suits.values()

    def shouldStart(self):
        if self.boss and not self.boss.isDead() and self.isBossInManager() and self.suit.getDistance(self.boss) > self.LEEWAY_DISTANCE:
            _helper_suits = 0
            # Let me find out how many other Cogs are helping the boss.
            for suit in self.suit.getManager().suits.values():
                if suit.doId != self.suit.doId:
                    if suit.brain:
                        if suit.brain.currentBehavior.__class__ == SuitFollowBossBehaviorAI:
                            # Alright, there's someone helping...
                            _helper_suits += 1
            if _helper_suits < self.MAX_BOSS_HELPERS:
                # There's room for me!
                return True
        return False
