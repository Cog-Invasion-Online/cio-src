########################################
# Filename: TurretGag.py
# Created by: DecodedLogic (10Aug15)
########################################

from pandac.PandaModules import CollisionSphere, CollisionNode, BitMask32, CollisionHandlerEvent, NodePath

from direct.showbase.DirectObject import DirectObject
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.actor.Actor import Actor

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags.GagManager import GagManager

class TurretGag(DirectObject):

    def __init__(self, turret, collideEventName, gagName):
        DirectObject.__init__(self)
        self.turret = turret
        self.collideEventName = collideEventName
        self.eventName = 'turretGagSensor' + str(id(self)) + '-into'
        self.trackName = 'turretGagTrack' + str(id(self))
        self.track = None
        self.gravityMult = 0.9
        self.duration = 2.5
        self.setClass(gagName)

    def setClass(self, gagName):
        gagMgr = GagManager()
        self.gagClass = gagMgr.getGagByName(gagName)
        self.gag = None

    def build(self):
        self.gagClass.build()
        self.gag = self.gagClass.getGag()
        self.gag.reparentTo(self.turret.getCannon())
        self.gag.setY(5.2)
        self.gag.setHpr(90, -90, 90)
        
        if isinstance(self.gag, Actor):
            self.gag.loop('chan')

    def shoot(self, rangeVector):
        if not self.gag:
            return

        rangeNode = NodePath('Shoot Range')
        rangeNode.reparentTo(self.turret.getCannon())
        rangeNode.setScale(render, 1)
        rangeNode.setPos(rangeVector)
        rangeNode.setHpr(90, -90, 90)

        self.gag.setScale(self.gag.getScale(render))
        self.gag.setScale(self.gag.getScale(render))
        self.gag.setPos(self.gag.getPos(render))
        self.gag.reparentTo(render)
        self.gag.setHpr(rangeNode.getHpr(render))

        base.audio3d.attachSoundToObject(self.gagClass.woosh, self.gag)
        self.gagClass.woosh.play()

        self.track = ProjectileInterval(self.gag,
                    startPos = self.gag.getPos(render), endPos = rangeNode.getPos(render),
                    gravityMult = self.gravityMult, duration = self.duration,
                    name = self.trackName
        )
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.cleanup)
        self.track.start()

        fireSfx = base.audio3d.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
        base.audio3d.attachSoundToObject(fireSfx, self.turret.getCannon())
        fireSfx.play()

        if self.turret.isLocal():
            self.buildCollisions()
            self.acceptOnce(self.eventName, self.handleCollision)

    def getGag(self):
        return self.gag

    def buildCollisions(self):
        pieSphere = CollisionSphere(0, 0, 0, 1)
        pieSensor = CollisionNode('turretGagSensor' + str(id(self)))
        pieSensor.addSolid(pieSphere)
        pieNP = self.gag.attachNewNode(pieSensor)
        pieNP.setCollideMask(BitMask32(0))
        pieNP.node().setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)

        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.addCollider(pieNP, event)

    def handleCollision(self, entry):
        messenger.send(self.collideEventName, [entry, self])

    def getID(self):
        return self.gagClass.getID()

    def getCollideEventName(self):
        return self.collideEventName

    def cleanup(self):
        if hasattr(self, 'collideEventName'):
            del self.collideEventName
        if self.track:
            self.track.finish()
            self.track = None
        if self.turret:
            if self.turret.entities and self in self.turret.entities:
                self.turret.entities.remove(self)
            self.turret = None
        self.ignore(self.eventName)
        self.duration = None
        self.gravityMult = None
        self.eventName = None
        self.trackName = None
        if self.gagClass:
            self.gagClass.cleanupGag()
            self.gagClass = None
        if self.gag:
            if isinstance(self.gag, Actor):
                self.gag.cleanup()
            self.gag.removeNode()
            self.gag = None
