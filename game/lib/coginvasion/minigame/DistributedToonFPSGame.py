# Filename: DistributedToonFPSGame.py
# Created by:  blach (30Mar15)

from panda3d.core import Vec4

from direct.interval.IntervalGlobal import Sequence, Func, LerpScaleInterval, LerpColorScaleInterval, Parallel
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.minigame import GunGameGlobals as GGG
from DistributedMinigame import DistributedMinigame

class DistributedToonFPSGame(DistributedMinigame):

    """Abstract class for minigames with FPS controls (client)"""

    notify = directNotify.newCategory("DistributedToonFPSGame")

    def __init__(self, cr):
        try:
            self.DistributedToonFPSGame_initialized
            return
        except:
            self.DistributedToonFPSGame_initialized = 1
        DistributedMinigame.__init__(self, cr)
        self.remoteAvatars = []
        self.myRemoteAvatar = None
        self.myKOTHPoints = 0
        self.KOTHKing = None
        
    def setMyKOTHPoints(self, points):
        self.myKOTHPoints = points
        
    def setKOTHKing(self, avId):
        if avId != 0:
            self.KOTHKing = self.cr.doId2do.get(avId)
        else:
            self.KOTHKing = None
            
    def getKOTHKing(self):
        return self.KOTHKing
    
    def makeSmokeEffect(self, pos):
        """Create a gunsmoke effect at the specified position (pos)"""

        smoke = loader.loadModel("phase_4/models/props/test_clouds.bam")
        smoke.setBillboardAxis()
        smoke.reparentTo(render)
        smoke.setPos(pos)
        smoke.setScale(0.05, 0.05, 0.05)
        smoke.setDepthWrite(False)
        track = Sequence(
            Parallel(
                LerpScaleInterval(smoke, 0.5, (0.1, 0.15, 0.15)),
                LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))),
            Func(smoke.removeNode))
        track.start()
        
    def enterFinalScores(self):
        if self.gameMode == GGG.GameModes.KOTH:
            from lib.coginvasion.gui.KOTHKingGui import KOTHKingGui
            self.finalScoreUI = KOTHKingGui(self, self.KOTHKing, self.myKOTHPoints)
        else:
            DistributedMinigame.enterFinalScores(self)
            
    def finalScores(self, avIdList, scoreList):
        if self.gameMode == GGG.GameModes.KOTH:
            self.finalScoreUI.start()
        else:
            DistributedMinigame.finalScores(self, avIdList, scoreList)
            
    def exitFinalScores(self):
        if self.gameMode == GGG.GameModes.KOTH:
            self.finalScoreUI.destroy()
            print "I should've destroyed"
        else:
            DistributedMinigame.exitFinalScores(self)

    def avatarHitByBullet(self, avId, damage):
        """(Network method) Called when a player gets hit by a bullet (sent by player who gets hit)"""
        
        pass

    def d_gunShot(self):
        """Send out a message that we are shooting our gun (make it happen on other screens)"""

        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('gunShot', [base.localAvatar.doId, timestamp])

    def jumpingAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.jump()

    def getMyRemoteAvatar(self):
        return self.myRemoteAvatar

    def damage(self, amount, avId):
        self.toonFps.damageTaken(amount, avId)

    def setupRemoteAvatar(self, avId):
        # Should be overridden by inheritors.
        pass

    def gunShot(self, avId, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        av = self.getRemoteAvatar(avId)
        if av:
            av.fsm.request('shoot', [ts])

    def deadAvatar(self, avId, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        av = self.getRemoteAvatar(avId)
        if av:
            av.fsm.request('die', [ts])

    def respawnAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.exitDead()
            av.fsm.requestFinalState()

    def getRemoteAvatar(self, avId):
        for avatar in self.remoteAvatars:
            if avatar.avId == avId:
                return avatar
        return None

    def disable(self):
        self.myRemoteAvatar.cleanup()
        self.myRemoteAvatar = None
        for av in self.remoteAvatars:
            av.cleanup()
            del av
        self.remoteAvatars = None
        DistributedMinigame.disable(self)
