from panda3d.core import TransformState
from panda3d.bullet import BulletCylinderShape, BulletSphereShape, BulletRigidBodyNode, ZUp

from direct.actor.Actor import Actor

from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.DistributedPhysicsEntity import DistributedPhysicsEntity

class BombProjectile(DistributedPhysicsEntity):
    
    def __init__(self, cr):
        DistributedPhysicsEntity.__init__(self, cr)
        self.tnt = None
        self.tntSound = None
        self.particle = None

    def getPhysBody(self):
        bsph = BulletSphereShape(0.6)
        bcy = BulletCylinderShape(0.25, 0.35, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(bsph, TransformState.makePosHpr((0.05, 0, 0.43), (86.597, 24.5539, 98.1435)))
        body.addShape(bcy, TransformState.makePosHpr((0.05, 0.655, 0.35), (86.597, 24.5539, 98.1435)))
        body.setKinematic(True)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.6)
        return body

    def explode(self):
        self.tntSound.stop()
        self.hide()
        self.particle.softStop()
        self.cleanupPhysics()
        CIGlobals.makeExplosion(self.getPos(render) + (0, 0, 5.0), 0.7, True)

    def announceGenerate(self):
        self.tnt = Actor('phase_14/models/props/cog_bomb.bam', {'chan': 'phase_5/models/props/tnt-chan.bam'})
        self.tnt.reparentTo(self)
        self.tnt.play('chan')

        self.tntSound = base.loadSfxOnNode("phase_14/audio/sfx/dynamite_loop.ogg", self.tnt)
        self.tntSound.setLoop(True)
        self.particle = loader.loadParticleEffect("phase_14/etc/tnt_spark.ptf")
        self.particle.start(self.tnt.find('**/joint_attachEmitter'), CIGlobals.getParticleRender())

        DistributedPhysicsEntity.announceGenerate(self)

        self.tntSound.play()

    def disable(self):
        if self.tnt:
            self.tnt.cleanup()
            self.tnt.removeNode()
        self.tnt = None
        if self.tntSound:
            self.tntSound.stop()
        self.tntSound = None
        if self.particle:
            self.particle.softStop()
        self.particle = None

        DistributedPhysicsEntity.disable(self)
