"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitAttacks.py
@author Brian Lach
@date April 04, 2015

"""

from panda3d.core import NodePath, Vec3, VBase4, Point3, BitMask32, Vec4, VBase3, TextNode
from panda3d.bullet import BulletSphereShape, BulletGhostNode

from direct.actor.Actor import Actor
from direct.showutil.Rope import Rope
from direct.task import Task
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, SoundInterval
from direct.interval.IntervalGlobal import ActorInterval, Parallel, LerpScaleInterval, LerpHprInterval
from direct.interval.IntervalGlobal import LerpColorScaleInterval
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.showbase.DirectObject import DirectObject
from direct.distributed import DelayDelete

from src.coginvasion.toon import ParticleLoader
from src.coginvasion.globals import CIGlobals, BSPUtility
from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.base.Precache import precacheModel, precacheSound, precacheActor
from SuitAttackGlobals import *
import SuitGlobals
from SuitType import SuitType

import random

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
    attack = SA_none
    attackName = 'Cog Attack'
    baseDamage = 10.0
    maxDist = 40.0
    length = 5.0
    taunts = ["Take a memo on this!"]

    particlesMdl = None

    def __init__(self, attacksClass, suit):
        self.attacksClass = attacksClass
        self.target = self.attacksClass.target
        self.suit = suit
        self.suitTrack = None
        self.collider = None
        self.throwTrack = None
        
    @classmethod
    def precache(cls):
        pass

    def startThrowTrack(self, prop, speed, distance):
        self.stopThrowTrack()

        self.throwTrack = self.getThrowTrack(prop, speed, distance)
        self.throwTrack.start()

    def stopThrowTrack(self):
        if self.throwTrack:
            self.throwTrack.pause()
        self.throwTrack = None

    def cleanupCollider(self):
        if self.collider:
            self.ignore(self.collider.getCollideEvent())
            self.collider.removeNode()
        self.collider = None

    def getThrowTrack(self, prop, speed, distance):
        startPos = prop.getPos(render)
        targetPos = self.target.getPart("head").getPos(render)
        dir = (targetPos - startPos).normalized()
        endPos = startPos + (dir * distance)
        duration = distance / speed
        return LerpPosInterval(prop, duration, endPos, startPos, other = render, fluid = 1)

    def makeWorldCollider(self, parent, radius = 1, mask = CIGlobals.WallGroup | CIGlobals.LocalAvGroup,
                          startNow = False):
        coll = WorldCollider(str(self.attack), radius, mask = mask,
                             myMask = CIGlobals.WeaponGroup, startNow = startNow,
                             exclusions = [self.suit])
        coll.reparentTo(parent)
        return coll

    @staticmethod
    def getSuitParticle(name):
        if not Attack.particlesMdl:
            Attack.particlesMdl = loader.loadModel("phase_3.5/models/props/suit-particles.bam")
        return Attack.particlesMdl.find("**/" + name)

    def removeProp(self, prop):
        if not prop or prop.isEmpty():
            return
        if isinstance(prop, Actor):
            prop.cleanup()
        else:
            prop.removeNode()

    def showProp(self, prop, parent, pos, hpr = None, scale = None):
        prop.reparentTo(parent)
        prop.setPos(pos)
        if hpr:
            prop.setHpr(hpr)
        if scale:
            prop.setScale(scale)

    def getPropTrack(self, prop, parent, posPoints, appearDelay, remainDelay,
                     scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5,
                     startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0,
                     animStartTime = 0.0):
        if anim:
            track = Sequence(Wait(appearDelay), Func(self.showProp, prop, parent *posPoints),
                             LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale = startScale),
                             ActorInterval(prop, propName, duration = animDuration, startTime = animStartTime),
                             Wait(remainDelay), Func(self.removeProp, prop))
        else:
            track = Sequence(Wait(appearDelay), Func(self.showProp, prop, parent, *posPoints),
                             LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale = startScale),
                             Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, Point3(0.01)), 
                             Func(self.removeProp, prop))
        return track

    def startSuitTrack(self, ts):
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, self.suitTrack.getName())
        self.suitTrack.start(ts)

    def announceHit(self, entry = None):
        if entry is not None:
            if not PhysicsUtils.isLocalAvatar(entry):
                return

        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.attack, base.localAvatar.doId,
                                                     base.localAvatar.getDistance(self.suit)])
        base.localAvatar.handleSuitAttack(self.attack)
            
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

    def finishedAttack(self):
        messenger.send(self.attacksClass.doneEvent)

    def interruptAttack(self):
        self.cleanup()

    def attackBlocked(self, pos):
        CIGlobals.makeDustCloud(pos, 1, base.audio3d.loadSfx("phase_4/audio/sfx/Golf_Hit_Barrier_1.ogg"))

    def cleanup(self):
        self.stopThrowTrack()
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        self.cleanupCollider()
        self.suit = None
        self.target = None
        self.attacksClass = None

from SuitType import SuitType

class ThrowAttack(Attack):
    notify = directNotify.newCategory("ThrowAttack")
    attackName = 'Throw Attack'
    length = 4

    # The frame of the throw animation at which the projectile is released.
    suitType2releaseFrame = {
        SuitType.C: {'throw-paper': 57, 'throw-object': 56},
        SuitType.A: {'throw-paper': 73, 'throw-object': 73},
        SuitType.B: {'throw-paper': 73, 'throw-object': 75}
    }

    speed = 1.5
    throwSpeed = 75.0
    throwDistance = 50.0
    
    throwMdlPath = None
    throwSfxPath = None

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.weapon_state = None
        self.weapon = None
        self.collider = None
        self.suitTrack = None
        self.weaponSfx = None
        self.throwTrajectory = None
        self.startNP = None
        self.theActorIval = None
        
    @classmethod
    def precache(cls):
        if cls.throwMdlPath:
            precacheModel(cls.throwMdlPath)
        if cls.throwSfxPath:
            precacheSound(cls.throwSfxPath)

    def handleWeaponCollision(self, entry):
        if PhysicsUtils.isLocalAvatar(entry):
            # We hit the local avatar.
            self.announceHit()
            return

        # We hit a wall or something, stop the projectile.
        self.handleWeaponTouch()

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
        
        self.collider = self.makeWorldCollider(self.weapon, collsphere_radius)
        
        self.startToonLockOn()

        releaseFrame = self.suitType2releaseFrame[self.suit.suitPlan.getSuitType()][animation_name]

        actorIval = ActorInterval(self.suit, animation_name, endFrame = releaseFrame, playRate = self.speed)
        actorIval2 = ActorInterval(self.suit, animation_name, startFrame = releaseFrame, playRate = self.speed)

        self.suitTrack = Parallel(Sequence(actorIval, actorIval2),
                                  Sequence(Wait(actorIval.getDuration()), Func(self.throwObject), Wait(1.0), Func(self.delWeapon)),
                                  name = track_name)

        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))

        self.startSuitTrack(ts)

    def playWeaponSound(self):
        if self.weapon and self.weaponSfx:
            base.audio3d.attachSoundToObject(self.weaponSfx, self.suit)
            base.playSfx(self.weaponSfx, node = self.suit)

    def throwObject(self, projectile = True):
        if not CIGlobals.isNodePathOk(self.weapon) or not CIGlobals.isNodePathOk(self.target):
            return
            
        self.stopToonLockOn()
        
        # Watch for a collision with our weapon.
        self.acceptOnce(self.collider.getCollideEvent(), self.handleWeaponCollision)
        self.collider.start()
        
        self.playWeaponSound()

        self.weapon.wrtReparentTo(render)
        self.weapon.setHpr(Vec3(0, 0, 0))

        self.throwTrajectory = self.getThrowTrack(self.weapon, self.throwSpeed, self.throwDistance)
        self.throwTrajectory.start()
        self.weapon_state = 'released'

    def interruptAttack(self):
        if self.throwTrajectory:
            if self.throwTrajectory.isStopped():
                self.delPhysics()
                self.delWeapon()

    def handleWeaponTouch(self):
        if CIGlobals.isNodePathOk(self.weapon):
            self.attackBlocked(self.weapon.getPos(render))
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
        if self.collider:
            self.collider.removeNode()
            self.collider = None

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
    attack = SA_canned
    attackName = 'Canned'
    baseDamage = 22.0
    taunts = ['Do you like it out of the can?',
            '"Can" you handle this?',
            "This one's fresh out of the can!",
            'Ever been attacked by canned goods before?',
            "I'd like to donate this canned good to you!",
            'Get ready to "Kick the can"!',
            'You think you "can", you think you "can".',
            "I'll throw you in the can!",
            "I'm making me a can o' toon-a!",
            "You don't taste so good out of the can."]

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
    attack = SA_hardball
    attackName = 'Play Hardball'
    baseDamage = 25.0
    taunts = ['So you wanna play hardball?',
            "You don't wanna play hardball with me.",
            'Batter up!',
            'Hey batter, batter!',
            "And here's the pitch...",
            "You're going to need a relief pitcher.",
            "I'm going to knock you out of the park.",
            "Once you get hit, you'll run home.",
            'This is your final inning!',
            "You can't play with me!",
            "I'll strike you out.",
            "I'm throwing you a real curve ball!"]
    throwMdlPath = "phase_5/models/props/baseball.bam"
    throwSfxPath = "phase_5/audio/sfx/SA_hardball_throw_only.ogg"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 10, 'doHardballAttack',
                            'throw-object', 0.1, 'hardballWeaponSphere', weapon_z = -0.5, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx(self.throwSfxPath)
        ThrowAttack.playWeaponSound(self)

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class ClipOnTieAttack(ThrowAttack):
    notify = directNotify.newCategory("ClipOnTieAttack")
    attack = SA_clipontie
    attackName = 'Clip-On-Tie'
    baseDamage = 7.0
    taunts = ['Better dress for our meeting.',
            "You can't go OUT without your tie.",
            'The best dressed Cogs wear them.',
            'Try this on for size.',
            'You should dress for success.',
            'No tie, no service.',
            'Do you need help putting this on?',
            'Nothing says powerful like a good tie.',
            "Let's see if this fits.",
            'This is going to choke you up.',
            "You'll want to dress up before you go OUT.",
            "I think I'll tie you up."]
    throwMdlPath = "phase_3.5/models/props/clip-on-tie-mod.bam"
    throwSfxPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 1, 'doClipOnTieAttack',
                            'throw-paper', 1.1, 'clipOnTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx(self.throwSfxPath)
        ThrowAttack.playWeaponSound(self)

class MarketCrashAttack(ThrowAttack):
    notify = directNotify.newCategory("MarketCrashAttack")
    attack = SA_marketcrash
    attackName = 'Market Crash'
    baseDamage = 12.0
    taunts = ["I'm going to crash your party.",
            "You won't survive the crash.",
            "I'm more than the market can bear.",
            "I've got a real crash course for you!",
            "Now I'll come crashing down.",
            "I'm a real bull in the market.",
            'Looks like the market is going down.',
            'You had better get out quick!',
            'Sell! Sell! Sell!',
            'Shall I lead the recession?',
            "Everybody's getting out, shouldn't you?"]
    throwMdlPath = "phase_5/models/props/newspaper.bam"
    throwSfxPath = None

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 3, 'doMarketCrashAttack',
                            'throw-paper', 0.35, 'marketCrashWeaponSphere', weapon_x = 0.41,
                            weapon_y = -0.06, weapon_z = -0.06, weapon_h = 90, weapon_r = 270, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

class SackedAttack(ThrowAttack):
    notify = directNotify.newCategory("SackedAttack")
    attack = SA_sacked
    attackName = 'Sacked'
    baseDamage = 16.0
    taunts = ["Looks like you're getting sacked.",
            "This one's in the bag.",
            "You've been bagged.",
            'Paper or plastic?',
            'My enemies shall be sacked!',
            'I hold the Toontown record in sacks per game.',
            "You're no longer wanted around here.",
            "Your time is up around here, you're being sacked!",
            'Let me bag that for you.',
            'No defense can match my sack attack!']
    throwMdlPath = "phase_5/models/props/sandbag-mod.bam"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 2, 'doSackedAttack',
                            'throw-paper', 1, 'sackedWeaponSphere', weapon_r = 180, weapon_p = 90,
                            weapon_y = -2.8, weapon_z = -0.3, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

class GlowerPowerAttack(Attack):
    notify = directNotify.newCategory("GlowerPowerAttack")
    attack = SA_glowerpower
    attackName = 'Glower Power'
    knifeScale = 0.4
    baseDamage = 28.0
    length = 2.5
    taunts = ['You looking at me?',
            "I'm told I have very piercing eyes.",
            'I like to stay on the cutting edge.',
            "Jeepers, Creepers, don't you love my peepers?",
            "Here's looking at you kid.",
            "How's this for expressive eyes?",
            'My eyes are my strongest feature.',
            'The eyes have it.',
            'Peeka-boo, I see you.',
            'Look into my eyes...',
            'Shall we take a peek at your future?']

    eyePosPoints = {
        SuitGlobals.TheBigCheese: [Point3(0.6, 4.5, 6), Point3(-0.6, 4.5, 6)],
        SuitGlobals.HeadHunter: [Point3(0.3, 4.3, 5.3), Point3(-0.3, 4.3, 5.3)],
        SuitGlobals.Tightwad: [Point3(0.4, 3.8, 3.7), Point3(-0.4, 3.8, 3.7)]
    }
    
    KnifeMdl = "phase_5/models/props/dagger.bam"
    KnifeSfx = "phase_5/audio/sfx/SA_glower_power.ogg"

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.knifeRoot = None
        self.knives = []
        self.sound = None
        
    @classmethod
    def precache(cls):
        precacheModel(cls.KnifeMdl)
        precacheSound(cls.KnifeSfx)

    def cleanup(self):
        Attack.cleanup(self)
        if self.knives:
            for knife in self.knives:
                knife.removeNode()
            self.knives = None
        if self.knifeRoot:
            self.knifeRoot.removeNode()
            self.knifeRoot = None

    def loadKnife(self):
        k = loader.loadModel(self.KnifeMdl)
        k.setScale(self.knifeScale)
        return k

    def setupKnifeAngle(self):
        if CIGlobals.isNodePathOk(self.target):
            self.knifeRoot.lookAt(self.target.find("**/def_head"))
            
    def announceHit(self, entry = None):
        Attack.announceHit(self, entry)
        if self.collider and not self.collider.isEmpty():
            self.attackBlocked(self.collider.getPos(render))
        if self.knifeRoot and not self.knifeRoot.isEmpty():
            self.knifeRoot.hide()

    def doAttack(self, ts = 0):
        left, right = self.eyePosPoints[self.suit.suitPlan.getName()]
        self.knifeRoot = self.suit.attachNewNode("knifeRoot")
        self.knifeRoot.setPos(0, left.getY(), left.getZ())

        self.sound = base.audio3d.loadSfx(self.KnifeSfx)
        base.audio3d.attachSoundToObject(self.sound, self.suit)
        
        self.collider = self.makeWorldCollider(self.knifeRoot)
        collEvent = self.collider.getCollideEvent()

        collTrack = Sequence(Func(self.startToonLockOn), Wait(1.1), Func(self.stopToonLockOn),
                             Func(self.setupKnifeAngle),
                             Func(self.collider.start),
                             Func(self.acceptOnce, collEvent, self.announceHit),
                             LerpPosInterval(self.collider, 1.0, (0, 50, 0), (0, 0, 0)),
                             Func(self.ignore, collEvent),
                             Func(self.collider.stop))
        
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
    attack = SA_pickpocket
    attackName = 'Pick Pocket'
    length = 3
    baseDamage = 3.0
    taunts = ['Let me check your valuables.',
            "Hey, what's that over there?",
            'Like taking candy from a baby.',
            'What a steal.',
            "I'll hold this for you.",
            'Watch my hands at all times.',
            'The hand is quicker than the eye.',
            "There's nothing up my sleeve.",
            'The management is not responsible for lost items.',
            "Finder's keepers.",
            "You'll never see it coming.",
            'One for me, none for you.',
            "Don't mind if I do.",
            "You won't be needing this..."]

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.dollar = None
        self.pickSfx = None
        
    @classmethod
    def precache(cls):
        precacheModel("phase_5/models/props/1dollar-bill-mod.bam")
        precacheSound("phase_5/audio/sfx/SA_pick_pocket.ogg")

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
            self.announceHit()

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
    attack = SA_fountainpen
    attackName = 'Fountain Pen'
    length = 3
    baseDamage = 8.0
    taunts = ['This is going to leave a stain.',
            "Let's ink this deal.",
            'Be prepared for some permanent damage.',
            "You're going to need a good dry cleaner.",
            'You should change.',
            'This fountain pen has such a nice font.',
            "Here, I'll use my pen.",
            'Can you read my writing?',
            'I call this the plume of doom.',
            "There's a blot on your performance.",
            "Don't you hate when this happens?"]
            
    SplatActorDef = ["phase_3.5/models/props/splat-mod.bam",
            {"chan": "phase_3.5/models/props/splat-chan.bam"}]

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.pen = None
        self.spray = None
        self.splat = None
        self.spraySfx = None
        self.sprayParticle = None
        self.sprayScaleIval = None
        
    @classmethod
    def precache(cls):
        precacheModel("phase_5/models/props/pen.bam")
        precacheModel("phase_3.5/models/props/spray.bam")
        precacheActor(cls.SplatActorDef)
        precacheSound("phase_5/audio/sfx/SA_fountain_pen.ogg")

    def loadAttack(self):
        self.pen = loader.loadModel("phase_5/models/props/pen.bam")
        self.pen.reparentTo(self.suit.find('**/joint_Rhold'))
        self.sprayParticle = ParticleLoader.loadParticleEffect("phase_5/etc/penSpill.ptf")
        self.spray = loader.loadModel("phase_3.5/models/props/spray.bam")
        self.spray.setColor(VBase4(0, 0, 0, 1))
        self.splat = Actor(*self.SplatActorDef)
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
        self.collider = self.makeWorldCollider(self.spray, radius = 0.5)

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
                Wait(1.2),
                Func(self.stopToonLockOn),
                Func(self.attachSpray),
                Func(self.spray.hide),
                Func(self.acceptOnce, self.collider.getCollideEvent(), self.handleSprayCollision),
                Func(self.collider.start),
                Func(self.playWeaponSound),
                Func(self.spray.show),
                Func(self.sprayParticle.start, self.pen.find('**/joint_toSpray'), self.pen.find('**/joint_toSpray')),
                self.sprayScaleIval,
                Wait(0.5),
                Func(self.sprayParticle.cleanup),
                Func(self.spray.setScale, 1),
                Func(self.spray.reparentTo, hidden),
                Func(self.ignore, self.collider.getCollideEvent()),
                Func(self.collider.stop)
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
        self.announceHit(entry)
        self.sprayScaleIval.pause()

    def playWeaponSound(self):
        self.spraySfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_fountain_pen.ogg")
        base.audio3d.attachSoundToObject(self.spraySfx, self.pen)
        base.playSfx(self.spraySfx, node = self.pen)

    def cleanup(self):
        Attack.cleanup(self)
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
    attack = SA_hangup
    attackName = 'Hang Up'
    baseDamage = 13.0
    length = 5
    taunts = ["You've been disconnected.",
            'Good bye!',
            "It's time I end our connection.",
            " ...and don't call back!",
            'Click!',
            'This conversation is over.',
            "I'm severing this link.",
            'I think you have a few hang ups.',
            "It appears you've got a weak link.",
            'Your time is up.',
            'I hope you receive this loud and clear.',
            'You got the wrong number.']

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.phone = None
        self.receiver = None
        self.phoneSfx = None
        self.hangupSfx = None
        self.shootIval = None
        self.cord = None
        self.receiverOutCord = None
        self.phoneOutCord = None
        
    @classmethod
    def precache(cls):
        precacheModel("phase_3.5/models/props/phone.bam")
        precacheModel("phase_3.5/models/props/receiver.bam")
        precacheSound("phase_3.5/audio/sfx/SA_hangup.ogg")
        precacheSound("phase_3.5/audio/sfx/SA_hangup_place_down.ogg")

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
        self.cord.hide(CIGlobals.ShadowCameraBitmask)
        BSPUtility.applyUnlitOverride(self.cord) # fixes crash in bsp levels
        self.phoneSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup.ogg")
        base.audio3d.attachSoundToObject(self.phoneSfx, self.phone)
        self.hangupSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup_place_down.ogg")
        base.audio3d.attachSoundToObject(self.hangupSfx, self.phone)
        self.collider = self.makeWorldCollider(self.phone, radius = 2)

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
                Func(self.acceptOnce, self.collider.getCollideEvent(), self.handleCollision),
                Func(self.collider.start),
                Func(self.shootOut),
                Parallel(
                    SoundInterval(self.hangupSfx, node = self.suit),
                    Sequence(
                        Wait(delayAfterShootToIgnoreCollisions),
                        Func(self.ignore, self.collider.getCollideEvent()),
                        Func(self.collider.stop)
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
        self.announceHit(entry)

    def shootOut(self):
        pathNode = NodePath('path')
        pathNode.reparentTo(self.suit)#.find('**/joint_Lhold'))
        pathNode.setPos(0, 50, self.phone.getZ(self.suit))

        self.collider.reparentTo(render)

        self.shootIval = LerpPosInterval(
            self.collider,
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
        if self.phoneSfx:
            self.phoneSfx.stop()
            self.phoneSfx = None

class RedTapeAttack(ThrowAttack):
    notify = directNotify.newCategory('RedTapeAttack')
    attack = SA_redtape
    attackName = 'Red Tape'
    baseDamage = 10.0
    taunts = ['This should wrap things up.',
             "I'm going to tie you up for awhile.",
             "You're on a roll.",
             'See if you can cut through this.',
             'This will get sticky.',
             "Hope you're claustrophobic.",
             "I'll make sure you stick around.",
             'Let me keep you busy.',
             'Just try to unravel this.',
             'I want this meeting to stick with you.']
    throwMdlPath = "phase_5/models/props/redtape.bam"
    throwSfxPath = "phase_5/audio/sfx/SA_red_tape.ogg"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 1, 'doRedTapeAttack',
                            'throw-paper', 0.5, 'redTapeWeaponSphere', weapon_p = 90,
                            weapon_y = 0.35, weapon_z = -0.5, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx(self.throwSfxPath)
        ThrowAttack.playWeaponSound(self)

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class PowerTieAttack(ThrowAttack):
    notify = directNotify.newCategory('PowerTieAttack')
    attack = SA_powertie
    attackName = 'Power Tie'
    baseDamage = 20.0
    taunts = ["I'll call later, you looked tied up.",
            "Are you ready to tie die?",
            "Ladies and gentlemen, it's a tie!",
            "You had better learn how to tie.",
            "I'll have you tongue-tied!",
            "This is the worst tie you'll ever get!",
            "Can you feel the power?",
            "My powers are far too great for you!",
            "I've got the power!",
            "By the powers vested in me, I'll tie you up."]
            
    throwMdlPath = "phase_5/models/props/power-tie.bam"
    throwSfxPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 4, 'doPowerTieAttack',
                            'throw-paper', 0.2, 'powerTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx(self.throwSfxPath)
        ThrowAttack.playWeaponSound(self)

class HalfWindsorAttack(ThrowAttack):
    notify = directNotify.newCategory('HalfWindsorAttack')
    attack = SA_halfwindsor
    attackName = 'Half Windsor'
    baseDamage = 15.0
    taunts = ["This is the fanciest tie you'll ever see!",
            'Try not to get too winded.',
            "This isn't even half the trouble you're in.",
            "You're lucky I don't have a whole windsor.",
            "You can't afford this tie.",
            "I bet you've never even SEEN a half windsor!",
            'This tie is out of your league.',
            "I shouldn't even waste this tie on you.",
            "You're not even worth half of this tie!"]
    throwMdlPath = "phase_5/models/props/half-windsor.bam"
    throwSfxPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 6, 'doHalfWindsorAttack',
                            'throw-paper', 0.2, 'halfWindsorWeaponSphere', weapon_r = 90, weapon_p = 0,
                            weapon_h = 90, weapon_z = -1, weapon_y = -1.6, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx(self.throwSfxPath)
        ThrowAttack.playWeaponSound(self)

class BiteAttack(ThrowAttack):
    notify = directNotify.newCategory('BiteAttack')
    attack = SA_bite
    attackName = 'Bite'
    baseDamage = 19.0
    taunts = ['Would you like a bite?',
          'Try a bite of this!',
          "You're biting off more than you can chew.",
          'My bite is bigger than my bark.',
          'Bite down on this!',
          'Watch out, I may bite.',
          "I don't just bite when I'm cornered.",
          "I'm just gonna grab a quick bite.",
          "I haven't had a bite all day.",
          'I just want a bite.  Is that too much to ask?']
    throwMdlPath = "phase_5/models/props/teeth-mod.bam"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 6, 'doBiteAttack',
                            'throw-object', 0.2, 'biteWeaponSphere', weapon_r = 180, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)
        if not self.weapon:
            return
        self.weapon.setH(self.weapon, -90)

class ChompAttack(ThrowAttack):
    notify = directNotify.newCategory('ChompAttack')
    attack = SA_chomp
    attackName = 'Chomp'
    baseDamage = 25.0
    taunts = ['Take a look at these chompers!',
           'Chomp, chomp, chomp!',
           "Here's something to chomp on.",
           'Looking for something to chomp on?',
           "Why don't you chomp on this?",
           "I'm going to have you for dinner.",
           'I love to feed on Toons!']
    throwMdlPath = "phase_5/models/props/teeth-mod.bam"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 6, 'doChompAttack',
                            'throw-object', 0.2, 'chompWeaponSphere', weapon_r = 180, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)
        if not self.weapon:
            return
        self.weapon.setH(self.weapon, -90)

class EvictionNoticeAttack(ThrowAttack):
    notify = directNotify.newCategory("EvictionNoticeAttack")
    attack = SA_evictionnotice
    attackName = 'Eviction Notice'
    baseDamage = 8.0
    taunts = ["It's moving time.",
            'Pack your bags, Toon.',
            'Time to make some new living arrangements.',
            'Consider yourself served.',
            "You're behind on your lease.",
            'This will be extremely unsettling.',
            "You're about to be uprooted.",
            "I'm going to send you packing.",
            "You're out of place.",
            'Prepare to be relocated.',
            "You're in a hostel position."]
    throwMdlPath = "phase_3.5/models/props/shredder-paper-mod.bam"

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, self.throwMdlPath, 1, 'doEvictionNoticeAttack',
                            'throw-paper', 1, 'evictionNoticeWeaponSphere', weapon_y = -0.15, weapon_z = -0.5,
                            weapon_x = -1.4, weapon_r = 90, weapon_h = 30, ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)

class RestrainingOrderAttack(EvictionNoticeAttack):
    notify = directNotify.newCategory('RestrainingOrderAttack')
    attack = SA_restrainingorder
    attackName = 'Restraining Order'
    baseDamage = 14.0
    taunts = ['You should show a little restraint.',
            "I'm slapping you with a restraining order!",
            "You can't come within five feet of me.",
            'Perhaps you better keep your distance.',
            'You should be restrained.',
            'Cogs! Restrain that Toon!',
            'Try and restrain yourself.',
            "I hope I'm being too much of a restraint on you.",
            'See if you can lift these restraints!',
            "I'm ordering you to restrain!",
            "Why don't we start with basic restraining?"]

class ParticleAttack(Attack):
    notify = directNotify.newCategory('ParticleAttack')
    attackName = 'Particle Attack'
    particleIvalDur = 1
    shooterDistance = 50
    length = 6.0

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.particles = []
        self.handObj = None
        self.particleSound = None
        self.particleMoveIval = None
        self.targetX = None
        self.targetY = None
        self.targetZ = None

    def handleWeaponTouch(self):
        pass

    def handleCollision(self, entry):
        self.announceHit(entry)

    def doAttack(self, particlePaths, track_name, particleCollId, animation_name,
                delayUntilRelease, animationSpeed = 1, handObjPath = None, handObjParent = None,
                startRightAway = True, ts = 0):
        for path in particlePaths:
            particle = ParticleLoader.loadParticleEffect(path)
            particle.hide(CIGlobals.ShadowCameraBitmask)
            self.particles.append(particle)

        self.collider = self.makeWorldCollider(hidden, radius = 2)
        
        self.startToonLockOn()

        self.targetX = self.attacksClass.target.getX(render)
        self.targetY = self.attacksClass.target.getY(render)
        self.targetZ = self.attacksClass.target.getZ(render)
        if len(self.particles) == 1:
            self.collider.reparentTo(self.particles[0])
        else:
            self.collider.reparentTo(self.suit)
        if handObjPath and handObjParent:
            if isinstance(handObjPath, str):
                self.handObj = loader.loadModel(handObjPath)
            elif isinstance(handObjPath, list):
                mdl = handObjPath[0]
                anims = handObjPath[1]
                self.handObj = Actor(mdl, anims)
            BSPUtility.applyUnlitOverride(self.handObj)
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
                if self.attack == SA_razzledazzle:
                    particle.setP(particle, 90)

            if onlyMoveColl:
                target = self.collider
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

            self.acceptOnce(self.collider.getCollideEvent(), self.handleCollision)
            self.collider.start()

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
        if self.collider is not None:
            self.ignore(self.collider.getCollideEvent())
        Attack.cleanup(self)
        self.targetX = None
        self.targetY = None
        self.targetZ = None
        self.stopParticles()
        if self.handObj:
            self.handObj.removeNode()
            self.handObj = None
        if self.particleMoveIval:
            self.particleMoveIval.pause()
            self.particleMoveIval = None
        self.particleSound = None
        self.particleIvalDur = None

class RazzleDazzleAttack(ParticleAttack):
    notify = directNotify.newCategory('RazzleDazzleAttack')
    attack = SA_razzledazzle
    attackName = 'Razzle Dazzle'
    particleIvalDur = 2.0
    taunts = ['Read my lips.',
            'How about these choppers?',
            "Aren't I charming?",
            "I'm going to wow you.",
            'My dentist does excellent work.',
            "Blinding aren't they?",
            "Hard to believe these aren't real.",
            "Shocking, aren't they?",
            "I'm going to cap this off.",
            'I floss after every meal.',
            'Say Cheese!']

    baseDamage = 7.0 # Doesn't do much damage, but blinds you.
    length = 3.5

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
    attack = SA_buzzword
    attackName = 'Buzz Word'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 50.0
    baseDamage = 12.0
    taunts = ['Pardon me if I drone on.',
              'Have you heard the latest?',
              'Can you catch on to this?',
              'See if you can hum this Toon.',
              'Let me put in a good word for you.',
              'I\'ll "B" perfectly clear.',
              'You should "B" more careful.',
              'See if you can dodge this swarm.',
              "Careful, you're about to get stung.",
              'Looks like you have a bad case of hives.']

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
    attack = SA_jargon
    attackName = 'Jargon'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 50.0
    baseDamage = 11.0
    taunts = ['What nonsense.',
            'See if you can make sense of this.',
            'I hope you get this loud and clear.',
            "Looks like I'm going to have to raise my voice.",
            'I insist on having my say.',
            "I'm very outspoken.",
            'I must pontificate on this subject.',
            'See, words can hurt you.',
            'Did you catch my meaning?',
            'Words, words, words, words, words.']

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
    attack = SA_mumbojumbo
    attackName = 'Mumbo Jumbo'
    particleIvalDur = 2.5
    afterIvalDur = 1.5
    shooterDistance = 50.0
    baseDamage = 15.0
    taunts = ['Let me make this perfectly clear.',
            "It's as simple as this.",
            "This is how we're going to do this.",
            'Let me supersize this for you.',
            'You might call this technobabble.',
            'Here are my five-dollar words.',
            'Boy, this is a mouth full.',
            'Some call me bombastic.',
            'Let me just interject this.',
            'I believe these are the right words.']

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
    attack = SA_filibuster
    attackName = 'Filibuster'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 40.0
    baseDamage = 14.0
    taunts = ["Shall I fill 'er up?",
            'This is going to take awhile.',
            'I could do this all day.',
            "I don't even need to take a breath.",
            'I keep going and going and going.',
            'I never get tired of this one.',
            'I can talk a blue streak.',
            'Mind if I bend your ear?',
            "I think I'll shoot the breeze.",
            'I can always get a word in edgewise.']

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
    attack = SA_doubletalk
    attackName = 'Double Talk'
    particleIvalDur = 3.0
    afterIvalDur = 1.5
    shooterDistance = 50.0
    baseDamage = 4.0

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
    attack = SA_schmooze
    attackName = 'Schmooze'
    particleIvalDur = 1.5
    afterIvalDur = 1.5
    shooterDistance = 40.0
    baseDamage = 17.0
    taunts = ["You'll never see this coming.",
              'This will look good on you.',
              "You've earned this.",
              "I don't mean to gush.",
              'Flattery will get me everywhere.',
              "I'm going to pile it on now.",
              'Time to lay it on thick.',
              "I'm going to get on your good side.",
              'That deserves a good slap on the back.',
              "I'm going to ring your praises.",
              'I hate to knock you off your pedestal, but...']

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
    attack = SA_fingerwag
    attackName = 'Finger Wag'
    particleIvalDur = 2
    afterIvalDur = 1.5
    shooterDistance = 35.0
    baseDamage = 6.5
    taunts = ['I have told you a thousand times.',
            'Now see here Toon.',
            "Don't make me laugh.",
            "Don't make me come over there.",
            "I'm tired of repeating myself.",
            "I believe we've been over this.",
            'You have no respect for us Cogs.',
            "I think it's time you pay attention.",
            'Blah, Blah, Blah, Blah, Blah.',
            "Don't make me stop this meeting.",
            'Am I going to have to separate you?',
            "We've been through this before."]

    def doAttack(self, ts):
        ParticleAttack.doAttack(
            self, ['phase_5/etc/fingerwag.ptf'], 'doFW', 'FWSphere',
            'fingerwag', 1.5, 1.5, None, None, False, ts
        )
        setEffectTexture(self.particles[0], 'blah', Vec4(0.55, 0, 0.55, 1))
        for particle in self.particles:
            particle.setZ(self.suit.find('**/joint_head').getZ(render))
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
    attack = SA_evileye
    attackName = 'Evil Eye'
    baseDamage = 21.0
    length = 7
    taunts = ["I'm giving you the evil eye.",
            "Could you eye-ball this for me?",
            "Wait. I've got something in my eye.",
            "I've got my eye on you!",
            "Could you keep an eye on this for me?",
            "I've got a real eye for evil.",
            "I'll poke you in the eye!",
            "\"Eye\" am as evil as they come!",
            "I'll put you in the eye of the storm!",
            "I'm rolling my eye at you."]

    posPoints = {
        SuitGlobals.CorporateRaider: [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)],
        SuitGlobals.TwoFace: [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)],
        SuitGlobals.LegalEagle: [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    }

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.eyeRoot = None
        self.eye = None
        self.sound = None
        
    @classmethod
    def precache(cls):
        precacheModel("phase_5/models/props/evil-eye.bam")
        precacheSound("phase_5/audio/sfx/SA_evil_eye.ogg")

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
        self.eye.setScale(0.01)

        self.sound = base.audio3d.loadSfx("phase_5/audio/sfx/SA_evil_eye.ogg")
        base.audio3d.attachSoundToObject(self.sound, self.eye)

        suitHoldStart = 1.06
        suitHoldStop = 1.69
        suitHoldDuration = suitHoldStop - suitHoldStart
        eyeHoldDuration = 1.1
        moveDuration = 1.0
        eyeScale = 11.0

        self.collider = self.makeWorldCollider(self.eye, 1.0 / eyeScale)

        self.suitTrack = Parallel(
            Sequence(Wait(1.3), SoundInterval(self.sound, node = self.eye)),
            Sequence(ActorInterval(self.suit, 'glower', endTime = suitHoldStart), Wait(suitHoldDuration), ActorInterval(self.suit, 'glower', startTime = suitHoldStart)),
            Sequence(Func(self.startToonLockOn), Wait(suitHoldStart), LerpScaleInterval(self.eye, suitHoldDuration, Point3(eyeScale)),
                     Wait(eyeHoldDuration * 0.3), LerpHprInterval(self.eye, 0.02, Point3(205, 40, 0)),
                     Wait(eyeHoldDuration * 0.7), Func(self.setupEyeAngle), Func(self.stopToonLockOn),
                     Func(self.eyeRoot.wrtReparentTo, render),
                     Func(self.acceptOnce, self.collider.getCollideEvent(), self.__handleEyeCollision),
                     Func(self.collider.start),
                     Parallel(LerpPosInterval(self.eye, moveDuration, (0, 65.0, 0), startPos = (0, 0, 0)),
                              LerpHprInterval(self.eye, moveDuration, Point3(0, 0, -180), other = self.eye)),
                     Func(self.ignore, self.collider.getCollideEvent()),
                     Func(self.collider.stop))
        )
        self.startSuitTrack(ts)

    def __handleEyeCollision(self, entry):
        self.announceHit(entry)
        if self.eye and not self.eye.isEmpty():
            self.eye.hide()

    def setupEyeAngle(self):
        self.eye.setHpr(205, 0, 0)
        self.eyeRoot.lookAt(self.target.find("**/def_head"))

    def cleanup(self):
        Attack.cleanup(self)
        if self.eye:
            self.eye.removeNode()
            self.eye = None
        if self.eyeRoot:
            self.eyeRoot.removeNode()
            self.eyeRoot = None

class DemotionAttack(Attack):
    attack = SA_demotion
    attackName = 'Demotion'

class TeeOffAttack(Attack):
    attack = SA_teeoff
    attackName = 'Tee Off'
    length = 7
    baseDamage = 19.0
    taunts = ["You're not up to par.",
            "Fore!",
            "I'm getting teed off.",
            "Caddie, I'll need my driver!",
            "Just try and avoid this hazard.",
            "Swing!",
            "This is a sure hole in one.",
            "You're in my fairway.",
            "Notice my grip.",
            "Watch the birdie!",
            "Keep your eye on the ball!",
            "Mind if I play through?"]

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
        self.ballVisRope = None
        
    @classmethod
    def precache(cls):
        precacheModel("phase_5/models/props/golf-ball.bam")
        precacheSound("phase_5/audio/sfx/SA_tee_off.ogg")

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

        self.collider = self.makeWorldCollider(self.ball, 1.0 / ballScale)

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
                     Func(self.acceptOnce, self.collider.getCollideEvent(), self.__handleGolfBallCollision),
                     Func(self.collider.start),
                     LerpPosInterval(self.ball, duration = 1.0, pos = (0, 85, 0), startPos = (0, 0, 0)),
                     Func(self.ball.hide),
                     Func(self.collider.stop),
                     Func(self.ignore, self.collider.getCollideEvent())), name = self.suit.uniqueName('golfBallSuitTrack'))
        self.startSuitTrack(ts)

    def setupBallAngle(self):
        self.ballRoot.lookAt(self.target.find("**/def_head"))
        
    def __handleGolfBallCollision(self, entry):
        self.announceHit(entry)
        if self.ball and not self.ball.isEmpty():
            self.attackBlocked(self.ball.getPos(render))
            self.ball.hide()
    
    def cleanup(self):
        Attack.cleanup(self)
        if self.visualizeBallPath and self.ballVisRope:
            self.ballVisRope.removeNode()
            self.ballVisRope = None
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
    attack = SA_watercooler
    attackName = 'Watercooler'
    length = 7
    baseDamage = 4.0
    taunts = ['This ought to cool you off.',
            "Isn't this refreshing?",
            "I deliver.",
            "Straight from the tap - into your lap.",
            "What's the matter, it's just spring water.",
            "Don't worry, it's purified.",
            "Ah, another satisfied customer.",
            "It's time for your daily delivery.",
            "Hope your colors don't run.",
            "Care for a drink?",
            "It all comes out in the wash.",
            "The drink's on you."]
            
    SprayAppearSfx = "phase_5/audio/sfx/SA_watercooler_appear_only.ogg"
    SpraySfx = "phase_5/audio/sfx/SA_watercooler_spray_only.ogg"
    CoolerMdl = "phase_5/models/props/watercooler.bam"
    SprayMdl = "phase_3.5/models/props/spray.bam"

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.cooler = None
        self.spray = None
        self.splash = None
        self.soundAppear = None
        self.soundSpray = None
        
    @classmethod
    def precache(cls):
        precacheSound(cls.SprayAppearSfx)
        precacheSound(cls.SpraySfx)
        precacheModel(cls.CoolerMdl)
        precacheModel(cls.SprayMdl)

    def doAttack(self, ts):
        Attack.doAttack(self, ts)

        def getCoolerSpout():
            spout = self.cooler.find("**/joint_toSpray")
            return spout.getPos(render)

        self.soundAppear = base.audio3d.loadSfx(self.SprayAppearSfx)
        base.audio3d.attachSoundToObject(self.soundAppear, self.suit)
        self.soundSpray = base.audio3d.loadSfx(self.SpraySfx)
        base.audio3d.attachSoundToObject(self.soundSpray, self.suit)

        self.cooler = loader.loadModel(self.CoolerMdl)
        self.cooler.reparentTo(self.suit.find("**/joint_Lhold"))
        self.cooler.setPosHpr(0.48, 0.11, -0.92, 20.403, 33.158, 69.511)
        self.cooler.hide()

        self.spray = loader.loadModel(self.SprayMdl)
        self.spray.setTransparency(True)
        self.spray.setColor(0.75, 0.75, 1.0, 0.8)
        self.spray.setScale(0.3, 1.0, 0.3)
        self.spray.reparentTo(render)
        self.spray.hide()

        self.collider = self.makeWorldCollider(self.spray)
        self.collider.setY(1.0)

        self.splash = loadSplat((0.75, 0.75, 1.0, 0.8))
        self.splash.setTransparency(True)
        self.splash.setScale(0.3)
        self.splash.setBillboardPointWorld()

        self.suitTrack = Parallel(
            ActorInterval(self.suit, 'watercooler'),
            Sequence(Func(self.startToonLockOn), Wait(1.01), Func(self.cooler.show), LerpScaleInterval(self.cooler, 0.5, Point3(1.15, 1.15, 1.15)),
                     Wait(1.6), Func(self.stopToonLockOn), Func(self.positionSpray), Func(self.setupSprayAngle), Func(self.spray.show),
                     Func(self.acceptOnce, self.collider.getCollideEvent(), self.announceHit), Func(self.collider.start),
                     LerpScaleInterval(self.spray, duration = 0.3, scale = (1, 20, 1), startScale = (1, 1, 1)),
                     Func(self.spray.hide), Func(self.collider.stop), Func(self.ignore, self.collider.getCollideEvent())),
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
        if self.spray:
            self.spray.removeNode()
            self.spray = None
        if self.cooler:
            self.cooler.removeNode()
            self.cooler = None

class WriteOffAttack(Attack):
    attack = SA_writeoff
    attackName = "Write Off"
    length = 6.3
    baseDamage = 10.0
    taunts = ["Let me increase your losses.",
              "Let's make the best of a bad deal.",
              "Time to balance the books.",
              "This won't look good on your books.",
              "I'm looking for some dividends.",
              "You must account for your losses.",
              "You can forget about a bonus.",
              "I'll shuffle your accounts around.",
              "You're about to suffer some losses.",
              "This is going to hurt your bottom line."]
              
    PadMdl = "phase_5/models/props/pad.bam"
    PencilMdl = "phase_5/models/props/pencil.bam"
    PenSfx = "phase_5/audio/sfx/SA_writeoff_pen_only.ogg"
    DingSfx = "phase_5/audio/sfx/SA_writeoff_ding_only.ogg"

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.check = None
        
    @classmethod
    def precache(cls):
        precacheModel(cls.PadMdl)
        precacheModel(cls.PencilMdl)
        precacheSound(cls.PenSfx)
        precacheSound(cls.DingSfx)

    def cleanup(self):
        Attack.cleanup(self)
        if self.check:
            self.check.removeNode()
        self.check = None

    def handleCheckCollision(self, entry):
        if PhysicsUtils.isLocalAvatar(entry):
            self.announceHit()
        else:
            self.attackBlocked(self.check.getPos(render))

        if CIGlobals.isNodePathOk(self.check):
            self.check.hide()

        self.stopThrowTrack()

    def fireCheck(self, pencil):
        self.check = render.attachNewNode('checkmark')
        check = Attack.getSuitParticle("checkmark").copyTo(self.check)
        check.setBillboardPointEye()
        check.setScale(1.6)
        self.check.setPosHpr(pencil, 0, 0, 0, 0, 0, 0)
        self.check.setP(0)
        self.check.setR(0)

        self.collider = self.makeWorldCollider(self.check, 0.7)
        self.acceptOnce(self.collider.getCollideEvent(), self.handleCheckCollision)
        self.collider.start()

        self.startThrowTrack(self.check, 65.0, 50.0)

    def doAttack(self, ts):
        Attack.doAttack(self, ts)

        pad = loader.loadModel(self.PadMdl)
        padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
        padPropTrack = self.getPropTrack(pad, self.suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))

        pencil = loader.loadModel(self.PencilMdl)
        pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
        extraArgsForShowProp = [pencil, self.suit.getRightHand()]
        extraArgsForShowProp.extend(pencilPosPoints)

        suitTrack = ActorInterval(self.suit, 'hold-pencil')

        pencilPropTrack = Sequence(Func(self.startToonLockOn), Wait(0.5), Func(self.showProp, *extraArgsForShowProp),
                                   LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5),
                                                     startScale=Point3(0.01)),
                                   Wait(2), Func(self.stopToonLockOn), Func(self.fireCheck, pencil))
        pencilPropTrack.append(Wait(0.3))
        pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, Point3(0.01)))
        pencilPropTrack.append(Func(self.removeProp, pencil))

        penSfx = base.audio3d.loadSfx(self.PenSfx)
        base.audio3d.attachSoundToObject(penSfx, pad)
        dingSfx = base.audio3d.loadSfx(self.DingSfx)
        base.audio3d.attachSoundToObject(dingSfx, pad)

        soundTrack = Sequence(Wait(2.3), SoundInterval(penSfx, duration=0.9), SoundInterval(dingSfx))

        self.suitTrack = Parallel(suitTrack, pencilPropTrack, padPropTrack, soundTrack)
        self.startSuitTrack(ts)

class RubberStampAttack(Attack):
    attack = SA_rubberstamp
    attackName = 'Rubber Stamp'
    baseDamage = 8.5
    length = 5.0
    taunts = ["I always make a good impression.",
              "It's important to apply firm and even pressure.",
              "A perfect imprint every time.",
              "I want to stamp you out.",
              "You must be RETURNED TO SENDER.",
              "You've been CANCELLED.",
              "You have a PRIORITY delivery.",
              "I'll make sure you RECEIVED my message.",
              "You're not going anyways - you have POSTAGE DUE.",
              "I'll need a response ASAP."]
              
    StampMdl = "phase_5/models/props/rubber-stamp.bam"
    PadMdl = "phase_5/models/props/pad.bam"
    StampSfx = "phase_5/audio/sfx/SA_rubber_stamp.ogg"

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.cancelled = None
        
    @classmethod
    def precache(cls):
        precacheModel(cls.StampMdl)
        precacheModel(cls.PadMdl)
        precacheSound(cls.StampSfx)

    def cleanup(self):
        Attack.cleanup(self)
        if self.cancelled:
            self.cancelled.removeNode()
        self.cancelled = None

    def __makeCancelledNodePath(self):
        tn = TextNode('CANCELLED')
        tn.setFont(CIGlobals.getSuitFont())
        tn.setText('CANCELLED\nCANCELLED\nCANCELLED')
        tn.setAlign(TextNode.ACenter)
        tntop = hidden.attachNewNode('CancelledTop')
        tnpath = tntop.attachNewNode(tn.generate())
        tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
        tnpath.setScale(1)
        tnpath.setColor(0.7, 0, 0, 1)
        tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
        tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
        tnpath.setScale(1)
        return tntop

    def handleTextCollision(self, entry):
        if PhysicsUtils.isLocalAvatar(entry):
            self.announceHit()
        else:
            self.attackBlocked(self.cancelled.getPos(render))

        if CIGlobals.isNodePathOk(self.cancelled):
            self.cancelled.hide()

        self.stopThrowTrack()

    def fireStamp(self, stamp):
        self.cancelled = render.attachNewNode('cancelled')
        text = self.__makeCancelledNodePath()
        text.reparentTo(self.cancelled)
        text.setScale(0.6)
        self.cancelled.setPosHpr(stamp, 0.81, -1.11, -0.16, 0, 0, 90)
        self.cancelled.setP(0)
        self.cancelled.setR(0)

        self.collider = self.makeWorldCollider(self.cancelled, 0.8)
        self.acceptOnce(self.collider.getCollideEvent(), self.handleTextCollision)
        self.collider.start()

        self.startThrowTrack(self.cancelled, 65.0, 50)

    def doAttack(self, ts):
        Attack.doAttack(self, ts)

        stamp = loader.loadModel(self.StampMdl)
        pad = loader.loadModel(self.PadMdl)
        suitType = self.suit.suitPlan.getSuitType()
        if suitType == SuitType.A:
            padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
            stampPosPoints = [Point3(-0.64, -0.17, -0.03), Point3(0)]
        elif suitType == SuitType.C:
            padPosPoints = [Point3(0.19, -0.55, -0.21), VBase3(-166.76, -4.001, -1.658)]
            stampPosPoints = [Point3(-0.64, -0.08, 0.11), Point3(0)]
        else:
            padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
            stampPosPoints = [Point3(-0.64, -0.17, -0.03), Point3(0)]

        suitTrack = ActorInterval(self.suit, 'rubber-stamp')
        padPropTrack = self.getPropTrack(pad, self.suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
        propTrack = Sequence(Func(self.startToonLockOn), Func(self.showProp, stamp, self.suit.getRightHand(),
                                                              stampPosPoints[0], stampPosPoints[1]),
                             LerpScaleInterval(stamp, 0.5, Point3(1)), Wait(2.6),
                             Func(self.stopToonLockOn), Func(self.fireStamp, stamp))
        propTrack.append(Wait(0.3))
        propTrack.append(LerpScaleInterval(stamp, 0.5, Point3(0.01)))
        propTrack.append(Func(self.removeProp, stamp))

        snd = base.loadSfxOnNode(self.StampSfx, stamp)
        soundTrack = Sequence(Wait(1.3), SoundInterval(snd, duration = 1.1))

        self.suitTrack = Parallel(soundTrack, suitTrack, padPropTrack, propTrack)
        self.startSuitTrack(ts)

class FiredAttack(Attack):
    attack = SA_fired
    attackName = 'Fired'
    baseDamage = 2.0 # damage base per flame that hits
    length = 7.0
    taunts = ["I hope you brought some marshmallows.",
              "It's going to get rather warm around here.",
              "This should take the chill out of the air.",
              "I hope you're cold blooded.",
              "Hot, hot and hotter.",
              "You better stop, drop, and roll!",
              "You're outta here.",
              "How does \"well-done\" sound?",
              "Can you say ouch?",
              "Hope you wore sunscreen.",
              "Do you feel a little toasty?",
              "You're going down in flames.",
              "You'll go out in a blaze.",
              "You're a flash in the pan.",
              "I think I have a bit of a flare about me.",
              "I just sparkle, don't I?",
              "Oh look, a crispy critter.",
              "You shouldn't run around half baked."]
    emitFlameIval = 0.3
    maxFlames = 10
    
    GlowMdl = "phase_14/models/props/lightglow.egg"
    FlameHitSfx = "phase_14/audio/sfx/SA_hot_air_flame_hit.ogg"
    FlameEmitSfx = "phase_14/audio/sfx/SA_hot_air_flame_emit.ogg"
    
    @classmethod
    def precache(cls):
        precacheModel(cls.GlowMdl)
        precacheSound(cls.FlameHitSfx)
        precacheSound(cls.FlameEmitSfx)

    class Flame(NodePath, DirectObject):
        flameSpeed = 30.0

        def __init__(self, attack):
            DirectObject.__init__(self)
            NodePath.__init__(self, 'flame')

            self.setLightOff(1)
            self.setMaterialOff(1)
            BSPUtility.applyUnlitOverride(self)
            
            self.attack = attack
            self.suit = self.attack.suit

            fireroot = self.attachNewNode('fireroot')
            fireroot.setScale(1.25)
            fireroot.setBillboardAxis()
            glow = loader.loadModel(FiredAttack.GlowMdl)
            glow.reparentTo(fireroot)
            glow.setTransparency(1)
            glow.setColorScale(1, 0.5, 0, 0.5)
            glow.setY(-0.01)
            glow.setTwoSided(1)
            glow.setScale(0.85)
            fire = Attack.getSuitParticle("fire").copyTo(fireroot)

            self.reparentTo(render)

            startPos = self.attack.suit.find("**/joint_head").getPos(render)
            endPos = self.attack.target.getPart("head").getPos(render)
            distance = (endPos - startPos).length()
            duration = distance / self.flameSpeed

            self.setPos(startPos)

            self.collider = self.attack.makeWorldCollider(self, 0.75)
            self.acceptOnce(self.collider.getCollideEvent(), self.handleCollision)

            self.ival = Parallel(Sequence(ProjectileInterval(self, startPos, endPos, duration, gravityMult = 0.7),
                                          Func(self.removeNode)),
                                 Sequence(Wait(0.01), Func(self.collider.start)),
                                 LerpScaleInterval(fireroot, 0.2, Point3(1.25), Point3(0.01)))
            self.ival.start()

        def handleCollision(self, entry):
            if not self.isEmpty():
                CIGlobals.makeDustCloud(self.getPos(render), scale = (0.25, 0.9, 1),
                                        sound = base.audio3d.loadSfx(FiredAttack.FlameHitSfx),
                                        color = (0.2, 0.2, 0.2, 0.6))

            if PhysicsUtils.isLocalAvatar(entry):
                if CIGlobals.isNodePathOk(self.suit):
                    self.suit.sendUpdate('toonHitByWeapon', [self.attack.attack, base.localAvatar.doId,
                                                             base.localAvatar.getDistance(self.suit)])
                base.localAvatar.handleSuitAttack(self.attack.attack)

            self.removeNode()

        def removeNode(self):
            if self.ival:
                self.ival.pause()
            self.ival = None
            if self.collider:
                self.ignore(self.collider.getCollideEvent())
                self.collider.removeNode()
            self.collider = None
            self.attack = None
            self.suit = None
            if not self.isEmpty():
                NodePath.removeNode(self)

    def __init__(self, ac, suit):
        Attack.__init__(self, ac, suit)
        self.emitSfx = None
        self.emitTask = None
        self.glow = None
        self.glowTrack = None

    def cleanup(self):
        Attack.cleanup(self)
        self.stopEmitting()
        if self.glowTrack:
            self.glowTrack.finish()
        self.glowTrack = None
        if self.glow:
            self.glow.removeNode()
        self.glow = None
        self.emitSfx = None

    def startEmitting(self):
        self.stopEmitting()

        self.emitTask = taskMgr.add(self.__emitTask, "FiredEmitTask")

    def __emitTask(self, task):
        self.emitSfx.play()
        self.glowTrack.start()

        # Just make it and forget it, the flame will clean itself up
        FiredAttack.Flame(self)

        task.delayTime = self.emitFlameIval
        return task.again

    def stopEmitting(self):
        if self.emitTask:
            self.emitTask.remove()
        self.emitTask = None

    def doAttack(self, ts):
        self.glow = loader.loadModel(FiredAttack.GlowMdl)
        self.glow.reparentTo(self.suit)
        self.glow.setLightOff(1)
        self.glow.setMaterialOff(1)
        BSPUtility.applyUnlitOverride(self.glow)
        self.glow.setP(90)
        self.glow.setTransparency(1)
        self.glow.setDepthOffset(1)
        self.glow.setColorScale(1, 0.5, 0, 0)
        self.glow.setScale(3)

        self.glowTrack = Sequence(LerpColorScaleInterval(self.glow, self.emitFlameIval / 2, (1, 0.5, 0, 0.5),
                                                         (1, 0.5, 0, 0), blendType = 'easeInOut'),
                                  LerpColorScaleInterval(self.glow, self.emitFlameIval / 2, (1, 0.5, 0, 0),
                                                         (1, 0.5, 0, 0.5), blendType = 'easeInOut'))

        self.emitSfx = base.loadSfxOnNode(FiredAttack.FlameEmitSfx, self.suit)
        self.suitTrack = Sequence(Func(self.startToonLockOn),
                                  ActorInterval(self.suit, 'magic2', endFrame = 32),
                                  Func(self.startEmitting),
                                  Func(self.suit.pingpong, 'magic2', 1, None, 32, 50),
                                  Wait(self.emitFlameIval * self.maxFlames),
                                  Func(self.stopEmitting),
                                  Func(self.stopToonLockOn),
                                  ActorInterval(self.suit, 'magic2', startFrame = 50))
        self.startSuitTrack(ts)

class HotAirAttack(FiredAttack):
    attack = SA_hotair
    attackName = 'Hot Air'
    baseDamage = 1.0
    taunts = ["We're having a heated discussion.",
              "You're experiencing a heat wave.",
              "I've reached my boiling point.",
              "This should cause some wind burn.",
              "I hate to grill you, but...",
              "Always remember, where there's smoke, there's fire.",
              "You're looking a little burned out.",
              "Another meeting up in smoke.",
              "Guess it's time to add fuel to the fire.",
              "Let me kindle a working relationship.",
              "I have some glowing remarks for you.",
              "Air Raid!!!"]

from direct.fsm.StateData import StateData

class SuitAttacks(StateData):
    notify = directNotify.newCategory("SuitAttacks")

    attack2attackClass = {
        SA_canned:              CannedAttack,
        SA_clipontie:           ClipOnTieAttack,
        SA_sacked:              SackedAttack,
        SA_glowerpower:         GlowerPowerAttack,
        SA_hardball:            HardballAttack,
        SA_marketcrash:         MarketCrashAttack,
        SA_pickpocket:          PickPocketAttack,
        SA_hangup:              HangUpAttack,
        SA_fountainpen:         FountainPenAttack,
        SA_redtape:             RedTapeAttack,
        SA_powertie:            PowerTieAttack,
        SA_halfwindsor:         HalfWindsorAttack,
        SA_bite:                BiteAttack,
        SA_chomp:               ChompAttack,
        SA_evictionnotice:      EvictionNoticeAttack,
        SA_restrainingorder:    RestrainingOrderAttack,
        SA_razzledazzle:        RazzleDazzleAttack,
        SA_buzzword:            BuzzWordAttack,
        SA_jargon:              JargonAttack,
        SA_mumbojumbo:          MumboJumboAttack,
        SA_filibuster:          FilibusterAttack,
        SA_doubletalk:          DoubleTalkAttack,
        SA_schmooze:            SchmoozeAttack,
        SA_fingerwag:           FingerWagAttack,
        #SA_demotion:           DemotionAttack,
        SA_evileye:             EvilEyeAttack,
        SA_teeoff:              TeeOffAttack,
        SA_watercooler:         WatercoolerAttack,
        SA_writeoff:            WriteOffAttack,
        SA_rubberstamp:         RubberStampAttack,
        SA_fired:               FiredAttack,
        SA_hotair:              HotAirAttack
    }

    def __init__(self, doneEvent, suit, target):
        StateData.__init__(self, doneEvent)
        self.suit = suit
        self.target = target
        self.currentAttack = None
        
    @staticmethod
    def precache():
        for cls in SuitAttacks.attack2attackClass.values():
            cls.precache()

    def load(self, attackId):
        StateData.load(self)
        className = self.attack2attackClass[attackId]
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
