from panda3d.core import Vec3, Quat, NodePath

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog.ai.tasks.BaseTaskAI import BaseTaskAI
from src.coginvasion.cog.ai.tasks.TasksAI import *
from src.coginvasion.avatar.Activities import ACT_WAKE_ANGRY, ACT_NONE, ACT_SMALL_FLINCH, ACT_DIE
from src.coginvasion.avatar.Motor import Motor
from src.coginvasion.battle.SoundEmitterSystemAI import *
from src.coginvasion.phys import PhysicsUtils
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
        
class Hearing:
    
    def __init__(self):
        self.soundList = []
        self.soundBits = 0
        
    def cleanup(self):
        self.soundList = None
        self.soundBits = None
        
class BaseCombatCharacterAI:
    notify = directNotify.newCategory("BaseCombatCharacterAI")
        
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
    MAX_VISION_DISTANCE_SQR = 400*400
    MAX_HEAR_DISTANCE_SQR = 50*50
    MAX_OLD_ENEMIES = 4
    
    BASE_SPEED = 10

    def __init__(self, battleZone = None):
        self.lastConditions = 0
        self.conditionsMask = 0

        self.memory = 0
        self.memoryPosition = None
        
        self.wallPoints = None
        
        self.attackLOSData = [True, Vec3()]
        
        self.lastHPPerct = 1.0
        
        # Must be derived from the Avatar class
        self.target = None
        
        self.rememberCurrentSchedule = True
        self.lastSchedule = None
        self.schedule = None
        self.npcState = STATE_IDLE
        self.npcStateTime = 0.0
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
                interruptMask = COND_NEW_TARGET|COND_SEE_FEAR|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_FRIEND_IN_WAY|COND_HEAR_SOMETHING|COND_IN_WALL
            ),

            "WAKE_ANGRY"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_Remember(self, MEMORY_COMBAT_WAKE)#,
                    #Task_SetActivity(self, ACT_WAKE_ANGRY),
                    #Task_AwaitActivity(self)#,
                    #Task_FaceIdeal(self)
                ]
            ),

            "COMBAT_FACE"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_NONE),
                    Task_FaceTarget(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED|COND_IN_WALL
            ),

            "TAKE_COVER_FROM_ORIGIN"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_FindCoverFromOrigin(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_Remember(self, MEMORY_IN_COVER),
                    Task_Func(self.setIdealYaw, [179])
                ],
                interruptMask = COND_NEW_TARGET|COND_FRIEND_IN_WAY|COND_IN_WALL
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
                interruptMask = COND_NEW_TARGET|COND_FRIEND_IN_WAY|COND_IN_WALL
            ),

            "CHASE_TARGET_FAILED"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_Wait(0.2),
                    Task_FindCoverFromTarget(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self),
                    Task_FaceTarget(self),
                    Task_Wait(1.0)
                ],
                interruptMask = COND_NEW_TARGET|COND_CAN_ATTACK|COND_FRIEND_IN_WAY|COND_IN_WALL
            ),

            "CHASE_TARGET"  :   Schedule(
                [
                    Task_StopAttack(self),
                    Task_GetPathToTarget(self),
                    Task_RunPath(self),
                    Task_AwaitMovement(self, toTarget = True)
                ],
                failSched = "CHASE_TARGET_FAILED",
                interruptMask = COND_NEW_TARGET | COND_TASK_FAILED | COND_CAN_ATTACK | COND_FRIEND_IN_WAY | COND_IN_WALL
            ),
            "ATTACK"        :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_FaceTarget(self),
                    Task_EquipAttack(self),
                    Task_SetFailSchedule(self, "MAKE_ATTACK_LOS"),
                    Task_TestAttackLOS(self),
                    Task_SetFailSchedule(self, "FAIL"),
                    Task_FireAttack(self),
                    Task_SpeakAttack(self),
                    Task_AwaitAttack(self),
                    Task_SetPostAttackSchedule(self)
                ],
                interruptMask=COND_FRIEND_IN_WAY|COND_HEAVY_DAMAGE|COND_LIGHT_DAMAGE|COND_TARGET_OCCLUDED|COND_TARGET_DEAD|COND_NEW_TARGET|COND_IN_WALL
            ),
            "MAKE_ATTACK_LOS"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_GetPathAttackLOS(self),
                    Task_RunPath(self, turnThenRun = False),
                    Task_AwaitMovement(self),
                    Task_RestartLastSchedule(self)
                ],
                interruptMask = COND_SCHEDULE_DONE|COND_TASK_FAILED
            ),
            "ALERT_FACE"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_SetActivity(self, ACT_NONE),
                    Task_FaceIdeal(self)
                ],
                interruptMask=COND_NEW_TARGET|COND_SEE_FEAR|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_IN_WALL
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
                interruptMask=COND_NEW_TARGET|COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE|COND_SEE_HATE|COND_SEE_DISLIKE|COND_FRIEND_IN_WAY|COND_IN_WALL
            ),
            "YIELD_TO_FRIEND"   :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_GetPathYieldToFriend(self),
                    Task_RunPath(self, turnThenRun = False),
                    Task_AwaitMovement(self, watchTarget = True)#,
                    #Task_RestartLastSchedule(self)
                ],
                interruptMask=COND_NEW_TARGET|COND_SCHEDULE_DONE|COND_TASK_FAILED|COND_IN_WALL
            ),
            "CLEAR_WALL"    :   Schedule(
                [
                    Task_StopMoving(self),
                    Task_StopAttack(self),
                    Task_GetPathToClearWall(self),
                    Task_RunPath(self, turnThenRun = False),
                    Task_AwaitMovement(self),
                    Task_RestartLastSchedule(self)
                ]
            )
        }

        self.motor = Motor(self)
        
        self.makeScheduleNames()

        #print self.schedules
        #print self.scheduleNames

        self.idealYaw = 0.0
        self.yawSpeed = 9.0
        
        self.avatarsInSight = []
        
        self.capableAttacks = []
        self.hearing = Hearing()
        
        self.oldTargets = deque(maxlen = self.MAX_OLD_ENEMIES)
        
        self.runAITask = None
        
    def resetFwdSpeed(self):
        baseSpeed = self.BASE_SPEED

        self.motor.fwdSpeed = baseSpeed
        self.motor.lookAtWaypoints = True
        
    def makeScheduleNames(self):
        self.scheduleNames = {v : k for k,v in self.schedules.items()}

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

        stepRight = self.getQuat().getRight() * coverDelta
        stepRight[2] = 0
        testLeft = testRight = self.getPos()

        world = self.getBattleZone().getPhysicsWorld()

        #print "findLateralCover"

        for i in xrange(coverChecks):
            testLeft -= stepRight
            testRight += stepRight
            
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
        
    def getYaw(self):
        return self.getH()
        
    def setYaw(self, yaw):
        self.setH(yaw)

    def changeYaw(self, yawSpeed = None):
        if not yawSpeed:
            yawSpeed = self.yawSpeed

        current = CIGlobals.angleMod(self.getYaw())
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

            self.setYaw(CIGlobals.angleMod(current + move))
        else:
            move = 0

        return move

    def makeIdealYaw(self, target):
        self.idealYaw = CIGlobals.vecToYaw(target - self.getPos())

    def setIdealYaw(self, yaw):
        self.idealYaw = CIGlobals.angleMod(yaw)

    def getYawDiff(self):
        currentYaw = CIGlobals.angleMod(self.getYaw())
        if currentYaw == self.idealYaw:
            return 0

        return CIGlobals.angleDiff(self.idealYaw, currentYaw)

    def isFacingIdeal(self, epsilon = 0.006):
        return abs(self.getYawDiff()) <= epsilon

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
        self.rememberCurrentSchedule = None
        self.memoryPosition = None
        self.npcState = None
        self.npcStateTime = None
        self.idealState = None
        self.capableAttacks = None
        self.schedules = None
        self.oldTargets = None
        self.lastConditions = None
        self.conditionsMask = None
        self.lastHPPerct = None
        self.avatarsInSight = None
        self.schedule = None
        self.lastSchedule = None
        self.hearing.cleanup()
        self.hearing = None
        
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
        if not CIGlobals.isNodePathOk(plyr) or not CIGlobals.isNodePathOk(self):
            return False

        plLeaf = self.battleZone.bspLoader.findLeaf(plyr.getPos() + (0, 0, 0.05))
        myLeaf = self.battleZone.bspLoader.findLeaf(self.getPos() + (0, 0, 0.05))
        return plLeaf == myLeaf

    def isPlayerInPVS(self, plyr):
        if not CIGlobals.isNodePathOk(plyr) or not CIGlobals.isNodePathOk(self):
            return False
        
        plLeaf = self.battleZone.bspLoader.findLeaf(plyr.getPos() + (0, 0, 0.05))
        myLeaf = self.battleZone.bspLoader.findLeaf(self.getPos() + (0, 0, 0.05))
        return self.battleZone.bspLoader.isClusterVisible(myLeaf, plLeaf)
        
    def getDistanceSquared(self, other):
        return (self.getPos(render) - other.getPos(render)).lengthSquared()

    def isPlayerAudible(self, plyr):
        return self.isPlayerInPVS(plyr) and self.getDistanceSquared(plyr) < self.MAX_HEAR_DISTANCE_SQR
        
    def doesLineTraceToPlayer(self, plyr):
        # Do we have a clear LOS to the player?
        world = self.battleZone.physicsWorld
        result = PhysicsUtils.rayTestClosestNotMe(self,
            self.getPos(render) + self.getEyePosition(), plyr.getPos(render) + plyr.getEyePosition(),
            CIGlobals.WorldGroup | CIGlobals.CharacterGroup, world)
            
        # Assume clear LOS if ray hit nothing
        if not result:
            return True
        
        # Also clear LOS if ray hits the player
        np = NodePath(result.getNode()).getParent()
        return np.getKey() == plyr.getKey()
        
    def isPlayerInVisionCone(self, plyr):
        # Is the player in my angle of vision?

        toPlyr = plyr.getPos() - self.getPos()
        yaw = CIGlobals.angleMod(CIGlobals.vecToYaw(toPlyr))
        diff = CIGlobals.angleDiff(yaw, CIGlobals.angleMod(self.getYaw()))

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
        
    def getBestVisibleTarget(self, avs = None):
        target = None
        bestRelationship = RELATIONSHIP_NONE
        nearest = 9999999
        
        if not avs:
            avs = self.avatarsInSight
        
        for i in xrange(len(avs)):
            av = avs[i]
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
        
        isDead = True
        try:
            isDead = self.target.entity.getHealth() <= 0
        except: pass
        
        if isDead:
            self.setConditions(COND_TARGET_DEAD)
            self.clearConditions(COND_SEE_TARGET | COND_TARGET_OCCLUDED)
            self.clearTarget()
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
            if attack.checkCapable(dot, distSqr) and attack.hasAmmo() and not attack.isCoolingDown():
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
            if ((self.target is None or target != self.target.entity) and target is not None and target.takesDamage()):
                if ((self.schedule and ((self.schedule.interruptMask & COND_NEW_TARGET) != 0)) or
                    not self.schedule):
                    self.pushTarget(self.target)
                    self.setConditions(COND_NEW_TARGET)
                    self.target = AITarget(target, relationship)
                        
        # Remember old targets
        if not self.target and self.popTarget():
            if ((self.schedule and ((self.schedule.interruptMask & COND_NEW_TARGET) != 0)) or
               not self.schedule):
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
            # IDLE goes to ALERT upon hearing a sound
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
                
            elif conditions & COND_HEAR_SOMETHING:
                bestSound = self.bestSound()
                if bestSound:
                    self.makeIdealYaw(bestSound.origin)
                    if ((bestSound.soundType & SOUND_COMBAT) or
                    (self.getRelationshipTo(bestSound.emitter) == RELATIONSHIP_HATE and (bestSound.soundType & SOUND_SPEECH))):
                        
                        # We just heart sounds of combat or somebody that we hate.
                        self.idealState = STATE_ALERT

        elif self.npcState == STATE_ALERT:

            # ALERT goes to IDLE upon becoming bored
            # ALERT goes to COMBAT upon sighting an enemy

            if conditions & (COND_NEW_TARGET|COND_SEE_TARGET):
                # If we see an enemy, we must attack
                self.idealState = STATE_COMBAT
                
            elif conditions & COND_HEAR_SOMETHING:
                self.idealState = STATE_ALERT
                bestSound = self.bestSound()
                if bestSound:
                    self.makeIdealYaw(bestSound.origin)
        
        elif self.npcState == STATE_COMBAT:
            if not self.target:
                self.idealState = STATE_ALERT

        elif self.npcState == STATE_DEAD:
            self.idealState = STATE_DEAD

        return self.idealState

    def getSchedule(self):
        
        if self.npcState == STATE_NONE:
            return None
            
        #elif (self.npcState not in [STATE_SCRIPT, STATE_DEAD]) and self.hasConditions(COND_FRIEND_IN_WAY):
            # We can yield to a friend in any active state
        #    return self.getScheduleByName("YIELD_TO_FRIEND")
        if (self.npcState not in [STATE_SCRIPT, STATE_DEAD]) and self.hasConditions(COND_IN_WALL):
            # Get out of the wall
            return self.getScheduleByName("CLEAR_WALL")

        elif self.npcState == STATE_IDLE:
            if self.hasConditions(COND_HEAR_SOMETHING):
                return self.getScheduleByName("ALERT_FACE")
            return self.getScheduleByName("IDLE_STAND")

        elif self.npcState == STATE_ALERT:
            if self.hasConditions(COND_LIGHT_DAMAGE|COND_HEAVY_DAMAGE):
                #if abs(self.getYawDiff()) < self.MAX_VISION_ANGLE * 0.5:
                return self.getScheduleByName("TAKE_COVER_FROM_ORIGIN")
                #else:
                #    return self.getScheduleByName("ALERT_SMALL_FLINCH")
            elif self.hasConditions(COND_HEAR_SOMETHING):
                return self.getScheduleByName("ALERT_FACE")
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
            if self.hasConditions(COND_NEW_TARGET) and not self.hasMemory(MEMORY_COMBAT_WAKE):
                return self.getScheduleByName("WAKE_ANGRY")
            elif self.hasConditions(COND_LIGHT_DAMAGE) and not self.hasMemory(MEMORY_FLINCHED):
                return self.getScheduleByName("SMALL_FLINCH")
            elif self.hasConditions(COND_HEAVY_DAMAGE):
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
        
    def shouldYield(self, av):
        if not self.canMove():
            return False
        elif self.canMove() and not av.canMove():
            return False
        elif av.getHealth() < self.getHealth():
            # Don't yield to someone who has less health than me.
            # We should probably protect them.
            return False
        elif hasattr(self, 'doId') and hasattr(av, 'doId') and self.doId < av.doId:
            # Don't yield to a younger friend (higher doId)
            return False
        elif id(self) < id(av):
            # Don't yield to a younger friend
            # (higher memory address? if that even means they are younger)
            return False
        
        return (self.getPos() - av.getPos()).length() < self.getYieldDistance()
        
    def getYieldDistance(self):
        return 5.0
        
    def getHearingSensitivity(self):
        return 1.0
        
    def bestSound(self):
        """Returns the closest sound to the NPC."""
        
        closestSoundDist = 500*500
        closestSound = None
        for sound in self.battleZone.soundEmitterSystem.getSounds():
            distToSound = (sound.origin - self.getPos()).lengthSquared()
            if distToSound < closestSoundDist:
                closestSound = sound
                closestSoundDist = distToSound
                
        return closestSound
        
    def listen(self):
        """Listen for nearby sounds."""
        
        self.clearConditions(COND_HEAR_DANGER | COND_HEAR_SOMETHING | COND_VP_JUMPING)
        
        self.hearing.soundList = []
        self.hearing.soundBits = 0
        
        myLeaf = self.battleZone.bspLoader.findLeaf(self.getPos() + (0, 0, 0.05))
        
        hearingSensitivity = self.getHearingSensitivity()
        
        bits = 0
        
        for sound in self.battleZone.soundEmitterSystem.getSounds():
            if sound.emitter == self:
                # I don't care about sounds I make
                continue
                
            soundLeaf = self.battleZone.bspLoader.findLeaf(sound.origin + (0, 0, 0.05))
            if not self.battleZone.bspLoader.isClusterVisible(myLeaf, soundLeaf):
                # Not potentially audible
                continue
            distToSound = (sound.origin - self.getPos()).length()
            maxHearDistance = sound.volume * hearingSensitivity
            if distToSound > maxHearDistance:
                # Too far to hear it
                continue
            # Well, we hear something
            bits |= COND_HEAR_SOMETHING
            if (sound.soundType & SOUND_VP_JUMP) != 0:
                bits |= COND_VP_JUMPING
                
            self.hearing.soundList.append(sound)
            self.hearing.soundBits |= sound.soundType
            
        self.setConditions(bits)
        
    def checkWalls(self):
        result = self.battleZone.physicsWorld.contactTest(self.bodyNode)
        for i in range(result.getNumContacts()):
            contact = result.getContact(i)
            other = contact.getNode1()
            mfld = contact.getManifoldPoint()
            if (other.getIntoCollideMask() & CIGlobals.CharacterGroup) != 0:
                self.wallPoints = [mfld.getPositionWorldOnA(), mfld.getPositionWorldOnB()]
                self.setConditions(COND_IN_WALL)
                return
                
        self.clearConditions(COND_IN_WALL)
        #self.wallPoints = None
        
    def look(self):
        """Look at the world in front of me."""

        self.clearConditions(COND_SEE_HATE | COND_SEE_FEAR | COND_SEE_DISLIKE |
                             COND_SEE_TARGET | COND_SEE_FRIEND | COND_FRIEND_IN_WAY)
        
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
                if (bits & COND_FRIEND_IN_WAY) == 0 and self.shouldYield(av):
                    # We need to move out of the way of our friend
                    bits |= COND_FRIEND_IN_WAY
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

    def changeSchedule(self, sched, remember = True):
        if sched:
            sched.reset()

        if self.rememberCurrentSchedule:
            self.lastSchedule = self.schedule
        self.rememberCurrentSchedule = remember
        self.schedule = sched
        self.conditionsMask = 0

    def setNPCState(self, state, makeIdeal = True):

        #print "Set state to", state

        if state == STATE_IDLE:
            # not allowed to have target anymore
            if self.target is not None:
                self.clearTarget()
            self.forget(MEMORY_COMBAT_WAKE)

        self.npcState = state
        self.npcStateTime = globalClock.getFrameTime()
        if makeIdeal:
            self.idealState = state
            
    def setIdealState(self, state):
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
                
                # Don't restart the same schedule
                if newSched != self.schedule or self.hasConditions(COND_SCHEDULE_DONE):
                    self.changeSchedule(newSched)

        if self.schedule:
            run = self.schedule.runSchedule()
            if run == SCHED_COMPLETE:
                self.setConditions(COND_SCHEDULE_DONE)
            elif run == SCHED_FAILED:
                self.setConditions(COND_TASK_FAILED)
            else:
                pass
        
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
            self.notify.warning("Cannot run AI without a battle zone!")
            return

        if self.isDead() and self.npcState != STATE_DEAD:
            self.setNPCState(STATE_DEAD, makeIdeal = False)
            
        # Don't bother with this crap if we are dead.
        if self.npcState != STATE_DEAD and self.npcState != STATE_NONE:
            self.look()
            self.listen()
            if self.canMove():
                self.checkWalls()
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

        
        
