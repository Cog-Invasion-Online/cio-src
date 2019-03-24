from panda3d.core import Vec3, Quat

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog.ai.tasks.BaseTaskAI import BaseTaskAI
from src.coginvasion.cog.ai.tasks.TasksAI import *
from src.coginvasion.avatar.Activities import ACT_WAKE_ANGRY, ACT_NONE, ACT_SMALL_FLINCH, ACT_DIE
from src.coginvasion.avatar.Motor import Motor
from ScheduleAI import Schedule
from ConditionsAI import *
from RelationshipsAI import *
from StatesAI import *
from ScheduleResultsAI import *
from MemoryAI import *

from collections import deque
import random

class AITarget:
    
    def __init__(self, entity, relationship):
        self.entity = entity
        self.relationship = relationship
        self.lastKnownPosition = entity.getPos(render)
        self.lkpUpdated = True
        
    def cleanup(self):
        self.entity = None
        self.relationship = None
        self.lastKnownPosition = None
        self.lkpUpdated = None
        
class TakeDamageInfo:
    
    def __init__(self, entity, damage, damageType):
        self.entity = entity # who damaged me
        self.damage = damage
        self.damageType = damageType
        
    def cleanup(self):
        self.entity = None
        self.damage = None
        self.damageType = None
        
class BaseCombatCharacterAI:
    notify = directNotify.newCategory("BaseCombatCharacterAI")
    
    def __init__(self, battleZone = None):
        self.battleZone = battleZone
        
    def setBattleZone(self, zone):
        self.battleZone = zone
        
    def getBattleZone(self):
        return self.battleZone
        
    def delete(self):
        self.battleZone = None
        
    def getAvailableAttacks(self):
        """
        Return a list of all attacks in this character's aresenal.
        
        The AI refers to this list to determine which attacks are capable
        of being used under the current conditions.
        """
        if hasattr(self, 'attacks'):
            return self.attacks.values()

        return []

class BaseNPCAI(BaseCombatCharacterAI):
    
    notify = directNotify.newCategory("BaseNPCAI")
    notify.setDebug(True)
    
    # 50% hp is considered low
    LOW_HP_PERCT = 0.5
    REACHABLE_DIST_SQR = 30*30
    MAX_VISION_ANGLE = 90
    MAX_VISION_DISTANCE_SQR = 75*75
    MAX_HEAR_DISTANCE_SQR = 50*50
    MAX_OLD_ENEMIES = 4

    def __init__(self, battleZone = None):
        BaseCombatCharacterAI.__init__(self, battleZone)
        self.lastConditions = 0
        self.conditionsMask = 0

        self.memory = 0
        self.memoryPosition = None
        
        self.lastHPPerct = 1.0
        
        # Must be derived from the Avatar class
        self.target = None
        
        self.schedule = None
        self.npcState = STATE_IDLE
        self.idealState = STATE_IDLE

        self.path = []

        self.schedules = {
            "DIE"           :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_DIE),
                    Task_Wait(-1)
                ],
                interruptMask = 0
            ),
            "SMALL_FLINCH"  :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_SMALL_FLINCH),
                    Task_Remember(self, MEMORY_FLINCHED),
                    Task_AwaitActivity(self)
                ]
            ),

            "IDLE_STAND"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_NONE),
                    Task_Wait(-1)
                ],
                interruptMask = COND_NEW_TARGET|COND_SEE_FEAR|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE
            ),

            "WAKE_ANGRY"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_SetActivity(self, ACT_WAKE_ANGRY),
                    Task_AwaitActivity(self)#,
                    #Task_FaceIdeal(self)
                ]
            ),

            "COMBAT_FACE"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_SetActivity(self, ACT_NONE),
                    Task_FaceTarget(self)
                ]
            ),

            "TAKE_COVER_FROM_ORIGIN"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_FindCoverFromOrigin(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_Remember(self, MEMORY_IN_COVER),
                    Task_Func(self.setIdealYaw, [179])
                ],
                interruptMask = COND_NEW_TARGET
            ),

            "TAKE_COVER_FROM_TARGET"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_Wait(0.2),
                    Task_FindCoverFromTarget(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_Remember(self, MEMORY_IN_COVER),
                    Task_FaceTarget(self),
                    Task_Wait(1.0)
                ],
                interruptMask = COND_NEW_TARGET
            ),

            "CHASE_TARGET_FAILED"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_Wait(0.2),
                    Task_FindCoverFromTarget(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_FaceTarget(self),
                    Task_Wait(1.0)
                ],
                interruptMask = COND_NEW_TARGET|COND_CAN_ATTACK
            ),

            "CHASE_TARGET"  :   Schedule(
                [
                    Task_GetPathToTarget(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self)
                ],
                failSched = "CHASE_TARGET_FAILED",
                interruptMask = COND_NEW_TARGET | COND_TASK_FAILED | COND_CAN_ATTACK
            ),
            "ATTACK"        :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_FaceTarget(self),
                    Task_EquipAttack(self),
                    Task_FireAttack(self),
                    Task_AwaitAttack(self),
                    Task_SetPostAttackSchedule(self)
                ],
                interruptMask=COND_HEAVY_DAMAGE|COND_LIGHT_DAMAGE|COND_TARGET_OCCLUDED|COND_TARGET_DEAD|COND_NEW_TARGET
            ),
            "ALERT_FACE"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_SetActivity(self, ACT_NONE),
                    Task_FaceIdeal(self)
                ],
                interruptMask=COND_NEW_TARGET|COND_SEE_FEAR|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE
            ),
            "ALERT_SMALL_FLINCH"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_SMALL_FLINCH),
                    Task_Remember(self, MEMORY_FLINCHED),
                    Task_AwaitActivity(self),
                    Task_SetSchedule(self, "ALERT_FACE")
                ]
            ),
            "RETURN_TO_MEMORY_POSITION" :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_StopMoving(self),
                    Task_GetPathToMemoryPosition(self),
                    Task_ForgetPosition(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_FaceIdeal(self)
                ],
                interruptMask=COND_NEW_TARGET|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_SEE_HATE|COND_SEE_DISLIKE
            ),
        }

        self.motor = Motor(self)

        self.scheduleNames = {v : k for k,v in self.schedules.items()}
        #print self.schedules
        #print self.scheduleNames

        self.idealYaw = 0.0
        self.yawSpeed = 9.0
        
        self.avatarsInSight = []
        
        self.capableAttacks = []
        
        self.oldTargets = deque(maxlen = self.MAX_OLD_ENEMIES)
        
        self.runAITask = None

    def remember(self, bits):
        self.memory |= bits

    def forget(self, bits):
        self.memory &= ~bits

    def hasMemory(self, bits):
        return (self.memory & bits) != 0

    def clearMemory(self):
        self.memory = 0

    def getCoverRadius(self):
        return 49

    def validateCover(self, coverLocation):
        return True

    def planPath(self, goal):
        path = self.getBattleZone().planPath(self.getPos(), goal)
        if len(path) > 1:
            self.getMotor().setWaypoints(path)

    def findCover(self, threatPos, viewOffset, minDist = 0, maxDist = None):
        """
        Tries to find a nearby node that will hide
        the caller from its enemy. 
        If supplied, search will return a node at least as far
        away as MinDist, but no farther than MaxDist. 
        if MaxDist isn't supplied, it defaults to a reasonable 
        value
        """

        if maxDist is None:
            maxDist = 49

        if minDist > 0.5 * maxDist:
            minDist = 0.5 * maxDist

        myPos = self.getPos()
        lookersOffset = threatPos + viewOffset

        world = self.getBattleZone().getPhysicsWorld()

        #print "findCover"

        # Find cover hint nodes in radius of me
        kdTree = self.getBattleZone().coverKDTree
        if kdTree:
            nearby = kdTree.query_ball_point([myPos[0], myPos[1], myPos[2]], maxDist)
        else:
            nearby = []
        for nodeIdx in nearby:
            nodePos = self.getBattleZone().coverHints[nodeIdx].getCEntity().getOrigin()
            result = world.rayTestClosest(nodePos + viewOffset, lookersOffset, CIGlobals.WorldGroup)
            #print "findCover result:", result, result.hasHit(), result.getNode()
            # if this cover point will block the threat's line of sight to me
            if result.hasHit():
                distToThreat = (threatPos - nodePos).lengthSquared()
                distToMe = (myPos - nodePos).lengthSquared()
                # ...and is also closer to me than the threat
                if distToMe <= distToThreat:
                    if self.validateCover(nodePos):
                        self.planPath(nodePos)
                        #print "Found cover node", nodePos
                        return True
                #else:
                    #print "Found cover, but the node is further away than the threat"
        return False

    def findLateralCover(self, threatPos, viewOffset):
        """
        Attempts to locate a spot in the world
        directly to the left or right of the caller that will
        conceal them from view of the threat.
        """
        coverChecks = 5 # how many checks are made
        coverDelta = 48 / 16.0 # distance between checks

        stepRight = Vec3.right() * coverDelta
        stepRight[2] = 0
        testLeft = testRight = Vec3.zero()

        world = self.getBattleZone().getPhysicsWorld()

        #print "findLateralCover"

        for i in xrange(coverChecks):
            testLeft = testLeft - stepRight
            testRight = testRight + stepRight
            
            result = world.rayTestClosest(threatPos + viewOffset, testLeft + self.getEyePosition(), CIGlobals.WorldGroup)
            #print "findLateralCover left result:", result, result.hasHit(), result.getNode()
            if result.hasHit():
                if self.validateCover(testLeft):
                    self.planPath(testLeft)
                    #print "Found left cover", testLeft
                    return True

            #print "findLateralCover right result:", result, result.hasHit(), result.getNode()
            result = world.rayTestClosest(threatPos + viewOffset, testRight + self.getEyePosition(), CIGlobals.WorldGroup)
            if result.hasHit():
                if self.validateCover(testRight):
                    self.planPath(testRight)
                    #print "Found right cover", testRight
                    return True

        return False
         
    def getMotor(self):
        return self.motor

    def changeYaw(self, yawSpeed = None):
        if not yawSpeed:
            yawSpeed = self.yawSpeed

        current = CIGlobals.angleMod(self.getH())
        ideal = self.idealYaw
        #print current, ideal
        if current != ideal:
            speed = yawSpeed * globalClock.getDt() * 10
            move = ideal - current
            if ideal > current:
                if move >= 180:
                    move -= 360
            else:
                if move <= -180:
                    move += 360

            if move > 0:
                if move > speed:
                    # turning left
                    move = speed
            else:
                if move < -speed:
                    # turning right
                    move = -speed

            self.setH(CIGlobals.angleMod(current + move))
        else:
            move = 0

        return move

    def makeIdealYaw(self, target):
        self.idealYaw = CIGlobals.vecToYaw(target - self.getPos())

    def setIdealYaw(self, yaw):
        self.idealYaw = CIGlobals.angleMod(yaw)

    def getYawDiff(self):
        currentYaw = CIGlobals.angleMod(self.getH())
        if currentYaw == self.idealYaw:
            return 0

        return CIGlobals.angleDiff(self.idealYaw, currentYaw)

    def isFacingIdeal(self):
        return abs(self.getYawDiff()) <= 0.006

    def getScheduleName(self, schedInst):
        return self.scheduleNames.get(schedInst, "Not found")

    def addSchedule(self, name, schedInst):
        self.schedules[name] = schedInst

    def getScheduleByName(self, name):
        return self.schedules.get(name, None)
        
    def delete(self):
        self.stopAI()
        self.clearTarget()
        for target in self.oldTargets:
            if target:
                target.cleanup()
        for sched in self.schedules.values():
            sched.cleanup()
        self.motor.cleanup()
        self.motor = None
        self.memoryPosition = None
        self.npcState = None
        self.idealState = None
        self.capableAttacks = None
        self.schedules = None
        self.oldTargets = None
        self.lastConditions = None
        self.conditionsMask = None
        self.lastHPPerct = None
        self.avatarsInSight = None
        BaseCombatCharacterAI.delete(self)
        
    #def setTarget(self, target):
    #    self.clearTarget()
    #    self.target = target
        
    def clearTarget(self):
        if self.target is not None:
            self.target.cleanup()
            self.target = None
        
    def setConditions(self, cond):
        self.conditionsMask |= cond
        
    def hasConditions(self, cond):
        return (self.conditionsMask & cond) != 0
        
    def getIgnoreConditions(self):
        """
        Override this function to return a mask of conditions that
        should be ignored by your AI implementation.
        """
        return 0
        
    def clearConditions(self, cond):
        self.conditionsMask &= ~cond
        
    def clearAllConditions(self):
        self.conditionsMask = 0

    def isPlayerAlive(self, plyr):
        return not plyr.isDead()

    def isSameLeafAsPlayer(self, plyr):
        plLeaf = self.battleZone.bspLoader.findLeaf(plyr)
        myLeaf = self.battleZone.bspLoader.findLeaf(self)
        return plLeaf == myLeaf

    def isPlayerInPVS(self, plyr):
        plLeaf = self.battleZone.bspLoader.findLeaf(plyr)
        myLeaf = self.battleZone.bspLoader.findLeaf(self)
        return self.battleZone.bspLoader.isClusterVisible(myLeaf, plLeaf)
        
    def getDistanceSquared(self, other):
        return (self.getPos(render) - other.getPos(render)).lengthSquared()

    def isPlayerAudible(self, plyr):
        return self.isPlayerInPVS(plyr) and self.getDistanceSquared(plyr) < self.MAX_HEAR_DISTANCE_SQR
        
    def doesLineTraceToPlayer(self, plyr):
        # Is the player occluded by any BSP faces?
        return self.battleZone.traceLine(self.getPos(render) + (0, 0, 3.5 / 2), plyr.getPos(render) + (0, 0, 2.0))
        
    def isPlayerInVisionCone(self, plyr):
        # Is the player in my angle of vision?

        toPlyr = plyr.getPos() - self.getPos()
        yaw = CIGlobals.angleMod(CIGlobals.vecToYaw(toPlyr))
        diff = CIGlobals.angleDiff(yaw, CIGlobals.angleMod(self.getH()))

        #print "Vision cone from self->player:", diff

        return abs(diff) <= self.MAX_VISION_ANGLE
        
    def isPlayerInVisionCone_FromPlayer(self, plyr):
        # Am I in the player's vision cone?

        toSelf = self.getPos() - plyr.getPos()
        yaw = CIGlobals.angleMod(CIGlobals.vecToYaw(toSelf))
        diff = CIGlobals.angleDiff(yaw, CIGlobals.angleMod(plyr.getH()))

        #print "Vision cone from player->self:", diff

        return abs(diff) <= self.MAX_VISION_ANGLE
        
    def isPlayerInVisionRange(self, plyr):
        # Is the player close enough to where I could see them?
        return self.getDistanceSquared(plyr) <= self.MAX_VISION_DISTANCE_SQR

    def isPlayerVisible(self, plyr, checkVisionAngle = True, checkVisionDistance = True):
        # Check if player is potentially visible from my leaf.
        if not self.isPlayerInPVS(plyr):
            return False

        if checkVisionAngle and not self.isPlayerInVisionCone(plyr):
            return False
                
        if checkVisionDistance and not self.isPlayerInVisionRange(plyr):
            return False

        return self.doesLineTraceToPlayer(plyr)
        
    def getBestVisibleTarget(self):
        target = None
        bestRelationship = RELATIONSHIP_NONE
        nearest = 9999999
        
        for i in xrange(len(self.avatarsInSight)):
            av = self.avatarsInSight[i]
            if av.getHealth() <= 0:
                continue
            
            rel = av.getRelationshipTo(self)
            if rel > bestRelationship:
                # entity is disliked more
                # don't check distance, just get mad
                bestRelationship = rel
                nearest = (av.getPos(render) - self.getPos(render)).lengthSquared()
                target = av
            elif rel == bestRelationship:
                # entity is disliked just as much
                # get mad if it is closer
                dist = (av.getPos(render) - self.getPos(render)).lengthSquared()
                if dist <= nearest:
                    nearest = dist
                    bestRelationship = rel
                    target = av
                    
        return (target, bestRelationship)
        
    def pushTarget(self, target):
        if not target:
            return
                
        if target in self.oldTargets:
            return
            
        self.oldTargets.appendleft(target)
        
    def popTarget(self):
        for i in xrange(len(self.oldTargets) - 1, -1, -1):
            target = self.oldTargets[i]
            if not target or not CIGlobals.isNodePathOk(target.entity):
                continue
                
            if target.entity.getHealth() > 0:
                self.target = target
                return True
            
            self.oldTargets.pop()
            
        return False
        
    def checkTarget(self):
        """
        Gets and stores data and conditions pertaining to the current target.
        Returns true if the target LKP was updated.
        """
        
        updatedLKP = False
        self.clearConditions(COND_TARGET_FACING_ME)
        
        if not self.isPlayerVisible(self.target.entity, False, False):
            assert not self.hasConditions(COND_SEE_TARGET), "COND_SEE_TARGET is set, but target is not visible."
            self.setConditions(COND_TARGET_OCCLUDED)
        else:
            self.clearConditions(COND_TARGET_OCCLUDED)
            
        if self.target.entity.getHealth() <= 0:
            self.setConditions(COND_TARGET_DEAD)
            self.clearConditions(COND_SEE_TARGET | COND_TARGET_OCCLUDED)
            return False
            
        targetPos = self.target.entity.getPos(render)
        distToTarget = (targetPos - self.getPos(render)).lengthSquared()
        
        if self.hasConditions(COND_SEE_TARGET):
            self.target.lastKnownPosition = targetPos
            updatedLKP = True
            
            # Alright, we can see the player, but can the player see us?
            if self.isPlayerInVisionCone_FromPlayer(self.target.entity):
                self.setConditions(COND_TARGET_FACING_ME)
            else:
                self.clearConditions(COND_TARGET_FACING_ME)
                
            if self.target.entity.movementDelta != Vec3.zero():
                # trail the enemy a bit
                self.target.lastKnownPosition = (
                    self.target.lastKnownPosition - self.target.entity.movementDelta * random.uniform(-0.05, 0)
                )
        elif not self.hasConditions(COND_TARGET_OCCLUDED|COND_SEE_TARGET) and distToTarget <= 256:
            # if the target is not occluded, and unseen, that means it is behind or beside us
            # let us know where the target is
            updatedLKP = True
            self.target.lastKnownPosition = targetPos
            
        if distToTarget >= self.MAX_VISION_DISTANCE_SQR:
            # Target is very far from us
            self.setConditions(COND_TARGET_TOOFAR)
        else:
            self.clearConditions(COND_TARGET_TOOFAR)

        if self.canCheckAttacks():
            self.checkAttacks(distToTarget)
            
        return updatedLKP

    def hasAttacks(self):
        return len(self.capableAttacks) > 0
        
    def canCheckAttacks(self):
        return self.hasConditions(COND_SEE_TARGET) and not self.hasConditions(COND_TARGET_TOOFAR)

    def canUseAttack(self, attackID):
        return attackID in self.capableAttacks
        
    def checkAttacks(self, distSqr):
        """
        Builds a list of usable attacks for a target entity.
        """
        del self.capableAttacks[:]

        self.clearConditions(COND_CAN_ATTACK)
        
        # Vec from me to target
        vec2LOS = (self.target.entity.getPos() - self.getPos()).getXy()
        vec2LOS.normalize()
        
        # How much are we facing the target?
        dot = vec2LOS.dot(self.getQuat().getForward().getXy())
        
        attacks = self.getAvailableAttacks()
        for i in xrange(len(attacks)):
            attack = attacks[i]
            if attack.checkCapable(dot, distSqr) and attack.hasAmmo():
                #print attack, "is capable"
                self.capableAttacks.append(attack.getID())
        
        if len(self.capableAttacks) > 0:
            self.setConditions(COND_CAN_ATTACK)
        
    def getTarget(self):
        """
        Find a target. By default, only target enemies (dislike or hate relationship).
        """
        if self.hasConditions(COND_SEE_HATE | COND_SEE_DISLIKE):
            #print "we see hate or dislike"
            target, relationship = self.getBestVisibleTarget()
            #print target, relationship
            if ((self.target is None or target != self.target.entity) and target is not None):
                if ((self.schedule and ((self.schedule.interruptMask & COND_NEW_TARGET) != 0)) or
                    not self.schedule):
                    #print "pushing target"
                    self.pushTarget(self.target)
                    self.setConditions(COND_NEW_TARGET)
                    self.target = AITarget(target, relationship)
                        
        # Remember old targets
        if not self.target and self.popTarget():
            #print "remembering old target"
            if ((self.schedule and ((self.schedule.interruptMask & COND_NEW_TARGET) != 0)) or
               not self.schedule):
                #print "selected old target"
                self.setConditions(COND_NEW_TARGET)
                    
        return self.target is not None

    def getScheduleFlags(self):
        """
        Returns an integer with all Conditions bits that are current set and also
        set in the current schedule's Interrupt mask.
        """
        if not self.schedule:
            return self.conditionsMask

        return self.conditionsMask & self.schedule.interruptMask

    def getIdealState(self):
        conditions = self.getScheduleFlags()

        if self.npcState == STATE_IDLE:

            # IDLE goes to ALERT upon being injured
            # IDLE goes to COMBAT upon sighting an enemy

            if conditions & COND_NEW_TARGET:
                # New target. This means that an idle NPC has seen someone
                # it dislikes, or that a NPC in combat has found a more suitable
                # target to attack
                self.idealState = STATE_COMBAT
            elif conditions & COND_LIGHT_DAMAGE:
                self.idealState = STATE_ALERT
            elif conditions & COND_HEAVY_DAMAGE:
                self.idealState = STATE_ALERT

        elif self.npcState == STATE_ALERT:

            # ALERT goes to IDLE upon becoming bored
            # ALERT goes to COMBAT upon sighting an enemy

            if conditions & (COND_NEW_TARGET|COND_SEE_TARGET):
                # If we see an enemy, we must attack
                self.idealState = STATE_COMBAT
        
        elif self.npcState == STATE_COMBAT:
            if not self.target:
                self.idealState = STATE_ALERT

        elif self.npcState == STATE_DEAD:
            self.idealState = STATE_DEAD

        return self.idealState

    def getSchedule(self):
        if self.npcState == STATE_NONE:
            return None

        elif self.npcState == STATE_IDLE:
        #    if self.hasConditions(COND_HEAR_SOUND):
        #        return self.getScheduleByName("ALERT_FACE")
            return self.getScheduleByName("IDLE_STAND")

        elif self.npcState == STATE_ALERT:
            if self.hasConditions(COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE):
                if abs(self.getYawDiff()) < self.MAX_VISION_ANGLE * 0.5:
                    return self.getScheduleByName("TAKE_COVER_FROM_ORIGIN")
                else:
                    return self.getScheduleByName("ALERT_SMALL_FLINCH")
            return self.getScheduleByName("IDLE_STAND")

        elif self.npcState == STATE_COMBAT:
            if self.hasConditions(COND_TARGET_DEAD):
                self.clearTarget()
                if self.getTarget():
                    self.clearConditions(COND_TARGET_DEAD)
                    return self.getSchedule()
                else:
                    self.setNPCState(STATE_ALERT)
                    return self.getSchedule()
            if self.hasConditions(COND_NEW_TARGET):
                return self.getScheduleByName("WAKE_ANGRY")
            elif self.hasConditions(COND_LIGHT_DAMAGE) and not self.hasMemory(MEMORY_FLINCHED):
                return self.getScheduleByName("SMALL_FLINCH")
            elif self.hasConditions(COND_HEAVY_DAMAGE):
                #print "We need to take cover from our target"
                return self.getScheduleByName("TAKE_COVER_FROM_TARGET")
            elif not self.hasConditions(COND_SEE_TARGET):
                if not self.hasConditions(COND_TARGET_OCCLUDED):
                    return self.getScheduleByName("COMBAT_FACE")
                else:
                    return self.getScheduleByName("CHASE_TARGET")
            else:
                if self.hasConditions(COND_CAN_ATTACK):
                    return self.getScheduleByName("ATTACK")
                elif not self.isFacingIdeal():
                    return self.getScheduleByName("COMBAT_FACE")
                else:
                    return self.getScheduleByName("CHASE_TARGET")

        elif self.npcState == STATE_DEAD:
            return self.getScheduleByName("DIE")


        return None
        
    def look(self):
        """Look at the world in front of me."""

        self.clearConditions(COND_SEE_HATE | COND_SEE_FEAR | COND_SEE_DISLIKE | COND_SEE_TARGET | COND_SEE_FRIEND)
        
        bits = 0
        
        del self.avatarsInSight[:]
        
        # Go through all known avatars in my zone.
        for i in xrange(len(base.air.avatars[self.battleZone.zoneId])):
            av = base.air.avatars[self.battleZone.zoneId][i]
            # Ignore myself
            if av == self:
                continue
                
            #if av.__class__.__name__ == 'DistributedPlayerToonAI':
            #    continue
                
            if av.getHealth() <= 0:
                #print "\tdead"
                continue
                
            relationship = av.getRelationshipTo(self)
            if relationship == RELATIONSHIP_NONE:
                continue

            if not self.isPlayerVisible(av):
                continue
                
            self.avatarsInSight.append(av)
                
            if self.target and av == self.target.entity:
                # the visible avatar happens to be our target
                bits |= COND_SEE_TARGET
                
            if relationship == RELATIONSHIP_HATE:
                bits |= COND_SEE_HATE
            elif relationship == RELATIONSHIP_FEAR:
                bits |= COND_SEE_FEAR
            elif relationship == RELATIONSHIP_FRIEND:
                bits |= COND_SEE_FRIEND
            elif relationship == RELATIONSHIP_DISLIKE:
                bits |= COND_SEE_DISLIKE
                
        self.setConditions(bits)

    def isScheduleValid(self):
        if not self.schedule:
            return False

        if self.hasConditions(self.schedule.interruptMask | COND_SCHEDULE_DONE | COND_TASK_FAILED):
            return False

        return True

    def setDamageConditions(self, dmgAmt):
        #print "damaged for", dmgAmt
        if dmgAmt >= self.getLightDamage():
            #print "Setting light damage"
            self.setConditions(COND_LIGHT_DAMAGE)
        if dmgAmt >= self.getHeavyDamage():
           # print "Setting heavy damage"
            self.setConditions(COND_HEAVY_DAMAGE)

    def scheduleChange(self):
        pass

    def changeSchedule(self, sched):
        if sched:
            sched.reset()

        #print "Change schedule to", self.getScheduleName(sched)

        self.schedule = sched
        self.conditionsMask = 0

    def setNPCState(self, state):

        #print "Set state to", state

        if state == STATE_IDLE:
            # not allowed to have target anymore
            if self.target is not None:
                self.clearTarget()

        self.npcState = state
        self.idealState = state

    def maintainSchedule(self):
        if not self.isScheduleValid() or self.npcState != self.idealState:
            # schedule must change

            self.scheduleChange()

            if (self.idealState != STATE_DEAD and
                (self.idealState != STATE_SCRIPT or self.idealState == self.npcState)):

                if ((self.conditionsMask and not self.hasConditions(COND_SCHEDULE_DONE)) or 
                    (self.schedule is not None and ((self.schedule.interruptMask & COND_SCHEDULE_DONE) != 0)) or
                    ((self.npcState == STATE_COMBAT) and (self.target is not None))):

                    self.getIdealState()

            if self.hasConditions(COND_TASK_FAILED) and self.npcState == self.idealState:
                if self.schedule and self.schedule.hasFailSchedule():
                    newSched = self.getScheduleByName(self.schedule.getFailSchedule())
                else:
                    newSched = self.getScheduleByName("FAIL")
                self.changeSchedule(newSched)
            else:
                self.setNPCState(self.idealState)
                if self.npcState == STATE_SCRIPT or self.npcState == STATE_DEAD:
                    newSched = BaseNPCAI.getSchedule(self)
                else:
                    newSched = self.getSchedule()
                self.changeSchedule(newSched)

        if self.schedule:
            run = self.schedule.runSchedule()
            if run == SCHED_COMPLETE:
                #print "schedule complete"
                self.setConditions(COND_SCHEDULE_DONE)
            elif run == SCHED_FAILED:
                #print "task failed"
                self.setConditions(COND_TASK_FAILED)
            else:
                pass
                #print "schedule still running"
        
    def startAI(self):
        self.stopAI()
        
        self.runAITask = taskMgr.add(self.__runAITask, "BaseNPCAI.runAITask-" + str(id(self)))
        
    def __runAITask(self, task):
        self.runAI()
        return task.cont
        
    def stopAI(self):
        if self.runAITask:
            self.runAITask.remove()
            self.runAITask = None
        
    def runAI(self):
        """
        Runs an AI step.
        """
        
        if not self.battleZone:
            #self.notify.warning("Cannot run AI without a battle zone!")
            return

        if self.isDead():
            self.npcState = STATE_DEAD
            
        # Don't bother with this crap if we are dead.
        if self.npcState != STATE_DEAD and self.npcState != STATE_NONE:
            self.look()
            self.clearConditions(self.getIgnoreConditions())
            self.getTarget()
            
            # Do these calculations if we have a target
            if self.target:
                self.checkTarget()

        self.maintainSchedule()

        #msg =  str(self) + "\n"
        #msg += " runAI: conditions\n"
        #for cond in AllConditions:
        #    msg += "\t{0}\t:\t{1}\n".format(cond, self.hasConditions(cond))
        #msg += "ideal state: " + str(self.idealState) + "\n"
        #msg += "state: " + str(self.npcState) + "\n"
        #msg += "schedule: "
        #if self.schedule:
        #    msg += self.getScheduleName(self.schedule) + "\n"
        #    msg += "\tcurrent task: " + str(self.schedule.currentTask) + "\n"
        #else:
        #    msg += "None\n"
        #msg += "target: " + str(self.target) + "\n"
        #msg += "=================================================="
        #self.notify.info(msg)

        self.clearConditions(COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE)

        
        
