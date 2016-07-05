# Filename: DodgeballFirstPerson.py
# Created by:  blach (18Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval, Parallel, Wait

from FirstPerson import FirstPerson
from MinigameUtils import *

ToonSpeedFactor = 1.0
ToonForwardSpeed = 16.0 * ToonSpeedFactor
ToonJumpForce = 0.0
ToonReverseSpeed = 16.0 * ToonSpeedFactor
ToonRotateSpeed = 80.0 * ToonSpeedFactor

class DodgeballFirstPerson(FirstPerson):
    """The first person controls for the local player in Winter Dodgeball"""

    notify = directNotify.newCategory("DodgeballFirstPerson")

    MaxPickupDistance = 5.0

    def __init__(self, mg):
        self.mg = mg
        self.crosshair = None
        self.soundCatch = None
        self.vModelRoot = None
        self.vModel = None
        self.ival = None
        self.soundPickup = base.loadSfx('phase_4/audio/sfx/MG_snowball_pickup.wav')
        self.fakeSnowball = loader.loadModel("phase_5/models/props/snowball.bam")
        self.hasSnowball = False
        self.mySnowball = None
        self.fsm = ClassicFSM.ClassicFSM("DodgeballFirstPerson",
                                         [State.State("off", self.enterOff, self.exitOff),
                                          State.State("hold", self.enterHold, self.exitHold),
                                          State.State("catch", self.enterCatch, self.exitCatch),
                                          State.State("throw", self.enterThrow, self.exitThrow)],
                                         "off", "off")
        self.fsm.enterInitialState()

        FirstPerson.__init__(self)

    def enterOff(self):
        if self.vModel:
            self.vModel.hide()

    def exitOff(self):
        if self.vModel:
            self.vModel.show()

    def enterHold(self):
        self.ival = Sequence(
            ActorInterval(self.vModel, "hold-start"),
            Func(self.vModel.loop, "hold"))
        self.ival.start()

    def exitHold(self):
        if self.ival:
            self.ival.finish()
            self.ival = None
        self.vModel.stop()

    def enterThrow(self):
        self.ival = Parallel(
            Sequence(Wait(0.4), Func(self.mySnowball.b_throw)),
            Sequence(ActorInterval(self.vModel, "throw"), Func(self.fsm.request, 'off')))
        self.ival.start()

    def exitThrow(self):
        if self.ival:
            self.ival.pause()
            self.ival = None
        self.vModel.stop()

    def enterCatch(self):
        self.ival = Parallel(
            Sequence(Wait(0.2), Func(self.__tryToCatchOrGrab)),
            Sequence(ActorInterval(self.vModel, "catch"), Func(self.__maybeHold)))
        self.ival.start()

    def __maybeHold(self):
        if self.hasSnowball:
            self.fsm.request('hold')
        else:
            self.fsm.request('off')

    def __tryToCatchOrGrab(self):
        snowballs = list(self.mg.snowballs)
        snowballs.sort(key = lambda snowball: snowball.getDistance(base.localAvatar))
        for i in xrange(len(snowballs)):
            snowball = snowballs[i]
            if (not snowball.hasOwner() and not snowball.isAirborne and
                snowball.getDistance(base.localAvatar) <= DodgeballFirstPerson.MaxPickupDistance):
                snowball.b_pickup()
                self.mySnowball = snowball
                self.fakeSnowball.setPosHpr(0, 0.73, 0, 0, 0, 0)
                self.fakeSnowball.reparentTo(self.vModel.exposeJoint(None, "modelRoot", "Bone.011"))
                base.playSfx(self.soundPickup)
                self.hasSnowball = True
                break

    def exitCatch(self):
        self.vModel.stop()
        if self.ival:
            self.ival.pause()
            self.ival = None

    def start(self):
        # Black crosshair because basically the entire arena is white.
        self.crosshair = getCrosshair(color = (0, 0, 0, 1), hidden = False)

        self.soundCatch = base.loadSfx("phase_4/audio/sfx/MG_sfx_vine_game_catch.ogg")

        self.vModelRoot = camera.attachNewNode('vModelRoot')
        self.vModelRoot.setPos(-0.09, 1.38, -2.48)

        self.vModel = Actor("phase_4/models/minigames/v_dgm.egg",
                            {"hold": "phase_4/models/minigames/v_dgm-ball-hold.egg",
                             "hold-start": "phase_4/models/minigames/v_dgm-ball-hold-start.egg",
                             "throw": "phase_4/models/minigames/v_dgm-ball-throw.egg",
                             "catch": "phase_4/models/minigames/v_dgm-ball-catch.egg"})
        self.vModel.setBlend(frameBlend = True)
        self.vModel.reparentTo(self.vModelRoot)
        self.vModel.setBin("fixed", 40)
        self.vModel.setDepthTest(False)
        self.vModel.setDepthWrite(False)
        self.vModel.hide()

        base.localAvatar.walkControls.setWalkSpeed(ToonForwardSpeed, ToonJumpForce,
                                                   ToonReverseSpeed, ToonRotateSpeed)

        FirstPerson.start(self)

    def reallyStart(self):
        FirstPerson.reallyStart(self)
        base.localAvatar.startTrackAnimToSpeed()

        self.accept('mouse3', self.__handleCatchOrGrabButton)
        self.accept('mouse1', self.__handleThrowButton)

    def __handleThrowButton(self):
        if self.hasSnowball and self.mySnowball and self.fsm.getCurrentState().getName() == 'hold':
            self.fakeSnowball.reparentTo(hidden)
            self.fsm.request('throw')

    def __handleCatchOrGrabButton(self):
        if not self.hasSnowball and not self.mySnowball and self.fsm.getCurrentState().getName() == 'off':
            self.fsm.request('catch')

    def reallyEnd(self):
        base.localAvatar.setWalkSpeedNormal()
        FirstPerson.reallyEnd(self)
