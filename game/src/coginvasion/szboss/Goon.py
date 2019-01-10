from panda3d.core import TransformState, Vec3, Point3

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, LerpFunc, Parallel, SoundInterval, LerpColorScaleInterval, LerpScaleInterval, LerpHprInterval
from direct.fsm.FSM import FSM

from src.coginvasion.avatar.Avatar import Avatar
from src.coginvasion.phys.Ragdoll import Ragdoll, RagdollLimbShapeDesc

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from GoonAI import GoonAI, GBSleep, GBPatrol

import random

class GoonRagdoll(Ragdoll):

    def setupLimbs(self):

        mass = 25

        # mike wazowski body
        self.addLimb("joint22", mass, shapes = [RagdollLimbShapeDesc(length = 0.7, radius = 0.7, localPos = (0, 0, 0.75), localHpr = (0, 0, 0))])

        # Left thigh
        self.addLimb("joint1", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Left leg
        self.addLimb("joint2", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Left foot
        self.addLimb("joint4", mass, shapes = [RagdollLimbShapeDesc(length = 1.5, radius = 0.3, localPos = (0.35, 0.2, 0), localHpr = (-30, 0, -95))])

        # Right thigh
        self.addLimb("joint6", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Right leg
        self.addLimb("joint2_3", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Right foot
        self.addLimb("joint4_4", mass, shapes = [RagdollLimbShapeDesc(length = 1.5, radius = 0.3, localPos = (0.35, 0, -0.2), localHpr = (0, 0, 60))])

    def setupJoints(self):
        # Left leg
        self.addJoint("joint22", "joint1", ((0.5,0,0), (0,0,90)), ((0,0,0), (0,0,0)), swing=(55, 0), twist= 45)
        self.addJoint("joint1", "joint2", ((1,0,0), (0,90,90)), ((0,0,0), (0,0,0)), swing=(0, 70), twist=0)
        self.addJoint("joint2", "joint4", ((1,0,0), (-90,0,-90)), ((0,0,0), (0,0,0)), swing=(0, 45), twist=0)
        # Right leg
        self.addJoint("joint22", "joint6", ((-0.5,0,0), (0,0,90)), ((0,0,0), (0,0,0)), swing=(55, 0), twist= 45)
        self.addJoint("joint6", "joint2_3", ((1,0,0), (0,90,90)), ((0,0,0), (0,0,0)), swing=(0, 70), twist=0)
        self.addJoint("joint2_3", "joint4_4", ((1,0,0), (0,0,0)), ((0,0,0), (0,0,0)), swing=(0, 45), twist=0)

class Goon(Avatar, FSM):

    IdleEyeColor = (1, 1, 0.5, 1)
    AttackEyeColor = (1.5, 0, 0, 1)
    DeadEyeColor = (1, 1, 1, 1)
    AsleepEyeColor = (0.5, 0.5, 0.5, 1)

    Security = 0
    Construction = 1
    Nothing = 2

    ScanDuration = 2.0

    def __init__(self, hatType = Nothing):
        Avatar.__init__(self, 0)
        FSM.__init__(self, 'Goon')
        self.hatType = hatType
        self.shootTrack = None
        self.shootSound = None
        self.detectSound = None
        self.whipSound = None
        self.idleSound = None
        self.dieSound = None
        self.hat = None
        self.brain = None

        self.lightScanIval = None

        self.scannerMdl = None
        self.scanBeginSound = None
        self.scanLoopSound = None
        self.scanEndSound = None
        self.scanLight = None
        self.lightGlow = None

        self.height = 3.5

        #self.shapeGroup = Globals.EnemyGroup

        self.eyeLaser = None

        self.ragdoll = None

        self.anims = {"walk": "phase_9/models/char/Cog_Goonie-walk.bam",
                        "idle": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "scan": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "wakeup": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "collapse": "phase_9/models/char/Cog_Goonie-collapse.bam",
                        "zero": "phase_9/models/char/Cog_Goonie-zero.bam"}

        self.baseBlendAnim = 'walk'

    def load(self):
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getEntnum()
        hat = loader.getEntityValueInt(entnum, "hat")
        self.hatType = hat
        self.generateGoon()
        self.reparentTo(render)
        self.playIdleAnim()
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles() - (180, 0, 0))

    def doRagdollMode(self):
        Avatar.doRagdollMode(self)
        #self.brain.stop()
        self.doUndetectGlow()
        if self.dieSound:
            self.dieSound.play()
        self.request('Off')
        self.setEyeColor(self.DeadEyeColor)

    def setBaseBlendAnim(self, anim):
        self.baseBlendAnim = anim
        self.stop()
        for otherAnim in self.anims.keys():
            self.setControlEffect(otherAnim, 0.0)
        self.setControlEffect(anim, 1.0)

    def blendAnimFromBase(self, val, anim):
        if anim == self.baseBlendAnim:
            return
        self.setControlEffect(self.baseBlendAnim, 1 - val)
        self.setControlEffect(anim, val)

    def setEyeColor(self, col):
        self.find("**/eye").setColorScale(col)

    def handleHitByToon(self, player, gagId, distance):
        if self.isDead():
            return

        gagName = GagGlobals.getGagByID(gagId)
        data = dict(GagGlobals.getGagData(gagId))
        data['distance'] = distance
        baseDmg = GagGlobals.calculateDamage(player, gagName, data)
        hp = self.health - baseDmg
        self.setHealth(hp)
        self.announceHealth(0, baseDmg, -1)
        self.doDamageFade()
        if self.isDead():
            self.doRagdollMode()

    def generateGoon(self):
        self.loadAvatar()
        self.setupPhysics(1.0, self.getHeight())
        self.enableRay()
        self.enableShadowRay()

        self.loadModel("phase_9/models/char/Cog_Goonie-zero.bam", "goon")
        self.loadAnims(self.anims, "goon")

        self.getGeomNode().setH(180)

        self.find("**/hard_hat").setTwoSided(True)
        self.find("**/security_hat").setTwoSided(True)
        self.find("**/eye").setLightOff(1)

        if self.hatType == Goon.Security:
            self.hat = self.find("**/security_hat")
            self.find("**/hard_hat").stash()
        elif self.hatType == Goon.Construction:
            self.hat = self.find("**/hard_hat")
            self.find("**/security_hat").stash()
            self.find("**/hard_hat").setMaterial(CIGlobals.getCharacterMaterial(shininess = 400.0))
        elif self.hatType == Goon.Nothing:
            self.find("**/hard_hat").stash()
            self.find("**/security_hat").stash()

        self.setEyeColor(self.IdleEyeColor)
        self.setMaterial(CIGlobals.getCharacterMaterial(shininess = 50.0))

        self.lightGlow = loader.loadModel("phase_14/models/props/lightglow.egg")
        self.lightGlow.setLightOff(1)
        self.lightGlow.setMaterialOff(1)
        self.lightGlow.setShaderOff(1)
        self.lightGlow.reparentTo(self)
        self.lightGlow.setP(90)
        self.lightGlow.setZ(0.01)
        self.lightGlow.setScale(3)
        self.lightGlow.setTransparency(1)
        self.lightGlow.setColorScale(1, 0, 0, 0)

        self.enableBlend()
        self.whipSound = base.audio3d.loadSfx("phase_5/audio/sfx/General_device_appear.ogg")
        base.audio3d.attachSoundToObject(self.whipSound, self)
        self.shootSound = base.audio3d.loadSfx("phase_5/audio/sfx/lightning_1.ogg")
        base.audio3d.attachSoundToObject(self.shootSound, self)
        self.detectSound = base.audio3d.loadSfx("phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg")
        base.audio3d.attachSoundToObject(self.detectSound, self)
        self.dieSound = base.audio3d.loadSfx("phase_14/audio/sfx/CHQ_GOON_hunker_down_fix.ogg")
        base.audio3d.attachSoundToObject(self.dieSound, self)

        self.scanBeginSound = base.audio3d.loadSfx("phase_11/audio/sfx/LB_laser_beam_on_2.ogg")
        base.audio3d.attachSoundToObject(self.scanBeginSound, self)
        self.scanLoopSound = base.audio3d.loadSfx("phase_14/audio/sfx/LB_laser_beam_hum_loop.ogg")
        base.audio3d.attachSoundToObject(self.scanLoopSound, self)
        self.scanEndSound = base.audio3d.loadSfx("phase_11/audio/sfx/LB_laser_beam_off_2.ogg")
        base.audio3d.attachSoundToObject(self.scanEndSound, self)

        self.wakeupSound = base.audio3d.loadSfx("phase_9/audio/sfx/CHQ_GOON_rattle_shake.ogg")
        base.audio3d.attachSoundToObject(self.wakeupSound, self)

        self.idleSound = base.audio3d.loadSfx("phase_9/audio/sfx/CHQ_FACT_stomper_raise.ogg")
        base.audio3d.attachSoundToObject(self.idleSound, self)
        self.idleSound.setLoop(True)

        self.scannerMdl = loader.loadModel("phase_14/models/props/lightscanner.egg")
        self.scannerMdl.setTransparency(1)
        self.scannerMdl.setColorScale(1, 1, 0.5, 0.5)
        self.scannerMdl.setTwoSided(True)
        self.scannerMdl.setH(180)
        self.scannerMdl.setZ(3.25)
        self.scannerMdl.setY(-0.8)
        self.scannerMdl.reparentTo(self.find("**/eye"))
        self.scannerMdl.hide()
        self.scannerMdl.setMaterialOff(1)
        self.scannerMdl.setShaderOff(1)
        self.scannerMdl.setLightOff(1)

        self.eyeLaser = loader.loadModel("phase_14/models/props/laser.egg")
        self.eyeLaser.find("**/laser").setBillboardAxis()
        #self.eyeLaser.setColorScale(1, 0, 0, 1)
        self.eyeLaser.setLightOff(1)
        self.eyeLaser.setMaterialOff(1)
        self.eyeLaser.setShaderOff(1)
        self.eyeLaser.setTwoSided(True)
        self.resetEyeLaser()

        self.ragdoll = GoonRagdoll(self, "goon")
        self.ragdoll.setup()
        self.ragdoll.mode = self.ragdoll.RMRagdoll

        # For the antenna
        self.find("**/unknown406").setTwoSided(True)

        self.nametag3d.setZ(self.getHeight())

        #self.getGeomNode().flattenStrong()

    def resetEyeLaser(self):
        self.eyeLaser.reparentTo(self.find("**/eye"))
        self.eyeLaser.setZ(3.25)
        self.eyeLaser.setY(-0.8)
        self.eyeLaser.setX(0)
        self.eyeLaser.setScale(1, 1, 0.001)
        self.eyeLaser.setP(-90)
        self.eyeLaser.setH(0)
        self.eyeLaser.setP(0)
        self.eyeLaser.hide()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def playIdleAnim(self):
        self.setBaseBlendAnim("idle")
        self.setPlayRate(1, "idle")
        self.pingpong("idle", fromFrame = 94, toFrame = 96)

    def playWalkAnim(self, rate = 1.5):
        self.setBaseBlendAnim("walk")
        self.setPlayRate(rate, "walk")
        self.loop("walk")

    def enterAsleep(self):
        self.disableBlend()
        self.pose('collapse', self.getNumFrames("collapse") - 1)

    def exitAsleep(self):
        self.enableBlend()

    def doDetectGlow(self):
        para = Parallel(LerpColorScaleInterval(self.lightGlow, 1.0, colorScale = (1, 0, 0, 0.5), startColorScale = (1, 0, 0, 0)),
                 LerpColorScaleInterval(self.find("**/eye"), colorScale = self.AttackEyeColor,
                                        startColorScale = self.IdleEyeColor, duration = 1.0, blendType = 'easeInOut'))
        para.start()

    def doUndetectGlow(self):
        para = Parallel(LerpColorScaleInterval(self.find("**/eye"), colorScale = self.IdleEyeColor, startColorScale = self.AttackEyeColor,
                                               duration = 0.5, blendType = 'easeInOut'),
                        LerpColorScaleInterval(self.lightGlow, 0.5, colorScale = (1, 0, 0, 0), startColorScale = (1, 0, 0, 0.5)))
        para.start()

    def enterScan(self):
        self.setPlayRate(1, "scan")
        self.pingpong("scan", fromFrame = 94, toFrame = 96)
        self.scannerMdl.setHpr(180, 0, 0)
        self.shootTrack = Sequence(LerpFunc(self.blendAnimFromBase, fromData = 0, toData = 1, duration = 0.5, extraArgs = ['scan']),
                                   Parallel(SoundInterval(self.scanBeginSound, node = self), Func(self.scannerMdl.show),
                                            Sequence(LerpScaleInterval(self.scannerMdl, duration = 0.5, scale = (0.3, 2, 1), startScale = (0.01, 0.01, 0.01)),
                                                     LerpScaleInterval(self.scannerMdl, duration = 0.5, scale = (2, 2, 1), startScale = (0.3, 2, 1)),
                                                     LerpHprInterval(self.scannerMdl, duration = 0.25, hpr = (180, 20, 0), startHpr = (180, 0, 0)))),
                                   Func(self.beginScan))
        self.shootTrack.start()

    def beginScan(self):
        taskMgr.add(self.__scanTask, self.taskName("scanTask"))
        if self.lightScanIval:
            self.lightScanIval.pause()
        self.lightScanIval = Sequence(LerpHprInterval(self.scannerMdl, hpr = (180, -20, 0), startHpr = (180, 20, 0), duration = 1, blendType = 'easeInOut'),
                                      LerpHprInterval(self.scannerMdl, hpr = (180, 20, 0), startHpr = (180, -20, 0), duration = 1, blendType = 'easeInOut'))
        self.lightScanIval.loop()
        base.playSfx(self.scanLoopSound, looping = 1, node = self)

    def __scanTask(self, task):
        if task.time >= Goon.ScanDuration:
            self.endScan()
            return task.done

        return task.cont

    def stopShootTrack(self):
        if self.shootTrack:
            self.shootTrack.finish()
            self.shootTrack = None

    def endScan(self):
        if self.shootTrack:
            self.shootTrack.finish()
        if self.lightScanIval:
            self.lightScanIval.pause()
        taskMgr.remove(self.taskName("scanTask"))

        self.scanLoopSound.stop()
        self.shootTrack = Parallel(SoundInterval(self.scanEndSound, node = self),
                                   Sequence(LerpHprInterval(self.scannerMdl, duration = 0.25, hpr = (180, 0, 0), startHpr = self.scannerMdl.getHpr()),
                                            LerpScaleInterval(self.scannerMdl, duration = 0.7, scale = (0.3, 2, 1), startScale = (2, 2, 1)),
                                            LerpScaleInterval(self.scannerMdl, duration = 0.7, scale = (0.01, 0.01, 0.01), startScale = (0.3, 2, 1)),
                                            Func(self.scannerMdl.hide),
                                            LerpFunc(self.blendAnimFromBase, fromData = 1, toData = 0, duration = 0.5, extraArgs = ['scan'])))
        self.shootTrack.start()

    def exitScan(self):
        self.endScan()
        if self.lightScanIval:
            self.lightScanIval.pause()
            self.lightScanIval = None
        self.stopShootTrack()

    def enterShoot(self, target = None):
        if not target:
            target = base.localAvatar
        self.pose("collapse", 1)
        self.shootTrack = Sequence(Parallel(
                    Sequence(LerpFunc(self.blendAnimFromBase, fromData = 0, toData = 1, duration = 0.25, extraArgs = ['collapse']),
                            ActorInterval(self, "collapse", startFrame = 1, endFrame = 5, playRate = 0.8),
                            ActorInterval(self, "collapse", startFrame = 5, endFrame = 22, playRate = 0.7),
                            ActorInterval(self, "collapse", startFrame = 22, endFrame = 5, playRate = 0.7),
                            LerpFunc(self.blendAnimFromBase, fromData = 1, toData = 0, duration = 0.25, extraArgs = ['collapse'])),

                    Sequence(Wait(0.1), SoundInterval(self.whipSound, node = self)),
                    Sequence(Wait(0.55), SoundInterval(self.shootSound, node = self)),
                    Sequence(Wait(0.635), Func(self.fireLaser, target))

                    ))
        self.shootTrack.start()

    def onHitLocalAvatar(self, char, dmg):
        char.sendUpdate('takeDamage', [dmg])

    def fireLaser(self, target):
        self.eyeLaser.show()
        self.eyeLaser.wrtReparentTo(render)
        self.eyeLaser.show()
        self.eyeLaser.lookAt(target, 0, 0, 0 if not hasattr(target, 'height') else target.height / 2.0)
        self.eyeLaser.setP(self.eyeLaser.getP() + 90)

        Sequence(Wait(1.0), Func(self.resetEyeLaser)).start()
        
        pDir = self.eyeLaser.getQuat(render).xform(Vec3.down())
        pPos = self.eyeLaser.getPos(render)
        pFrom = pPos + (pDir * 1.01)
        pTo = pPos + (pDir * 50)
        result = base.physicsWorld.rayTestClosest(pFrom, pTo)
        if result.hasHit():
            node = result.getNode()
            mask = node.getIntoCollideMask()
            point = result.getHitPos()
            dist = (point - pPos).length()
            self.eyeLaser.setScale(1, 1, dist)
            if not (mask & CIGlobals.LocalAvGroup).isZero():
                if node.hasPythonTag("localAvatar"):
                    char = node.getPythonTag("localAvatar")
                    self.onHitLocalAvatar(char, CIGlobals.calcAttackDamage(dist, 5, 50))
        else:
            self.eyeLaser.setScale(1, 1, 50)

    def exitShoot(self):
        self.stopShootTrack()
