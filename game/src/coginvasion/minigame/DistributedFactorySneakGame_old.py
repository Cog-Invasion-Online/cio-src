"""

  Filename: DistributedFactorySneakGame.py
  Created by: mliberty (30Mar15)

"""

import DistributedToonFPSGame
from panda3d.core import Point3, Vec3
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from src.coginvasion.minigame.FactorySneakGameToonFPS import FactorySneakGameToonFPS
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
from src.coginvasion.globals import CIGlobals
import random

class DistributedFactorySneakGame(DistributedToonFPSGame.DistributedToonFPSGame):
    notify = directNotify.newCategory("DistributedFactorySneakGame")

    def __init__(self, cr):
        try:
            self.DistributedFactorySneakGame_initalized
            return
        except:
            self.DistributedFactorySneakGame_initalized = 1
        DistributedToonFPSGame.DistributedToonFPSGame.__init__(self, cr)
        self.fsm.addState(State('countdown', self.enterCountdown, self.exitCountdown, ['play']))
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.environ = None
        self.whistleSfx = None
        self.toonFps = FactorySneakGameToonFPS(self)
        self.spawnPoints = []

    def createSpawnPoint(self, pos, hpr = Vec3(0, 0, 0)):
        self.spawnPoints.append((pos, hpr))

    def loadSpawnPoints(self):
        self.createSpawnPoint(Point3(21, 14.5, 3.73))
        self.createSpawnPoint(Point3(200, 250, 8.68), hpr = Vec3(90, 0, 0))
        self.createSpawnPoint(Point3(-97.2, 324, 18.73), hpr = Vec3(90, 0, 0))
        self.createSpawnPoint(Point3(-97.2, 305, 18.73), hpr = Vec3(90, 0, 0))

    def chooseSpawnPoint(self):
        spawn = [Vec3(0, 0, 0), Vec3(0, 0, 0)]
        if len(self.spawnPoints) > 0:
            spawn = random.choice(self.spawnPoints)
        else:
            self.notify.info("Could not find spawn point to spawn player at.")
        return spawn

    def enterCountdown(self):
        countdownSounds = []
        sfx = 5
        for _ in range(5):
            print sfx
            countdownSounds.append(base.loadSfx("phase_4/audio/sfx/announcer_begins_%ssec.ogg" % (sfx)))
            sfx -= 1
        text = OnscreenText(text = "", scale = 0.1, pos = (0, 0.5), fg = (1, 1, 1, 1), shadow = (0,0,0,1))
        self.text = text
        self.toonFps.disableMouse()
        def playSfx(id):
            countdownSounds[id].play()
        self.countdownSeq = Sequence(
            Func(playSfx, 0),
            Func(text.setText, "5"),
            Wait(1),
            Func(playSfx, 1),
            Func(text.setText, "4"),
            Wait(1),
            Func(playSfx, 2),
            Func(text.setText, "3"),
            Wait(1),
            Func(playSfx, 3),
            Func(text.setText, "2"),
            Wait(1),
            Func(playSfx, 4),
            Func(text.setText, "1"),
            Wait(1),
            Func(text.setText, "SNEAK!"),
            Func(self.whistleSfx.play),
            Func(self.fsm.request, 'play'),
            Wait(1),
            Func(text.destroy)
        )
        self.countdownSeq.start()

    def exitCountdown(self):
        self.countdownSeq.pause()
        del self.countdownSeq
        self.text.destroy()
        del self.text

    def allPlayersReady(self):
        self.fsm.request('countdown')

    def createBarrel(self):
        barrel = loader.loadModel("phase_4/models/cogHQ/gagTank.bam")
        jarIcon = loader.loadModel("phase_3.5/models/gui/jar_gui.bam")
        barrel.setScale(0.5)
        label = barrel.find('**/gagLabelDCS')
        label.setColor(0.15, 0.15, 0.1)
        iconNode = barrel.attachNewNode('iconNode')
        iconNode.setPosHpr(0.0, -2.62, 4.0, 0, 0, 0)
        iconNode.setColorScale(0.7, 0.7, 0.6, 1)
        jarIcon.reparentTo(iconNode)
        jarIcon.setPos(0, -0.1, 0)
        jarIcon.setScale(13)
        return barrel

    def load(self):
        print "Loading the environment."
        destroy = ['ZONE12', 'ZONE30', 'ZONE31', 'ZONE32', 'ZONE33', 'ZONE34', 'ZONE35', 'ZONE36', 'ZONE37', 'ZONE38', 'ZONE60', 'ZONE61']
        self.environ = loader.loadModel("phase_9/models/cogHQ/SelbotLegFactory.bam")
        for item in destroy:
            self.environ.find('**/%s' % (item)).removeNode()
        self.environ.reparentTo(render)
        self.loadSpawnPoints()
        self.toonFps.load()
        pos, hpr = self.chooseSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)
        self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
        self.setMinigameMusic("phase_12/audio/bgm/Bossbot_Entry_v3.ogg")
        self.setDescription("Sneak around the Sellbot Factory and collect jellybean barrels. " + \
                            "Avoid the guards and exit by the Factory Foreman to redeem your jellybeans.")
        self.toonFps.start()
        self.toonFps.enableMouse()
        self.whistleSfx = loader.loadSfx("phase_4/audio/sfx/AA_sound_whistle.ogg")
        DistributedToonFPSGame.DistributedToonFPSGame.load(self)

    def enterPlay(self):
        DistributedToonFPSGame.DistributedToonFPSGame.enterPlay(self)
        self.toonFps.reallyStart()
        base.localAvatar.disableChatInput()

    def exitPlay(self):
        DistributedToonFPSGame.DistributedToonFPSGame.exitPlay(self)
        self.toonFps.end()
        base.localAvatar.createChatInput()

    def announceGenerate(self):
        DistributedToonFPSGame.DistributedToonFPSGame.announceGenerate(self)
        self.load()
        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))
        base.camLens.setFar(250)

    def disable(self):
        self.deleteWorld()
        self.spawnPoints = None
        self.whistleSfx = None
        self.toonFps.reallyEnd()
        self.toonFps = None
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.camLens.setFar(CIGlobals.DefaultCameraFar)
        DistributedToonFPSGame.DistributedToonFPSGame.disable(self)

    def deleteWorld(self):
        if self.environ:
            self.environ.destroy()
            self.environ = None
