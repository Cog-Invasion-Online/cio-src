"""

  Filename: Timer.py
  Created by: blach (19Oct14)

"""

from direct.gui.DirectGui import OnscreenImage, DirectLabel
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals

class Timer:

    def __init__(self):
        try:
            self.Timer_initialized
            return
        except:
            self.Timer_initialized = 1
        self.timer = None
        self.timeLbl = None
        self.initTime = 0
        self.zeroCommand = None
        self.time = 0
        self.timerSeq = None
        return

    def setInitialTime(self, initTime):
        self.initTime = initTime

    def getInitialTime(self):
        return self.initTime

    def setZeroCommand(self, command):
        self.zeroCommand = command

    def getZeroCommand(self):
        return self.zeroCommand

    def startTiming(self):
        seq = Sequence()
        for second in range(self.initTime):
            seq.append(Func(self.setTime, self.initTime - second))
            seq.append(Wait(1.0))
        if self.zeroCommand != None:
            seq.append(Func(self.zeroCommand))
        seq.start()
        self.timerSeq = seq

    def stopTiming(self):
        if self.timerSeq:
            self.timerSeq.pause()
            self.timerSeq = None

    def load(self):
        self.unload()
        timer = loader.loadModel("phase_3.5/models/gui/clock_gui.bam")
        self.timer = OnscreenImage(image=timer.find('**/alarm_clock'), pos=(-0.15, 0, -0.15), scale=0.4, parent=base.a2dTopRight)
        self.timeLbl = DirectLabel(text="0", parent=self.timer, text_scale=0.3, text_pos=(0, -0.13),
                                text_font=CIGlobals.getMickeyFont(), text_fg=(1, 0, 0, 1),
                                relief=None)
        timer.removeNode()
        self.timer.setBin('gui-popup', 60)
        del timer

    def unload(self):
        self.stopTiming()
        if self.timer:
            self.timer.destroy(); self.timer = None
        if self.timeLbl:
            self.timeLbl.destroy(); self.timeLbl = None

    def cleanup(self):
        self.zeroCommand = None
        self.initTime = None
        self.time = None

    def setTime(self, time):
        self.time = time
        if self.timeLbl:
            self.timeLbl['text'] = str(time)
            if len(str(time)) > 2:
                self.timeLbl['text_scale'] = 0.2
                self.timeLbl['text_pos'] = (0, -0.11)
            else:
                self.timeLbl['text_scale'] = 0.3
                self.timeLbl['text_pos'] = (0, -0.13)
