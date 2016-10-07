########################################
# Filename: DistributedPieTurret.py
# Created by: blach (14Jun15)
# Updated by: DecodedLogic (10Aug15)
########################################

from pandac.PandaModules import Point3, Vec3, Vec4, CollisionSphere, CollisionNode

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpScaleInterval, LerpPosInterval
from direct.interval.IntervalGlobal import LerpColorScaleInterval, LerpQuatInterval, Func, Wait
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.battle.TurretGag import TurretGag

import random

class DistributedPieTurret(DistributedAvatar, DistributedSmoothNode):
    notify = directNotify.newCategory('DistributedPieTurret')

    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)
        self.fsm = ClassicFSM(
            'DistributedPieTurret',
            [
                State('off', self.enterOff, self.exitOff),
                State('scan', self.enterScan, self.exitScan),
                State('shoot', self.enterShoot, self.exitShoot)
             ],
             'off', 'off'
         )
        self.fsm.enterInitialState()
        self.reloadTime = 0.25
        self.cannon = None
        self.track = None
        self.owner = None
        self.gag = None
        self.readyGag = None
        self.hitGag = None
        self.explosion = None
        self.wallCollNode = None
        self.eventCollNode = None
        self.event = None
        self.suit = None
        self.eventId = None
        self.entities = []
        self.upgradeID = None
        self.deathEvent = None

    def setOwner(self, avatar):
        self.owner = avatar

    def getOwner(self):
        return self.owner

    def setGag(self, upgradeId):
        gags = {0 : CIGlobals.WholeCreamPie, 1 : CIGlobals.WholeFruitPie, 2 : CIGlobals.BirthdayCake, 3 : CIGlobals.WeddingCake}
        self.gag = gags.get(upgradeId)
        if not self.readyGag:
            self.loadGagInTurret()

    def b_setGag(self, upgradeId):
        self.sendUpdate('setGag', [upgradeId])
        self.setGag(upgradeId)
        self.upgradeID = upgradeId

    def getGag(self):
        return self.gag

    def getGagID(self):
        return self.upgradeID

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        DistributedSmoothNode.announceGenerate(self)
        self.healthLabel.setScale(1.1)
        self.deathEvent = self.uniqueName('DistributedPieTurret-death')
        self.makeTurret()

    def disable(self):
        self.fsm.requestFinalState()
        del self.fsm

        # This should fix crashes related to Sequences.
        if self.track:
            self.track.pause()
            self.track = None

        # Cleanup entities.
        for ent in self.entities:
            ent.cleanup()
        self.entities = None

        # Get rid of explosions.
        if self.explosion:
            self.explosion.removeNode()
            self.explosion = None

        self.removeTurret()
        DistributedSmoothNode.disable(self)
        DistributedAvatar.disable(self)

    def showAndMoveHealthLabel(self):
        self.unstashHpLabel()
        self.stopMovingHealthLabel()
        moveTrack = LerpPosInterval(self.healthLabel,
                                duration = 0.5,
                                pos = Point3(0, 0, 5),
                                startPos = Point3(0, 0, 0),
                                blendType = 'easeOut')
        self.healthLabelTrack = Sequence(moveTrack, Wait(1.0), Func(self.stashHpLabel))
        self.healthLabelTrack.start()

    # BEGIN STATES

    def enterShoot(self, suitId):
        if self.cannon:
            smoke = loader.loadModel("phase_4/models/props/test_clouds.bam")
            smoke.setBillboardPointEye()
            smoke.reparentTo(self.cannon.find('**/cannon'))
            smoke.setPos(0, 6, -3)
            smoke.setScale(0.5)
            smoke.wrtReparentTo(render)
            self.suit = self.cr.doId2do.get(suitId)
            self.cannon.find('**/cannon').lookAt(self.suit.find('**/joint_head'))
            self.cannon.find('**/square_drop_shadow').headsUp(self.suit.find('**/joint_head'))
            self.track = Sequence(Parallel(LerpScaleInterval(smoke, 0.5, 3), LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.removeNode))
            self.track.start()
            self.createAndShootGag()

    def exitShoot(self):
        if hasattr(self, 'suit'):
            del self.suit

    def shoot(self, suitId):
        self.fsm.request('shoot', [suitId])

    def scan(self, timestamp = None, afterShooting = 0):
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        self.fsm.request('scan', [ts, afterShooting])
        
    def buildScanTrack(self, ts = None):
        if self.track:
            self.track.pause()
            self.track = None
        self.track = Parallel(
            Sequence(
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (60, 0, 0),
                    startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
                    startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
            ),
            Sequence(
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (60, 0, 0),
                    startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
                    startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
            )
        )
        if ts:
            self.track.loop(ts)
        else:
            self.track.loop()

    def enterScan(self, ts = 0, afterShooting = 0):
        if afterShooting:
            self.track = Parallel(
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
                    startHpr = self.cannon.find('**/cannon').getHpr(), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
                    startHpr = self.cannon.find('**/square_drop_shadow').getHpr(), blendType = 'easeInOut'),
                name = "afterShootTrack" + str(id(self))
            )
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getDoneEvent(), self._afterShootTrackDone)
            self.track.start(ts)
        else:
            self.buildScanTrack(ts)

    def exitScan(self):
        if self.track:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            self.track = None

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    # END STATES

    def _afterShootTrackDone(self):
        self.buildScanTrack()

    def makeTurret(self):
        self.cannon = loader.loadModel('phase_4/models/minigames/toon_cannon.bam')
        self.cannon.reparentTo(self)
        self.loadGagInTurret()
        self.setupWallSphere()
        if self.isLocal():
            self.setupEventSphere()

    def removeTurret(self):
        self.removeWallSphere()
        self.removeGagInTurret()
        if self.cannon:
            self.cannon.removeNode()
            self.cannon = None

    def getCannon(self):
        return self.cannon.find('**/cannon')

    def setupWallSphere(self):
        sphere = CollisionSphere(0.0, 0.0, 0.0, 3.0)
        node = CollisionNode('DistributedPieTurret.WallSphere')
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.wallCollNode = self.cannon.attachNewNode(node)
        self.wallCollNode.setZ(2)
        self.wallCollNode.setY(1.0)

    def removeWallSphere(self):
        if self.wallCollNode:
            self.wallCollNode.removeNode()
            self.wallCollNode = None

    def createAndShootGag(self):
        if not self.readyGag:
            self.loadGagInTurret()
        if self.readyGag:
            self.readyGag.shoot(Point3(0, 200, -90))
            self.entities.append(self.readyGag)
            collideEventName = self.readyGag.getCollideEventName()
            self.readyGag = None
            if self.isLocal():
                self.acceptOnce(collideEventName, self.handleGagCollision)
        Sequence(Wait(self.reloadTime), Func(self.loadGagInTurret)).start()

    def loadGagInTurret(self):
        if self.cannon and self.gag:
            self.removeGagInTurret()
            self.eventId = random.uniform(0, 100000000)
            self.readyGag = TurretGag(self, self.uniqueName('pieTurretCollision') + str(self.eventId), self.gag)
            self.readyGag.build()

    def removeGagInTurret(self):
        if self.readyGag:
            self.readyGag.cleanup()
            self.readyGag = None

    def makeSplat(self, index, pos):
        if index >= len(self.entities):
            return
        ent = self.entities[index]
        gagClass = ent.gagClass
        splat = gagClass.buildSplat(gagClass.splatScale, gagClass.splatColor)
        base.audio3d.attachSoundToObject(gagClass.hitSfx, splat)
        splat.reparentTo(render)
        splat.setPos(pos[0], pos[1], pos[2])
        gagClass.hitSfx.play()
        Sequence(Wait(0.5), Func(splat.cleanup)).start()
        self.hitGag = None

    def d_makeSplat(self, index, pos):
        self.sendUpdate('makeSplat', [index, pos])

    def b_makeSplat(self, index, pos):
        self.d_makeSplat(index, pos)
        self.makeSplat(index, pos)

    def handleGagCollision(self, entry, ent):
        x, y, z = ent.getGag().getPos(render)
        self.b_makeSplat(self.entities.index(ent), [x, y, z])
        if self.isLocal():
            intoNP = entry.getIntoNodePath()
            avNP = intoNP.getParent()
            for key in self.cr.doId2do.keys():
                obj = self.cr.doId2do[key]
                if obj.__class__.__name__ == 'DistributedSuit':
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() > 0:
                            obj.sendUpdate('hitByGag', [ent.getID()])
        ent.cleanup()

    def setHealth(self, hp):
        DistributedAvatar.setHealth(self, hp)
        if self.isLocal():
            base.localAvatar.getMyBattle().getTurretManager().updateTurretGui()

    def die(self):
        self.fsm.requestFinalState()
        turretPos = self.cannon.getPos(render)
        self.removeTurret()
        self.explosion = loader.loadModel("phase_3.5/models/props/explosion.bam")
        self.explosion.setScale(0.5)
        self.explosion.reparentTo(render)
        self.explosion.setBillboardPointEye()
        self.explosion.setPos(turretPos + (0, 0, 5))
        sfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.ogg")
        base.audio3d.attachSoundToObject(sfx, self)
        base.playSfx(sfx)
        messenger.send(self.deathEvent)

    def isLocal(self):
        return self.getOwner() == base.localAvatar.doId

    def getDeathEvent(self):
        return self.deathEvent
