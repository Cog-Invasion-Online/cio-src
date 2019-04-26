from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.toon.SmartCamera import SmartCamera
from src.coginvasion.gui.Crosshair import Crosshair
from src.coginvasion.gui.GagSelectionGui import GagSelectionGui

from src.coginvasion.globals import CIGlobals

class BaseLocalAvatar:
    notify = directNotify.newCategory("BaseLocalAvatar")

    def __init__(self):
        self.walkControls = None
        self.smartCamera = SmartCamera()
        self.crosshair = Crosshair()
        self.crosshair.hide()
        self.doId = 0
        self.defaultShard = 0
        self.avatarMovementEnabled = False
        self.isSwimming = False
        self.touchingWater = False
        self.invGui = None
        self.playState = False
        self.battleControls = False
        self.selectedGag = -1
        self.lastSelectedGag = -1
        self.needsToSwitchToGag = None
        self.gagsEnabled = False
        
    def updateAttackAmmo(self, attackId, ammo, maxAmmo, ammo2, maxAmmo2, clip, maxClip):
        if self.invGui:
            self.invGui.update()

    def setupAttacks(self):
        if self.getBattleZone() and (not self.getBattleZone().getGameRules().useBackpack()):
            self.reloadInvGui()
        
    def setEquippedAttack(self, gagId):
        if gagId != -1:
            if self.battleControls:
                self.crosshair.setCrosshair(self.getAttack(gagId).crosshair)
                self.crosshair.show()
                self.b_setLookMode(self.LMCage)
        else:
            # We've unequipped
            if not self.walkControls:
                return
            if self.battleControls:
                self.crosshair.hide()
                self.b_setLookMode(self.LMHead)
            else:
                self.b_setLookMode(self.LMOff)
        if self.invGui:
            self.invGui.update()
        
    def createInvGui(self):
        self.invGui = GagSelectionGui()
        self.invGui.load()
        self.invGui.hide()

    def reloadInvGui(self):
        self.destroyInvGui()
        self.createInvGui()
        if self.areGagsAllowed():
            self.enableGags(0)

    def destroyInvGui(self):
        if self.invGui:
            self.invGui.cleanup()
            self.invGui = None
        
    def handleHealthChange(self, hp, oldHp):
        if self.walkControls:
            if hp < oldHp and self.isFirstPerson():
                self.getFPSCam().doDamageFade(1, 0, 0, (self.getHealth() - hp) / 30.0)

        if hp <= 0 and oldHp > 0:
            # Take appropriate action upon death.
            if self.getBattleZone():
                self.getBattleZone().getGameRules().onPlayerDied()

    def canUseGag(self):
        return (self.getEquippedAttack() != -1
                and self.getAttackAmmo(self.getEquippedAttack()) > 0
                and self.gagsEnabled)
        
    def enableGags(self, andKeys = 0):
        if self.avatarMovementEnabled and andKeys:
            self.enableGagKeys()
            self.selectGag(self.selectedGag, False)
        self.invGui.show()
        self.invGui.enableControls()

    def enableGagKeys(self):
        if not self.areGagsAllowed():
            return

        # Using attacks
        CIGlobals.acceptWithModifiers(self, base.inputStore.PrimaryFire,            self.primaryFirePress)
        CIGlobals.acceptWithModifiers(self, base.inputStore.PrimaryFire + '-up',    self.primaryFireRelease)
        CIGlobals.acceptWithModifiers(self, base.inputStore.SecondaryFire,          self.secondaryFirePress)
        CIGlobals.acceptWithModifiers(self, base.inputStore.SecondaryFire + '-up',  self.secondaryFireRelease)
        CIGlobals.acceptWithModifiers(self, base.inputStore.Reload,                 self.reloadPress)
        CIGlobals.acceptWithModifiers(self, base.inputStore.Reload + '-up',         self.reloadRelease)
        
        self.gagsEnabled = True

    def disableGagKeys(self):
        self.gagsEnabled = False

        CIGlobals.ignoreWithModifiers(self, base.inputStore.PrimaryFire)
        CIGlobals.ignoreWithModifiers(self, base.inputStore.PrimaryFire + '-up')
        CIGlobals.ignoreWithModifiers(self, base.inputStore.SecondaryFire)
        CIGlobals.ignoreWithModifiers(self, base.inputStore.SecondaryFire + '-up')
        CIGlobals.ignoreWithModifiers(self, base.inputStore.Reload)
        CIGlobals.ignoreWithModifiers(self, base.inputStore.Reload + '-up')

    def disableGags(self):
        self.disableGagKeys()
        if self.invGui:
            self.invGui.hide()
            self.invGui.disableControls()
        self.b_setEquippedAttack(-1)
        
    def resetHeadHpr(self, override = False):
        pass
        
    def getBackpack(self):
        return None
        
    def enableAvatarControls(self, wantMouse = 0):
        self.walkControls.enableControls(wantMouse)
        self.avatarMovementEnabled = True
        
    def disableAvatarControls(self, chat = False):
        self.walkControls.disableControls(chat)
        self.avatarMovementEnabled = False
        self.resetSpeeds()
        
    def handleJumpLand(self):
        pass
        
    def handleJumpHardLand(self):
        pass
        
    def startSmartCamera(self):
        self.smartCamera.startUpdateSmartCamera()

    def resetSmartCamera(self):
        self.stopSmartCamera()
        self.startSmartCamera()

    def stopSmartCamera(self):
        self.smartCamera.stopUpdateSmartCamera()

    def detachCamera(self):
        camera.reparentTo(render)
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)

    def printPos(self):
        x, y, z = self.getPos(render)
        h, p, r = self.getHpr(render)
        print "Pos: (%s, %s, %s), Hpr: (%s, %s, %s)" % (x, y, z, h, p, r)
        
    def printPos_cam(self):
        x, y, z = camera.getPos(render)
        h, p, r = camera.getHpr(render)
        print "Pos: (%s, %s, %s), Hpr: (%s, %s, %s)" % (x, y, z, h, p, r)
        
    def setWalkSpeedNormal(self):
        pass

    def setWalkSpeedNormalNoJump(self):
        pass

    def setWalkSpeedSlow(self):
        pass
        
    def setupControls(self):
        pass
        
    def attachCamera(self):
        self.walkControls.attachCamera()
        
    def destroyControls(self):
        if not self.walkControls:
            return
            
        self.walkControls.disableControls()
        self.walkControls.stopControllerUpdate()
        self.walkControls = None
        
    def isMoving(self):
        return self.walkControls.isMoving()
        
    def areGagsAllowed(self):
        state = (self.isFirstPerson() and self.getFPSCam().mouseEnabled) or (self.isThirdPerson() and self.battleControls)
        return (self.avatarMovementEnabled and self.walkControls.controlsEnabled and
                (self.invGui is not None and self.invGui.getCurrentOrNextState() != 'Select') and state)
        
    def collisionsOn(self):
        pass
        
    def collisionsOff(self):
        pass
        
    def startSmooth(self):
        self.notify.warning("Tried to call startSmooth() on the local avatar!")
        
    def b_unEquipGag(self):
        self.b_setEquippedAttack(-1)
       
    def switchToLastSelectedGag(self):
        self.selectGag(self.lastSelectedGag)
        
    def selectGag(self, gagId, record = True):
        if record:
            # Forget this gag if they ran out of ammo
            if self.lastSelectedGag != -1 and self.getAttackAmmo(self.lastSelectedGag) <= 0:
                self.lastSelectedGag = -1
            else:
                self.lastSelectedGag = self.selectedGag
                
        self.selectedGag = gagId
        self.needsToSwitchToGag = gagId
        self.b_setEquippedAttack(gagId)
        
    def setBattleControls(self, flag):
        self.battleControls = flag
        if self.playState:
            self.disableAvatarControls()
            self.enableAvatarControls(1)
        
    def d_broadcastPositionNow(self):
        self.d_clearSmoothing()
        if self.d_broadcastPosHpr:
            self.d_broadcastPosHpr()
        
    def b_setLookMode(self, mode):
        self.setLookMode(mode)
        self.sendUpdate('setLookMode', [mode])
        
    def isFirstPerson(self):
        return self.walkControls.mode == self.walkControls.MFirstPerson and self.battleControls

    def isThirdPerson(self):
        return self.walkControls.mode == self.walkControls.MThirdPerson or not self.battleControls

    def getViewModel(self):
        return self.walkControls.fpsCam.viewModel

    def getFPSCam(self):
        return self.walkControls.fpsCam
        
    def showCrosshair(self):
        self.crosshair.show()
        
    def hideCrosshair(self):
        self.crosshair.hide()
        
    def setupCamera(self):
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
        self.smartCamera.initializeSmartCamera()
        self.smartCamera.initCameraPositions()
        self.smartCamera.setCameraPositionByIndex(0)
        
    def resetSpeeds(self):
        self.walkControls.speed = 0.0
        self.walkControls.rotationSpeed = 0.0
        self.walkControls.slideSpeed = 0.0
        
    def startPlay(self, gags = False, wantMouse = 1):
        if self.playState:
            return
            
        if not self.walkControls.getCollisionsActive():
            self.walkControls.setCollisionsActive(1)
        self.enableAvatarControls(wantMouse)
        
        if gags:
            self.enableGags(1)
        
        self.startPosHprBroadcast()
        self.d_broadcastPositionNow()
        
        self.playState = True
        
    def stopPlay(self):
        if not self.playState:
            return
            
        self.disableGags()
            
        self.collisionsOff()
        if self.walkControls.getCollisionsActive():
            self.walkControls.setCollisionsActive(0, andPlaceOnGround=1)
        self.disableAvatarControls()
        self.stopPosHprBroadcast()

        self.playState = False
