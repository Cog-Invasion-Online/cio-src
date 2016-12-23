# Filename: DistributedCinemaInterior.py
# Created by:  blach (29Jul15)

from pandac.PandaModules import TextureStage, MovieTexture, NodePath, CardMaker

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import SoundInterval, Sequence, Wait, Func
from direct.gui.DirectGui import DirectLabel

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import DistributedToonInterior
import CinemaGlobals

CardScaleDivisor = 50.0

class DistributedCinemaInterior(DistributedToonInterior.DistributedToonInterior):
    notify = directNotify.newCategory("DistributedCinemaInterior")

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DCinemaInterior', [State.State('off', self.enterOff, self.exitOff),
            State.State('show', self.enterShow, self.exitShow),
            State.State('intermission', self.enterIntermission, self.exitIntermission)],
            'off', 'off')
        self.fsm.enterInitialState()
        self.state = None
        self.cinemaIndex = None
        self.movieTex = None
        self.movieCard = None
        self.movieSound = None
        self.movieTrack = None
        self.intermissionText = None

    def makeInterior(self):
        # Always use the same room for cinemas.
        DistributedToonInterior.DistributedToonInterior.makeInterior(self, roomIndex = 0)

    def announceGenerate(self):
        DistributedToonInterior.DistributedToonInterior.announceGenerate(self)
        self.sendUpdate('requestStateAndTimestamp')

    def disable(self):
        self.fsm.requestFinalState()
        self.fsm = None
        self.state = None
        self.cinemaIndex = None
        self.movieTex = None
        self.movieCard = None
        self.movieSound = None
        self.movieTrack = None
        self.intermissionText = None
        self.cr.playGame.hood.loader.interiorMusic.stop()
        DistributedToonInterior.DistributedToonInterior.disable(self)

    def darkenInterior(self):
        darkenIval = self.interior.colorScaleInterval(3.0, colorScale = (0.3, 0.3, 0.3, 1.0),
            startColorScale = (1.0, 1.0, 1.0, 1.0), blendType = 'easeInOut')
        darkenIval.start()

    def lightenInterior(self):
        lightenIval = self.interior.colorScaleInterval(3.0, colorScale = (1, 1, 1, 1.0),
            startColorScale = (0.3, 0.3, 0.3, 1.0), blendType = 'easeInOut')
        lightenIval.start()

    def enterShow(self, ts = 0):
        self.darkenInterior()
        self.cr.playGame.hood.loader.interiorMusic.stop()

        videoFile = CinemaGlobals.Cinemas[self.cinemaIndex][0]
        audioFile = CinemaGlobals.Cinemas[self.cinemaIndex][1]

        self.movieTex = MovieTexture(self.uniqueName("movieTex"))
        self.movieTex.read(videoFile)
        card = CardMaker(self.uniqueName('movieCard'))
        card.setFrame(-1.5, 1.5, -1, 1)
        self.movieCard = NodePath(card.generate())
        self.movieCard.reparentTo(render)
        self.movieCard.setPos(self.interior.find('**/sign_origin;+s').getPos(render))
        #self.movieCard.setX(self.movieCard, -0.05)
        self.movieCard.setHpr(self.interior.find('**/sign_origin;+s').getHpr(render))
        self.movieCard.setDepthWrite(1, 1)
        self.movieCard.setTwoSided(True)
        self.movieCard.setTexture(self.movieTex)
        self.movieCard.setTexScale(TextureStage.getDefault(), self.movieTex.getTexScale())
        self.movieCard.setScale(2.5)
        self.movieSound = base.loadSfx(audioFile)
        self.movieTex.synchronizeTo(self.movieSound)
        self.movieTrack = SoundInterval(self.movieSound, name = self.uniqueName('movieTrack'))
        self.movieTrack.setDoneEvent(self.movieTrack.getName())
        self.acceptOnce(self.movieTrack.getDoneEvent(), self.fsm.request, ['off'])
        self.movieTrack.start(ts)

    def exitShow(self):
        self.ignore(self.movieTrack.getDoneEvent())
        self.movieTrack.finish()
        self.movieTrack = None
        self.movieSound = None
        self.movieCard.removeNode()
        self.movieCard = None
        self.movieTex = None

        self.lightenInterior()
        self.cr.playGame.hood.loader.interiorMusic.play()

    def enterIntermission(self, ts = 0):
        self.intermissionText = DirectLabel(relief = None, text_decal = True, text = "",
            scale = 0.7, parent = self.interior.find('**/sign_origin;+s'),
            text_font = CIGlobals.getMickeyFont(), text_fg = (1, 0.9, 0, 1))
        self.movieTrack = Sequence(name = self.uniqueName('intermissionTrack'))
        for second in range(CinemaGlobals.IntermissionLength + 1):
            timeRemaining = CinemaGlobals.IntermissionLength - second
            self.movieTrack.append(Func(self.setIntermissionText, "Next show in:\n%d" % timeRemaining))
            self.movieTrack.append(Wait(1.0))
        self.movieTrack.setDoneEvent(self.movieTrack.getName())
        self.acceptOnce(self.movieTrack.getDoneEvent(), self.fsm.request, ['off'])
        self.movieTrack.start(ts)

    def setIntermissionText(self, text):
        self.intermissionText['text'] = text

    def exitIntermission(self):
        self.ignore(self.movieTrack.getDoneEvent())
        self.movieTrack.finish()
        self.movieTrack = None
        self.intermissionText.destroy()
        self.intermissionText = None

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def setCinemaIndex(self, index):
        self.cinemaIndex = index

    def getCinemaIndex(self):
        return self.cinemaIndex

    def setState(self, state, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.state = state
        self.fsm.request(state, [ts])

    def getState(self):
        return self.state
