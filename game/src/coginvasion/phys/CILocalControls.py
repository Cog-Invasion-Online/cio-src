from BaseLocalControls import BaseLocalControls

class CILocalControls(BaseLocalControls):

    def __init__(self):
        BaseLocalControls.__init__(self)
        
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
