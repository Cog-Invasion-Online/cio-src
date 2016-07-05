"""

  Filename: FactorySneakGameBullet.py
  Created by: blach (30Mar15)

"""

import Bullet

class FactorySneakGameBullet(Bullet.Bullet):

    def __init__(self, mg, gunNozzle, local, gunName):
        Bullet.Bullet.__init__(self, mg, gunNozzle, local, gunName)

    def handleCollision(self, entry):
        Bullet.Bullet.handleCollision(self, entry)

        # TODO:
        # Damage the cog guard that the bullet hit.

        self.deleteBullet()
