# Filename: RemoteDodgeballAvatar.py
# Created by:  blach (30Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectWaitBar

if game.process == 'client':
    from lib.coginvasion.base import ToontownIntervals

from RemoteAvatar import RemoteAvatar
from DistributedDodgeballGame import TEAM_COLOR_BY_ID

class RemoteDodgeballAvatar(RemoteAvatar):
    """A wrapper around a remote DistributedToon for use in the Dodgeball minigame (client side)"""

    notify = directNotify.newCategory("RemoteDodgeballAvatar")

    def __init__(self, mg, cr, avId):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.health = 100
        self.retrieveAvatar()
        if game.process == 'client':
            self.healthBar = DirectWaitBar(value = 100)
            self.healthBar.setBillboardAxis()
            self.healthBar.reparentTo(self.avatar)
            self.healthBar.setZ(self.avatar.nametag3d.getZ(self.avatar) + 1)
            print "generated health bar"

    def setHealth(self, hp):
        self.avatar.announceHealth(0, self.health - hp)
        self.health = hp
        self.healthBar['value'] = hp
        print self.healthBar['value']
        ToontownIntervals.start(ToontownIntervals.getPulseSmallerIval(self.healthBar, self.mg.uniqueName('RemoteDodgeballAvatar-PulseHPBar')))

    def setTeam(self, team):
        print "set team {0}".format(team)
        RemoteAvatar.setTeam(self, team)
        self.healthBar['barColor'] = TEAM_COLOR_BY_ID[team]
        self.teamText.node().setText("")
        self.teamText.node().setTextColor(TEAM_COLOR_BY_ID[team])

    def cleanup(self):
        self.healthBar.destroy()
        self.healthbar = None
        self.health = None
        RemoteAvatar.cleanup(self)
