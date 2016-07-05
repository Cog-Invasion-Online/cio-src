########################################
# Filename: SuitAttacks.py
# Created by: blach (04Apr15)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, SoundInterval
from direct.interval.IntervalGlobal import ActorInterval, Parallel, LerpScaleInterval
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.showbase.DirectObject import DirectObject
from direct.distributed import DelayDelete
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerEvent, NodePath, Vec3, VBase4, Point3, BitMask32, Vec4
from lib.coginvasion.toon import ParticleLoader
from direct.actor.Actor import Actor
from lib.coginvasion.globals import CIGlobals
from direct.showutil.Rope import Rope
from direct.task import Task

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
                    #'razzledazzle': 3,
                    'buzzword': 6,
                    'jargon': 6,
                    'mumbojumbo': 6,
                    'filibuster': 6,
                    'doubletalk': 6,
                    'schmooze': 6,
                    'fingerwag': 6
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
                'powertie': 13,
                'halfwindsor': 13,
                "bite": 7,
                "chomp": 5.5,
                'evictionnotice': 9,
                'restrainingorder': 8,
                #'razzledazzle': 9,
                'buzzword': 10,
                'jargon': 9,
                'mumbojumbo': 9.5,
                'filibuster': 9.5,
                'doubletalk': 10,
                'schmooze': 8,
                'fingerwag': 8
                }
    
THROW_ATTACK_IVAL_TIME = 0.75
GLOWER_POWER_IVAL_TIME = 0.5

def setEffectTexture(effect, texture, color):
    particles = effect.getParticlesNamed('particles-1')
    sparticles = loader.loadModel('phase_3.5/models/props/suit-particles.bam')
    np = sparticles.find('**/' + texture)
    particles.renderer.setColor(color)
    particles.renderer.setFromNode(np)

class Attack(DirectObject):
    notify = directNotify.newCategory("Attack")
    attack = 'attack'

    def __init__(self, attacksClass, suit):
        self.attacksClass = attacksClass
        self.suit = suit
        self.suitTrack = None
        self.attackName2attackId = {}
        for index in range(len(self.attacksClass.attackName2attackClass.keys())):
            self.attackName2attackId[SuitAttackLengths.keys()[index]] = index

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
        self.attacksClass = None
        self.attackName2attackId = None

class ThrowAttack(Attack):
    notify = directNotify.newCategory("ThrowAttack")
    attack = 'throw'

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.weapon_state = None
        self.weapon = None
        self.wss = None
        self.wsnp = None
        self.suitTrack = None
        self.weaponSfx = None
        self.throwTrajectory = None
        self.targetX = None
        self.targetY = None
        self.targetZ = None
        self.startNP = None
        self.theActorIval = None

    def handleWeaponCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)
            self.suit.b_handleWeaponTouch()

    def doAttack(self, weapon_path, weapon_scale, track_name,
                animation_name, collsphere_radius, weapon_coll_id,
                weapon_h = 0, weapon_p = 0, weapon_r = 0, weapon_x = 0,
                weapon_y = 0, weapon_z = 0, ts = 0):
        self.weapon_state = 'start'
        if hasattr(self.suit, 'uniqueName'):
            track_name = self.suit.uniqueName(track_name)
            weapon_coll_id = self.suit.uniqueName(weapon_coll_id)
        self.weapon = loader.loadModel(weapon_path)
        self.weapon.setScale(weapon_scale)
        self.weapon.setHpr(weapon_h, weapon_p, weapon_r)
        self.weapon.setPos(weapon_x, weapon_y, weapon_z)
        self.wss = CollisionSphere(0, 0, 0, collsphere_radius)
        self.wss.setTangible(0)

        self.targetX = self.attacksClass.target.getX(render)
        self.targetY = self.attacksClass.target.getY(render)
        self.targetZ = self.attacksClass.target.getZ(render)

        if not self.attack in ['glowerpower']:
            actorIval = ActorInterval(self.suit, animation_name, playRate = 3.0, duration = 0.7)
            actorIval2 = ActorInterval(self.suit, animation_name, playRate = 2.0, startTime = 1.0)
        else:
            actorIval = ActorInterval(self.suit, animation_name)

        seq = Sequence()

        if not self.attack in ['glowerpower']:
            self.suitTrack = Parallel(Sequence(actorIval, actorIval2), name = track_name)
            self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
            waitTime = 0.9
            if self.suit.suitPlan.getSuitType() == "C":
                waitTime -= 0.05
            seq.append(Wait(waitTime))
            if self.suit.suitPlan.getSuitType() != "C":
                seq.append(Wait(0.3))
            seq.append(Func(self.throwObject))
            seq.append(Wait(1.0))
            seq.append(Func(self.delWeapon))
        else:
            self.suitTrack = Parallel(actorIval, name = track_name)
            seq.append(Wait(1))
            seq.append(Func(self.throwObject))
            seq.append(Wait(0.5))
            seq.append(Func(self.delWeapon))
        self.suitTrack.append(seq)

        wsnode = CollisionNode(weapon_coll_id)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WeaponBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, track_name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        if self.weapon and self.weaponSfx:
            base.audio3d.attachSoundToObject(self.weaponSfx, self.suit)
            base.playSfx(self.weaponSfx, node = self.suit)

    def throwObject(self, projectile = True):
        if not self.weapon:
            return

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
        startNP.lookAt(render, self.targetX, self.targetY, self.targetZ)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(startNP)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)

        if self.attack in ['clipontie', 'powertie', 'halfwindsor']:
            self.weapon.setHpr(pathNP.getHpr(render))

        if projectile == True:
            self.throwTrajectory = ProjectileInterval(
                self.weapon,
                startPos = self.suit.find('**/joint_Rhold').getPos(render),
                endPos = pathNP.getPos(render),
                gravityMult = 0.7,
                duration = THROW_ATTACK_IVAL_TIME
            )
        else:
            self.weapon.setH(pathNP.getH(render))
            self.throwTrajectory = LerpPosInterval(
                self.weapon,
                duration = GLOWER_POWER_IVAL_TIME,
                pos = pathNP.getPos(render) + (0, 0, 2),
                startPos = startNP.getPos(render) + (0, 3, 0)
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
                self.delWeapon()

    def handleWeaponTouch(self):
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delWeapon()

    def delWeapon(self):
        if self.weapon:
            self.weapon.removeNode()
            self.weapon = None

    def cleanup(self):
        Attack.cleanup(self)
        self.targetX = None
        self.targetY = None
        self.targetZ = None
        self.weapon_state = None
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delWeapon()
        self.wss = None
        if self.wsnp:
            self.wsnp.node().clearSolids()
            self.wsnp.removeNode()
            self.wsnp = None

class CannedAttack(ThrowAttack):
    notify = directNotify.newCategory("CannedAttack")
    attack = 'canned'

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

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_3.5/models/props/clip-on-tie-mod.bam", 1, 'doClipOnTieAttack',
                            'throw-paper', 1.1, 'clipOnTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
        ThrowAttack.playWeaponSound(self)

class MarketCrashAttack(ThrowAttack):
    notify = directNotify.newCategory("MarketCrashAttack")
    attack = 'marketcrash'

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

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/sandbag-mod.bam", 2, 'doSackedAttack',
                            'throw-paper', 1, 'sackedWeaponSphere', weapon_r = 180, weapon_p = 90,
                            weapon_y = -2.8, weapon_z = -0.3, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

class GlowerPowerAttack(ThrowAttack):
    notify = directNotify.newCategory("GlowerPowerAttack")
    attack = 'glowerpower'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/dagger.bam", 1, 'doGlowerPowerAttack',
                            'glower', 1, 'glowerPowerWeaponSphere', ts = ts)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_glower_power.ogg")
        ThrowAttack.playWeaponSound(self)

class PickPocketAttack(Attack):
    notify = directNotify.newCategory("PickPocketAttack")
    attack = 'pickpocket'

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.dollar = None
        self.pickSfx = None

    def doAttack(self, ts = 0):
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
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)

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
        sphere = CollisionSphere(0, 0, 0, 0.5)
        sphere.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            collName = self.suit.uniqueName('fountainPenCollNode')
        else:
            collName = 'fountainPenCollNode'
        collNode = CollisionNode(collName)
        collNode.addSolid(sphere)
        collNode.setCollideMask(CIGlobals.WeaponBitmask)
        self.wsnp = self.spray.attachNewNode(collNode)
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
                Wait(1.2),
                Func(self.acceptOnce, "enter" + self.wsnp.node().getName(), self.handleSprayCollision),
                Func(self.playWeaponSound),
                Func(self.attachSpray),
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

    def handleSprayCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)
        self.sprayScaleIval.pause()

    def playWeaponSound(self):
        self.spraySfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_fountain_pen.ogg")
        base.audio3d.attachSoundToObject(self.spraySfx, self.pen)
        base.playSfx(self.spraySfx, node = self.pen)

    def cleanup(self):
        Attack.cleanup(self)
        if self.wsnp:
            self.wsnp.node().clearSolids()
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
        collSphere = CollisionSphere(0, 0, 0, 2)
        collSphere.setTangible(0)
        collNode = CollisionNode('phone_shootout')
        collNode.addSolid(collSphere)
        collNode.setCollideMask(CIGlobals.WeaponBitmask)
        self.collNP = self.phone.attachNewNode(collNode)
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
                Wait(delay2playSound),
                SoundInterval(self.phoneSfx, duration = 2.1, node = self.suit),
                Wait(delayAfterSoundToPlaceDownReceiver),
                Func(self.receiver.setPos, 0, 0, 0),
                Func(self.receiver.setH, 0.0),
                Func(self.receiver.reparentTo, self.phone),
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
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)

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
            self.collNP.node().clearSolids()
            self.collNP.removeNode()
            self.collNP = None
        if self.phoneSfx:
            self.phoneSfx.stop()
            self.phoneSfx = None

class BounceCheckAttack(ThrowAttack):
    notify = directNotify.newCategory('BounceCheckAttack')
    MaxBounces = 3
    WeaponHitDistance = 0.5

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

        print pathNP.getPos(base.render)

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

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_5/models/props/power-tie.bam", 4, 'doPowerTieAttack',
                            'throw-paper', 0.2, 'powerTieWeaponSphere', weapon_r = 180, ts = ts)

    def playWeaponSound(self):
        self.weaponSfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
        ThrowAttack.playWeaponSound(self)

class HalfWindsorAttack(ThrowAttack):
    notify = directNotify.newCategory('HalfWindsorAttack')
    attack = 'halfwindsor'

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

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, "phase_3.5/models/props/shredder-paper-mod.bam", 1, 'doEvictionNoticeAttack',
                            'throw-paper', 1, 'evictionNoticeWeaponSphere', weapon_y = -0.15, weapon_z = -0.5,
                            weapon_x = -1.4, weapon_r = 90, weapon_h = 30, ts = ts)
        self.wsnp.setZ(1.5)

    def throwObject(self):
        ThrowAttack.throwObject(self, False)

class RestrainingOrderAttack(EvictionNoticeAttack):
    notify = directNotify.newCategory('RestrainingOrderAttack')
    attack = 'restrainingorder'

class ParticleAttack(Attack):
    notify = directNotify.newCategory('ParticleAttack')
    attack = 'particleattack'
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
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)

    def doAttack(self, particlePaths, track_name, particleCollId, animation_name,
                delayUntilRelease, animationSpeed = 1, handObjPath = None, handObjParent = None,
                startRightAway = True, ts = 0):
        for path in particlePaths:
            particle = ParticleLoader.loadParticleEffect(path)
            self.particles.append(particle)
        sphere = CollisionSphere(0, 0, 0, 2)
        sphere.setTangible(0)
        node = CollisionNode(particleCollId)
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WeaponBitmask)

        self.targetX = self.attacksClass.target.getX(render)
        self.targetY = self.attacksClass.target.getY(render)
        self.targetZ = self.attacksClass.target.getZ(render)
        if len(self.particles) == 1:
            self.shootOutCollNP = self.particles[0].attachNewNode(node)
        else:
            self.shootOutCollNP = self.suit.attachNewNode(node)
        if handObjPath and handObjParent:
            self.handObj = loader.loadModel(handObjPath)
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
        if None not in [self.targetX, self.targetY, self.targetZ]:
            startNP.lookAt(render, self.targetX, self.targetY, self.targetZ + 2)
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

    def cleanup(self):
        Attack.cleanup(self)
        self.targetX = None
        self.targetY = None
        self.targetZ = None
        if self.particles:
            for particle in self.particles:
                particle.cleanup()
        self.particles = None
        if self.handObj:
            self.handObj.removeNode()
            self.handObj = None
        if self.shootOutCollNP:
            self.ignore('enter' + self.shootOutCollNP.node().getName())
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
    particleIvalDur = 2.0

    def doAttack(self, ts):
        ParticleAttack.doAttack(
            self, ['phase_5/etc/smile.ptf'], 'doRazzleDazzle', 'razzleDazzleSphere',
            'glower', 1, 1, 'phase_5/models/props/smile-mod.bam', self.suit.find('**/joint_Rhold'), ts = ts
        )

    def releaseAttack(self):
        ParticleAttack.releaseAttack(self, self.handObj.find('**/scale_joint_sign'), onlyMoveColl = False, blendType = 'easeIn')

    def playParticleSound(self):
        self.particleSound = base.audio3d.loadSfx('phase_5/audio/sfx/SA_razzle_dazzle.ogg')
        ParticleAttack.playParticleSound(self)

class BuzzWordAttack(ParticleAttack):
    notify = directNotify.newCategory('BuzzWordAttack')
    attack = 'buzzword'
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
        #'razzledazzle': RazzleDazzleAttack,
        'buzzword': BuzzWordAttack,
        'jargon': JargonAttack,
        'mumbojumbo': MumboJumboAttack,
        'filibuster': FilibusterAttack,
        'doubletalk': DoubleTalkAttack,
        'schmooze': SchmoozeAttack,
        'fingerwag': FingerWagAttack
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
