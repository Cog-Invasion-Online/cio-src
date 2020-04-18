from direct.gui.DirectGui import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpColorScaleInterval

class SplashScreen:

    def __init__(self, doneCallback):
        self.cioimg = OnscreenImage(image = 'materials/engine/coginvasiononline.png')
        self.cioimg.hide()
        self.cioimg.setColorScale(0, 0, 0, 1)
        self.pandaimg = OnscreenImage(image = 'materials/engine/powered_by_panda3d.png')
        self.pandaimg.hide()
        self.pandaimg.setColorScale(0, 0, 0, 1)
        self.discimg = OnscreenImage(image = 'materials/engine/disclaimer.png')
        self.discimg.hide()
        self.discimg.setColorScale(0, 0, 0, 1)
        
        self.doneCallback = doneCallback
        
        self.splashIval = Sequence(
            Func(self.cioimg.show),
            Wait(1.0),
            #Func(base.playMusic, "encntr_suit_HQ_nbrhood"),
            LerpColorScaleInterval(self.cioimg, 1.0, (1, 1, 1, 1), (0, 0, 0, 1)),
            Wait(3),
            LerpColorScaleInterval(self.cioimg, 1.0, (0, 0, 0, 1), (1, 1, 1, 1)),
            Func(self.cioimg.hide),
        
            Func(self.pandaimg.show),
            LerpColorScaleInterval(self.pandaimg, 1.0, (1, 1, 1, 1), (0, 0, 0, 1)),
            Wait(1.0),
            LerpColorScaleInterval(self.pandaimg, 1.0, (0, 0, 0, 1), (1, 1, 1, 1)),
            Func(self.pandaimg.hide),
            
            Func(self.discimg.show),
            LerpColorScaleInterval(self.discimg, 1.0, (1, 1, 1, 1), (0, 0, 0, 1)),
            Wait(3.5),
            LerpColorScaleInterval(self.discimg, 1.0, (0, 0, 0, 1), (1, 1, 1, 1)),
            Func(self.discimg.hide),
            
            Func(self.cleanup),
            Func(self.doneCallback)
        )
        self.splashIval.start()
        
        base.accept('space', self.splashIval.finish)
        
    def cleanup(self):
        base.ignore('space')
        self.splashIval.finish()
        self.splashIval = None
        self.pandaimg.destroy()
        self.pandaimg = None
        self.cioimg.destroy()
        self.cioimg = None
        self.discimg.destroy()
        self.discimg = None
