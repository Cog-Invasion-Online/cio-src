from src.coginvasion.avatar.BaseActivity import BaseActivity

from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

class PressButton(BaseActivity):

    def doActivity(self):
        startFrame = 38
        pressFrame = 62
        endFrame = 95
        speed = 1.0
        
        def clearForce():
            self.avatar.clearForcedTorsoAnim()
            self.avatar.loop("neutral")
            
        self.avatar.setForcedTorsoAnim("toss")
        self.avatar.loop("neutral")
        
        animTrack = Sequence()
        animTrack.append(ActorInterval(self.avatar, "toss", playRate = speed, startFrame = startFrame, endFrame = pressFrame, partName = "torso-top"))
        animTrack.append(ActorInterval(self.avatar, "toss", playRate = speed, startFrame = pressFrame + 1, endFrame = endFrame, partName = "torso-top"))
        animTrack.append(Func(clearForce))
        return animTrack
