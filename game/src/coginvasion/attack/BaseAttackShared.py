from direct.directnotify.DirectNotifyGlobal import directNotify

from Attacks import ATTACK_NONE

from src.coginvasion.globals import CIGlobals

class BaseAttackShared:
    """
    Shared client/server functionality for an attack, useable by Avatars.

    This new attack system is designed to be character/interface-agnostic, meaning
    that attack code can be shared between Toons, Cogs, NPCs, etc, on the Client or Server.

    The design is tightly coupled with the new AI, which is also designed to be
    character/interface-agnostic.
    """

    notify = directNotify.newCategory("BaseAttackShared")

    HasClip = False
    HasSecondary = False
    ID = ATTACK_NONE
    Name = "Base Attack"

    Server = False

    StateIdle = 0

    PlayRate = 1.0

    def __init__(self):
        self.maxClip = 10
        self.clip = 10
        self.maxAmmo = 10
        self.ammo = 10
        self.baseDamage = 10
        self.damageMaxDistance = 40.0

        self.secondaryAmmo = 1
        self.secondaryMaxAmmo = 1

        self.action = self.StateIdle
        self.actionStartTime = 0
        self.nextAction = None

        self.equipped = False
        self.thinkTask = None

        self.avatar = None

    def canUse(self):
        if self.HasClip:
            return self.hasClip() and self.hasAmmo()
        return self.hasAmmo() and self.action == self.StateIdle

    def getBaseDamage(self):
        return self.baseDamage

    def getDamageMaxDistance(self):
        return self.damageMaxDistance

    def calcDamage(self, distance = 10.0):
        return CIGlobals.calcAttackDamage(distance, self.getBaseDamage(), self.getDamageMaxDistance())

    def getID(self):
        return self.ID

    def isServer(self):
        return self.Server

    def setAvatar(self, avatar):
        #assert isinstance(avatar, AvatarShared), "BaseAttackShared.setAvatar(): not a valid avatar"

        self.avatar = avatar

    def hasAvatar(self):
        return CIGlobals.isNodePathOk(self.avatar)

    def getAvatar(self):
        return self.avatar
        
    def getActionTime(self):
        return (globalClock.getFrameTime() - self.actionStartTime)
        
    def setNextAction(self, action):
        self.nextAction = action

    def getNextAction(self):
        return self.nextAction
        
    def setAction(self, action):
        self.actionStartTime = globalClock.getFrameTime()
        self.action = action
        self.onSetAction(action)
        
    def onSetAction(self, action):
        pass

    def getAction(self):
        return self.action

    def __thinkTask(self, task):
        if not self.equipped:
            return task.done

        self.think()

        return task.cont

    def think(self):
        pass

    def equip(self):
        if self.equipped:
            return False

        self.equipped = True

        self.thinkTask = taskMgr.add(self.__thinkTask, "attackThink-" + str(id(self)))

        return True

    def unEquip(self):
        if not self.equipped:
            return False

        self.equipped = False

        if self.thinkTask:
            self.thinkTask.remove()
            self.thinkTask = None

        return True

    def primaryFirePress(self, data = None):
        pass

    def primaryFireRelease(self, data = None):
        pass

    def secondaryFirePress(self, data = None):
        pass

    def secondaryFireRelease(self, data = None):
        pass

    def reloadPress(self, data = None):
        pass

    def reloadRelease(self, data = None):
        pass

    def getSecondaryAmmo(self):
        return self.secondaryAmmo

    def getSecondaryMaxAmmo(self):
        return self.getSecondaryMaxAmmo

    def usesSecondary(self):
        return self.HasSecondary

    def hasSecondaryAmmo(self):
        return self.secondaryAmmo > 0

    def needsReload(self):
        return self.clip == 0

    def usesClip(self):
        return self.HasClip

    def hasClip(self):
        return self.clip > 0

    def isClipFull(self):
        return self.clip >= self.maxClip

    def isAmmoFull(self):
        return self.ammo >= self.maxAmmo

    def getClip(self):
        return self.clip

    def getMaxClip(self):
        return self.maxClip

    def setMaxAmmo(self, ammo):
        self.maxAmmo = ammo

    def getMaxAmmo(self):
        return self.maxAmmo

    def setAmmo(self, ammo):
        self.ammo = ammo

    def getAmmo(self):
        return self.ammo

    def hasAmmo(self):
        return self.ammo > 0

    def cleanup(self):
        self.unEquip()
        del self.ammo
        del self.maxAmmo
        del self.avatar
        del self.secondaryAmmo
        del self.secondaryMaxAmmo
        del self.maxClip
        del self.clip
        del self.equipped
        del self.thinkTask
        del self.nextAction
        del self.action
        del self.actionStartTime
