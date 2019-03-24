from panda3d.bullet import BulletCylinderShape, BulletRigidBodyNode, ZUp

from direct.actor.Actor import Actor

from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.DistributedPhysicsEntity import DistributedPhysicsEntity

class TNTProjectile(DistributedPhysicsEntity):
    
    def __init__(self, cr):
        DistributedPhysicsEntity.__init__(self, cr)
        self.tnt = None
        self.tntSound = None
        self.particle = None

    def getPhysBody(self):
        shape = BulletCylinderShape(0.3925, 1.4, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(shape)
        body.setKinematic(True)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.3925)
        return body

    def explode(self):
        self.tntSound.stop()
        self.hide()
        self.particle.softStop()
        self.cleanupPhysics()
        CIGlobals.makeExplosion(self.getPos(render) + (0, 0, 5.0), 0.7, True)

    def announceGenerate(self):
        self.tnt = Actor('phase_14/models/props/tnt.bam', {'chan': 'phase_5/models/props/tnt-chan.bam'})
        self.tnt.reparentTo(self)
        self.tnt.play('chan')
        self.tnt.setP(97.492)
        self.tnt.setY(0.38)
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
