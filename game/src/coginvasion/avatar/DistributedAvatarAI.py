"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedAvatarAI.py
@author Brian Lach
@date November 02, 2014

"""

from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape, ZUp
from panda3d.core import TransformState, Point3, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedSmoothNodeAI
from src.coginvasion.globals import CIGlobals

from AvatarTypes import AVATAR_NONE
from AvatarShared import AvatarShared
from Activities import ACT_NONE
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_NONE

class DistributedAvatarAI(DistributedSmoothNodeAI.DistributedSmoothNodeAI, AvatarShared):
    notify = directNotify.newCategory("DistributedAvatarAI")
    
    AvatarType = AVATAR_NONE
    # AI relationships to other types of avatars
    Relationships = {}
    
    Moving = True
    NeedsPhysics = True

    def __init__(self, air):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.__init__(self, air)
        AvatarShared.__init__(self)
        
        self.lastPos = Point3(0)
        self.movementDelta = Vec3(0)
        self.movementVector = Vec3(0)
        return

    def getActivityDuration(self, act):
        return self.activities.get(act, 0.0)

    def getLightDamage(self):
        return 1

    def getHeavyDamage(self):
        return 10

    def b_setAttackIds(self, ids):
        self.sendUpdate('setAttackIds', [ids])
        self.setAttackIds(ids)

    def b_setActivity(self, activity):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setActivity', [activity, timestamp])
        self.setActivity(activity, timestamp)

    def __stopActivityTask(self):
        taskMgr.remove("activityTask-" + str(id(self)))

    def setActivity(self, activity, timestamp):
        AvatarShared.setActivity(self, activity, timestamp)

        self.__stopActivityTask()

        if activity == -1 or activity not in self.activities:
            self.doingActivity = False
            return

        self.doingActivity = True
        taskMgr.doMethodLater(self.activities[activity], self.__activityTask, "activityTask-" + str(id(self)))
        
    def __activityTask(self, task):
        self.doingActivity = False
        self.b_setActivity(ACT_NONE)
        return task.done

    def d_playAnimation(self, animName):
        self.sendUpdate('playAnimation', [animName, globalClockDelta.getFrameNetworkTime()])

    def b_setAttackState(self, state):
        self.sendUpdate('setAttackState', [state])
        self.setAttackState(state)
        
    def getMovementVector(self):
        return self.movementVector
        
    def __avatarTick(self, task):
        if self.isEmpty():
            return task.done
            
        pos = self.getPos()
        
        if (pos - self.lastPos).lengthSquared() <= 0.001:
            self.movementDelta.set(0, 0, 0)
            self.movementVector.set(0, 0, 0)
            self.lastPos = pos
            return task.cont
        
        # Determine movement vector, used by AI sensing.
        self.movementDelta = pos - self.lastPos
        self.movementVector = self.movementDelta.normalized()
        self.lastPos = pos
            
        return task.cont
        
    def takeDamage(self, dmgInfo):
        hp = self.getHealth() - dmgInfo.damageAmount
        if hp < 0:
            hp = 0
        self.b_setHealth(hp)
        self.d_announceHealth(0, -dmgInfo.damageAmount)
        try:    self.setDamageConditions(dmgInfo.damageAmount)
        except: pass

    def d_setHood(self, hood):
        self.sendUpdate('setHood', [hood])

    def b_setHood(self, hood):
        self.d_setHood(hood)
        self.setHood(hood)

    def d_setName(self, name):
        self.sendUpdate("setName", [name])

    def b_setName(self, name):
        self.d_setName(name)
        self.setName(name)

    def d_setMaxHealth(self, health):
        self.sendUpdate("setMaxHealth", [health])

    def b_setMaxHealth(self, health):
        self.d_setMaxHealth(health)
        self.setMaxHealth(health)

    def b_setPlace(self, place):
        self.sendUpdate("setPlace", [place])
        self.setPlace(place)

    def setHealth(self, health):
        # Let's send out an event to let listeners know that our health changed.
        # The new health and the previous health are sent out in that order.
        messenger.send(self.getHealthChangeEvent(), [health, self.getHealth()])
        AvatarShared.setHealth(self, health)

    def d_setHealth(self, health):
        self.sendUpdate("setHealth", [health])

    def b_setHealth(self, health):            
        self.d_setHealth(health)
        self.setHealth(health)

    def d_announceHealth(self, level, hp, extraId = -1):
        # There's no need to announce when the avatar's health doesn't change.
        if hp != 0:
            self.sendUpdate('announceHealth', [level, hp, extraId])
            
    def toonUp(self, hp, announce = 1, sound = 1):
        amt = hp
        originalHealth = self.getHealth()
        hp = self.getHealth() + hp
        if hp > self.getMaxHealth():
            amt = self.getMaxHealth() - originalHealth
            hp = self.getMaxHealth()
        self.b_setHealth(hp)
        #if announce and sound:
        #    self.d_announceHealthAndPlaySound(1, amt)
        #elif announce and not sound:
        if announce:
            self.d_announceHealth(1, amt)
            
    def getHealthChangeEvent(self):
        # This is sent once our health changes.
        if hasattr(self, 'doId'):
            return 'DAvatarAI-healthChanged-{0}'.format(self.doId)
        return None
        
    def b_updateAttackAmmo(self, attackID, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip):
        self.sendUpdate('updateAttackAmmo', [attackID, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip])
        self.updateAttackAmmo(attackID, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip)
        
    def handleLogicalZoneChange(self, newZoneId, oldZoneId):
        """Make sure the avatar lists are updated with our new zone."""
        
        self.air.removeAvatar(self)
        self.air.addAvatar(self, newZoneId)
        
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.handleLogicalZoneChange(self, newZoneId, oldZoneId)
        
    def getRelationshipTo(self, avatar):
        if not hasattr(avatar, 'AvatarType'):
            return RELATIONSHIP_NONE
            
        return self.Relationships.get(avatar.AvatarType, RELATIONSHIP_NONE)

    def setupPhysics(self):
        if not self.NeedsPhysics:
            return

        bodyNode = BulletRigidBodyNode(self.uniqueName('avatarBodyNode'))

        radius = self.getWidth()
        height = self.getHeight()# - (radius * 2)
        zOfs = (height / 2.0) + radius
        capsule = BulletCapsuleShape(radius, height)
        bodyNode.addShape(capsule, TransformState.makePos(Point3(0, 0, zOfs)))
        bodyNode.setKinematic(True)
        bodyNode.setMass(0.0)
        
        self.notify.debug("setupPhysics(r{0}, h{1}) hitboxData: {2}".format(radius, height, self.hitboxData))
        
        AvatarShared.setupPhysics(self, bodyNode, True)
        
    def announceGenerate(self):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.announceGenerate(self)
        AvatarShared.announceGenerate(self)

        self.setupPhysics()

        # Add ourself to the avatar list for the zone
        base.air.addAvatar(self)
        
        if self.Moving:
            self.lastPos = self.getPos(render)
            taskMgr.add(self.__avatarTick, self.uniqueName('avatarTick'))
        
    def disable(self):
        pass
    
    def delete(self):
        self.__stopActivityTask()
        base.air.removeAvatar(self)
        
        if self.Moving:
            taskMgr.remove(self.uniqueName('avatarTick'))

        self.movementVector = None
        self.movementDelta = None
        self.lastPos = None
        
        AvatarShared.delete(self)
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.delete(self)
