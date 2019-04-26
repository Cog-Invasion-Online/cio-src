from BaseLocalControls import BaseLocalControls

class CILocalControls(BaseLocalControls):

    def __init__(self):
        BaseLocalControls.__init__(self)
        
    def getFootstepIval(self, speed):
        # 8 frames in between footsteps in run animation
        # take absolute value, running backwards would give us a negative footstep ival
        if base.localAvatar.playingAnim == 'run':
            return (8 / 24.0) * abs(base.localAvatar.playingRate) 
        elif base.localAvatar.playingAnim == 'walk':
            return (11 / 24.0) * abs(base.localAvatar.playingRate)
        elif base.localAvatar.playingAnim == 'dwalk':
            return (15 / 24.0) * abs(base.localAvatar.playingRate)
            
        return BaseLocalControls.getFootstepIval(self, speed)
        
    def enableControls(self, wantMouse = 0):
        if self.controlsEnabled:
            return
            
        BaseLocalControls.enableControls(self, wantMouse)

        if base.localAvatar.battleControls:
            self.accept(base.inputStore.LastGag, base.localAvatar.switchToLastSelectedGag)
            base.localAvatar.setWalkSpeedNormal()
            self.idealFwd = self.BattleNormalSpeed
            self.idealRev = self.BattleNormalSpeed
            self.fwdSpeed = self.idealFwd
            self.revSpeed = self.idealRev
        else:
            if base.localAvatar.getHealth() > 0: 
                base.localAvatar.setWalkSpeedNormal()
            else:
                base.localAvatar.setWalkSpeedSlow()
