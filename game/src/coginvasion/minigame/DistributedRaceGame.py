"""

  Filename: DistributedRaceGame.py
  Created by: blach (07Oct14)

"""

from panda3d.core import Vec3

from direct.gui.DirectGui import DirectLabel
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil

import RaceGameMovement
import DistributedMinigame

class DistributedRaceGame(DistributedMinigame.DistributedMinigame):

    def __init__(self, cr):
        try:
            self.DistributedRaceGame_initialized
            return
        except:
            self.DistributedRaceGame_initialized = 1
        DistributedMinigame.DistributedMinigame.__init__(self, cr)
        self.movement = RaceGameMovement.RaceGameMovement(base.localAvatar)
        self.raceFSM = ClassicFSM('DistributedRaceGame', [State('race', self.enterRace, self.exitRace),
                        State('raceTransition', self.enterRaceTransition, self.exitRaceTransition),
                        State('off', self.enterRaceOff, self.exitRaceOff)],
                        'off', 'off')
        self.raceFSM.enterInitialState()
        self.cr = cr
        self.track = None
        self.olc = None
        self.countSfx = base.loadSfx("phase_5/audio/sfx/firehydrant_popup.ogg")
        self.goSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.ogg")
        self.game = CIGlobals.RaceGame
        self.trackPath = "phase_4/models/minigames/sprint_track.egg"
        self.skyPath = "phase_3.5/models/props/TT_sky.bam"
        self.lanePos = [(-22.00, -205.00, 0.00),
                        (-11.66, -205.00, 0.00),
                        (0.00, -205.00, 0.00),
                        (-33.66, -205.00, 0.00)]
        self.initialCamPos = {"pos": (41.10, -145.00, 25.88),
                            "hpr": (135.00, 345.96, 0.0)}
        self.raceCamPos = (-24.52, -37.22, 25.00)
        self.lane = 0
        return

    def load(self):
        self.deleteWorld()
        self.track = loader.loadModel(self.trackPath)
        self.track.reparentTo(render)
        self.olc = ZoneUtil.getOutdoorLightingConfig(CIGlobals.ToontownCentral)
        self.olc.setupAndApply()
        self.setMinigameMusic("phase_4/audio/bgm/MG_toontag.mid")
        self.setDescription("Tap the left and right arrow keys repeatedly, in turns, as fast as " + \
            "you can to win the race! Every time your power bar hits the top, the boost bar starts" + \
            " to fill. When the boost bar is full, press CTRL to boost for a few seconds.")
        self.setWinnerPrize(100)
        self.setLoserPrize(5)
        self.d_requestToonLane()
        camera.reparentTo(render)
        camera.setPos(self.initialCamPos["pos"])
        camera.setHpr(self.initialCamPos["hpr"])
        DistributedMinigame.DistributedMinigame.load(self)

    def enterPlay(self):
        DistributedMinigame.DistributedMinigame.enterPlay(self)
        self.raceFSM.request('raceTransition')

    def exitPlay(self):
        DistributedMinigame.DistributedMinigame.exitPlay(self)
        self.raceFSM.request('off')

    def enterRace(self):
        self.startMovement()

    def exitRace(self):
        self.stopMovement()

    def enterRaceOff(self):
        pass

    def exitRaceOff(self):
        pass

    def enterRaceTransition(self):
        self.raceTrans = Sequence(Wait(0.5), Func(self.moveCameraToToon), Wait(4.5), Func(self.moveCameraToTop),
            Wait(4.5), Func(self.startCountdown))
        self.raceTrans.start()

    def exitRaceTransition(self):
        self.raceTrans.pause()
        del self.raceTrans

    def startMovement(self):
        self.movement.createGui()
        self.movement.fsm.request('run')

    def enterGameOver(self, winner=0, winnerDoId=0, allPrize = 0):
        self.raceFSM.request('off')
        DistributedMinigame.DistributedMinigame.enterGameOver(self, winner, winnerDoId, allPrize)

    def stopMovement(self):
        self.movement.cleanup()
        self.movement.deleteGui()

    def startCountdown(self):
        """ Start the countdown to the start of the race. """
        self.countdownLbl = DirectLabel(text="", text_scale=0.3, text_font=CIGlobals.getMickeyFont(),
                                    text_fg=(1, 1, 0, 1), pos=(0, 0, 0.5))
        Sequence(Func(self.setCountdownText, "3"), Wait(1.0), Func(self.setCountdownText, "2"),
                Wait(1.0), Func(self.setCountdownText, "1"), Wait(1.0), Func(self.setCountdownText, "GO!"),
                Wait(1.5), Func(self.deleteCountdownLabel)).start()

    def setCountdownText(self, number):
        self.countdownLbl['text'] = number
        if number == "GO!":
            self.countdownLbl['text_fg'] = (0, 1, 0, 1)
            self.goSfx.play()
            self.raceFSM.request('race')
        else:
            self.countSfx.play()

    def deleteCountdownLabel(self):
        self.countdownLbl.destroy()
        del self.countdownLbl

    def moveCameraToToon(self):
        camPInt = LerpPosInterval(camera,
                                duration=3.0,
                                pos=self.localAv.getPos(render) + (0, 15, 3),
                                startPos=(camera.getPos(render)),
                                blendType="easeInOut")
        camQInt = camera.quatInterval(3.0, hpr=Vec3(180, 0, 0), blendType="easeInOut")
        camPInt.start()
        camQInt.start()

    def moveCameraToTop(self):
        camera.setPos(camera.getPos(self.localAv))
        camera.reparentTo(self.localAv)
        oldPos = camera.getPos()
        camera.setPos(self.raceCamPos)
        oldHpr = camera.getHpr()
        camera.lookAt(self.localAv.getPart('head'))
        newHpr = camera.getHpr()
        camera.setHpr(oldHpr)
        camera.setPos(oldPos)
        camPInt = LerpPosInterval(camera,
                                duration=3.0,
                                pos=self.raceCamPos,
                                startPos=oldPos,
                                blendType="easeInOut")
        camQInt = camera.quatInterval(3.0, hpr=newHpr, blendType="easeInOut")
        camPInt.start()
        camQInt.start()

    def deleteWorld(self):
        if self.track:
            self.track.removeNode()
            self.track = None
        if self.olc:
            self.olc.cleanup()
            self.olc = None

    def setToonLane(self, lane):
        self.lane = lane
        base.localAvatar.setPos(self.lanePos[lane])
        base.localAvatar.setHpr(0, 0, 0)

    def getToonLane(self):
        return self.lane

    def d_requestToonLane(self):
        self.sendUpdate('requestToonLane', [])

    def announceGenerate(self):
        DistributedMinigame.DistributedMinigame.announceGenerate(self)
        self.load()

    def disable(self):
        DistributedMinigame.DistributedMinigame.disable(self)
        self.deleteWorld()
        self.raceFSM.requestFinalState()
        del self.raceFSM
        self.countSfx = None
        self.goSfx = None
