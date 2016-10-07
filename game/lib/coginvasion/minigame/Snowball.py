# Filename: Snowball.py
# Created by:  blach (19Apr16)

from pandac.PandaModules import NodePath, CollisionNode, CollisionSphere, BitMask32, CollisionHandlerEvent

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import ProjectileInterval
from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.globals import CIGlobals

class Snowball(NodePath, DirectObject):
    """Represents a useable snowball in Winter Dodgeball minigame (client)"""

    notify = directNotify.newCategory("Snowball")

    def __init__(self, mg, index):
        # The minigame
        self.mg = mg

        self.index = index

        # The snowball geometry
        self.model = None
        self.collNP = None

        # Has the snowball been thrown and is it currently in the air?
        self.isAirborne = False

        # The RemoteDodgeballAvatar that is currently holding this snowball.
        self.owner = None

        self.throwIval = None

        self.impactSound = base.loadSfx('phase_4/audio/sfx/snowball_hit.ogg')

        NodePath.__init__(self, "snowball")

    def load(self):
        self.model = loader.loadModel("phase_5/models/props/snowball.bam")
        self.model.reparentTo(self)

        base.audio3d.attachSoundToObject(self.impactSound, self)

        # Setup collisions
        sphere = CollisionSphere(0, 0, 0, 0.35)
        sphere.setTangible(0)
        node = CollisionNode('snowball-coll-' + str(id(self)))
        node.addSolid(sphere)
        node.setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)
        self.collNP = self.attachNewNode(node)
        self.collNP.setCollideMask(BitMask32(0))
        #self.collNP.show()
        self.collNP.setZ(0.35)

        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.add_collider(self.collNP, event)

    def setOwner(self, owner):
        """
        Sets the owner of this snowball.
        owner - A DodgeballRemoteAvatar instance
        """
        self.owner = owner

    def getOwner(self):
        return self.owner

    def hasOwner(self):
        """Returns whether or not this snowball has an owner."""
        return self.owner is not None

    def b_throw(self):
        p = camera.getP(render)
        self.d_throw(p)
        self.throw(p)

    def d_throw(self, p):
        self.mg.sendUpdate('throw', [self.index, p])

    def throw(self, p):
        self.isAirborne = True
        self.owner.avatar.play('pie', partName = 'torso', fromFrame = 62)
        base.playSfx(self.owner.throwSound, node = self.owner.avatar)

        start = NodePath('StartPath')
        start.reparentTo(self.owner.avatar)
        start.setScale(render, 1)
        start.setPos(0, 0, 0)
        start.setP(p)

        end = NodePath('ThrowPath')
        end.reparentTo(start)
        end.setScale(render, 1)
        end.setPos(0, 160, -35)
        end.setHpr(90, -90, 90)

        self.wrtReparentTo(render)
        self.setScale(1.0)

        self.throwIval = ProjectileInterval(
            self, startPos = self.owner.avatar.find('**/def_joint_right_hold').getPos(render),
            endPos = end.getPos(render), gravityMult = 0.9, duration = 2)
        self.throwIval.start()
        if self.owner.avId == base.localAvatar.doId:
            self.accept('snowball-coll-' + str(id(self)) + '-into', self.__handleSnowballCollision)

        start.removeNode()
        del start
        end.removeNode()
        del end

    def pauseThrowIval(self):
        if self.owner:
            if self.owner.throwSound:
                self.owner.throwSound.stop()
            
        if self.throwIval:
            self.throwIval.pause()
            self.throwIval = None

    def handleHitWallOrPlayer(self):
        self.pauseThrowIval()
        self.reparentTo(render)
        self.setPos(self.mg.SnowballData[self.index])
        self.setHpr(0, 0, 0)
        self.isAirborne = False
        self.owner = None
        
    def handleHitGround(self):
        self.pauseThrowIval()
        self.reparentTo(render)
        self.setZ(0.5)
        self.setHpr(0, 0, 0)
        self.isAirborne = False
        self.owner = None

    def __handleSnowballCollision(self, entry):
        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        name = intoNP.getName()
        
        if 'barrier' in name:
            # Don't react to hitting a team barrier.
            return
        else:
            self.ignore('snowball-coll-' + str(id(self)) + '-into')
            
        self.pauseThrowIval()
        if self.owner.avId == base.localAvatar.doId:
            self.mg.firstPerson.mySnowball = None
            self.mg.firstPerson.hasSnowball = False
        self.isAirborne = False
        self.owner = None
        base.playSfx(self.impactSound, node = self, volume = 1.5)
        if 'wall' in name or 'fence' in name:
            # We hit a wall. Go back to our center position.
            self.mg.sendUpdate('snowballHitWall', [self.index])
            self.handleHitWallOrPlayer()
        elif 'floor' in name or 'ground' in name or name == 'team_divider':
            # We hit the floor. Stay on the ground.
            self.mg.sendUpdate('snowballHitGround', [self.index])
            self.handleHitGround()
        else:
            for av in self.mg.remoteAvatars:
                if av.avatar.getKey() == avNP.getKey():
                    # We hit this toon!
                    self.handleHitWallOrPlayer()
                    friendly = int(av.team == self.mg.team)
                    if friendly:
                        av.unFreeze()
                    else:
                        av.freeze()
                    self.mg.sendUpdate('snowballHitPlayer', [av.avId, self.mg.team, self.index])

    def b_pickup(self):
        self.d_pickup(self.mg.cr.localAvId)
        self.pickup(self.mg.getMyRemoteAvatar())

    def d_pickup(self, avId):
        self.mg.sendUpdate('snowballPickup', [self.index, avId])

    def pickup(self, remoteAv):
        self.setPosHpr(0, 0, 0, 0, 0, 0)
        self.reparentTo(remoteAv.avatar.find('**/def_joint_right_hold'))
        self.owner = remoteAv
        self.isAirborne = False

    def removeNode(self):
        self.pauseThrowIval()
        if self.model:
            self.model.removeNode()
            self.model = None
        if self.collNP:
            self.collNP.removeNode()
            self.collNP = None
        self.isAirborne = None
        self.owner = None
        self.mg = None
        NodePath.removeNode(self)
