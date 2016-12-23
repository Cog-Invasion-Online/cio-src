"""

  Filename: RaceGameMovement.py
  Created by: blach (10Oct14)

"""

from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.task import Task
from src.coginvasion.globals import CIGlobals
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM
import math

class RaceGameMovement(DirectObject):
    MINIMUM_POWER = 0.3
    MINIMUM_KEY_DELAY = 0.015
    POWER_FACTOR = 2.5
    defaultBoostBarColor = (0.4, 0.4, 0.7, 1.0)
    fullBoostBarColor = (0.0, 0.0, 0.7, 1.0)
    RUN_FACTOR = 20.0
    RUN_MAX = 1.0
    RUN_PR_FACTOR = 1.2

    def __init__(self, avatar):
        DirectObject.__init__(self)
        self.avatar = avatar
        self.power = self.MINIMUM_POWER
        self.boost = 0.0
        self.fsm = ClassicFSM('RaceGameMovement', [State('off', self.enterOff, self.exitOff, ['run']),
                            State('run', self.enterRun, self.exitRun, ['fall', 'off']),
                            State('fall', self.enterFall, self.exitFall, ['run', 'off']),
                            State('final', self.enterFinal, self.exitFinal)],
                            'off', 'final')
        self.fsm.enterInitialState()
        self.boostFSM = ClassicFSM('Boost', [State('off', self.enterBoostOff, self.exitBoostOff, ['boost']),
                    State('boost', self.enterBoost, self.exitBoost)],
                    'off', 'off')
        self.boostFSM.enterInitialState()
        self.keysPressed = {"arrow_left": 0,
                        "arrow_right": 0}
        self.startTime = 0.0
        self.endTime = 0.0
        self.fallTrack = None
        self.isStopped = True
        self.isBoosting = False
        return

    def setBoosting(self, value):
        self.isBoosting = value

    def getBoosting(self):
        return self.isBoosting

    def enterBoostOff(self):
        self.ignore("control")

    def exitBoostOff(self):
        pass

    def createGui(self):
        """ Create the GUI that will tell the client how much
        running power they have. """
        self.powerFrame = DirectFrame()
        self.powerBg = OnscreenImage(image=DGG.getDefaultDialogGeom(), scale=(0.5, 1.0, 0.5), pos=(1.02, 0, 0.7), parent=self.powerFrame, color=CIGlobals.DialogColor)
        self.powerBar = DirectWaitBar(barColor=(0, 0.7, 0, 1), range=20.0, value=0, parent=self.powerFrame, scale=(0.15, 0, 1.1), pos=(1.02, 0, 0.66))
        self.powerBar.setR(-90)
        self.powerTitle = DirectLabel(text="POWER", text_scale=0.08, pos=(1.02, 0, 0.85), relief=None, parent=self.powerFrame, text_fg=(1, 1, 0, 1), text_font=CIGlobals.getMickeyFont())

        self.boostFrame = DirectFrame()
        self.boostBg = OnscreenImage(image=DGG.getDefaultDialogGeom(), scale=(0.5, 1.0, 0.5), pos=(0.45, 0, 0.7), parent=self.boostFrame, color=CIGlobals.DialogColor)
        self.boostBar = DirectWaitBar(barColor=self.defaultBoostBarColor, range=10, value=0, parent=self.boostFrame, scale=(0.15, 0, 1.1), pos=(0.45, 0, 0.66))
        self.boostBar.setR(-90)
        self.boostTitle = DirectLabel(text="BOOST", text_scale=0.08, pos=(0.45, 0, 0.85), relief=None, parent=self.boostFrame, text_fg=(1, 1, 0, 1), text_font=CIGlobals.getMickeyFont())
        self.boostFullLbl = DirectLabel(text="BOOST READY", text_scale=0.065, pos=(0.45, 0, 0.3), relief=None, parent=self.boostFrame, text_fg=self.fullBoostBarColor,
                    text_shadow=(0.4, 0.4, 0.4, 1.0), text_font=CIGlobals.getToonFont())
        self.boostFullLbl.hide()

    def deleteGui(self):
        """ Delete the GUI that will tell the client how much
        running power they have. """
        self.powerFrame.destroy()
        self.powerBg.destroy()
        self.powerBar.destroy()
        self.powerTitle.destroy()
        self.boostFrame.destroy()
        self.boostBg.destroy()
        self.boostBar.destroy()
        self.boostTitle.destroy()
        self.boostFullLbl.destroy()

    def enableArrowKeys(self):
        """ Enable the arrow keys to increase movement power. """
        self.accept("arrow_left", self.keyPressed, ["arrow_left"])
        self.accept("arrow_right", self.keyPressed, ["arrow_right"])

    def disableArrowKeys(self):
        """ Disable the arrow keys to increase movement power. """
        self.ignore("arrow_left")
        self.ignore("arrow_right")

    def boostKeyPressed(self):
        self.boostFullLbl.hide()
        self.boostFSM.request('boost')

    def keyPressed(self, key):
        """ Figure out which key was pressed and increment the movement power
        if the values of both keys are 1. Also, make the avatar fall down if
        the time between key presses is too fast or the avatar pressed the same
        key more than once."""
        self.stopDelayTimer()
        if self.keysPressed[key] == 1 or self.isTooFast():
            self.resetKeys()
            self.fsm.request('fall')
            return
        self.keysPressed[key] = 1
        if self.keysPressed["arrow_left"] == 1 and self.keysPressed["arrow_right"] == 1:
            self.resetKeys()
            self.changePower()
            self.restartDelayTimer()

    def enterBoost(self):
        self.disableArrowKeys()
        self.resetKeys()
        base.localAvatar.b_setAnimState("swim")
        self.power = 30.0
        taskMgr.add(self.boostTask, 'boostTask')
        self.boostSfx = base.loadSfx("phase_6/audio/sfx/KART_turboLoop.ogg")
        base.playSfx(self.boostSfx, looping = 1)

    def exitBoost(self):
        self.enableArrowKeys()
        base.localAvatar.b_setAnimState("run")
        self.power = 17.0
        taskMgr.remove('boostTask')
        self.boostSfx.stop()
        del self.boostSfx

    def boostTask(self, task):
        if self.boostBar['value'] <= 0.0:
            self.boostFSM.request('off')
            self.boostBar['barColor'] = self.defaultBoostBarColor
            return task.done
        self.boostBar['value'] -= 0.3
        task.delayTime = 0.05
        return task.again

    def enterFall(self):
        """ The avatar is pressing his arrow keys too fast. Stop running and
        make the avatar fall down. """
        self.avatar.b_setAnimState("fallFWD")
        self.fallTrack = Sequence(Wait(2.5), Func(self.fsm.request, "run"))
        self.fallTrack.start()

    def exitFall(self):
        self.fallTrack.pause()
        self.fallTrack = None

    def isTooFast(self):
        """ Determine if the delay between key presses in seconds is too low. """
        return (self.getDelayTime() < self.MINIMUM_KEY_DELAY)

    def resetKeys(self):
        """ Reset the value of the keys. """
        for key in self.keysPressed:
            self.keysPressed[key] = 0

    def changePower(self):
        """ Increase the avatar's movement power. """
        self.power = self.POWER_FACTOR / self.getDelayTime()
        if self.boostBar['barColor'] != self.fullBoostBarColor:
            if self.power >= self.powerBar['range']:
                self.boostBar['value'] += 0.8
                if self.boostBar['value'] >= self.boostBar['range']:
                    self.boostBar['barColor'] = self.fullBoostBarColor
                    self.boostFullLbl.show()
                    self.acceptOnce("control", self.boostKeyPressed)
        self.powerBar.update(self.power)

    def startDelayTimer(self):
        self.startTime = globalClock.getFrameTime()

    def stopDelayTimer(self):
        self.endTime = globalClock.getFrameTime()

    def resetDelayTimer(self):
        self.startTime = 0.0
        self.endTime = 0.0

    def restartDelayTimer(self):
        self.stopDelayTimer()
        self.resetDelayTimer()
        self.startDelayTimer()

    def getDelayTime(self):
        return self.endTime - self.startTime

    def enterRun(self):
        """ Start moving the avatar, make the avatar run, and
        start tracking the delay between key presses. """
        self.avatar.enableBlend()
        self.avatar.setControlEffect('neutral', self.RUN_MAX)
        self.avatar.setControlEffect('run', 0.0)
        self.avatar.loop('run')
        self.avatar.loop('neutral')
        taskMgr.add(self.move, "move")
        if self.boostBar['barColor'] == self.fullBoostBarColor:
            self.boostFullLbl.show()
            self.acceptOnce("control", self.boostKeyPressed)
        self.startDelayTimer()
        self.enableArrowKeys()
        self.isStopped = False

    def exitRun(self):
        """ Stop moving the avatar, make the avatar stand, and stop
        tracking the delay between key presses. """
        taskMgr.remove("move")
        self.boostFSM.request('off')
        if self.boostBar['barColor'] == self.fullBoostBarColor:
            self.boostFullLbl.hide()
            self.ignore("control")
        self.stopDelayTimer()
        self.resetDelayTimer()
        self.disableArrowKeys()
        self.avatar.disableBlend()
        self.isStopped = True
        self.avatar.setPlayRate(1.0, 'run')
        self.power = self.MINIMUM_POWER
        self.powerBar.update(0)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterFinal(self):
        pass

    def exitFinal(self):
        pass

    def decreasePower(self, task):
        """ Decrease power so the avatar does not keep the same amount
        of power while not tapping the arrow keys. """
        if self.power > self.MINIMUM_POWER:
            self.power -= self.POWER_FACTOR / 0.01
            if self.power < self.MINIMUM_POWER:
                self.power = self.MINIMUM_POWER
        task.delayTime = 0.5
        return Task.again

    def move(self, task):
        """ Move the avatar forward on the Y axis with the current amount of power. """
        dt = globalClock.getDt()
        runEffectRaw = self.power / self.RUN_FACTOR
        runEffect = min(self.RUN_MAX, runEffectRaw)
        neutralEffect = self.RUN_MAX - runEffect
        self.avatar.setControlEffect('run', runEffect)
        self.avatar.setControlEffect('neutral', neutralEffect)
        if runEffectRaw > self.RUN_MAX:
            print runEffectRaw
            self.avatar.setPlayRate(runEffectRaw * self.RUN_PR_FACTOR, 'run')
        else:
            self.avatar.setPlayRate(1.0, 'run')
        self.avatar.setY(self.avatar.getY() + self.power * dt)
        return Task.cont

    def cleanup(self):
        self.fsm.requestFinalState()
