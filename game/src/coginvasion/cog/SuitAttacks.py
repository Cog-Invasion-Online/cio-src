"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitAttacks.py
@author Brian Lach
@date April 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, SoundInterval
from direct.interval.IntervalGlobal import ActorInterval, Parallel, LerpScaleInterval, LerpHprInterval
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.showbase.DirectObject import DirectObject
from direct.distributed import DelayDelete
from panda3d.core import NodePath, Vec3, VBase4, Point3, BitMask32, Vec4, VBase3
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from src.coginvasion.toon import ParticleLoader
from direct.actor.Actor import Actor
from src.coginvasion.globals import CIGlobals
from direct.showutil.Rope import Rope
from direct.task import Task
import SuitGlobals

import random

SuitAttackLengths = {"canned": 4,
                    "clipontie": 4,
                    "sacked": 4,
                    "glowerpower": 2.5,
                    "playhardball": 4,
                    "marketcrash": 4,
                    "pickpocket": 3,
                    "fountainpen": 3,
                    "hangup": 5,
                    'redtape': 4,
                    'powertie': 4,
                    'halfwindsor': 4,
                    "bite": 4,
                    "chomp": 4,
                    'evictionnotice': 4,
                    'restrainingorder': 4,
                    'razzledazzle': 3.5,
                    'buzzword': 6,
                    'jargon': 6,
                    'mumbojumbo': 6,
                    'filibuster': 6,
                    'doubletalk': 6,
                    'schmooze': 6,
                    'fingerwag': 6,
                    'teeoff': 7,
                    'evileye': 7,
                    'watercooler': 7
                    }
SuitAttackDamageFactors = {"canned": 5.5,
                "clipontie": 13,
                "sacked": 7,
                "glowerpower": 5.5,
                "playhardball": 5.5,
                "marketcrash": 8,
                "pickpocket": 10,
                "fountainpen": 9,
                "hangup": 7,
                'redtape': 8,
                'powertie': 9,
                'halfwindsor': 11,
                "bite": 7,
                "chomp": 5.5,
                'evictionnotice': 9,
                'restrainingorder': 8,
                'razzledazzle': 9,
                'buzzword': 10,
                'jargon': 9,
                'mumbojumbo': 9.5,
                'filibuster': 9.5,
                'doubletalk': 10,
                'schmooze': 8,
                'fingerwag': 8,
                'teeoff': 10,
                'evileye': 8,
                'watercooler': 12
                }
    
THROW_ATTACK_IVAL_TIME = 0.75
GLOWER_POWER_IVAL_TIME = 0.5

def setEffectTexture(effect, texture, color):
    particles = effect.getParticlesNamed('particles-1')
    sparticles = loader.loadModel('phase_3.5/models/props/suit-particles.bam')
    np = sparticles.find('**/' + texture)
    particles.renderer.setColor(color)
    particles.renderer.setFromNode(np)

def setEffectOffsetVelo(effect, velo):
    particles = effect.getParticlesNamed('particles-1')
    particles.emitter.setOffsetForce(Vec3(0.0, velo, 0.0))

def makeCollision(radius, name):
    sph = BulletSphereShape(radius)

    node = BulletGhostNode(name)
    node.addShape(sph)
    node.setKinematic(True)
    node.setIntoCollideMask(CIGlobals.WeaponGroup)
    base.physicsWorld.attach(node)

    return node

def loadSplat(color):
    splat = Actor("phase_3.5/models/props/splat-mod.bam",
            {"chan": "phase_3.5/models/props/splat-chan.bam"})
    splat.setColor(color)
    return splat

class Attack(DirectObject):
    notify = directNotify.newCategory("Attack")
    attack = 'attack'
    attackName = 'Cog Attack'

    def __init__(self, attacksClass, suit):
        self.attacksClass = attacksClass
        self.target = self.attacksClass.target
        self.suit = suit
        self.suitTrack = None
        self.attackName2attackId = {}
        for index in range(len(self.attacksClass.attackName2attackClass.keys())):
            self.attackName2attackId[SuitAttackLengths.keys()[index]] = index

    def startSuitTrack(self, ts):
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, self.suitTrack.getName())
        self.suitTrack.start(ts)

    def announceHit(self, foo = None):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            
    def lockOnToonTask(self, task):
        if (not CIGlobals.isNodePathOk(self.suit) or
            not CIGlobals.isNodePathOk(self.target)):
            return task.done
            
        self.suit.headsUp(self.target)
        return task.cont
        
    def startToonLockOn(self):
        taskMgr.add(self.lockOnToonTask, self.suit.uniqueName("attackLockOnToon"))
        
    def stopToonLockOn(self):
        taskMgr.remove(self.suit.uniqueName("attackLockOnToon"))

    def doAttack(self, ts = 0.0):
        pass

    def getAttackId(self, attackStr):
        return self.attackName2attackId[attackStr]

    def finishedAttack(self):
        messenger.send(self.attacksClass.doneEvent)

    def interruptAttack(self):
        self.cleanup()

    def cleanup(self):
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        self.attack = None
        self.suit = None
        self.target = None
        self.attacksClass = None
        self.attackName2attackId = None

from SuitType import SuitType

class ThrowAttack(Attack):
    notify = directNotify.newCategory("ThrowAttack")
    attack = 'throw'
    attackName = 'Throw Attack'

    # The frame of the throw animation at which the projectile is released.
    suitType2releaseFrame = {
        SuitType.C: {'throw-paper': 57, 'throw-object': 56},
        SuitType.A: {'throw-paper': 73, 'throw-object': 73},
        SuitType.B: {'throw-paper': 73, 'throw-object': 75}
    }

    speed = 1.5

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.weapon_state = None
        self.weapon = None
        self.wss = None
        self.wsnp = None
        self.suitTrack = None
        self.weaponSfx = None
        self.throwTrajectory = None
        self.startNP = None
        self.theActorIval = None

    def handleWeaponCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            #self.suit.b_handleWeaponTouch()

    def doAttack(self, weapon_path, weapon_scale, track_name,
                animation_name, collsphere_radius, weapon_coll_id,
                weapon_h = 0, weapon_p = 0, weapon_r = 0, weapon_x = 0,
                weapon_y = 0, weapon_z = 0, ts = 0):
        self.weapon_state = 'start'
        if hasattr(self.suit, 'uniqueName'):
            track_name = self.suit.uniqueName(track_name)
            weapon_coll_id = self.suit.uniqueName(weapon_coll_id)
        if isinstance(weapon_path, str):
            self.weapon = loader.loadModel(weapon_path)
        else:
            self.weapon = NodePath("weaponRoot")
        self.weapon.setScale(weapon_scale)
        self.weapon.setHpr(weapon_h, weapon_p, weapon_r)
        self.weapon.setPos(weapon_x, weapon_y, weapon_z)
        self.wss = BulletSphereShape(collsphere_radius)
        
        self.startToonLockOn()

        releaseFrame = self.suitType2releaseFrame[self.suit.suitPlan.getSuitType()][animation_name]

        actorIval = ActorInterval(self.suit, animation_name, endFrame = releaseFrame, playRate = self.speed)
        actorIval2 = ActorInterval(self.suit, animation_name, startFrame = releaseFrame, playRate = self.speed)

        self.suitTrack = Parallel(Sequence(actorIval, actorIval2),
                                  Sequence(Wait(actorIval.getDuration()), Func(self.throwObject), Wait(1.0), Func(self.delWeapon)),
                                  name = track_name)

        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))

        wsnode = BulletGhostNode(weapon_coll_id)
        wsnode.addShape(self.wss)
        wsnode.setKinematic(True)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.wsnp.setCollideMask(CIGlobals.WeaponGroup)
        self.startSuitTrack(ts)

    def playWeaponSound(self):
        if self.weapon and self.weaponSfx:
            base.audio3d.attachSoundToObject(self.weaponSfx, self.suit)
            base.playSfx(self.weaponSfx, node = self.suit)

    def throwObject(self, projectile = True):
        if not CIGlobals.isNodePathOk(self.weapon) or not CIGlobals.isNodePathOk(self.target):
            return
            
        self.stopToonLockOn()
        
        # Watch for a local avatar collision with our weapon.
        base.physicsWorld.attach(self.wsnp.node())
        self.acceptOnce("enter" + self.wsnp.node().getName(), self.handleWeaponCollision)
        
        self.playWeaponSound()
        if self.weapon:
            self.weapon.wrtReparentTo(render)
            self.weapon.setHpr(Vec3(0, 0, 0))

        if not self.attack in ['glowerpower']:
            parent = self.suit.find('**/joint_Rhold')
        else:
            parent = self.suit.find('**/joint_head')

        startNP = parent.attachNewNode('startNp')
        startNP.lookAt(self.target.find("**/def_head"))
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(startNP)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)

        if self.attack in ['clipontie', 'powertie', 'halfwindsor']:
            self.weapon.setHpr(pathNP.getHpr(render))

        self.throwTrajectory = LerpPosInterval(
            self.weapon,
            startPos = parent.getPos(render),
            pos = pathNP.getPos(render),
            duration = THROW_ATTACK_IVAL_TIME
        )

        self.throwTrajectory.start()
        self.weapon_state = 'released'

        startNP.removeNode()
        del startNP
        pathNP.removeNode()
        del pathNP

    def interruptAttack(self):
        if self.throwTrajectory:
            if self.throwTrajectory.isStopped():
                self.delPhysics()
                self.delWeapon()

    def handleWeaponTouch(self):
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delPhysics()
        self.delWeapon()

    def delWeapon(self):
        if self.weapon:
            self.weapon.removeNode()
            self.weapon = None
            
    def delPhysics(self):
        self.wss = None
        if self.wsnp:
            print "delPhysics: removing the ThrowAttack ghost node"
            base.physicsWorld.remove(self.wsnp.node())
            self.wsnp.removeNode()
            self.wsnp = None

    def cleanup(self):
        Attack.cleanup(self)
        self.weapon_state = None
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delPhysics()
        self.delWeapon()

class CannedAttack(ThrowAttack):
    notify = directNotify.newCategory("CannedAttack")
    attack = 'canned'
    attackName = 'Canned'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/can.bam", 15, 'doCannedAttack',
                            'throw-object', 0.05, 'cannedWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.ogg")
        ThrowAttack.playWeaponSound(self)

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class HardballAttack(ThrowAttack):
    notify = directNotify.newCategory("HardballAttack")
    attack = 'playhardball'
    attackName = 'Play Hardball'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/baseball.bam", 10, 'doHardballAttack',
                            'throw-object', 0.1, 'hardballWeaponSphere', weapon_z = -0.5, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_hardball_throw_only.ogg")
        ThrowAttack.playWeaponSound(self)

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class ClipOnTieAttack(ThrowAttack):
    notify = directNotify.newCategory("ClipOnTieAttack")
    attack = 'clipontie'
    attackName = 'Clip-On-Tie'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_3.5/models/props/clip-on-tie-mod.bam", 1, 'doClipOnTieAttack',
                            'throw-paper', 1.1, 'clipOnTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
        ThrowAttack.playWeaponSound(self)

class MarketCrashAttack(ThrowAttack):
    notify = directNotify.newCategory("MarketCrashAttack")
    attack = 'marketcrash'
    attackName = 'Market Crash'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/newspaper.bam", 3, 'doMarketCrashAttack',
                            'throw-paper', 0.35, 'marketCrashWeaponSphere', weapon_x = 0.41,
                            weapon_y = -0.06, weapon_z = -0.06, weapon_h = 90, weapon_r = 270, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

class SackedAttack(ThrowAttack):
    notify = directNotify.newCategory("SackedAttack")
    attack = 'sacked'
    attackName = 'Sacked'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/sandbag-mod.bam", 2, 'doSackedAttack',
                            'throw-paper', 1, 'sackedWeaponSphere', weapon_r = 180, weapon_p = 90,
                            weapon_y = -2.8, weapon_z = -0.3, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

class GlowerPowerAttack(Attack):
    notify = directNotify.newCategory("GlowerPowerAttack")
    attack = 'glowerpower'
    attackName = 'Glower Power'
    knifeScale = 0.4

    eyePosPoints = {
        SuitGlobals.TheBigCheese: [Point3(0.6, 4.5, 6), Point3(-0.6, 4.5, 6)],
        SuitGlobals.HeadHunter: [Point3(0.3, 4.3, 5.3), Point3(-0.3, 4.3, 5.3)],
        SuitGlobals.Tightwad: [Point3(0.4, 3.8, 3.7), Point3(-0.4, 3.8, 3.7)]
    }

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.knifeRoot = None
        self.knives = []
        self.sound = None
        self.collNP = None

    def cleanup(self):
        Attack.cleanup(self)
        if self.collNP:
            print "cleanup: removing the GlowerPowerAttack ghost node"
            base.physicsWorld.remove(self.collNP.node())
            self.collNP.removeNode()
            self.collNP = None
        if self.knives:
            for knife in self.knives:
                knife.removeNode()
            self.knives = None
        if self.knifeRoot:
            self.knifeRoot.removeNode()
            self.knifeRoot = None

    def loadKnife(self):
        k = loader.loadModel("phase_5/models/props/dagger.bam")
        k.setScale(self.knifeScale)
        return k

    def doAttack(self, ts = 0):
        left, right = self.eyePosPoints[self.suit.suitPlan.getName()]
        self.knifeRoot = self.suit.attachNewNode("knifeRoot")
        self.knifeRoot.setPos(0, left.getY(), left.getZ())
        self.knifeRoot.lookAt(self.target.find("**/def_head"))

        self.sound = base.audio3d.loadSfx("phase_5/audio/sfx/SA_glower_power.ogg")
        base.audio3d.attachSoundToObject(self.sound, self.suit)

        collName = self.suit.uniqueName("glowerPowerColl")
        self.collNP = self.knifeRoot.attachNewNode(makeCollision(1.0, collName))
        collTrack = Sequence(Func(self.startToonLockOn), Wait(0.9), Func(self.stopToonLockOn), Wait(0.2),
                             Func(self.acceptOnce, 'enter' + collName, self.announceHit),
                             LerpPosInterval(self.collNP, 1.0, (0, 50, 0), (0, 0, 0)),
                             Func(self.ignore, 'enter' + collName))
        
        leftTracks = Parallel()
        rightTracks = Parallel()
        knifeDelay = 0.11
        for i in xrange(0, 3):
            lk = self.loadKnife()
            lk.reparentTo(self.knifeRoot)
            lk.hide()
            rk = self.loadKnife()
            rk.reparentTo(self.knifeRoot)
            rk.hide()
            self.knives.append(lk)
            self.knives.append(rk)
            leftTrack = Sequence(Wait(1.1), Wait(i * knifeDelay), Func(lk.show),
                                 LerpPosInterval(lk, 1.0, (left.getX(), 50 / self.knifeScale, 0), (left.getX(), 0, 0)),
                                 Func(lk.hide))
            rightTrack = Sequence(Wait(1.1), Wait(i * knifeDelay), Func(rk.show),
                                 LerpPosInterval(rk, 1.0, (right.getX(), 50 / self.knifeScale, 0), (right.getX(), 0, 0)),
                                 Func(rk.hide))
            leftTracks.append(leftTrack)
            rightTracks.append(rightTrack)
            
        self.suitTrack = Parallel(
            ActorInterval(self.suit, 'glower'),
            Sequence(Wait(1.1), SoundInterval(self.sound, node = self.suit)),
            leftTracks, rightTracks, collTrack)
        self.startSuitTrack(ts)

class PickPocketAttack(Attack):
    notify = directNotify.newCategory("PickPocketAttack")
    attack = 'pickpocket'
    attackName = 'Pick Pocket'

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.dollar = None
        self.pickSfx = None

    def doAttack(self, ts = 0):
        self.startToonLockOn()
        
        self.dollar = loader.loadModel("phase_5/models/props/1dollar-bill-mod.bam")
        self.dollar.setY(0.22)
        self.dollar.setHpr(289.18, 252.75, 0.00)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doPickPocketAttack')
        else:
            name = 'doPickPocketAttack'
        self.suitTrack = Parallel(ActorInterval(self.suit, "pickpocket"),
            Sequence(Wait(0.4), Func(self.attemptDamage)), name = name)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def attemptDamage(self):
        self.stopToonLockOn()
        
        shouldDamage = False
        suitH = self.suit.getH(render) % 360
        myH = base.localAvatar.getH(render) % 360
        if not -90.0 <= (suitH - myH) <= 90.0:
            if base.localAvatar.getDistance(self.suit) <= 15.0:
                shouldDamage = True
        if shouldDamage:
            self.playWeaponSound()
            self.dollar.reparentTo(self.suit.find('**/joint_Rhold'))
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])

    def playWeaponSound(self):
        self.pickSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_pick_pocket.ogg")
        base.audio3d.attachSoundToObject(self.pickSfx, self.suit)
        self.pickSfx.play()

    def cleanup(self):
        Attack.cleanup(self)
        if self.pickSfx:
            self.pickSfx.stop()
            self.pickSfx = None
        if self.dollar:
            self.dollar.removeNode()
            self.dollar = None

class FountainPenAttack(Attack):
    notify = directNotify.newCategory("FountainPenAttack")
    attack = 'fountainpen'
    attackName = 'Fountain Pen'

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.pen = None
        self.spray = None
        self.splat = None
        self.spraySfx = None
        self.sprayParticle = None
        self.sprayScaleIval = None
        self.wsnp = None

    def loadAttack(self):
        self.pen = loader.loadModel("phase_5/models/props/pen.bam")
        self.pen.reparentTo(self.suit.find('**/joint_Rhold'))
        self.sprayParticle = ParticleLoader.loadParticleEffect("phase_5/etc/penSpill.ptf")
        self.spray = loader.loadModel("phase_3.5/models/props/spray.bam")
        self.spray.setColor(VBase4(0, 0, 0, 1))
        self.splat = Actor("phase_3.5/models/props/splat-mod.bam",
            {"chan": "phase_3.5/models/props/splat-chan.bam"})
        self.splat.setColor(VBase4(0, 0, 0, 1))
        self.sprayScaleIval = LerpScaleInterval(
            self.spray,
            duration = 0.3,
            scale = (1, 20, 1),
            startScale = (1, 1, 1)
        )
        if hasattr(self.suit, 'uniqueName'):
            collName = self.suit.uniqueName('fountainPenCollNode')
        else:
            collName = 'fountainPenCollNode'
        self.wsnp = self.spray.attachNewNode(makeCollision(0.5, collName))
        self.wsnp.setY(1)
        #self.wsnp.show()

    def doAttack(self, ts = 0):
        self.loadAttack()
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doFountainPenAttack')
        else:
            name = 'doFountainPenAttack'
        self.suitTrack = Parallel(name = name)
        self.suitTrack.append(ActorInterval(self.suit, "fountainpen"))
        self.suitTrack.append(
            Sequence(
                Func(self.startToonLockOn),
                Wait(0.8),
                Func(self.stopToonLockOn),
                Func(self.attachSpray),
                Func(self.spray.hide),
                Wait(0.4),
                Func(self.acceptOnce, "enter" + self.wsnp.node().getName(), self.handleSprayCollision),
                Func(self.playWeaponSound),
                Func(self.spray.show),
                Func(self.sprayParticle.start, self.pen.find('**/joint_toSpray'), self.pen.find('**/joint_toSpray')),
                self.sprayScaleIval,
                Wait(0.5),
                Func(self.sprayParticle.cleanup),
                Func(self.spray.setScale, 1),
                Func(self.spray.reparentTo, hidden),
                Func(self.ignore, "enter" + self.wsnp.node().getName())
            )
        )
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def attachSpray(self):
        self.spray.reparentTo(self.pen.find('**/joint_toSpray'))
        #self.spray.setH(100)
        pos = self.spray.getPos(render)
        hpr = self.spray.getHpr(render)
        self.spray.reparentTo(render)
        self.spray.setPos(pos)
        self.spray.setHpr(hpr)
        self.spray.setP(0)
        if self.suit.suitPlan.getSuitType() == "C":
            self.spray.setH(self.spray.getH() + 7.5)
        self.spray.setTwoSided(True)
        self.spray.lookAt(self.target.find("**/def_head"))

    def handleSprayCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
        self.sprayScaleIval.pause()

    def playWeaponSound(self):
        self.spraySfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_fountain_pen.ogg")
        base.audio3d.attachSoundToObject(self.spraySfx, self.pen)
        base.playSfx(self.spraySfx, node = self.pen)

    def cleanup(self):
        Attack.cleanup(self)
        if self.wsnp:
            base.physicsWorld.remove(self.wsnp.node())
            self.wsnp.removeNode()
            self.wsnp = None
        if self.pen:
            self.pen.removeNode()
            self.pen = None
        if self.sprayParticle:
            self.sprayParticle.cleanup()
            self.sprayParticle = None
        if self.spray:
            self.spray.removeNode()
            self.spray = None
        if self.splat:
            self.splat.cleanup()
            self.splat = None
        if self.sprayScaleIval:
            self.sprayScaleIval.pause()
            self.sprayScaleIval = None
        self.spraySfx = None

class HangUpAttack(Attack):
    notify = directNotify.newCategory("HangUpAttack")
    attack = 'hangup'
    attackName = 'Hang Up'

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.phone = None
        self.receiver = None
        self.collNP = None
        self.phoneSfx = None
        self.hangupSfx = None
        self.shootIval = None
        self.cord = None
        self.receiverOutCord = None
        self.phoneOutCord = None

    def loadAttack(self):
        self.phone = loader.loadModel("phase_3.5/models/props/phone.bam")
        self.phone.setHpr(0, 0, 180)
        if self.suit.suitPlan.getSuitType() == "B":
            self.phone.setPos(0.7, 0.15, 0)
        elif self.suit.suitPlan.getSuitType() == "C":
            self.phone.setPos(0.25, 0, 0)
        self.receiver = loader.loadModel("phase_3.5/models/props/receiver.bam")
        self.receiver.reparentTo(self.phone)
        self.cord = Rope()
        self.cord.ropeNode.setUseVertexColor(1)
        self.cord.ropeNode.setUseVertexThickness(1)
        self.cord.setup(3, ({'node': self.phone, 'point': (0.8, 0, 0.2), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': self.phone, 'point': (2, 0, 0), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': self.receiver, 'point': (1.1, 0.25, 0.5), 'color': (0, 0, 0, 1), 'thickness': 1000}), [])
        self.cord.setH(180)
        self.phoneSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup.ogg")
        base.audio3d.attachSoundToObject(self.phoneSfx, self.phone)
        self.hangupSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup_place_down.ogg")
        base.audio3d.attachSoundToObject(self.hangupSfx, self.phone)
        self.collNP = self.phone.attachNewNode(makeCollision(2, 'phone_shootout'))
        #self.collNP.show()

    def doAttack(self, ts = 0):
        self.loadAttack()
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doHangupAttack')
        else:
            name = 'doHangupAttack'
        if self.suit.suitPlan.getSuitType() == "A":
            delay2playSound = 1.0
            delayAfterSoundToPlaceDownReceiver = 0.2
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.0
            receiverInHandPos = Point3(-0.5, 0.5, -1)
        elif self.suit.suitPlan.getSuitType() == "B":
            delay2playSound = 1.5
            delayAfterSoundToPlaceDownReceiver = 0.7
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.5
            receiverInHandPos = Point3(-0.3, 0.5, -0.8)
        elif self.suit.suitPlan.getSuitType() == "C":
            delay2playSound = 1.0
            delayAfterSoundToPlaceDownReceiver = 1.15
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.5
            receiverInHandPos = Point3(-0.3, 0.5, -0.8)
        self.suitTrack = Parallel(name = name)
        self.suitTrack.append(
            ActorInterval(self.suit, 'phone')
        )
        self.suitTrack.append(
            Sequence(
                Func(self.startToonLockOn),
                Wait(delay2playSound),
                SoundInterval(self.phoneSfx, duration = 2.1, node = self.suit),
                Wait(delayAfterSoundToPlaceDownReceiver),
                Func(self.receiver.setPos, 0, 0, 0),
                Func(self.receiver.setH, 0.0),
                Func(self.receiver.reparentTo, self.phone),
                Func(self.stopToonLockOn),
                Func(self.acceptOnce, "enter" + self.collNP.node().getName(), self.handleCollision),
                Func(self.shootOut),
                Parallel(
                    SoundInterval(self.hangupSfx, node = self.suit),
                    Sequence(
                        Wait(delayAfterShootToIgnoreCollisions),
                        Func(self.ignore, "enter" + self.collNP.node().getName())
                    )
                )
            )
        )
        self.suitTrack.append(
            Sequence(
                Func(self.phone.reparentTo, self.suit.find('**/joint_Lhold')),
                Func(self.cord.reparentTo, render),
                Wait(delay2PickUpReceiver),
                Func(self.receiver.reparentTo, self.suit.find('**/joint_Rhold')),
                Func(self.receiver.setPos, receiverInHandPos),
                Func(self.receiver.setH, 270.0),
            )
        )
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def handleCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])

    def shootOut(self):
        pathNode = NodePath('path')
        pathNode.reparentTo(self.suit)#.find('**/joint_Lhold'))
        pathNode.setPos(0, 50, self.phone.getZ(self.suit))

        self.collNP.reparentTo(render)

        self.shootIval = LerpPosInterval(
            self.collNP,
            duration = 1.0,
            pos = pathNode.getPos(render),
            startPos = self.phone.getPos(render)
        )
        self.shootIval.start()
        pathNode.removeNode()
        del pathNode

    def cleanup(self):
        Attack.cleanup(self)
        if self.shootIval:
            self.shootIval.pause()
            self.shootIval = None
        if self.cord:
            self.cord.removeNode()
            self.cord = None
        if self.phone:
            self.phone.removeNode()
            self.phone = None
        if self.receiver:
            self.receiver.removeNode()
            self.receiver = None
        if self.collNP:
            base.physicsWorld.remove(self.collNP.node())
            self.collNP.removeNode()
            self.collNP = None
        if self.phoneSfx:
            self.phoneSfx.stop()
            self.phoneSfx = None

class BounceCheckAttack(ThrowAttack):
    notify = directNotify.newCategory('BounceCheckAttack')
    MaxBounces = 3
    WeaponHitDistance = 0.5
    attack = 'bouncecheck'
    attackName = 'Bounce Check'

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'bouncecheck'
        self.bounceSound = None
        self.numBounces = 0

    def __pollCheckDistance(self, task):
        if base.localAvatar.getDistance(self.weapon) <= self.WeaponHitDistance:
            self.handleWeaponCollision(None)
            return Task.done
        else:
            return Task.cont

    def loadAttack(self):
        self.weapon = loader.loadModel('phase_5/models/props/bounced-check.bam')
        self.weapon.setScale(10)
        self.weapon.setTwoSided(1)
        self.bounceSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_bounce_check_bounce.ogg')
        base.audio3d.attachSoundToObject(self.bounceSound, self.suit)
        cSphere = CollisionSphere(0, 0, 0, 0.1)
        cSphere.setTangible(0)
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('bounced_check_collision')
        else:
            name = 'bounced_check_collision'
        cNode = CollisionNode(name)
        cNode.addSolid(cSphere)
        cNode.setFromCollideMask(CIGlobals.FloorBitmask)
        cNP = self.weapon.attachNewNode(cNode)
        cNP.setCollideMask(BitMask32(0))
        self.event = CollisionHandlerEvent()
        self.event.setInPattern('%fn-into')
        self.event.setOutPattern('%fn-out')
        base.cTrav.addCollider(cNP, self.event)
        self.wsnp = cNP
        self.wsnp.show()

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.loadAttack()
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('doBounceCheckAttack')
        else:
            name = 'doBounceCheckAttack'
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        if self.suit.suitPlan.getSuitType() == "C":
            self.suitTrack.append(Wait(2.3))
        else:
            self.suitTrack.append(Wait(3))
        self.suit.play('throw-paper')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.start(ts)

    def throwObject(self):
        ThrowAttack.throwObject(self)
        taskMgr.add(self.__pollCheckDistance, "pollCheckDistance")
        self.__doThrow(0)

    def __doThrow(self, alreadyThrown):
        self.weapon.setScale(1)
        pathNP = NodePath('throwPath')
        if not alreadyThrown:
            pathNP.reparentTo(self.suit)
        else:
            pathNP.reparentTo(self.weapon)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 30, -100)
        pathNP.setHpr(90, -90, 90)

        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None

        if alreadyThrown:
            startPos = self.weapon.getPos(base.render)
            gravity = 0.7
        else:
            gravity = 0.7
            startPos = self.suit.find('**/joint_Rhold').getPos(base.render)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = startPos,
            endPos = pathNP.getPos(base.render),
            gravityMult = gravity,
            duration = 3.0
        )
        self.throwTrajectory.start()
        self.weapon.setScale(10)
        self.weapon.reparentTo(render)
        self.weapon.setHpr(pathNP.getHpr(render))
        self.weapon_state = 'released'
        self.acceptOnce(self.wsnp.node().getName() + "-into", self.__handleHitFloor)

    def __handleHitFloor(self, entry):
        self.numBounces += 1
        # Bounce again if we still have bounces left.
        if self.numBounces >= self.MaxBounces:
            self.cleanup()
            return
        base.playSfx(self.bounceSound)
        self.__doThrow(1)

    def cleanup(self):
        taskMgr.remove("pollCheckDistance")
        self.ignore(self.wsnp.node().getName() + "-into")
        self.bounceSound = None
        ThrowAttack.cleanup(self)

class RedTapeAttack(ThrowAttack):
    notify = directNotify.newCategory('RedTapeAttack')
    attack = 'redtape'
    attackName = 'Red Tape'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/redtape.bam", 1, 'doRedTapeAttack',
                            'throw-paper', 0.5, 'redTapeWeaponSphere', weapon_p = 90,
                            weapon_y = 0.35, weapon_z = -0.5, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_red_tape.ogg")
        ThrowAttack.playWeaponSound(self)

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class PowerTieAttack(ThrowAttack):
    notify = directNotify.newCategory('PowerTieAttack')
    attack = 'powertie'
    attackName = 'Power Tie'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/power-tie.bam", 4, 'doPowerTieAttack',
                            'throw-paper', 0.2, 'powerTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
        ThrowAttack.playWeaponSound(self)

class HalfWindsorAttack(ThrowAttack):
    notify = directNotify.newCategory('HalfWindsorAttack')
    attack = 'halfwindsor'
    attackName = 'Half Windsor'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/half-windsor.bam", 6, 'doHalfWindsorAttack',
                            'throw-paper', 0.2, 'halfWindsorWeaponSphere', weapon_r = 90, weapon_p = 0,
                            weapon_h = 90, weapon_z = -1, weapon_y = -1.6, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
        ThrowAttack.playWeaponSound(self)

class BiteAttack(ThrowAttack):
    notify = directNotify.newCategory('BiteAttack')
    attack = 'bite'
    attackName = 'Bite'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/teeth-mod.bam", 6, 'doBiteAttack',
                            'throw-object', 0.2, 'biteWeaponSphere', weapon_r = 180, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)
        if not self.weapon:
            return
        self.weapon.setH(self.weapon, -90)

class ChompAttack(ThrowAttack):
    notify = directNotify.newCategory('ChompAttack')
    attack = 'chomp'
    attackName = 'Chomp'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/teeth-mod.bam", 6, 'doChompAttack',
                            'throw-object', 0.2, 'chompWeaponSphere', weapon_r = 180, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)
        if not self.weapon:
            return
        self.weapon.setH(self.weapon, -90)

class EvictionNoticeAttack(ThrowAttack):
    notify = directNotify.newCategory("EvictionNoticeAttack")
    attack = 'evictionnotice'
    attackName = 'Eviction Notice'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_3.5/models/props/shredder-paper-mod.bam", 1, 'doEvictionNoticeAttack',
                            'throw-paper', 1, 'evictionNoticeWeaponSphere', weapon_y = -0.15, weapon_z = -0.5,
                            weapon_x = -1.4, weapon_r = 90, weapon_h = 30, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)

class RestrainingOrderAttack(EvictionNoticeAttack):
    notify = directNotify.newCategory('RestrainingOrderAttack')
    attack = 'restrainingorder'
    attackName = 'Restraining Order'

class ParticleAttack(Attack):
    notify = directNotify.newCategory('ParticleAttack')
    attack = 'particleattack'
    attackName = 'Particle Attack'
    particleIvalDur = 1
    shooterDistance = 50

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.particles = []
        self.handObj = None
        self.shootOutCollNP = None
        self.particleSound = None
        self.particleMoveIval = None
        self.targetX = None
        self.targetY = None
        self.targetZ = None

    def handleWeaponTouch(self):
        pass

    def handleCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])

    def doAttack(self, particlePaths, track_name, particleCollId, animation_name,
                delayUntilRelease, animationSpeed = 1, handObjPath = None, handObjParent = None,
                startRightAway = True, ts = 0):
        for path in particlePaths:
            particle = ParticleLoader.loadParticleEffect(path)
            self.particles.append(particle)

        node = makeCollision(2, particleCollId)
        
        self.startToonLockOn()

        self.targetX = self.attacksClass.target.getX(render)
        self.targetY = self.attacksClass.target.getY(render)
        self.targetZ = self.attacksClass.target.getZ(render)
        if len(self.particles) == 1:
            self.shootOutCollNP = self.particles[0].attachNewNode(node)
        else:
            self.shootOutCollNP = self.suit.attachNewNode(node)
        if handObjPath and handObjParent:
            if isinstance(handObjPath, str):
                self.handObj = loader.loadModel(handObjPath)
            elif isinstance(handObjPath, list):
                mdl = handObjPath[0]
                anims = handObjPath[1]
                self.handObj = Actor(mdl, anims)
            self.handObj.setShaderOff(1)
            self.handObj.reparentTo(handObjParent)
        if hasattr(self.suit, 'uniqueName'):
            track_name = self.suit.uniqueName(track_name)
            particleCollId = self.suit.uniqueName(particleCollId)
        self.suitTrack = Parallel(ActorInterval(self.suit, animation_name, playRate = animationSpeed), name = track_name)
        seq = Sequence()
        seq.append(Wait(delayUntilRelease))
        seq.append(Func(self.releaseAttack))
        seq.append(Wait(self.particleIvalDur))
        seq.setDoneEvent(self.suitTrack.getName())
        self.suitTrack.append(seq)
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        if startRightAway:
            self.suitTrack.start(ts)

    def releaseAttack(self, releaseFromJoint, onlyMoveColl = True, blendType = 'noBlend'):
        startNP = releaseFromJoint.attachNewNode('startNP')
        self.stopToonLockOn()
        if CIGlobals.isNodePathOk(self.target):
            startNP.lookAt(self.target.find("**/def_head"))
            pathNP = NodePath('path')
            pathNP.reparentTo(startNP)
            pathNP.setScale(render, 1.0)
            pathNP.setPos(0, self.shooterDistance, 0)
            
            for particle in self.particles:
                if not onlyMoveColl:
                    particle.start(render)
                else:
                    particle.start(self.suit)
                particle.lookAt(pathNP)
                if self.attack == 'razzledazzle':
                    particle.setP(particle, 90)

            if onlyMoveColl:
                target = self.shootOutCollNP
                target.wrtReparentTo(render)
            else:
                target = self.particles[0]
            self.particleMoveIval = LerpPosInterval(
                target, duration = self.particleIvalDur,
                pos = pathNP.getPos(render),
                startPos = startNP.getPos(render),
                blendType = blendType
            )
            self.particleMoveIval.start()

            self.acceptOnce('enter' + self.shootOutCollNP.node().getName(), self.handleCollision)

            pathNP.removeNode()
            startNP.removeNode()
            del pathNP
            del startNP

        self.playParticleSound()

    def playParticleSound(self):
        if self.particleSound:
            base.audio3d.attachSoundToObject(self.particleSound, self.suit)
            base.playSfx(self.particleSound, node = self.suit)

    def stopParticles(self):
        if self.particles:
            for particle in self.particles:
                particle.cleanup()
        self.particles = None

    def cleanup(self):
        Attack.cleanup(self)
        self.targetX = None
        self.targetY = None
        self.targetZ = None
        self.stopParticles()
        if self.handObj:
            self.handObj.removeNode()
            self.handObj = None
        if self.shootOutCollNP:
            self.ignore('enter' + self.shootOutCollNP.node().getName())
            base.physicsWorld.remove(self.shootOutCollNP.node())
            self.shootOutCollNP.removeNode()
            self.shootOutCollNP = None
        if self.particleMoveIval:
            self.particleMoveIval.pause()
            self.particleMoveIval = None
        self.particleSound = None
        self.particleIvalDur = None

class RazzleDazzleAttack(ParticleAttack):
    notify = directNotify.newCategory('RazzleDazzleAttack')
    attack = 'razzledazzle'
    attackName = 'Razzle Dazzle'
    particleIvalDur = 2.0

    def doAttack(self, ts):
        ParticleAttack.doAttack(
            self, ['phase_5/etc/smile.ptf'], 'doRazzleDazzle', 'razzleDazzleSphere',
            'glower', 1.25, 1, ['phase_5/models/props/smile-mod.bam', {'chan': 'phase_5/models/props/smile-chan.bam'}], self.suit.find('**/joint_Rhold'), ts = ts
        )

        # Fix up the smile sign:
        self.handObj.setPosHprScale(0.0, -0.42, -0.04, 
                                    180, 36.03, 1.15,
                                    1.39, 1.39, 1.39)
        self.handObj.loop('chan')

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.handObj.find('**/scale_joint_sign'), onlyMoveColl = False, blendType = 'easeIn')

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_razzle_dazzle.ogg')
        ParticleAttack.playParticleSound(self)

class BuzzWordAttack(ParticleAttack):
    notify = directNotify.newCategory('BuzzWordAttack')
    attack = 'buzzword'
    attackName = 'Buzz Word'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 50.0

    def doAttack(self, ts):
        texturesList = ['buzzwords-crash',
                     'buzzwords-inc',
                     'buzzwords-main',
                     'buzzwords-over',
                     'buzzwords-syn']
        particleList = []
        for i in xrange(0, 5):
            particleList.append('phase_5/etc/buzzWord.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doBuzzWord', 'buzzWordSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 5):
            effect = self.particles[i]
            if random.random() > 0.5:
                setEffectTexture(effect, texturesList[i], Vec4(1, 0.94, 0.02, 1))
            else:
                setEffectTexture(effect, texturesList[i], Vec4(0, 0, 0, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'))

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_buzz_word.ogg')
        ParticleAttack.playParticleSound(self)

class JargonAttack(ParticleAttack):
    notify = directNotify.newCategory("JargonAttack")
    attack = 'jargon'
    attackName = 'Jargon'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 50.0

    def doAttack(self, ts):
        texturesList = ['jargon-brow',
                     'jargon-deep',
                     'jargon-hoop',
                     'jargon-ipo']
        reds = [1, 0, 1, 0]
        particleList = []
        for i in xrange(0, 4):
            particleList.append('phase_5/etc/jargonSpray.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doJargon', 'jargonSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 4):
            effect = self.particles[i]
            setEffectTexture(effect, texturesList[i], Vec4(reds[i], 0, 0, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'))

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_jargon.ogg')
        self.particleSound.setLoop(True)
        ParticleAttack.playParticleSound(self)

class MumboJumboAttack(ParticleAttack):
    notify = directNotify.newCategory('MumboJumboAttack')
    attack = 'mumbojumbo'
    attackName = 'Mumbo Jumbo'
    particleIvalDur = 2.5
    afterIvalDur = 1.5
    shooterDistance = 50.0

    def doAttack(self, ts):
        texturesList = ['mumbojumbo-boiler',
                     'mumbojumbo-creative',
                     'mumbojumbo-deben',
                     'mumbojumbo-high',
                     'mumbojumbo-iron']
        particleList = []
        for i in xrange(0, 2):
            particleList.append('phase_5/etc/mumboJumboSpray.ptf')
        for i in xrange(0, 3):
            particleList.append('phase_5/etc/mumboJumboSmother.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doMumJum', 'mumJumSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 5):
            effect = self.particles[i]
            setEffectTexture(effect, texturesList[i], Vec4(1, 0, 0, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'), blendType = 'easeIn')

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_mumbo_jumbo.ogg')
        self.particleSound.setLoop(True)
        ParticleAttack.playParticleSound(self)

class FilibusterAttack(ParticleAttack):
    notify = directNotify.newCategory("FilibusterAttack")
    attack = 'filibuster'
    attackName = 'Filibuster'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 40.0

    def doAttack(self, ts):
        texturesList = ['filibuster-cut',
                     'filibuster-fiscal',
                     'filibuster-impeach',
                     'filibuster-inc']
        particleList = []
        for i in xrange(0, 4):
            particleList.append('phase_5/etc/filibusterSpray.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doFili', 'filiSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 4):
            effect = self.particles[i]
            setEffectTexture(effect, texturesList[i], Vec4(0.4, 0, 0, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'))

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_filibuster.ogg')
        self.particleSound.setLoop(True)
        ParticleAttack.playParticleSound(self)

class DoubleTalkAttack(ParticleAttack):
    notify = directNotify.newCategory('DoubleTalkAttack')
    attack = 'doubletalk'
    attackName = 'Double Talk'
    particleIvalDur = 3.0
    afterIvalDur = 1.5
    shooterDistance = 50.0

    def doAttack(self, ts):
        texturesList = ['doubletalk-double',
                     'doubletalk-good']
        particleList = []
        particleList.append('phase_5/etc/doubleTalkLeft.ptf')
        particleList.append('phase_5/etc/doubleTalkRight.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doDT', 'DTSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 2):
            effect = self.particles[i]
            setEffectTexture(effect, texturesList[i], Vec4(0, 1.0, 0, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'), blendType = 'easeIn')

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_filibuster.ogg')
        self.particleSound.setLoop(True)
        ParticleAttack.playParticleSound(self)

class SchmoozeAttack(ParticleAttack):
    notify = directNotify.newCategory("SchmoozeAttack")
    attack = 'schmooze'
    attackName = 'Schmooze'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 40.0

    def doAttack(self, ts):
        texturesList = ['schmooze-genius',
                     'schmooze-instant',
                     'schmooze-master',
                     'schmooze-viz']
        particleList = []
        particleList.append('phase_5/etc/schmoozeUpperSpray.ptf')
        particleList.append('phase_5/etc/schmoozeLowerSpray.ptf')
        ParticleAttack.doAttack(
            self, particleList, 'doSch', 'SchSphere',
            'speak', 1.5, 1.5, None, None, False, ts
        )
        for i in xrange(0, 2):
            effect = self.particles[i]
            setEffectTexture(effect, texturesList[i], Vec4(0, 0, 1, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'))

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_schmooze.ogg')
        self.particleSound.setLoop(True)
        ParticleAttack.playParticleSound(self)

class FingerWagAttack(ParticleAttack):
    notify = directNotify.newCategory('FingerWagAttack')
    attack = 'fingerwag'
    attackName = 'Finger Wag'
    particleIvalDur = 2
    afterIvalDur = 1.5
    shooterDistance = 35.0

    def doAttack(self, ts):
        ParticleAttack.doAttack(
            self, ['phase_5/etc/fingerwag.ptf'], 'doFW', 'FWSphere',
            'fingerwag', 1.5, 1.5, None, None, False, ts
        )
        setEffectTexture(self.particles[0], 'blah', Vec4(0.55, 0, 0.55, 1))
        self.suitTrack.append(Wait(self.afterIvalDur))
        self.suitTrack.start(ts)

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.suit.find('**/joint_head'), blendType = 'easeIn')
        self.particles[0].setH(self.particles[0], 90)

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_finger_wag.ogg')
        self.particleSound.setLoop(False)
        ParticleAttack.playParticleSound(self)

class EvilEyeAttack(Attack):
    attack = 'evileye'
    attackName = 'Evil Eye'

    posPoints = {
        SuitGlobals.CorporateRaider: [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)],
        SuitGlobals.TwoFace: [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)],
        SuitGlobals.LegalEagle: [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    }

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.eyeRoot = None
        self.eye = None
        self.eyeColl = None
        self.sound = None

    def doAttack(self, ts):
        Attack.doAttack(self, ts)

        posPoints = self.posPoints.get(self.suit.suitPlan.getName(),
                                       [Point3(-0.4, 3.65, 5.01),
                                        VBase3(-155.0, -20.0, 0.0)])

        self.eyeRoot = self.suit.attachNewNode("eyeRoot")
        self.eyeRoot.setPos(posPoints[0])
        
        self.eye = loader.loadModel("phase_5/models/props/evil-eye.bam")
        self.eye.reparentTo(self.eyeRoot)
        self.eye.setHpr(posPoints[1])

        self.sound = base.audio3d.loadSfx("phase_5/audio/sfx/SA_evil_eye.ogg")
        base.audio3d.attachSoundToObject(self.sound, self.eye)

        suitHoldStart = 1.06
        suitHoldStop = 1.69
        suitHoldDuration = suitHoldStop - suitHoldStart
        eyeHoldDuration = 1.1
        moveDuration = 1.1
        eyeScale = 11.0

        collName = self.suit.uniqueName("eyeColl")
        self.eyeColl = self.eye.attachNewNode(makeCollision(1.0 / eyeScale, collName))

        self.suitTrack = Parallel(
            Sequence(Wait(1.3), SoundInterval(self.sound, node = self.eye)),
            Sequence(ActorInterval(self.suit, 'glower', endTime = suitHoldStart), Wait(suitHoldDuration), ActorInterval(self.suit, 'glower', startTime = suitHoldStart)),
            Sequence(Func(self.startToonLockOn), Wait(suitHoldStart), LerpScaleInterval(self.eye, suitHoldDuration, Point3(eyeScale)),
                     Wait(eyeHoldDuration * 0.3), LerpHprInterval(self.eye, 0.02, Point3(205, 40, 0)),
                     Wait(eyeHoldDuration * 0.7), Func(self.setupEyeAngle), Func(self.stopToonLockOn),
                     Func(self.eyeRoot.wrtReparentTo, render),
                     Func(self.acceptOnce, 'enter' + collName, self.__handleEyeCollision),
                     Parallel(LerpPosInterval(self.eye, moveDuration, (0, 50.0, 0), startPos = (0, 0, 0)),
                              LerpHprInterval(self.eye, moveDuration, Point3(0, 0, -180))),
                     Func(self.ignore, 'enter' + collName))
        )
        self.startSuitTrack(ts)

    def __handleEyeCollision(self, entry):
        self.announceHit()
        if self.eye and not self.eye.isEmpty():
            self.eye.hide()

    def setupEyeAngle(self):
        self.eye.setHpr(205, 0, 0)
        self.eyeRoot.lookAt(self.target.find("**/def_head"))

    def cleanup(self):
        Attack.cleanup(self)
        if self.eyeColl:
            base.physicsWorld.remove(self.eyeColl.node())
            self.eyeColl.removeNode()
            self.eyeColl = None
        if self.eye:
            self.eye.removeNode()
            self.eye = None
        if self.eyeRoot:
            self.eyeRoot.removeNode()
            self.eyeRoot = None


class DemotionAttack(Attack):
    attack = 'demotion'
    attackName = 'Demotion'

class TeeOffAttack(Attack):
    attack = 'teeoff'
    attackName = 'Tee Off'

    visualizeBallPath = False

    ballPosPoints = {
        SuitGlobals.Yesman: (2.1, 0, 0.1),
        SuitGlobals.TheBigCheese: (4.1, 0, 0.1),
        SuitGlobals.TheMingler: (3.2, 0, 0.1),
        SuitGlobals.RobberBaron: (4.2, 0, 0.1)
    }

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.ball = None
        self.ballRoot = None
        self.club = None
        self.sound = None
        self.ballCNP = None
        self.ballVisRope = None

    def doAttack(self, ts):
        Attack.doAttack(self, ts)
        self.suit.headsUp(self.target)
        self.ballRoot = self.suit.attachNewNode("golfBallRoot")
        self.ballRoot.setPos(*self.ballPosPoints[self.suit.suitPlan.getName()])

        ballScale = 1.5

        if self.visualizeBallPath:
            self.ballVisRope = Rope(self.suit.uniqueName('teeOffPathVis'))
            self.ballVisRope.setup(1, ({'node': self.ballRoot, 'point': (0, 0, 0), 'color': (0, 0, 0, 1)},
                                       {'node': self.ballRoot, 'point': (0, 85, 0), 'color': (0, 0, 0, 1)}))
            self.ballVisRope.reparentTo(render)

        self.ball = loader.loadModel("phase_5/models/props/golf-ball.bam")
        self.ball.reparentTo(self.ballRoot)
        self.ball.setScale(ballScale)
        collName = self.suit.uniqueName('golfBallColl')
        self.ballCNP = self.ball.attachNewNode(makeCollision(1.0 / ballScale, collName))
        self.club = loader.loadModel("phase_5/models/props/golf-club.bam")
        self.club.reparentTo(self.suit.find("**/joint_Lhold"))
        self.club.setHpr(63.097, 43.988, -18.435)
        self.club.setScale(1.1)
        self.sound = base.audio3d.loadSfx("phase_5/audio/sfx/SA_tee_off.ogg")
        base.audio3d.attachSoundToObject(self.sound, self.suit)
        self.suitTrack = Parallel(
            ActorInterval(self.suit, 'golf'),
            Sequence(Wait(4.1), Func(base.playSfx, self.sound)),
            Sequence(Func(self.startToonLockOn), Wait(4.2), Func(self.stopToonLockOn), Func(self.setupBallAngle), Func(self.ballRoot.wrtReparentTo, render),
                     Func(self.acceptOnce, 'enter' + collName, self.__handleGolfBallCollision),
                     LerpPosInterval(self.ball, duration = 1.0, pos = (0, 85, 0), startPos = (0, 0, 0)),
                     Func(self.ball.hide),
                     Func(self.ignore, 'enter' + collName)), name = self.suit.uniqueName('golfBallSuitTrack'))
        self.startSuitTrack(ts)

    def setupBallAngle(self):
        self.ballRoot.lookAt(self.target.find("**/def_head"))
        
    def __handleGolfBallCollision(self, entry):
        self.announceHit()
        if self.ball and not self.ball.isEmpty():
            self.ball.hide()
    
    def cleanup(self):
        Attack.cleanup(self)
        if self.visualizeBallPath and self.ballVisRope:
            self.ballVisRope.removeNode()
            self.ballVisRope = None
        if self.ballCNP:
            base.physicsWorld.remove(self.ballCNP.node())
            self.ballCNP.removeNode()
            self.ballCNP = None
        if self.ball:
            self.ball.removeNode()
            self.ball = None
        if self.ballRoot:
            self.ballRoot.removeNode()
            self.ballRoot = None
        if self.club:
            self.club.removeNode()
            self.club = None

class WatercoolerAttack(Attack):
    attack = 'watercooler'
    attackName = 'Watercooler'

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.cooler = None
        self.spray = None
        self.splash = None
        self.soundAppear = None
        self.soundSpray = None
        self.collNP = None

    def doAttack(self, ts):
        Attack.doAttack(self, ts)

        def getCoolerSpout():
            spout = self.cooler.find("**/joint_toSpray")
            return spout.getPos(render)

        self.soundAppear = base.audio3d.loadSfx("phase_5/audio/sfx/SA_watercooler_appear_only.ogg")
        base.audio3d.attachSoundToObject(self.soundAppear, self.suit)
        self.soundSpray = base.audio3d.loadSfx("phase_5/audio/sfx/SA_watercooler_spray_only.ogg")
        base.audio3d.attachSoundToObject(self.soundSpray, self.suit)

        self.cooler = loader.loadModel("phase_5/models/props/watercooler.bam")
        self.cooler.reparentTo(self.suit.find("**/joint_Lhold"))
        self.cooler.setPosHpr(0.48, 0.11, -0.92, 20.403, 33.158, 69.511)
        self.cooler.hide()

        self.spray = loader.loadModel("phase_3.5/models/props/spray.bam")
        self.spray.setTransparency(True)
        self.spray.setColor(0.75, 0.75, 1.0, 0.8)
        self.spray.setScale(0.3, 1.0, 0.3)
        self.spray.reparentTo(render)
        self.spray.hide()

        collName = self.suit.uniqueName("sprayColl")
        self.collNP = self.spray.attachNewNode(makeCollision(1.0, collName))
        self.collNP.setY(1.0)

        self.splash = loadSplat((0.75, 0.75, 1.0, 0.8))
        self.splash.setTransparency(True)
        self.splash.setScale(0.3)
        self.splash.setBillboardPointWorld()

        self.suitTrack = Parallel(
            ActorInterval(self.suit, 'watercooler'),
            Sequence(Func(self.startToonLockOn), Wait(1.01), Func(self.cooler.show), LerpScaleInterval(self.cooler, 0.5, Point3(1.15, 1.15, 1.15)),
                     Wait(1.3), Func(self.stopToonLockOn), Func(self.positionSpray), Func(self.setupSprayAngle), Wait(0.3), Func(self.spray.show),
                     Func(self.acceptOnce, 'enter' + collName, self.announceHit), LerpScaleInterval(self.spray, duration = 0.3, scale = (1, 20, 1), startScale = (1, 1, 1)),
                     Func(self.spray.hide), Func(self.ignore, 'enter' + collName)),
            Sequence(Wait(1.1), SoundInterval(self.soundAppear, node = self.suit, duration = 1.4722), Wait(0.4), SoundInterval(self.soundSpray, node = self.suit, duration = 2.313)),
        )
        self.startSuitTrack(ts)

    def positionSpray(self):
        self.spray.setPos(self.cooler.find("**/joint_toSpray").getPos(render))

    def setupSprayAngle(self):
        self.spray.lookAt(self.target.find("**/def_head"))

    def cleanup(self):
        Attack.cleanup(self)
        if self.splash:
            self.splash.cleanup()
            self.splash = None
        if self.collNP:
            base.physicsWorld.remove(self.collNP.node())
            self.collNP.removeNode()
            self.collNP = None
        if self.spray:
            self.spray.removeNode()
            self.spray = None
        if self.cooler:
            self.cooler.removeNode()
            self.cooler = None


from direct.fsm.StateData import StateData

class SuitAttacks(StateData):
    notify = directNotify.newCategory("SuitAttacks")
    attackName2attackClass = {
        "canned": CannedAttack,
        "clipontie": ClipOnTieAttack,
        "sacked": SackedAttack,
        "glowerpower": GlowerPowerAttack,
        "playhardball": HardballAttack,
        "marketcrash": MarketCrashAttack,
        "pickpocket": PickPocketAttack,
        "hangup": HangUpAttack,
        "fountainpen": FountainPenAttack,
        "redtape": RedTapeAttack,
        'powertie': PowerTieAttack,
        'halfwindsor': HalfWindsorAttack,
        "bite": BiteAttack,
        "chomp": ChompAttack,
        'evictionnotice': EvictionNoticeAttack,
        'restrainingorder': RestrainingOrderAttack,
        'razzledazzle': RazzleDazzleAttack,
        'buzzword': BuzzWordAttack,
        'jargon': JargonAttack,
        'mumbojumbo': MumboJumboAttack,
        'filibuster': FilibusterAttack,
        'doubletalk': DoubleTalkAttack,
        'schmooze': SchmoozeAttack,
        'fingerwag': FingerWagAttack,
        #'demotion': DemotionAttack,
        'evileye': EvilEyeAttack,
        'teeoff': TeeOffAttack,
        'watercooler': WatercoolerAttack
    }

    def __init__(self, doneEvent, suit, target):
        StateData.__init__(self, doneEvent)
        self.suit = suit
        self.target = target
        self.currentAttack = None

    def load(self, attackName):
        StateData.load(self)
        className = self.attackName2attackClass[attackName]
        self.currentAttack = className(self, self.suit)

    def enter(self, ts = 0):
        StateData.enter(self)
        self.currentAttack.doAttack(ts)

    def exit(self):
        self.currentAttack.cleanup()
        StateData.exit(self)

    def unload(self):
        self.cleanup()
        StateData.unload(self)

    def cleanup(self):
        self.suit = None
        self.currentAttack = None
        self.target = None
