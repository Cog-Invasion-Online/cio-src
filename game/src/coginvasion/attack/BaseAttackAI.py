from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import NodePath

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog.ai.AIGlobal import RELATIONSHIP_FRIEND
from TakeDamageInfo import TakeDamageInfo
from src.coginvasion.attack.BaseAttackShared import BaseAttackShared
from src.coginvasion.phys import PhysicsUtils

class BaseAttackAI(BaseAttackShared):
    notify = directNotify.newCategory("BaseAttackAI")

    Server = True
    FriendlyFire = False

    def __init__(self, sharedMetadata = None):
        BaseAttackShared.__init__(self)
        self.actionLengths = {self.StateIdle: -1}
        
        if sharedMetadata:
            for key in sharedMetadata.__dict__.keys():
                setattr(self, key, sharedMetadata.__dict__.get(key))
        
    def canDamage(self, obj):
        if self.FriendlyFire:
            return True
            
        return self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND

    def equip(self):
        if not BaseAttackShared.equip(self):
            return False

        self.b_setAction(self.StateIdle)

        return True

    def onProjectileHit(self, contact, collider, intoNP):
        avNP = intoNP.getParent()

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                 self.calcDamage((currProj - collider.getInitialPos()).length()),
                                 currProj, collider.getInitialPos())

        for obj in base.air.avatars[self.avatar.zoneId]:
            if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and
                self.canDamage(obj)):

                obj.takeDamage(dmgInfo)
                break

        collider.requestDelete()

    def __handleHitSomething_trace(self, hitNode, hitPos, distance, origin, traces = 1):
        avNP = hitNode.getParent()
        
        for obj in base.air.avatars[self.avatar.zoneId]:
            if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and 
            self.canDamage(obj)):
                
                for i in xrange(traces):
                    dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                        self.calcDamage(distance),
                                        hitPos, origin)
                    
                    obj.takeDamage(dmgInfo)

                break

    def doTraceAndDamage(self, origin, dir, dist, traces = 1):
        # Trace a line from the trace origin outward along the trace direction
        # to find out what we hit, and adjust the direction of the hitscan
        traceEnd = origin + (dir * dist)
        hit = PhysicsUtils.rayTestClosestNotMe(self.avatar,
                                                origin,
                                                traceEnd,
                                                CIGlobals.WorldGroup | CIGlobals.CharacterGroup,
                                                self.avatar.getBattleZone().getPhysicsWorld())
        if hit is not None:
            node = hit.getNode()
            hitPos = hit.getHitPos()
            distance = (hitPos - origin).length()
            self.__handleHitSomething_trace(NodePath(node), hitPos, distance, origin, traces)

    def getPostAttackSchedule(self):
        return None
        
    def getTauntPhrases(self):
        return []
        
    def getTauntChance(self):
        return 0.0

    def cleanup(self):
        del self.actionLengths
        BaseAttackShared.cleanup(self)

    def takeAmmo(self, amount):
        self.ammo += amount
        if self.hasAvatar():
            self.avatar.sendUpdate('updateAttackAmmo', [self.getID(), self.ammo])
            
    def isActionIndefinite(self):
        return self.actionLengths[self.action] == -1

    def isActionComplete(self):
        length = self.actionLengths[self.action]
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
        pass
