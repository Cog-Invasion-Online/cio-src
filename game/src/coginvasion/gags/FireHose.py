"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FireHose.py
@author Brian Lach
@date November 15, 2015

"""

from panda3d.core import Point3, Vec3, NodePath

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, LerpScaleInterval, Parallel

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon import ParticleLoader
from src.coginvasion.phys import PhysicsUtils
from GagState import GagState
from SquirtGag import SquirtGag
import GagGlobals

PARTICLE_DIST = 50.0
PARTICLE_LIFE = 0.5

class FireHose(SquirtGag):

    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.FireHose, "phase_5/models/props/firehose-mod.bam", 30,
                           GagGlobals.NULL_SFX, GagGlobals.FIREHOSE_SFX, GagGlobals.NULL_SFX, 'firehose',
                           0, 0)
        self.setHealth(GagGlobals.FIREHOSE_HEAL)
        self.setImage('phase_3.5/maps/fire-hose.png')
        self.anim = 'phase_5/models/props/firehose-chan.bam'
        self.sprayScale = 0.2
        self.dmgIval = 0.2
        self.lastDmgTime = 0.0
        self.scale = 1.0
        self.holdTime = 0.0
        self.hydrant = None
        self.hydrantNode = None
        self.hydrantScale = None
        self.hoseTrack = None
        self.timeout = 6
        self.sprayRotation = Vec3(0, 5, 0)

        self.sprayParticleRoot = None
        self.waterStreamParent = None
        self.spRootUpdateTask = None
        self.spraySound = base.audio3d.loadSfx("phase_14/audio/sfx/squirtgun_spray_loop.ogg")
        self.sprayParticle = None

    def cleanupHydrantNode(self):
        if self.hydrantNode:
            self.hydrantNode.removeNode()
            self.hydrentNode = None

    def reset(self):
        SquirtGag.reset(self)
        self.deleteHoseStuff()

    def equip(self):
        self.deleteHoseStuff()

        SquirtGag.equip(self)
        
        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMGag(self.gag, pos = (-1.8, 1.06, -4.13), hpr = (0, 90, 0), hand = 1, animate = False)
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "hose_draw"), Func(vm.loop, "hose_idle")))
            
        self.origin = self.getSprayStartPos()
        self.hydrant = loader.loadModel('phase_5/models/props/battle_hydrant.bam')
        self.gag.reparentTo(self.hydrant)
        self.gag.pose('chan', 2)
        self.hydrantNode = self.avatar.attachNewNode('hydrantNode')
        self.hydrantNode.clearTransform(self.avatar.getGeomNode().getChild(0))
        self.hydrantScale = self.hydrantNode.attachNewNode('hydrantScale')
        self.hydrant.reparentTo(self.hydrantScale)
        self.avatar.pose('firehose', 30)
        self.avatar.update(0)
        torso = self.avatar.getPart('torso')
        if 'dgm' in self.avatar.getTorso():
            self.hydrant.setPos(torso, 0, 0, -1.85)
        else:
            self.hydrant.setPos(torso, 0, 0, -1.45)
        hbase = self.hydrant.find('**/base')
        hbase.setColor(1, 1, 1, 0.5)
        hbase.setPos(self.avatar, 0, 0, 0)

        self.avatar.loop('neutral')

        self.sprayParticleRoot = render.attachNewNode('sprayParticleRoot')
        self.sprayParticleRoot.setLightOff()
        self.sprayParticleRoot.setMaterialOff()
        self.sprayParticleRoot.setShaderOff()

        tAppearDelay = 0.7
        dAnimHold = 5.1
        dHoseHold = 0.7
        tSprayDelay = 2.8
        track = Parallel()
        toonTrack = Sequence(Wait(tAppearDelay),
                             Func(self.avatar.setForcedTorsoAnim, 'firehose'),
                             ActorInterval(self.avatar, 'firehose', endFrame = 30))
        propTrack = Sequence(Func(self.hydrantNode.reparentTo, self.avatar), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.5, Point3(1, 1, 1.4),
            startScale=Point3(1, 1, 0.01)), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.3, Point3(1, 1, 0.8), startScale=Point3(1, 1, 1.4)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1.2), startScale=Point3(1, 1, 0.8)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1), startScale=Point3(1, 1, 1.2)),
            ActorInterval(self.gag, 'chan', endFrame = 30))
        track.append(toonTrack)
        track.append(propTrack)
        self.setAnimTrack(track, startNow = True)

    def deleteHoseStuff(self):
        self.stopParticle()
        if self.spRootUpdateTask:
            taskMgr.remove(self.spRootUpdateTask)
            self.spRootUpdateTask = None
        if self.sprayParticleRoot:
            self.sprayParticleRoot.removeNode()
            self.sprayParticleRoot = None
        if self.hoseTrack:
            self.hoseTrack.pause()
            self.hoseTrack = None
        if self.hydrant:
            self.hydrant.removeNode()
            self.hydrant = None
        if self.hydrantNode:
            self.hydrantNode.removeNode()
            self.hydrantNode = None
        if self.hydrantScale:
            self.hydrantScale.removeNode()
            self.hydrantScale = None
        if self.gag:
            self.gag.cleanup()
            self.gag.removeNode()
            self.gag = None

    def delete(self):
        self.deleteHoseStuff()
        SquirtGag.delete(self)
        
    def loadParticle(self):
        self.stopParticle()
        gag = self.gag if not self.isLocal() else self.getVMGag()
        self.waterStreamParent = gag.find("**/joint_water_stream").attachNewNode("particleParent")
        self.sprayParticle = ParticleLoader.loadParticleEffect("phase_14/etc/spray.ptf")
        if self.isLocal():
            # Update now to prevent one particle spraying out the side when we begin.
            self.__updateParticleParent()
            
    def __handleSprayCollision(self, intoNP, hitPos, distance):
        avNP = intoNP.getParent()
        
        if base.localAvatarReachable() and self.isLocal():
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ in CIGlobals.SuitClasses:
                    if obj.getKey() == avNP.getKey():
                        obj.sendUpdate('hitByGag', [self.getID(), distance])
                elif obj.__class__.__name__ == "DistributedToon":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() < obj.getMaxHealth():
                            self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])

            self.splatPos = hitPos
            self.splatDist = distance
            gagPos = hitPos
            self.handleSplat()
            self.avatar.sendUpdate('setSplatPos', [self.getID(), gagPos.getX(), gagPos.getY(), gagPos.getZ()])
        
    def __updateParticleParent(self, task = None):
        time = globalClock.getFrameTime()
        
        streamPos = self.waterStreamParent.getPos(render)
        pFrom = camera.getPos(render)
        pTo = pFrom + camera.getQuat(render).xform(Vec3.forward()) * (PARTICLE_DIST + (pFrom - streamPos).length())
        hitPos = Point3(pTo)
        result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.FloorGroup | CIGlobals.WallGroup | CIGlobals.StreetVisGroup)
        distance = PARTICLE_DIST
        if result.hasHit():
            node = result.getNode()
            hitPos = result.getHitPos()
            distance = (hitPos - streamPos).length()
            if time - self.lastDmgTime >= self.dmgIval:
                self.__handleSprayCollision(NodePath(node), hitPos, distance)
                self.lastDmgTime = time
            
        self.waterStreamParent.lookAt(render, hitPos)
        
        if self.sprayParticle:
            system = self.sprayParticle.getParticlesNamed('particles-1')
            # Make the particles die off at the hit point.
            lifespan = min(1, distance / PARTICLE_DIST) * PARTICLE_LIFE
            system.factory.setLifespanBase(lifespan)
        
        if task:
            return task.cont

    def start(self):
        base.audio3d.attachSoundToObject(self.spraySound, self.avatar)
        self.spraySound.setLoop(True)
        self.spraySound.play()
        self.loadParticle()
        self.sprayParticle.start(self.waterStreamParent, self.sprayParticleRoot)

        if self.isLocal():
            self.spRootUpdateTask = taskMgr.add(self.__updateParticleParent, "FH.uPP", sort = -100)
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "hose_shoot_begin"), Func(vm.loop, "hose_shoot_loop")))
            
    def stopParticle(self):
        if self.spRootUpdateTask:
            self.spRootUpdateTask.remove()
            self.spRootUpdateTask = None
        if self.waterStreamParent:
            self.waterStreamParent.removeNode()
            self.waterStreamParent = None
        if self.sprayParticle:
            self.sprayParticle.softStop()
            self.sprayParticle = None

    def throw(self):
        self.spraySound.stop()
        
        if self.avatar.isEmpty():
            return
            
        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "hose_shoot_end"), Func(vm.loop, "hose_idle")))
            base.localAvatar.enableGagKeys()
            
        self.stopParticle()

        self.state = GagState.LOADED

    def getSprayStartPos(self):
        self.sprayJoint = self.gag.find('**/joint_water_stream')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(self.avatar)
        n.setPos(self.sprayJoint.getPos(self.avatar) + Point3(0, -0.55, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p
