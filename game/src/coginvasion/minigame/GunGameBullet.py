"""

  Filename: GunGameBullet.py
  Created by: blach (30Mar15)

"""

import Bullet

class GunGameBullet(Bullet.Bullet):

    def __init__(self, mg, gunNozzle, local, gunName):
        Bullet.Bullet.__init__(self, mg, gunNozzle, local, gunName)

    def handleCollision(self, entry):
        Bullet.Bullet.handleCollision(self, entry)
        dmg = int(self.damageFactor / self.timeSinceShoot)
        if dmg > self.max_dmg:
            dmg = self.max_dmg
        self.mg.sendUpdate("avatarHitByBullet", [base.localAvatar.doId, dmg])
        self.deleteBullet()
