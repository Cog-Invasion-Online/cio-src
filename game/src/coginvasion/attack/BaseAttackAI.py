from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import NodePath, TransformState, Vec3
from panda3d.bullet import BulletSphereShape

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog.ai.AIGlobal import RELATIONSHIP_FRIEND
from TakeDamageInfo import TakeDamageInfo
from src.coginvasion.attack.BaseAttackShared import BaseAttackShared
from src.coginvasion.phys import PhysicsUtils, Surfaces
from src.coginvasion.battle.SoundEmitterSystemAI import SOUND_COMBAT

import random

class BaseAttackAI(BaseAttackShared):
    notify = directNotify.newCategory("BaseAttackAI")
    
    Cost = 0

    Server = True
    FriendlyFire = False
    
    HealFriends = False
    HealAmount = 0
    
    HasCooldown = False
    CooldownTime = 0.0

    TraceMask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup

    def __init__(self, sharedMetadata = None):
        BaseAttackShared.__init__(self, sharedMetadata)
        self.actionLengths = {self.StateIdle: -1}
        self.cooldownStart = 0.0
        self.coolingDown = False
        
    def npc_testAttackLOS(self, startPos, endPos):
        # Makes sure the NPC has a line-of-sight to endPos for this attack
        # If not, tries to find a new position either directly to the left
        # or right of startPos that has a line-of-sight to endPos.
        
        losChecks = 5
        losStep = 1.0
        
        stepRight = self.avatar.getQuat().getRight() * losStep
        stepRight[2] = 0
        testLeft = Vec3(startPos)
        testRight = Vec3(startPos)
        
        sphere = BulletSphereShape(1.0)
        
        # Test center
        result = self.avatar.battleZone.physicsWorld.sweepTestClosest(
            sphere, TransformState.makePos(startPos), TransformState.makePos(endPos), CIGlobals.WorldGroup)
        if not result.hasHit():
            # We have a line-of-sight from start to end
            return [True, Vec3()]
        
        for i in xrange(losChecks):
            testLeft -= stepRight
            testRight += stepRight
            
            # Test to the left
            result = self.avatar.battleZone.physicsWorld.sweepTestClosest(
                sphere, TransformState.makePos(testLeft), TransformState.makePos(endPos), CIGlobals.WorldGroup)
            if not result.hasHit():
                # We now have a line-of-sight, move to the new position
                vecMove = testLeft - startPos
                return [False, vecMove]
                
            # Test to the right
            result = self.avatar.battleZone.physicsWorld.sweepTestClosest(
                sphere, TransformState.makePos(testRight), TransformState.makePos(endPos), CIGlobals.WorldGroup)
            if not result.hasHit():
                # We now have a line-of-sight, move to the new position
                vecMove = testRight - startPos
                return [False, vecMove]
        
        # Couldn't get a line-of-sight, randomly choose left or right and try again
        return [False, random.choice([testLeft, testRight]) - startPos]
        
    def canDamage(self, obj):
        if not hasattr(self, 'avatar'):
            return False
            
        bz = self.avatar.getBattleZone()
        if bz:
            return bz.getGameRules().canDamage(self.avatar, obj, self)

        # No GameRules to determine, just damage them.
        return True

    def equip(self):
        if not BaseAttackShared.equip(self):
            return False

        self.b_setAction(self.StateIdle)

        return True

    def onProjectileHit(self, contact, collider, intoNP, deleteIt = True):
        bz = base.air.getBattleZone(collider.zoneId)
        surface = Surfaces.getSurfaceFromContact(contact, bz)
        bz.d_emitSound(surface.getBulletImpacts(), contact.getHitPos(), 0.5)
        
        avNP = intoNP.getParent()

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        try:
            dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                     self.calcDamage((currProj - collider.getInitialPos()).length()),
                                     currProj, collider.getInitialPos())
        
        
            # Sometimes the avatar could be deleted unexpectedly.
            for obj in base.air.avatars[self.avatar.getBattleZone().zoneId]:
                if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey()):
                    if self.canDamage(obj):
                        obj.takeDamage(dmgInfo)
                    elif self.avatar.getRelationshipTo(obj) == RELATIONSHIP_FRIEND and self.HealFriends:
                        obj.heal(self.HealAmount)
                        obj.handleRule("HealedByFriend")
                    break
        except: pass

        if deleteIt:
            collider.requestDelete()
            
        # Emit a sound at the hit point
        self.avatar.emitSound(SOUND_COMBAT, contact.getHitPos(), duration = 0.25)

    def __handleHitSomething_trace(self, hitNode, hitPos, hitNormal, distance, origin, contact, traces = 1, impact = True):
        traceDir = (hitPos - origin).normalized()
        
        if impact and hasattr(self, 'avatar'):
            surface = Surfaces.getSurfaceFromContact(contact, self.avatar.getBattleZone())
            self.avatar.getBattleZone().d_emitSound(surface.getBulletImpacts(), hitPos, 0.5)
            decals = surface.getImpactDecals()
            if len(decals):
                self.avatar.getBattleZone().getTempEnts().makeDecalTrace(
                    random.choice(decals), 0.3, 0, origin, hitPos + (traceDir * 0.1))

            if "metal" in Surfaces.getSurfaceName(surface):
                for _ in xrange(traces * random.randint(2, 4)):
                    self.avatar.getBattleZone().getTempEnts().makeBulletRicochet(hitPos, traceDir, hitNormal)
                    
            # Emit a sound at the hit point
            self.avatar.emitSound(SOUND_COMBAT, contact.getHitPos(), duration = 0.25)
            
        avNP = hitNode.getParent()
        
        try:
            # Again, sometimes the avatar can be deleted unexpectedly.
            for obj in base.air.avatars[self.avatar.getBattleZone().zoneId]:
                if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and 
                self.canDamage(obj)):
                    
                    for _ in xrange(traces):
                        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                            self.calcDamage(distance),
                                            hitPos, origin)
                        
                        obj.takeDamage(dmgInfo)
    
                    break
        except: pass

    def doTraceAndDamage(self, origin, dir, dist, traces = 1, impact = True):
        # Trace a line from the trace origin outward along the trace direction
        # to find out what we hit, and adjust the direction of the hitscan
        traceEnd = origin + (dir * dist)
        hit = PhysicsUtils.rayTestClosestNotMe(self.avatar,
                                                origin,
                                                traceEnd,
                                                self.TraceMask,
                                                self.avatar.getBattleZone().getPhysicsWorld())
        if hit is not None:
            node = hit.getNode()
            hitPos = hit.getHitPos()
            distance = (hitPos - origin).length()
            norm = hit.getHitNormal()
            self.__handleHitSomething_trace(NodePath(node), hitPos, norm, distance, origin, hit, traces, impact)
            return node

        return None

    def getPostAttackSchedule(self):
        return None
        
    def getTauntPhrases(self):
        return []
        
    def getTauntChance(self):
        return 0.0

    def cleanup(self):
        del self.actionLengths
        BaseAttackShared.cleanup(self)
        
    def d_updateAttackAmmo(self):
        if self.hasAvatar():
            
            problematic = 0
            if self.ammo < 0:
                self.ammo = abs(self.ammo)
                problematic = 1
            if self.maxAmmo < 0:
                self.maxAmmo = abs(self.maxAmmo)
                problematic = 1
            
            if problematic: self.notify.info('Attack ID {0} had problematic data. Ammo or max ammo or both had values less than 0!'.format(self.getID(), self.ammo, self.maxAmmo))
                
            
            self.avatar.sendUpdate('updateAttackAmmo', [self.getID(), self.ammo, self.maxAmmo, self.secondaryAmmo,
                                                        self.secondaryMaxAmmo, self.clip, self.maxClip])

    def takeAmmo(self, amount):
        self.ammo += amount
        self.d_updateAttackAmmo()
        
    def getActionLength(self, action):
        return self.actionLengths.get(action, -1)
            
    def isActionIndefinite(self):
        return self.getActionLength(self.action) == -1

    def isActionComplete(self):
        length = self.getActionLength(self.action)
        if length == -1:
            return False
        return self.getActionTime() >= length

    def shouldGoToNextAction(self, complete):
        return complete

    def determineNextAction(self, completedAction):
        return self.StateIdle

    def b_setAction(self, action):
        if self.hasAvatar():
            self.avatar.sendUpdate('setAttackState', [action])
        self.setAction(action)

    def think(self):
        complete = self.isActionComplete()

        if complete and self.nextAction is None:
            nextAction = self.determineNextAction(self.action)
            if self.action != nextAction or nextAction != self.StateIdle:
                self.b_setAction(nextAction)
        elif (self.nextAction is not None and
              self.shouldGoToNextAction(complete or self.isActionIndefinite())):
            self.b_setAction(self.nextAction)
            self.nextAction = None
        
        now = globalClock.getFrameTime()
        if self.coolingDown and now - self.cooldownStart >= self.CooldownTime:
            self.coolingDown = False
            
    def startCooldown(self):
        self.coolingDown = True
        self.cooldownStart = globalClock.getFrameTime()
        
    def stopCooldown(self):
        self.coolingDown = False
        
    def isCoolingDown(self):
        return self.HasCooldown and self.coolingDown

    def checkCapable(self, dot, squaredDistance):
        """
        Returns whether or not this attack is capable of being performed by an AI,
        based on how much the NPC is facing the target, and the distance to the target.

        NOTE: It's squared distance
        """
        return True
    
    def npcUseAttack(self, target):
        """
        Called when an NPC wants to fire this attack on `target`.
        Each attack should override this function to implement
        specific functionality for how an NPC aims and fires
        this attack.
        """
        return False
