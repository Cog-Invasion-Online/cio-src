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
from Activities import ACT_NONE, ACT_FINISH
from src.coginvasion.phys.PhysicsNodePathAI import BasePhysicsObjectAI
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_NONE
from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI
from src.coginvasion.battle.SoundEmitterSystemAI import SOUND_SPEECH

import random

class DistributedAvatarAI(DistributedEntityAI, AvatarShared):
    notify = directNotify.newCategory("DistributedAvatarAI")
    
    AvatarType = AVATAR_NONE
    # AI relationships to other types of avatars
    Relationships = {}
    
    # <rule name> -> ([<response list>], <chance>)
    RulesAndResponses = {}
    
    Moving = True
    NeedsPhysics = True

    def __init__(self, air, dispatch = None):
        DistributedEntityAI.__init__(self, air, dispatch)
        BasePhysicsObjectAI.__init__(self)
        AvatarShared.__init__(self)
        
        self.latestDamage = None
        
        self.blockAIChat = False
        
        # Activity translations
        self.actTable = {}
        
        self.lastPos = Point3(0)
        self.movementDelta = Vec3(0)
        self.movementVector = Vec3(0)
        self.attackFinished = False
        
        return
        
    def npcFinishAttack(self):
        self.attackFinished = True
        
    def setBlockAIChat(self, flag):
        self.blockAIChat = flag
        
    def canMove(self):
        return True
        
    def takesDamage(self):
        return True
        
    def translateActivity(self, act):
        return self.actTable.get(act, act)
        
    def getViewOrigin(self):
        return self.getPos(render) + (0, 0, self.getHeight() * 0.5)
        
    def getViewVector(self, n):
        quat = self.getQuat(render)
        if n == 0:
            return quat.getRight()
        elif n == 1:
            return quat.getForward()
        elif n == 2:
            return quat.getUp()
        
        return None
        
    def isPreservable(self):
        # Avatars should always be preserved during level transitions.
        return True
        
    def d_setChat(self, chat):
        """For when we set chat from the server."""
        
        AvatarShared.d_setChat(self, chat)
        
        self.emitSound(SOUND_SPEECH)
        
    def setChat(self, chat):
        """For when chat is set from the client."""
        
        AvatarShared.setChat(self, chat)
        
        self.emitSound(SOUND_SPEECH)

    def getAttackMgr(self):
        return self.air.attackMgr

    def getActivityDuration(self, act):
        return self.activities.get(act, 0.0)

    def getLightDamage(self):
        return 1

    def getHeavyDamage(self):
        return 10

    def d_doRagdollMode(self, force = None, forcePos = None):
        if not force and self.latestDamage:
            force = self.latestDamage.damageForce
        else:
            force = Vec3(0)
            
        if not forcePos and self.latestDamage:
            forcePos = self.latestDamage.damagePos
        else:
            forcePos = self.getPos()
            
        self.sendUpdate('doRagdollMode', [force[0], force[1], force[2],
                                          forcePos[0], forcePos[1], forcePos[2]])

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
        activity = self.translateActivity(activity)
        AvatarShared.setActivity(self, activity, timestamp)

        self.__stopActivityTask()

        if activity < 0 or activity not in self.activities:
            self.doingActivity = False
            return

        self.doingActivity = True
        if self.activities[activity] != -1:
            taskMgr.doMethodLater(self.activities[activity], self.__activityTask, "activityTask-" + str(id(self)))
        
    def onActivityFinish(self):
        pass
        
    def __activityTask(self, task):
        self.doingActivity = False
        self.onActivityFinish()
        self.b_setActivity(ACT_FINISH)
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
        
    def d_handleDamage(self, damagePos):
        self.sendUpdate('handleDamage', [damagePos[0], damagePos[1], damagePos[2]])
        
    def takeDamage(self, dmgInfo):
        self.latestDamage = dmgInfo
        hp = self.getHealth() - dmgInfo.damageAmount
        if hp < 0:
            hp = 0
        self.b_setHealth(hp)
        self.d_announceHealth(0, -dmgInfo.damageAmount)
        self.d_handleDamage(dmgInfo.damageOrigin)
        try:    self.setDamageConditions(dmgInfo.damageAmount)
        except: pass
        
    def heal(self, amount):
        amount = max(0, amount)
        
        newHP = self.getHealth() + amount
        if newHP > self.getMaxHealth():
            newHP = self.getMaxHealth()
            amount = self.getMaxHealth() - self.getHealth()
            
        if amount == 0:
            return
            
        self.b_setHealth(newHP)
        self.d_announceHealth(1, amount)

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
        
        DistributedEntityAI.handleLogicalZoneChange(self, newZoneId, oldZoneId)
        
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
        
        BasePhysicsObjectAI.setupPhysics(self, bodyNode, True)
        
    def handleRule(self, ruleName):
        if ruleName in self.RulesAndResponses:
            responseInfo = self.RulesAndResponses[ruleName]
            responses = responseInfo[0]
            chance = responseInfo[1]
            if random.random() <= chance:
                if isinstance(responses, list):
                    response = random.choice(responses)
                else:
                    response = responses
                self.d_setChat(response)
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        AvatarShared.announceGenerate(self)
        
        self.accept('globalrule', self.handleRule)

        self.setupPhysics()

        # Add ourself to the avatar list for the zone
        # But if we somehow are already in there, remove us.
        base.air.removeAvatar(self)
        base.air.addAvatar(self)
        
        if self.Moving:
            self.lastPos = self.getPos(render)
            taskMgr.add(self.__avatarTick, self.uniqueName('avatarTick'))
    
    def delete(self):
        self.ignore('globalrule')
        self.__stopActivityTask()
        base.air.removeAvatar(self)
        
        if self.Moving:
            taskMgr.remove(self.uniqueName('avatarTick'))

        self.movementVector = None
        self.movementDelta = None
        self.lastPos = None
        self.blockAIChat = None
        self.latestDamage = None
        self.attackFinished = None
        
        AvatarShared.delete(self)
        DistributedEntityAI.delete(self)
