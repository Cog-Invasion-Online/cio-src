"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedPlayerToon.py
@author Maverick Liberty/Brian Lach
@date June 15, 2018

This is to get away from the legacy way of having all Toons in the game, including NPCs, 
share the same code.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func, SoundInterval
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval, LerpHprInterval

from DistributedPlayerToonShared import DistributedPlayerToonShared
from src.coginvasion.toon.DistributedToon import DistributedToon
from src.coginvasion.gags.backpack.Backpack import Backpack
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gui.LaffOMeter import LaffOMeter
from src.coginvasion.hood import LinkTunnel
from src.coginvasion.globals import ChatGlobals
from src.coginvasion.quest.QuestGlobals import QUEST_DATA_UPDATE_EVENT
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.distributed import AdminCommands

class DistributedPlayerToon(DistributedToon, DistributedPlayerToonShared):
    notify = directNotify.newCategory('DistributedPlayerToon')
    
    def __init__(self, cr):
        try:
            self.DistributedPlayerToon_initialized
            return
        except:
            self.DistributedPlayerToon_initialized = 1
        DistributedToon.__init__(self, cr)
        DistributedPlayerToonShared.__init__(self)
        self.role = None
        self.ghost = 0
        self.puInventory = []
        self.equippedPU = -1
        self.backpack = Backpack(self)
        self.battleMeter = None
        self.headMeter = None
        self.firstTimeChangingHP = True
        
        # Quest-related variables.
        self.quests = ""
        self.tier = None
        self.questHistory = None
        
        self.busy = 1
        self.friends = None
        self.tutDone = 0
        self.hoodsDiscovered = []
        self.teleportAccess = []
        self.lastHood = 0
        self.defaultShard = 0
        self.tunnelTrack = None
        self.trackExperience = dict(GagGlobals.DefaultTrackExperiences)
        
        self.takeDmgSfx = base.audio3d.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonHit.ogg')
        base.audio3d.attachSoundToObject(self.takeDmgSfx, self)
        return
        
    def getHealth(self):
        return DistributedPlayerToonShared.getHealth(self)
        
    def getMaxHealth(self):
        return DistributedPlayerToonShared.getMaxHealth(self)
    
    def stopSmooth(self):
        DistributedToon.stopSmooth(self)
        localAvatarReachable = (hasattr(base, 'localAvatar') and base.localAvatar)
        if localAvatarReachable and self.doId != base.localAvatar.doId:
            self.resetTorsoRotation()

    def handleHealthChange(self, hp, oldHp):
        if hp < oldHp and not self.firstTimeChangingHP:
            # We took damage, make oof sound.
            self.takeDmgSfx.play()

    def setHealth(self, health):
        self.handleHealthChange(health, self.getHealth())
        DistributedToon.setHealth(self, health)
        if self.doId != base.localAvatar.doId:
            if not self.firstTimeChangingHP:
                if health < self.getMaxHealth():
                    if not self.headMeter:
                        self.__makeHeadMeter()
                    else:
                        self.__updateHeadMeter()
                else:
                    self.__removeHeadMeter()
        self.firstTimeChangingHP = False

    def announceHealthAndPlaySound(self, level, hp, extraId = -1):
        DistributedToon.announceHealth(self, level, hp, extraId)
        hpSfx = base.audio3d.loadSfx('phase_11/audio/sfx/LB_toonup.ogg')
        base.audio3d.attachSoundToObject(hpSfx, self)
        SoundInterval(hpSfx, node = self).start()
        del hpSfx
        
    def setChat(self, chat):
        chat = ChatGlobals.filterChat(chat, self.animal)
        DistributedToon.setChat(self, chat)
    
    def goThroughTunnel(self, toZone, inOrOut, requestStatus = None):
        # inOrOut: 0 = in; 1 = out

        if self.tunnelTrack:
            self.ignore(self.tunnelTrack.getDoneEvent())
            self.tunnelTrack.finish()
            self.tunnelTrack = None

        linkTunnel = LinkTunnel.getTunnelThatGoesToZone(toZone)
        if not linkTunnel:
            return
        self.tunnelTrack = Parallel(name = self.uniqueName('Place.goThroughTunnel'))

        if inOrOut == 0:
            # Going in a tunnel!
            pivotPoint = linkTunnel.inPivotPoint
            pivotPointNode = linkTunnel.tunnel.attachNewNode('tunnelPivotPoint')
            pivotPointNode.setPos(pivotPoint)
            pivotPointNode.setHpr(linkTunnel.inPivotStartHpr)
                
            x, y, z = self.getPos(render)
            surfZ = PhysicsUtils.getNearestGroundSurfaceZ(self, self.getHeight() + self.getHeight() / 2.0)
            
            if not surfZ == -1:
                # Let's use the ray-tested surface z-point instead so we don't come out of the tunnel hovering.
                # This is just in case the user jumped into the tunnel, which in that case would mean that they are
                # airborne and we can't depend on their current Z value.
                z = surfZ
            
            if base.localAvatar.doId == self.doId:
                doneMethod = self._handleWentInTunnel
                extraArgs = [requestStatus]
                base.localAvatar.walkControls.setCollisionsActive(0, andPlaceOnGround=1)
                self.resetHeadHpr(override = True)
                camera.wrtReparentTo(linkTunnel.tunnel)
                currCamPos = camera.getPos()
                currCamHpr = camera.getHpr()
                tunnelCamPos = linkTunnel.camPos
                tunnelCamHpr = linkTunnel.camHpr
                camera.setPos(tunnelCamPos)
                camera.setHpr(tunnelCamHpr)
                self.tunnelTrack.append(LerpPosInterval(
                    camera,
                    duration = 0.7,
                    pos = tunnelCamPos,
                    startPos = currCamPos,
                    blendType = 'easeOut'
                ))
                self.tunnelTrack.append(LerpQuatInterval(
                    camera,
                    duration = 0.7,
                    quat = tunnelCamHpr,
                    startHpr = currCamHpr,
                    blendType = 'easeOut'
                ))

            self.wrtReparentTo(pivotPointNode)
            self.setPos(x, y, z)
            self.resetTorsoRotation()
            self.stopLookAround()
            
            if linkTunnel.__class__.__name__ == "SafeZoneLinkTunnel":
                self.setHpr(180, 0, 0)
            else:
                self.setHpr(0, 0, 0)
            
            exitSeq = Sequence(Func(self.loop, 'run'))
            if base.localAvatar.doId == self.doId:
                exitSeq.append(Wait(2.0))
                exitSeq.append(Func(base.transitions.irisOut))
            self.tunnelTrack.append(exitSeq)
            self.tunnelTrack.append(Sequence(
                LerpHprInterval(
                    pivotPointNode,
                    duration = 2.0,
                    hpr = linkTunnel.inPivotEndHpr,
                    startHpr = linkTunnel.inPivotStartHpr,
            ), LerpPosInterval(
                    pivotPointNode,
                    duration = 1.0,
                    pos = (linkTunnel.inPivotEndX, pivotPointNode.getY(), pivotPointNode.getZ()),
                    startPos = (linkTunnel.inPivotStartX, pivotPointNode.getY(), pivotPointNode.getZ())
            ), Func(self.reparentTo, hidden)))
        elif inOrOut == 1:
            
            # Going out!
            pivotPoint = linkTunnel.outPivotPoint
            pivotPointNode = linkTunnel.tunnel.attachNewNode('tunnelPivotPoint')
            pivotPointNode.setPos(pivotPoint)
            pivotPointNode.setHpr(linkTunnel.outPivotStartHpr)
            
            exitSeq = Sequence()
            
            if base.localAvatar.doId == self.doId:
                base.localAvatar.walkControls.setCollisionsActive(0, andPlaceOnGround=1)
                base.localAvatar.detachCamera()
                camera.reparentTo(linkTunnel.tunnel)
                tunnelCamPos = linkTunnel.camPos
                tunnelCamHpr = linkTunnel.camHpr
                camera.setPos(tunnelCamPos)
                camera.setHpr(tunnelCamHpr)
                doneMethod = self._handleCameOutTunnel
                extraArgs = []
                
                exitSeq.append(Func(base.transitions.irisIn))
            else:
                self.stopSmooth()
                
            self.reparentTo(pivotPointNode)
            self.setHpr(linkTunnel.toonOutHpr)
            self.setPos(linkTunnel.toonOutPos)
            
            seq = Sequence(
                Func(self.loop, 'run'),
                LerpPosInterval(
                    pivotPointNode,
                    duration = 1.0,
                    pos = (linkTunnel.outPivotEndX, pivotPointNode.getY(), pivotPointNode.getZ()),
                    startPos = (linkTunnel.outPivotStartX, pivotPointNode.getY(), pivotPointNode.getZ())
                ),
                LerpHprInterval(
                    pivotPointNode,
                    duration = 2.0,
                    hpr = linkTunnel.outPivotEndHpr,
                    startHpr = linkTunnel.outPivotStartHpr,
                )
            )
            if base.localAvatar.doId != self.doId:
                seq.append(Func(self.startSmooth))
            seq.append(Func(self.wrtReparentTo, render))
            exitSeq.append(seq)
            self.tunnelTrack.append(exitSeq)

        if base.localAvatar.doId == self.doId:
            self.tunnelTrack.setDoneEvent(self.tunnelTrack.getName())
            self.acceptOnce(self.tunnelTrack.getDoneEvent(), doneMethod, extraArgs)

        self.tunnelTrack.start()
        
    def setDefaultShard(self, shardId):
        self.defaultShard = shardId

    def getDefaultShard(self):
        return self.defaultShard

    def setLastHood(self, zoneId):
        self.lastHood = zoneId

    def b_setLastHood(self, zoneId):
        self.sendUpdate('setLastHood', [zoneId])
        self.setLastHood(zoneId)

    def getLastHood(self):
        return self.lastHood

    def setTeleportAccess(self, array):
        self.teleportAccess = array

    def getTeleportAccess(self):
        return self.teleportAccess

    def setHoodsDiscovered(self, array):
        self.hoodsDiscovered = array

    def b_setHoodsDiscovered(self, array):
        self.sendUpdate('setHoodsDiscovered', [array])
        self.setHoodsDiscovered(array)

    def getHoodsDiscovered(self):
        return self.hoodsDiscovered

    def setTutorialCompleted(self, value):
        self.tutDone = value

    def getTutorialCompleted(self):
        return self.tutDone

    def setFriendsList(self, friends):
        self.friends = friends

    def getFriendsList(self):
        return self.friends

    def setBusy(self, busy):
        self.busy = busy

    def getBusy(self):
        return self.busy

    def setTier(self, tier):
        self.tier = tier

    def getTier(self):
        return self.tier

    def setQuestHistory(self, array):
        self.questHistory = array

    def getQuestHistory(self):
        return self.questHistory

    def setQuests(self, dataStr):
        oldDataStr = self.quests
        self.quests = dataStr
        
        if self == base.localAvatar:
            base.localAvatar.questManager.makeQuestsFromData()
        
            # Let's send our quest data update event.
            messenger.send(QUEST_DATA_UPDATE_EVENT, [oldDataStr, dataStr])

    def getQuests(self):
        return self.quests

    def maybeMakeHeadMeter(self):
        if base.localAvatar.doId != self.doId:
            if self.getHealth() < self.getMaxHealth():
                if not self.headMeter:
                    self.__makeHeadMeter()

    def __makeHeadMeter(self):
        self.headMeter = LaffOMeter(forRender = True)
        r, g, b, _ = self.getHeadColor()
        animal = self.getAnimal()
        maxHp = self.getMaxHealth()
        hp = self.getHealth()
        self.headMeter.generate(r, g, b, animal, maxHP = maxHp, initialHP = hp)
        self.headMeter.reparentTo(self)
        self.headMeter.setZ(self.getHeight() + 2)
        self.headMeter.setScale(0.4)
        self.headMeter.setBillboardAxis()
        self.__updateHeadMeter()

    def __removeHeadMeter(self):
        if self.headMeter:
            self.headMeter.disable()
            self.headMeter.delete()
            self.headMeter = None

    def __updateHeadMeter(self):
        if self.headMeter:
            self.headMeter.updateMeter(self.getHealth())
            
    def d_createBattleMeter(self):
        self.sendUpdate('makeBattleMeter', [])

    def b_createBattleMeter(self):
        self.makeBattleMeter()
        self.d_createBattleMeter()

    def d_cleanupBattleMeter(self):
        self.sendUpdate('destroyBattleMeter', [])

    def b_cleanupBattleMeter(self):
        self.destroyBattleMeter()
        self.d_cleanupBattleMeter()

    def makeBattleMeter(self):
        if self.getHealth() < self.getMaxHealth():
            if not self.battleMeter:
                self.battleMeter = LaffOMeter()
                r, g, b, _ = self.getHeadColor()
                animal = self.getAnimal()
                maxHp = self.getMaxHealth()
                hp = self.getHealth()
                self.battleMeter.generate(r, g, b, animal, maxHP = maxHp, initialHP = hp)
                self.battleMeter.reparentTo(self)
                self.battleMeter.setZ(self.getHeight() + 5)
                self.battleMeter.setScale(0.5)
                self.battleMeter.start()

    def destroyBattleMeter(self):
        if self.battleMeter:
            self.battleMeter.stop()
            self.battleMeter.disable()
            self.battleMeter.delete()
            self.battleMeter = None

    def setEquippedPU(self, index):
        self.equippedPU = index

    def getEquippedPU(self):
        return self.equippedPU

    def setPUInventory(self, array):
        self.puInventory = array

    def getPUInventory(self):
        return self.puInventory

    def setGhost(self, value):
        self.ghost = value
        self.handleGhost(value)

    def d_setGhost(self, value):
        self.sendUpdate("setGhost", [value])

    def b_setGhost(self, value):
        self.d_setGhost(value)
        self.setGhost(value)

    def getGhost(self):
        return self.ghost

    def getBackpack(self):
        return self.backpack

    def setEquippedAttack(self, attackID):
        try: 
            self.backpack.setCurrentGag(attackID) 
        except:
            # If we couldn't do this, it means that the avatar was most likely disabled. 
            pass
        DistributedToon.setEquippedAttack(self, attackID)

    def getCurrentGag(self):
        return self.getEquippedAttack()

    def setLoadout(self, gagIds):
        if self.backpack:
            loadout = []
            for i in range(len(gagIds)):
                gagId = gagIds[i]
                gag = self.backpack.getGagByID(gagId)
                if gag:
                    loadout.append(gag)
            self.backpack.setLoadout(loadout)
    
    def setBackpackAmmo(self, netString):
        if len(self.attackIds) != 0 or len(self.attacks) != 0:
            self.cleanupAttacks()
            self.clearAttackIds()
        return self.backpack.updateSuppliesFromNetString(netString)
    
    def getBackpackAmmo(self):
        if self.backpack:
            return self.backpack.netString
        return GagGlobals.getDefaultBackpack().toNetString()
    
    def setTrackExperience(self, netString):
        self.trackExperience = GagGlobals.getTrackExperienceFromNetString(netString)
        if GagGlobals.processTrackData(self.trackExperience, self.backpack) and self == base.localAvatar:
            if base.localAvatar.invGui:
                base.localAvatar.reloadInvGui()
        
    def getTrackExperience(self):
        return GagGlobals.trackExperienceToNetString(self.trackExperience)

    def updateAttackAmmo(self, gagId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip):
        if self.useBackpack():
            self.backpack.setSupply(gagId, ammo)
        else:
            DistributedToon.updateAttackAmmo(self, gagId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip)

    def setMoney(self, money):
        self.money = money

    def getMoney(self):
        return self.money

    def setAccessLevel(self, value):
        prevLevel = self.getAccessLevel()
        self.role = AdminCommands.Roles.get(value, None)
        
        if prevLevel != AdminCommands.NoAccess:
            # Let's remove any tokens that already are showing up.
            DistributedToon.removeAdminToken(self)
        
        if self.role:
            # Let's put a new token above our head.
            DistributedToon.setAdminToken(self, self.role.token)

    def getAccessLevel(self):
        return AdminCommands.NoAccess if not self.role else self.role.accessLevel
    
    def disable(self):
        base.audio3d.detachSound(self.takeDmgSfx)
        self.takeDmgSfx = None
        if self.tunnelTrack:
            self.ignore(self.tunnelTrack.getDoneEvent())
            self.tunnelTrack.finish()
            self.tunnelTrack = None
        self.role = None
        self.ghost = None
        self.puInventory = None
        self.equippedPU = None
        if self.backpack:
            self.backpack.cleanup()
            self.backpack = None
        self.firstTimeChangingHP = None
        self.quests = None
        self.tier = None
        self.questHistory = None
        self.busy = None
        self.friends = None
        self.tutDone = None
        self.hoodsDiscovered = None
        self.teleportAccess = None
        self.lastHood = None
        self.defaultShard = None
        self.trackExperience = None
        self.__removeHeadMeter()
        self.destroyBattleMeter()
        DistributedToon.disable(self)
    
    def delete(self):
        try:
            self.DistributedPlayerToon_deleted
        except:
            self.DistributedPlayerToon_deleted = 1
            DistributedPlayerToonShared.delete(self)
            del self.takeDmgSfx
            del self.tunnelTrack
            del self.role
            del self.ghost
            del self.puInventory
            del self.equippedPU
            del self.backpack
            del self.firstTimeChangingHP
            del self.quests
            del self.tier
            del self.questHistory
            del self.busy
            del self.friends
            del self.tutDone
            del self.hoodsDiscovered
            del self.teleportAccess
            del self.lastHood
            del self.defaultShard
            del self.trackExperience
            del self.battleMeter
            del self.headMeter
            DistributedToon.delete(self)
        return
