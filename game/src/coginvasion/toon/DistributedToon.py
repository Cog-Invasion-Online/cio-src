"""

  Filename: DistributedToon.py
  Created by: blach (17June14)

"""

from src.coginvasion.toon import Toon
from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from src.coginvasion.gags.backpack.Backpack import Backpack
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gui.LaffOMeter import LaffOMeter
from src.coginvasion.quests.QuestManager import QuestManager
from src.coginvasion.globals import ChatGlobals
from src.coginvasion.hood import LinkTunnel

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DelayDeletable import DelayDeletable
from direct.distributed import DelayDelete
from direct.interval.SoundInterval import SoundInterval
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval, LerpHprInterval
from direct.directnotify.DirectNotify import DirectNotify
from pandac.PandaModules import Point3
import random
import types

from src.coginvasion.cog import SuitAttacks

notify = DirectNotify().newCategory("DistributedToon")

class DistributedToon(Toon.Toon, DistributedAvatar, DistributedSmoothNode, DelayDeletable):

    def __init__(self, cr):
        try:
            self.DistributedToon_initialized
            return
        except:
            self.DistributedToon_initialized = 1
        Toon.Toon.__init__(self, cr)
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)
        self.questManager = QuestManager()
        self.token = -1
        self.ghost = 0
        self.puInventory = []
        self.equippedPU = -1
        self.backpack = None
        self.animState2animId = {}
        self.battleMeter = None
        for index in range(len(self.animFSM.getStates())):
            self.animState2animId[self.animFSM.getStates()[index].getName()] = index
        self.animId2animState = {v: k for k, v in self.animState2animId.items()}
        self.headMeter = None
        self.firstTimeChangingHP = True
        self.quests = []
        self.tier = None
        self.questHistory = None
        self.busy = 1
        self.friends = None
        self.tutDone = 0
        self.hoodsDiscovered = []
        self.teleportAccess = []
        self.lastHood = 0
        self.defaultShard = 0
        self.dmgFadeIval = None
        self.tunnelTrack = None
        self.numGagSlots = 0
        return

    def setNumGagSlots(self, num):
        self.numGagSlots = num

    def getNumGagSlots(self):
        return self.numGagSlots

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
            self.stopSmooth()
            self.wrtReparentTo(pivotPointNode)
            if linkTunnel.__class__.__name__ == "SafeZoneLinkTunnel":
                self.setHpr(180, 0, 0)
            else:
                self.setHpr(0, 0, 0)
            if base.localAvatar.doId == self.doId:
                doneMethod = self._handleWentInTunnel
                extraArgs = [requestStatus]
                self.walkControls.setCollisionsActive(0)
                camera.wrtReparentTo(linkTunnel.tunnel)
                currCamPos = camera.getPos()
                currCamHpr = camera.getHpr()
                tunnelCamPos = linkTunnel.camPos
                tunnelCamHpr = linkTunnel.camHpr
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
            )))
        elif inOrOut == 1:
            # Going out!
            pivotPoint = linkTunnel.outPivotPoint
            pivotPointNode = linkTunnel.tunnel.attachNewNode('tunnelPivotPoint')
            pivotPointNode.setPos(pivotPoint)
            pivotPointNode.setHpr(linkTunnel.outPivotStartHpr)
            if base.localAvatar.doId == self.doId:
                base.localAvatar.walkControls.setCollisionsActive(0)
                base.localAvatar.detachCamera()
                camera.reparentTo(linkTunnel.tunnel)
                tunnelCamPos = linkTunnel.camPos
                tunnelCamHpr = linkTunnel.camHpr
                camera.setPos(tunnelCamPos)
                camera.setHpr(tunnelCamHpr)
                doneMethod = self._handleCameOutTunnel
                extraArgs = []
            self.reparentTo(pivotPointNode)
            self.setHpr(linkTunnel.toonOutHpr)
            self.setPos(linkTunnel.toonOutPos)
            exitSeq = Sequence(
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
                ),
                Func(self.wrtReparentTo, render),
                Func(self.startSmooth)
            )
            self.tunnelTrack.append(exitSeq)

        if base.localAvatar.doId == self.doId:
            self.tunnelTrack.setDoneEvent(self.tunnelTrack.getName())
            self.acceptOnce(self.tunnelTrack.getDoneEvent(), doneMethod, extraArgs)

        self.tunnelTrack.start()

    def setupNameTag(self, tempName = None):
        Toon.Toon.setupNameTag(self, tempName)
        self.nametag.getNametag3d().setClickEvent('toonClicked', [self.doId])
        self.nametag.getNametag2d().setClickEvent('toonClicked', [self.doId])

    def setDefaultShard(self, shardId):
        self.defaultShard = shardId

    def getDefaultShard(self):
        return self.defaultShard

    def doSmoothTask(self, task):
        self.smoother.computeAndApplySmoothPosHpr(self, self)
        if not hasattr(base, 'localAvatar'):
            return task.done
        else:
            if self.doId != base.localAvatar.doId:
                self.setSpeed(self.smoother.getSmoothForwardVelocity(),
                              self.smoother.getSmoothRotationalVelocity(),
                              self.smoother.getSmoothLateralVelocity())
        return task.cont

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

    def incrementQuestObjective(self, questId):
        self.questManager.incrementObjective(questId)

    def setQuestObjective(self, questId, objId):
        self.questManager.setCurrentObjective(questId, objId)

    def getQuestObjective(self, questId):
        return self.questManager.getQuestByID(questId).getCurrentObjective()

    def setQuestHistory(self, array):
        self.questHistory = array

    def getQuestHistrory(self):
        return self.questHistory

    def setQuests(self, questIds, currentObjectives, currentObjectivesProgress):
        self.quests = [questIds, currentObjectives, currentObjectivesProgress]
        self.questManager.makeQuestsFromData()

    def getQuests(self):
        return self.quests

    def maybeMakeHeadMeter(self):
        if base.localAvatar.doId != self.doId:
            if self.health < self.getMaxHealth():
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

    def setHealth(self, health):
        self.health = health
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
        if value:
            self.ghostOn()
        else:
            self.ghostOff()

    def d_setGhost(self, value):
        self.sendUpdate("setGhost", [value])

    def b_setGhost(self, value):
        self.d_setGhost(value)
        self.setGhost(value)

    def getGhost(self):
        return self.ghost

    def setDNAStrand(self, dnaStrand):
        Toon.Toon.setDNAStrand(self, dnaStrand)
        self.maybeMakeHeadMeter()

    def d_setDNAStrand(self, dnaStrand):
        self.sendUpdate("setDNAStrand", [dnaStrand])

    def b_setDNAStrand(self, dnaStrand):
        self.setDNAStrand(dnaStrand)
        self.d_setDNAStrand(dnaStrand)

    def lookAtObject(self, h, p, r, blink=1):
        if self.getPart('head').getHpr() == (h, p, r):
            return
        Toon.Toon.lerpLookAt(self, self.getPart('head'), tuple((h, p, r)))
        if blink:
            self.stopBlink()
            maxBlinks = random.randint(1, 2)
            numBlinks = 0
            delay = 0
            for blink in range(maxBlinks):
                if numBlinks == 0:
                    taskMgr.add(self.doBlink, self.uniqueName("blinkOnTurn"))
                else:
                    delay += 0.22
                    taskMgr.doMethodLater(delay, self.doBlink, self.doBlinkTaskName)
                numBlinks += 1
            taskMgr.doMethodLater(delay, self.__startBlinkAfterLook, self.uniqueName("sBAL"))

    def __startBlinkAfterLook(self, task):
        self.startBlink()
        return task.done

    def toonUp(self):
        pass

    def b_lookAtObject(self, h, p, r, blink=1):
        self.d_lookAtObject(h, p, r, blink)
        self.lookAtObject(h, p, r, blink)

    def d_lookAtObject(self, h, p, r, blink=1):
        self.sendUpdate('lookAtObject', [h, p, r, blink])

    def setChat(self, chat):
        chat = ChatGlobals.filterChat(chat, self.animal)
        Toon.Toon.setChat(self, chat)

    def setTarget(self, gagId, targetId):
        gag = self.backpack.getGagByID(gagId)
        target = self.cr.doId2do.get(targetId, None)
        gag.setTarget(target)

    def trapActivate(self, gagId, avId, entityId, suitId):
        sender = self.cr.doId2do.get(avId, None)
        suit = self.cr.doId2do.get(suitId, None)
        if sender:
            backpack = sender.getBackpack()
            trapGag = backpack.getGagByID(gagId)
            if backpack and trapGag:
                entity = None
                if hasattr(trapGag, 'getEntities') and 0 <= entityId <= (len(trapGag.getEntities()) - 1):
                    entity = trapGag.getEntities()[entityId]
                    trapGag.onActivate(entity, suit)

    def b_trapActivate(self, gagId, avId, entityId, suitId):
        self.trapActivate(gagId, avId, entityId, suitId)
        self.d_trapActivate(gagId, avId, entityId, suitId)

    def d_trapActivate(self, gagId, avId, entityId, suitId):
        self.sendUpdate('trapActivate', [gagId, avId, entityId, suitId])

    def gagCollision(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        gag.doCollision()

    def b_gagCollision(self, gagId):
        self.sendUpdate("gagCollision", [gagId])
        self.gagCollision(gagId)

    def gagActivate(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        if hasattr(gag, 'activate'):
            gag.activate()

    def b_gagActivate(self, gagId):
        self.sendUpdate("gagActivate", [gagId])
        self.gagActivate(gagId)

    def setDropLoc(self, gagId, x, y, z):
        gag = self.backpack.getGagByID(gagId)
        gag.setEndPos(x, y, z)

    def setGagPos(self, gagId, x, y, z):
        pos = Point3(x, y, z)
        gag = self.backpack.getGagByID(gagId)
        ent = gag.getGag()
        if ent:
            ent.setPos(pos)

    def setThrowPower(self, gagId, power):
        gag = self.backpack.getGagByID(gagId)
        if gag:
            gag.setPower(power)

    def gagStart(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        if gag:
            gag.start()

    def b_gagStart(self, gagId):
        self.sendUpdate("gagStart", [gagId])
        self.gagStart(gagId)

    def gagThrow(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        if gag:
            gag.throw()

    def b_gagThrow(self, gagId):
        self.sendUpdate("gagThrow", [gagId])
        self.gagThrow(gagId)

    def gagRelease(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        if gag and hasattr(gag, 'name'):
            gag.release()

    def b_gagRelease(self, gagId):
        self.sendUpdate("gagRelease", [gagId])
        self.gagRelease(gagId)

    def setSplatPos(self, gagId, x, y, z):
        splatGag = self.backpack.getGagByID(gagId)
        if splatGag:
            splatGag.setSplatPos(x, y, z)

    def d_setSplatPos(self, gagId, x, y, z):
        self.sendUpdate('setSplatPos', [gagId, x, y, z])

    def gagBuild(self, gagId):
        gag = self.backpack.getGagByID(gagId)
        if gag:
            gag.build()

    def b_gagBuild(self, gagId):
        self.gagBuild(gagId)
        self.sendUpdate('gagBuild', [gagId])

    def handleSuitAttack(self, attack_id, suit_id):
        attack = SuitAttacks.SuitAttackLengths.keys()[attack_id]
        if attack == "canned":
            sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_canned_impact_only.ogg")
            base.audio3d.attachSoundToObject(sfx, self)
            SoundInterval(sfx, node = self).start()
        elif attack == "playhardball":
            sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_hardball_impact_only_alt.ogg")
            base.audio3d.attachSoundToObject(sfx, self)
            SoundInterval(sfx, node = self).start()
        elif attack == "clipontie":
            sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_impact.ogg")
            base.audio3d.attachSoundToObject(sfx, self)
            SoundInterval(sfx, node = self).start()
        if not self.isDead():
            if attack in ["fountainpen"]:
                self.getPart("head").setColorScale(0, 0, 0, 1)
                Sequence(Wait(3.0), Func(self.resetHeadColor)).start()

        self.doDamageFade()

    def resetHeadColor(self):
        head = self.getPart('head')
        if head:
            head.setColorScale(1, 1, 1, 1)

    def b_handleSuitAttack(self, attack_id, suit_id):
        self.handleSuitAttack(attack_id, suit_id)
        self.b_lookAtObject(0, 0, 0, blink = 1)
        self.sendUpdate('handleSuitAttack', [attack_id, suit_id])

    def equip(self, gagId):
        if self.backpack:
            self.backpack.setCurrentGag(gagId)

    def unEquip(self):
        if self.backpack:
            self.backpack.setCurrentGag(None)

    def b_unEquip(self):
        self.unEquip()
        self.sendUpdate('unEquip', [])

    def b_equip(self, gag_id):
        self.equip(gag_id)
        self.sendUpdate('equip', [gag_id])

    def getBackpack(self):
        return self.backpack

    def setLoadout(self, gagIds):
        if self.backpack:
            loadout = []
            for i in range(len(gagIds)):
                gagId = gagIds[i]
                gag = self.backpack.getGagByID(gagId)
                if gag:
                    loadout.append(gag)
            self.backpack.setLoadout(loadout)

    def setBackpackAmmo(self, gagIds, ammoList):
        if not self.backpack:
            self.backpack = Backpack(self)
        # We just want to update the network ammo sometimes,
        # let's ignore updates if we're not constructing a backpack.
        for i in xrange(len(gagIds)):
            gagId = gagIds[i]
            ammo = ammoList[i]

            if not self.backpack.hasGag(gagId):
                self.backpack.addGag(gagId, ammo, GagGlobals.getGagData(gagId).get('maxSupply'))
            else:
                self.backpack.setSupply(gagId, ammo)

    def getBackpackAmmo(self):
        return [], []

    def setGagAmmo(self, gagId, ammo):
        self.backpack.setSupply(gagId, ammo)

    def setMoney(self, money):
        self.money = money

    def getMoney(self):
        return self.money

    def setAdminToken(self, value):
        self.token = value
        if value > -1:
            # Put an icon over my head.
            Toon.Toon.setAdminToken(self, value)
        else:
            Toon.Toon.removeAdminToken(self)

    def getAdminToken(self):
        return self.token

    def setAnimState(self, anim, timestamp = None, callback = None, extraArgs = []):
        self.anim = anim
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        if type(anim) == types.IntType:
            anim = self.animId2animState[anim]
        if self.animFSM.getStateNamed(anim):
            self.animFSM.request(anim, [ts, callback, extraArgs])

    def b_setAnimState(self, anim):
        self.d_setAnimState(anim)
        self.setAnimState(anim, None)

    def d_setAnimState(self, anim):
        if type(anim) == types.StringType:
            anim = self.animState2animId[anim]
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate("setAnimState", [anim, timestamp])

    def getAnimState(self):
        return self.anim

    def setName(self, name):
        Toon.Toon.setName(self, name)
        if self.cr.isShowingPlayerIds:
            self.showAvId()

    def d_setName(self, name):
        self.sendUpdate('setName', [name])

    def b_setName(self, name):
        self.d_setName(name)
        self.setName(name)

    def showAvId(self):
        self.setDisplayName(self.getName() + "\n" + str(self.doId))

    def showName(self):
        self.setDisplayName(self.getName())

    def setDisplayName(self, name):
        self.setupNameTag(tempName = name)

    def wrtReparentTo(self, parent):
        DistributedSmoothNode.wrtReparentTo(self, parent)

    def announceHealthAndPlaySound(self, level, hp, extraId = -1):
        DistributedAvatar.announceHealth(self, level, hp, extraId)
        hpSfx = base.audio3d.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        base.audio3d.attachSoundToObject(hpSfx, self)
        SoundInterval(hpSfx, node = self).start()
        del hpSfx

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        if self.animFSM.getCurrentState().getName() == 'off':
            self.setAnimState('neutral')
        self.startBlink()

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)
        self.startSmooth()

    def disable(self):
        if self.tunnelTrack:
            self.ignore(self.tunnelTrack.getDoneEvent())
            self.tunnelTrack.finish()
            self.tunnelTrack = None
        if self.dmgFadeIval:
            self.dmgFadeIval.finish()
            self.dmgFadeIval = None
        if self.questManager:
            self.questManager.cleanup()
        if self.token:
            self.token = None
        if self.ghost:
            self.ghost = None
        if self.puInventory:
            self.puInventory = None
        if self.equippedPU:
            self.equippedPU = None
        if self.backpack:
            self.backpack = None
        if self.animState2animId:
            self.animState2animId = None
        if self.animId2animState:
            self.animId2animState = None
        if self.firstTimeChangingHP:
            self.firstTimeChangingHP = None
        if self.quests:
            self.quests = None
        if self.tier:
            self.tier = None
        if self.questHistory:
            self.questHistory = None
        if self.busy:
            self.busy = None
        if self.friends:
            self.friends = None
        if self.tutDone:
            self.tutDone = None
        if self.hoodsDiscovered:
            self.hoodsDiscovered = None
        if self.teleportAccess:
            self.teleportAccess = None
        if self.lastHood:
            self.lastHood = None
        if self.defaultShard:
            self.defaultShard = None
        if self.numGagSlots:
            self.numGagSlots = None
        self.__removeHeadMeter()
        self.destroyBattleMeter()

        taskMgr.remove(self.uniqueName('sBAL'))
        taskMgr.remove(self.uniqueName('blinkOnTurn'))
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        self.stopBlink()
        self.ignore('showAvId')
        self.ignore('showName')
        self.token = None
        self.stopSmooth()
        Toon.Toon.disable(self)
        DistributedAvatar.disable(self)
        DistributedSmoothNode.disable(self)

    def delete(self):
        try:
            self.DistributedToon_deleted
        except:
            self.DistributedToon_deleted = 1
            del self.tunnelTrack
            del self.dmgFadeIval
            del self.questManager
            del self.token
            del self.ghost
            del self.puInventory
            del self.equippedPU
            del self.backpack
            del self.animState2animId
            del self.animId2animState
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
            del self.numGagSlots
            Toon.Toon.delete(self)
            DistributedAvatar.delete(self)
            DistributedSmoothNode.delete(self)
        return
