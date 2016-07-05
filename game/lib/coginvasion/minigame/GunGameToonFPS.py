"""

  Filename: GunGameToonFPS.py
  Created by: blach (30Mar15)

"""

import ToonFPS
from GunGameBullet import GunGameBullet
from direct.distributed.ClockDelta import globalClockDelta
import GunGameGlobals as GGG
import random

from lib.coginvasion.gui.KOTHGui import KOTHGui

class GunGameToonFPS(ToonFPS.ToonFPS):

    def __init__(self, mg, weaponName = "pistol"):
        self.kills = 0
        self.deaths = 0
        self.points = 0
        self.kothGui = None
        ToonFPS.ToonFPS.__init__(self, mg, weaponName)

    def load(self):
        ToonFPS.ToonFPS.load(self)
        if self.weaponName in ['shotgun', 'sniper']:
            if self.mg.gameMode in GGG.FFA_MODES:
                color = random.choice(GGG.TeamColorById.values())
            else:
                color = GGG.TeamColorById[self.mg.team]
            self.weapon.setColorScale(color)
            
        if self.mg.gameMode == GGG.GameModes.KOTH:
            self.kothGui = KOTHGui()
            
    def setKOTHPoints(self, points):
        if self.kothGui:
            self.kothGui.setPoints(points)

    def resetStats(self):
        self.points = 0
        self.kills = 0
        self.deaths = 0
        self.gui.updateStats()

    def enterAlive(self):
        pos, hpr = self.mg.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.walkControls.setCollisionsActive(1)
        
        if self.kothGui:
            self.kothGui.show()
        
        ToonFPS.ToonFPS.enterAlive(self)
        if self.mg.fsm.getCurrentState().getName() == "play":
            self.mg.sendUpdate("respawnAvatar", [base.localAvatar.doId])

    def enterDead(self, killer):
        base.localAvatar.walkControls.setCollisionsActive(0)
        if self.mg.gameMode == GGG.GameModes.CTF:
            if self.mg.localAvHasFlag:
                x, y, z = base.localAvatar.getPos(render)
                self.mg.getFlagOfOtherTeam(self.mg.team).b_dropFlag(x, y, z + 1)
        self.deaths += 1
        self.updatePoints()
        self.gui.updateStats()
        
        if self.kothGui:
            self.kothGui.hide()
        
        self.mg.getMyRemoteAvatar().fsm.request('die', [0])
        ToonFPS.ToonFPS.enterDead(self, killer)

    def doFreezeCam(self):
        ToonFPS.ToonFPS.doFreezeCam(self)
        taskMgr.doMethodLater(
            3.0,
            self.respawnAfterDeathTask,
            "respawnAfterDeath"
        )

    def respawnAfterDeathTask(self, task):
        self.fsm.request('alive')
        return task.done

    def exitDead(self):
        taskMgr.remove("respawnAfterDeath")
        ToonFPS.ToonFPS.exitDead(self)
        self.mg.getMyRemoteAvatar().exitDead()
        self.mg.getMyRemoteAvatar().fsm.requestFinalState()

    def cleanup(self):
        taskMgr.remove("respawnAfterDeath")
        self.kills = None
        self.deaths = None
        self.points = None
        
        # Let's clean up the GUI if we need to.
        if self.kothGui:
            self.kothGui.destroy()
            self.kothGui = None
        
        ToonFPS.ToonFPS.cleanup(self)

    def damageTaken(self, amount, avId):
        # We can't die more than once!
        if self.fsm.getCurrentState().getName() == "dead" and self.hp <= 0:
            return
        self.hp -= amount
        if self.fsm.getCurrentState().getName() != "dead" and self.hp <= 0:
            self.mg.sendUpdate('dead', [avId])
        if self.hp <= 0.0:
            timestamp = globalClockDelta.getFrameNetworkTime()
            self.mg.sendUpdate("deadAvatar", [base.localAvatar.doId, timestamp])
        ToonFPS.ToonFPS.damageTaken(self, amount, avId)

    def killedSomebody(self):
        self.kills += 1
        self.updatePoints()
        self.gui.updateStats()

    def enterShoot(self):
        ToonFPS.ToonFPS.enterShoot(self)
        if self.weaponName == "pistol":
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)
        elif self.weaponName == "shotgun":
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)
        elif self.weaponName == "sniper":
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)
        self.mg.d_gunShot()

    def traverse(self):
        ToonFPS.ToonFPS.traverse(self)
        if self.shooterHandler.getNumEntries() > 0:
            self.shooterHandler.sortEntries()
            hitObj = self.shooterHandler.getEntry(0).getIntoNodePath()
            avId = hitObj.getParent().getPythonTag('player')
            avatar = self.mg.cr.doId2do.get(avId)
            if avatar:
                remoteAvatar = self.mg.getRemoteAvatar(avatar.doId)
                if remoteAvatar:
                    if remoteAvatar.getTeam() == None or remoteAvatar.getTeam() != self.mg.team:
                        # Good, this player isn't on my team. I can damage them.
                        damage = self.calcDamage(avatar)
                        if damage <= 0:
                            # Don't heal the player!
                            damage = 1
                        self.mg.sendUpdate('avatarHitByBullet', [avatar.doId, damage])
