from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.interval.IntervalGlobal import LerpColorScaleInterval, LerpScaleInterval, LerpPosInterval, Parallel

from src.coginvasion.globals import CIGlobals

class QuestUpdateGUI(DirectFrame):
    
    MAX_LINES = 4
    LINE_Y_OFFSET = 0.095
    LINE_MINIMUM_POS = (0.0, -(LINE_Y_OFFSET * MAX_LINES) * 1.66666667)
    LINE_MAXIMUM_POS = (0.0, (LINE_Y_OFFSET * (MAX_LINES + 2)))
    
    SHOW_DURATION = 3.0
    FADE_DURATION = 2.0
    
    SHADOW_MODIFIER = 0.45
    YELLOW_COLOR = (243.0 / 255.0, 236.0 / 255.0, 32.0 / 255.0, 1.0)
    ORANGE_COLOR = (241.0 / 255.0, 127.0 / 255.0, 43.0 / 255.0, 1.0)
    
    def __init__(self):
        DirectFrame.__init__(self, parent = aspect2d, pos = (0.0, 0.0, 0.0))
        
        # Dictionary containing OnscreenText and an ival as a value
        self.lines = []
        self.ivalDict = {}
        self.alertSfx = base.loadSfx('phase_5.5/audio/sfx/mailbox_alert.ogg')
        
        self.initialiseoptions(QuestUpdateGUI)
        
    def addLine(self, text, color):
        if len(self.lines) == self.MAX_LINES:
            oldestLine = self.lines[len(self.lines)-1]
            ival = self.ivalDict.get(oldestLine, None)
            ival.finish()
        
        newLine = OnscreenText(parent = self, 
            text = text, 
            fg = color, 
            shadow = (color[0] * self.SHADOW_MODIFIER, color[1] * self.SHADOW_MODIFIER, color[2] * self.SHADOW_MODIFIER, 1.0),
            mayChange = 1,
        font = CIGlobals.getMinnieFont())
        
        newLine.setPos(*self.LINE_MINIMUM_POS)
        
        initScale = (1.0, 1.0, 1.0)
        growScale = (1.15, 1.15, 1.15)
    
        """
        LerpScaleInterval(newLine, 0.5, 
            scale = initScale,
            blendType = 'easeIn',
            bakeInStart = 0),
        """
        
        lineIval = Sequence(
            Func(self.alertSfx.play),
            LerpScaleInterval(newLine, 0.5, 
                scale = initScale,
                startScale = (0.01, 0.01, 0.01),
                blendType = 'easeOut',
                bakeInStart = 0),
            Wait(0.5),
            Wait(self.SHOW_DURATION),
            Parallel(
                LerpPosInterval(newLine, self.FADE_DURATION, 
                    pos = (0.0, 0.0, (self.LINE_Y_OFFSET * (self.MAX_LINES + 1.8))), 
                    blendType = 'easeIn',
                    bakeInStart = 0,
                    other = self),
                LerpColorScaleInterval(newLine, self.FADE_DURATION - 0.5, (1.0, 1.0, 1.0, 0.01), blendType = 'easeIn')
            ),
            Func(self.deleteLine, newLine)
        )
        
        self.lines.insert(0, newLine)
        self.ivalDict.update({newLine : lineIval})

        for i in range(1, len(self.lines)):
            line = self.lines[i]
            
            if not line.isEmpty():
                # Let's reposition this element.
                line.setPos(line.getX(), self.LINE_MINIMUM_POS[1] + (self.LINE_Y_OFFSET * i))
        
        lineIval.start()
        
    def deleteLine(self, line):
        if line in self.lines:
            index = self.lines.index(line)
            lineIval = self.ivalDict.get(line, None)
            
            if lineIval:
                lineIval.pause()
                lineIval = None
            line.destroy()
            self.lines.pop(index)
            self.ivalDict.pop(line)
            
    def clear(self):
        for line in self.lines:
            self.deleteLine(line)
            
    def cleanup(self):
        self.clear()
        self.lines = None
        self.ivalDict = None
        self.alertSfx = None
        DirectFrame.cleanup(self)
