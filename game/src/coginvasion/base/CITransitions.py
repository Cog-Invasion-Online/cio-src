from panda3d.core import Vec3, AsyncFuture

from direct.showbase.Transitions import Transitions
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import LerpScaleInterval, Sequence, Func

class CITransitions(Transitions):
    
    REFRESH_TIMES = 2
    
    def __init__(self, loader,
                 model=None,
                 scale=3.0,
                 pos=Vec3(0, 0, 0)):
        Transitions.__init__(self, loader, model, scale, pos)
        
    def fadeScreen(self, alpha=0.5):
        Transitions.fadeScreen(self, alpha=alpha)
        self.refreshGraphicsEngine()
        
    def irisIn(self, t=0.5, finishIval=None, blendType='noBlend'):
        status = Transitions.irisIn(self, t=t, finishIval=finishIval, blendType=blendType)
        self.refreshGraphicsEngine()
        return status
    
    def getIrisInInterval(self, t=0.5, finishIval=None, blendType='noBlend'):
        " Similar to #irisIn(), but it returns an irisIn interval. Lacks AsyncFuture support. "

        if (t > 0):
            scale = 0.18 * max(base.a2dRight, base.a2dTop)
            transitionIval = Sequence(
                Func(self.noTransitions),
                Func(self.refreshGraphicsEngine),
                Func(self.loadIris),
                Func(self.iris.reparentTo, aspect2d, DGG.FADE_SORT_INDEX),
                LerpScaleInterval(self.iris, t, scale = scale,
                    startScale = 0.01, blendType=blendType),
                Func(self.iris.detachNode),
            name = self.irisTaskName)

            if finishIval:
                transitionIval.append(finishIval)
            return transitionIval
    
    def refreshGraphicsEngine(self):
        for _ in xrange(self.REFRESH_TIMES):
            base.graphicsEngine.renderFrame()
        