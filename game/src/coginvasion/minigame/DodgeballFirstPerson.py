# Filename: DodgeballFirstPerson.py
# Created by:  blach (18Apr16)

from panda3d.core import Point3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval, Parallel, Wait, LerpPosInterval, LerpQuatInterval

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
        self.waitingOnPickupResp = False
        self.camPivotNode = base.localAvatar.attachNewNode('cameraPivotNode')
        self.camFSM = ClassicFSM.ClassicFSM("DFPCamera",
                                            [State.State('off', self.enterCamOff, self.exitCamOff),
                                             State.State('frozen', self.enterFrozen, self.exitFrozen),
                                             State.State('unfrozen', self.enterUnFrozen, self.exitUnFrozen)],
                                            'off', 'off')
        self.camFSM.enterInitialState()
        self.fsm = ClassicFSM.ClassicFSM("DodgeballFirstPerson",
                                         [State.State("off", self.enterOff, self.exitOff),
                                          State.State("hold", self.enterHold, self.exitHold),
                                          State.State("catch", self.enterCatch, self.exitCatch),
                                          State.State("throw", self.enterThrow, self.exitThrow)],
                                         "off", "off")
        self.fsm.enterInitialState()

        FirstPerson.__init__(self)

    def enterCamOff(self):
        self.releaseSnowball()

    def exitCamOff(self):
        pass

    def releaseSnowball(self):
        if self.hasSnowball:
            if self.mySnowball and not self.mySnowball.isAirborne:
                self.hasSnowball = False
                self.mySnowball.resetSnowball()
                self.mySnowball = None
                self.fsm.request('off')

    def enterFrozen(self):
        self.releaseSnowball()

        self.vModel.hide()
        base.localAvatar.getGeomNode().show()
        camera.wrtReparentTo(self.camPivotNode)
        camHeight = max(base.localAvatar.getHeight(), 3.0)
        nrCamHeight = base.localAvatar.getHeight()
        heightScaleFactor = camHeight * 0.3333333333
        defLookAt = Point3(0.0, 1.5, camHeight)
        idealData = (Point3(0.0, -12.0 * heightScaleFactor, camHeight),
                     defLookAt)
        self.camTrack = Parallel(
            LerpPosInterval(
                camera,
                duration = 1.0,
                pos = idealData[0],
                startPos = camera.getPos(),
                blendType = 'easeOut'
            ),
            LerpQuatInterval(
                camera,
                duration = 1.0,
                hpr = idealData[1],
                startHpr = camera.getHpr(),
                blendType = 'easeOut'
            )
        )
        self.camTrack.start()
        self.max_camerap = 0.0
        self.disableMouse()

    def cameraMovement(self, task):
        if not self.camFSM:
            return task.done
            
        if self.camFSM.getCurrentState().getName() == 'frozen':
            if hasattr(self, 'min_camerap') and hasattr(self, 'max_camerap'):
                md = base.win.getPointer(0)
                x = md.getX()
                y = md.getY()
                if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                    self.camPivotNode.setP(self.camPivotNode.getP() - (y - base.win.getYSize()/2)*0.1)
                    self.camPivotNode.setH(self.camPivotNode.getH() - (x - base.win.getXSize()/2)*0.1)
                    if self.camPivotNode.getP() < self.min_camerap:
                        self.camPivotNode.setP(self.min_camerap)
                    elif self.camPivotNode.getP() > self.max_camerap:
                        self.camPivotNode.setP(self.max_camerap)
                return task.cont
            else:
                return task.done

        return FirstPerson.cameraMovement(self, task)

    def exitFrozen(self):
        self.camTrack.finish()
        del self.camTrack
        self.max_camerap = 90.0
        self.vModel.show()
        self.enableMouse()
        base.localAvatar.stopSmartCamera()

    def enterUnFrozen(self):
        base.localAvatar.getGeomNode().hide()
        self.reallyStart()
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        camera.reparentTo(self.player_node)
        camera.setZ(base.localAvatar.getHeight())

    def exitUnFrozen(self):
        self.end()
        self.enableMouse()

    def enterOff(self):
        if self.vModel:
            self.vModel.hide()
        if self.waitingOnPickupResp:
            taskMgr.add(self.__waitForPickupRespTask, "waitForPickupRespTask")

    def __waitForPickupRespTask(self, task):
        if not self.waitingOnPickupResp:
            if self.hasSnowball:
                self.fsm.request('hold')
            return task.done
        return task.cont

    def exitOff(self):
        if self.vModel:
            self.vModel.show()
        taskMgr.remove("waitForPickupRespTask")

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
                self.waitingOnPickupResp = True
                self.mg.sendUpdate('reqPickupSnowball', [snowball.index])
                break

    def snowballPickupResp(self, flag, idx):
        if flag:
            snowball = self.mg.snowballs[idx]
            snowball.b_pickup()
            self.mySnowball = snowball
            self.fakeSnowball.setPosHpr(0, 0.73, 0, 0, 0, 0)
            self.fakeSnowball.reparentTo(self.vModel.exposeJoint(None, "modelRoot", "Bone.011"))
            base.playSfx(self.soundPickup)
            self.hasSnowball = True
        self.waitingOnPickupResp = False

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

    def end(self):
        base.localAvatar.stopTrackAnimToSpeed()
        self.ignore('mouse3')
        self.ignore('mouse1')
        FirstPerson.end(self)

    def __handleThrowButton(self):
        if self.hasSnowball and self.mySnowball and self.fsm.getCurrentState().getName() == 'hold':
            self.fakeSnowball.reparentTo(hidden)
            self.fsm.request('throw')

    def __handleCatchOrGrabButton(self):
        if not self.hasSnowball and not self.mySnowball and self.fsm.getCurrentState().getName() == 'off':
            self.fsm.request('catch')

    def reallyEnd(self):
        base.localAvatar.setWalkSpeedNormal()
        if self.camFSM:
            self.camFSM.requestFinalState()
            self.camFSM = None
        if self.fsm:
            self.fsm.requestFinalState()
            self.fsm = None
        if self.crosshair:
            self.crosshair.destroy()
            self.crosshair = None
        if self.vModel:
            self.vModel.removeNode()
            self.vModel = None
        if self.vModelRoot:
            self.vModelRoot.removeNode()
            self.vModelRoot = None
        self.soundCatch = None
        FirstPerson.reallyEnd(self)
