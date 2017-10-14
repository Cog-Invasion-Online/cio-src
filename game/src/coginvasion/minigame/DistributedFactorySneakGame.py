# Filename: DistributedFactorySneakGame.py
# Created by:  blach (21Aug15)

from panda3d.core import CollisionNode, CollisionSphere, BitMask32

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from DistributedToonFPSGame import DistributedToonFPSGame
from FactorySneakWorld import FactorySneakWorld
import CogGuardGlobals as CGG

class DistributedFactorySneakGame(DistributedToonFPSGame):
    notify = directNotify.newCategory("DistributedFactorySneakGame")

    def __init__(self, cr):
        DistributedToonFPSGame.__init__(self, cr)
        self.gameWorld = None

    def load(self):
        self.setMinigameMusic("phase_4/audio/bgm/MG_Escape.ogg")
        self.setDescription(
            "Sneak around the Sellbot Factory and collect jellybean barrels. "
            "Avoid the guards and exit by the Factory Foreman to redeem your jellybeans.")
        DistributedToonFPSGame.load(self)

    def enterPlay(self):
        self.gameWorld.enablePlayerControls()
        DistributedToonFPSGame.enterPlay(self)

    def exitPlay(self):
        DistributedToonFPSGame.exitPlay(self)
        self.gameWorld.disablePlayerControls()

    def announceGenerate(self):
        DistributedToonFPSGame.announceGenerate(self)

        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))
        base.camLens.setFar(250)
        base.localAvatar.setPythonTag('localAvatar', 1)
        self.avatarBody = base.localAvatar.attachNewNode(CollisionNode('sphereforguardeyes'))
        self.avatarBody.node().addSolid(CollisionSphere(0, 0, 0, 1.2))
        self.avatarBody.node().setFromCollideMask(BitMask32.allOff())
        self.avatarBody.node().setIntoCollideMask(CGG.GuardBitmask)
        """
        self.gameWorld = FactorySneakWorld(self)
        self.gameWorld.loadWorld()
        self.gameWorld.loadJellybeanBarrels()
        #self.gameWorld.makeGuards()
        self.gameWorld.showWorld()
        self.gameWorld.setupPlayer()
        """
        self.load()

    def disable(self):
        if self.gameWorld:
            self.gameWorld.cleanup()
            self.gameWorld = None

        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.camLens.setFar(CIGlobals.DefaultCameraFar)

        DistributedToonFPSGame.disable(self)
