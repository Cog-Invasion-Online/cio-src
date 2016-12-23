########################################
# Filename: SuitAttackBehavior.py
# Created by: DecodedLogic (13Sep15)
########################################

from SuitHabitualBehavior import SuitHabitualBehavior
from SuitType import SuitType
import SuitAttacks
import SuitGlobals
import SuitUtils

from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.task.Task import Task
import random, operator

class SuitAttackBehavior(SuitHabitualBehavior):

    ATTACK_DISTANCE = 40.0
    ATTACK_COOLDOWN = 10
    MAX_ATTACKERS = 3
    ABANDON_ATTACK_PERCT = 0.18

    def __init__(self, suit):
        SuitHabitualBehavior.__init__(self, suit, doneEvent = 'suit%s-attackDone' % suit.doId)
        self.avatarsInRange = []
        self.maxAttacksPerSession = 3
        self.attacksThisSession = 0
        self.attacksDone = 0
        self.target = None
        self.canAttack = True
        self.origHealth = None
        self.isAttacking = False
        
        self.suitAttackTurretTrack = None

        level = self.suit.getLevel()
        if 1 <= level <= 5:
            self.maxAttacksPerSession = 3
        elif 5 <= level <= 10:
            self.maxAttacksPerSession = 4
        elif 9 <= level <= 12:
            self.maxAttacksPerSession = 5

    def enter(self):
        SuitHabitualBehavior.enter(self)
        self.origHealth = self.suit.getHealth()
        self.attacksThisSession = 0
        self.startAttacking()

    def exit(self):
        SuitHabitualBehavior.exit(self)
        
        taskMgr.remove(self.suit.uniqueName('attackTask'))
        taskMgr.remove(self.suit.uniqueName('finalAttack'))
        
        if hasattr(self, 'isAttacking') and hasattr(self, 'suit'):
            if self.isAttacking and self.suit:
                self.suit.d_interruptAttack()
                
                if self.suitAttackTurretTrack:
                    self.suitAttackTurretTrack.pause()
                    self.suitAttackTurretTrack = None

    def unload(self):
        SuitHabitualBehavior.exit(self)
        self.avatarsInRange = None
        self.origHealth = None
        del self.isAttacking
        del self.origHealth
        del self.avatarsInRange
        del self.maxAttacksPerSession
        del self.attacksThisSession
        del self.attacksDone
        del self.target
        del self.canAttack
        del self.suitAttackTurretTrack

    def startAttacking(self, task = None):
        if hasattr(self.suit, 'DELETED') or not hasattr(self, 'attacksThisSession'):
            self.stopAttacking()
            if task:
                return Task.done
        # Do we need to reset the avatars in-range?
        if self.attacksThisSession > 0:
            self.resetAvatarsInRange()

        # Stop attacking if low on health or if there's nothing around to attack.
        if hasattr(self.suit, 'DELETED'):
            self.stopAttacking()
            return

        # Let's check our panic behavior.
        from src.coginvasion.cog.SuitPanicBehavior import SuitPanicBehavior
        brain = self.suit.getBrain()
        panicBehavior = brain.getBehavior(SuitPanicBehavior)
        healthPerct = float(self.suit.getHealth()) / float(self.suit.getMaxHealth())
        origHealthPerct = float(self.origHealth) / float(self.suit.getMaxHealth())

        if len(self.avatarsInRange) < 1 or panicBehavior and healthPerct <= panicBehavior.getPanicHealthPercentage() or healthPerct - origHealthPerct >= self.ABANDON_ATTACK_PERCT:
            self.stopAttacking()
            return
        
        # Let's check if we have a backup behavior if toons get out of control.
        from src.coginvasion.cog.SuitCallInBackupBehavior import SuitCallInBackupBehavior
        backupBehavior = brain.getBehavior(SuitCallInBackupBehavior)
        
        if not backupBehavior is None:
            if backupBehavior.shouldStart():
                brain.queueBehavior(SuitCallInBackupBehavior)
                self.stopAttacking()
                return
        
        # Let's select a target and look at them.
        target = self.avatarsInRange[0]
        attack = SuitUtils.attack(self.suit, target)
        
        # Let's handle when we're attacking a turret.
        if target.__class__.__name__ == 'DistributedPieTurretAI':
            distance = self.suit.getDistance(target)
            speed = 50.0
            
            if attack == 'glowerpower':
                speed = 100.0
            
            timeUntilRelease = distance / speed
            if attack != 'glowerpower':
                if self.suit.getSuit()[0].getSuitType() == SuitType.C:
                    timeUntilRelease += 2.2
                else:
                    timeUntilRelease += 3.0
            else:
                timeUntilRelease += 1.0
            turretPos = target.getPos(render)
            hp = int(self.suit.getMaxHealth() / SuitAttacks.SuitAttackDamageFactors[attack])
            
            if self.suit.suitPlan.getName() == SuitGlobals.VicePresident:
                hp = int(200 / SuitAttacks.SuitAttackDamageFactors[attack])
            
            self.suitAttackTurretTrack = Sequence(
                Wait(timeUntilRelease),
                Func(
                    self.damageTurret,
                    target,
                    turretPos,
                    hp
                )
            )
            self.suitAttackTurretTrack.start()
        
        self.isAttacking = True
        self.attacksThisSession += 1
        self.attacksDone += 1

        self.ATTACK_COOLDOWN = SuitAttacks.SuitAttackLengths[attack]

        # Are we allowed to continue attacking?
        if self.attacksThisSession < self.maxAttacksPerSession and not target.isDead():
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.startAttacking, self.suit.uniqueName('attackTask'))
        else:
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.stopAttacking, self.suit.uniqueName('finalAttack'))

        if task:
            return Task.done
        
    def damageTurret(self, target, position, hp):
        if not target.isEmpty():
            if (target.getPos(render) - position).length() <= 1:
                if not target.isDead():
                    target.b_setHealth(target.getHealth() - hp)
                    target.d_announceHealth(0, hp)
                    self.suit.d_handleWeaponTouch()

    def __doAttackCooldown(self, task):
        self.canAttack = True

    def stopAttacking(self, task = None):
        if hasattr(self, 'suit'):
            self.canAttack = False
            self.isAttacking = False
            self.origHealth = self.suit.getHealth()
            self.attacksThisSession = 0
            self.avatarsInRange = []
            self.ATTACK_COOLDOWN = random.randint(8, 20)
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.__doAttackCooldown, self.suit.uniqueName('Attack Cooldown'))
        self.exit()
        if task:
            return Task.done

    def resetAvatarsInRange(self):
        toonObjsInRange = {}
        self.avatarsInRange = []

        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if className in ['DistributedToonAI', 'DistributedPieTurretAI']:
                if obj.zoneId == self.suit.zoneId:
                    if not obj.isDead():
                        dist = obj.getDistance(self.suit)
                        if className == 'DistributedToonAI' and obj.getNumAttackers() >= self.MAX_ATTACKERS or className == 'DistributedToonAI' and obj.getGhost():
                            continue
                        if dist <= self.ATTACK_DISTANCE:
                            toonObjsInRange.update({obj : dist})

        toonObjsInRange = sorted(toonObjsInRange.items(), key = operator.itemgetter(1))
        for toonObj, _ in toonObjsInRange:
            self.avatarsInRange.append(toonObj)

    def shouldStart(self):
        self.resetAvatarsInRange()

        if len(self.avatarsInRange) > 0 and self.canAttack:
            return True
        return False

    def getTarget(self):
        return self.target

    def getAttacksDone(self):
        return self.attacksDone
