"""

  Filename: FactorySneakGameToonFPS.py
  Created by: blach (30Mar15)

"""

import ToonFPS
from FactorySneakGameBullet import FactorySneakGameBullet

class FactorySneakGameToonFPS(ToonFPS.ToonFPS):

    def __init__(self, mg):
        ToonFPS.ToonFPS.__init__(self, mg)

    def enterShoot(self):
        ToonFPS.ToonFPS.enterShoot(self)
        FactorySneakGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 0, self.weaponName)

    def traverse(self):
        ToonFPS.ToonFPS.traverse(self)
        if self.shooterHandler.getNumEntries() > 0:
            self.shooterHandler.sortEntries()
            hitObj = self.shooterHandler.getEntry(0).getIntoNodePath()
            guard = hitObj.getParent().getPythonTag('guard')
            if guard:
                if guard.getHealth() > 0:
                    damage = self.calcDamage(guard)
                    messenger.send(self.mg.gameWorld.GUARD_SHOT_EVENT, [guard, damage])
