from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.phys.PhysicsNodePath import BasePhysicsObject

from src.coginvasion.globals import CIGlobals

from src.coginvasion.attack import AttackClasses

class AvatarShared(BasePhysicsObject):
    """
    Base class shared between Server and Client implementations of the Avatar.
    
    It MUST be inherited by a DistributedObject, at least. (It calls sendUpdate())
    """

    notify = directNotify.newCategory("AvatarShared")

    def __init__(self):
        BasePhysicsObject.__init__(self)
        self.shapeGroup = CIGlobals.CharacterGroup
        self.health = 100
        self.maxHealth = 100
        self.moveBits = 0
        self.hood = ""
        self._name = ""
        self.place = 0

        # Shape, width, and height specification for the avatar's hitbox
        self.hitboxData = [0, 1, 1]

        # Id's of attacks available to avatar
        self.attackIds = []
        # Instances of attack classes available to avatar
        self.attacks = {}
        self.equippedAttack = -1

        self.lookPitch = 0

        self.doingActivity = False
        self.activity = 0
        self.activityTimetamp = 0
        self.activities = {}

    def getEyePosition(self):
        return (0, 0, self.getHeight() * 0.8)

    def setAttackIds(self, ids):
        self.attackIds = ids
        self.rebuildAttacks()

    def getAttackIds(self):
        return self.attackIds

    def setActivities(self, actDict):
        """
        On the client, this is a dictionary of Activity ID -> Activity instance.
        On the server, this is a dictionary of Activity ID -> Activity duration (in seconds).
        """
        self.activities = actDict

    def getActivities(self):
        return self.activities

    def isDoingActivity(self):
        return self.doingActivity

    def setActivity(self, activity, timestamp):
        self.activity = activity
        self.activityTimetamp = timestamp

    def getActivity(self):
        return [self.activity, self.activityTimetamp]

    def setLookPitch(self, pitch):
        self.lookPitch = pitch

    def b_setLookPitch(self, pitch):
        self.sendUpdate('setLookPitch', [pitch])
        self.setLookPitch(pitch)

    def getLookPitch(self):
        return self.lookPitch

    def hasEquippedAttack(self):
        return self.equippedAttack != -1

    def primaryFirePress(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].primaryFirePress(data)

    def primaryFireRelease(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].primaryFireRelease(data)

    def secondaryFirePress(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].secondaryFirePress(data)

    def secondaryFireRelease(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].secondaryFireRelease(data)

    def reloadPress(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].reloadPress(data)

    def reloadRelease(self, data = None):
        if not self.hasEquippedAttack():
            return

        self.attacks[self.equippedAttack].reloadRelease(data)

    def setEquippedAttack(self, attackID):
        if attackID != -1 and not attackID in self.attacks:
            # ?
            self.notify.warning("Tried to equip attack {0}, but not in attacks.".format(attackID))
            return

        if self.equippedAttack != -1:
            if self.equippedAttack in self.attacks:
                self.attacks[self.equippedAttack].unEquip()

        self.equippedAttack = attackID

        if self.equippedAttack != -1:
            self.attacks[self.equippedAttack].equip()

    def b_setEquippedAttack(self, attackID):
        self.sendUpdate('setEquippedAttack', [attackID])
        self.setEquippedAttack(attackID)

    def getEquippedAttack(self):
        return self.equippedAttack

    def updateAttackAmmo(self, attackID, ammo):
        if not attackID in self.attacks:
            # ?
            self.notify.warning("Tried to update ammo on attack {0}, but not in attacks.".format(attackID))
            return

        self.attacks[attackID].setAmmo(ammo)

    def setAttackState(self, state):
        if self.equippedAttack == -1:
            return

        self.attacks[self.equippedAttack].setAction(state)

    def getAttackState(self):
        if self.equippedAttack == -1:
            return 0

        return self.attacks[self.equippedAttack].getAction()

    def setHeight(self, height):
        self.hitboxData[2] = height

    def b_setHeight(self, height):
        self.setHeight(height)
        self.b_setHitboxData(*self.hitboxData)

    def getHeight(self):
        return self.hitboxData[2]

    def getWidth(self):
        return self.hitboxData[1]

    def setHitboxData(self, htype, width, height):
        self.hitboxData = [htype, width, height]
        if self.arePhysicsSetup():
            self.setupPhysics()

    def b_setHitboxData(self, htype, width, height):
        self.d_setHitboxData(htype, width, height)
        self.setHitboxData(htype, width, height)
        
    def d_setHitboxData(self, htype, width, height):
        self.sendUpdate('setHitboxData', [htype, width, height])

    def getHitboxData(self):
        return self.hitboxData

    def setHealth(self, health):
        self.health = health
        
    def getHealth(self):
        return self.health
        
    def getHealthPercentage(self):
        return float(self.health) / float(self.maxHealth)

    def setMaxHealth(self, health):
        self.maxHealth = health

    def getMaxHealth(self):
        return self.maxHealth
        
    def isDead(self):
        return self.health <= 0
      
    def isAlive(self):
        return not self.isDead()
        
    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def setMoveBits(self, bits):
        self.moveBits = bits

    def getMoveBits(self):
        return self.moveBits

    def setHood(self, hood):
        self.hood = hood

    def getHood(self):
        return self.hood

    def setPlace(self, place):
        self.place = place
        
    def getPlace(self):
        return self.place
        
    def d_setChat(self, chat):
        self.sendUpdate("setChat", [chat])

    def setupAttacks(self):
        for aId in self.attackIds:
            attackCls = base.attackMgr.getAttackClassByID(aId)
            if attackCls:
                attack = attackCls()
                attack.setAvatar(self)
                attack.load()
                self.attacks[aId] = attack

    def cleanupAttacks(self):
        for attack in self.attacks.values():
            attack.cleanup()
        self.attacks = {}

    def rebuildAttacks(self):
        self.cleanupAttacks()
        self.setupAttacks()

    def announceGenerate(self):
        self.setupAttacks()

    def delete(self):
        self.cleanupPhysics()
        self.cleanupAttacks()
        del self.doingActivity
        del self.activities
        del self.activity
        del self.activityTimetamp
        del self.health
        del self.maxHealth
        del self._name
        del self.place
        del self.hood
        del self.moveBits
        del self.lookPitch
        del self.hitboxData
        del self.attacks
        del self.attackIds
        del self.equippedAttack
