# Filename: FactorySneakJellybeanBarrel.py
# Created by:  blach (20Aug15)

from panda3d.core import NodePath, CollisionNode, CollisionSphere, Vec4

from direct.fsm import FSM
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

class FactorySneakJellybeanBarrel(NodePath, FSM.FSM):
    notify = directNotify.newCategory("FactorySneakJellybeanBarrel")

    AVAILABLE_CS = Vec4(1.0, 1.0, 1.0, 1.0)
    DISABLED_CS = Vec4(0.5, 0.5, 0.5, 1.0)

    BARREL_MODEL_PATH = "phase_4/models/cogHQ/gagTank.bam"
    JAR_MODEL_PATH = "phase_3.5/models/gui/jar_gui.bam"
    COLLECT_SOUND_PATH = "phase_4/audio/sfx/SZ_DD_treasure.ogg"

    BEANS_VALUE = 25

    def __init__(self, gameWorld):
        NodePath.__init__(self, 'jbsBarrel')
        FSM.FSM.__init__(self, 'jbsBarrelFSM')
        self.gameWorld = gameWorld
        self.barrelMdl = None
        self.collisionName = "fsJBSBarrel" + str(id(self))
        self.collisionNode = None
        self.soundCollected = None

    def setupCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 2)
        sphere.setTangible(0)
        node = CollisionNode(self.collisionName)
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.collisionNode = self.attachNewNode(node)

    def loadBarrel(self):
        barrel = base.loader.loadModel(self.BARREL_MODEL_PATH)
        jarIcon = base.loader.loadModel(self.JAR_MODEL_PATH)
        barrel.setScale(0.5)
        label = barrel.find('**/gagLabelDCS')
        label.setColor(0.15, 0.15, 0.1)
        iconNode = barrel.attachNewNode('iconNode')
        iconNode.setPosHpr(0.0, -2.62, 4.0, 0, 0, 0)
        iconNode.setColorScale(0.7, 0.7, 0.6, 1)
        jarIcon.reparentTo(iconNode)
        jarIcon.setPos(0, -0.1, 0)
        jarIcon.setScale(13)
        barrel.reparentTo(self)
        self.barrelMdl = barrel
        self.soundCollected = base.loadSfx(self.COLLECT_SOUND_PATH)
        self.setupCollisions()

    def cleanup(self):
        self.request('Off')
        self.soundCollected = None
        if self.barrelMdl:
            self.barrelMdl.removeNode()
            self.barrelMdl = None
        if self.collisionNode:
            self.collisionNode.removeNode()
            self.collisionNode = None

    def enterAvailable(self):
        self.setColorScale(self.AVAILABLE_CS)
        self.acceptOnce("enter" + self.collisionName, self.__handleBarrelCollision)

    def __handleBarrelCollision(self, entry):
        base.playSfx(self.soundCollected, node = self)
        self.gameWorld.player.setBeansCollected(self.gameWorld.player.getBeansCollected() + self.BEANS_VALUE)
        self.request('Disabled')

    def exitAvailable(self):
        self.ignore("enter" + self.collisionName)

    def enterDisabled(self):
        self.setColorScale(self.DISABLED_CS)

    def exitDisabled(self):
        pass
