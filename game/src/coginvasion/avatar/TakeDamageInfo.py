from panda3d.core import Point3

from DamageTypes import DMG_GENERIC

class TakeDamageInfo:
    
    def __init__(self, damagerAvatar = None, attackID = 0, damageAmount = 10,
                 damagePos = Point3(0), damageOrigin = Point3(0), damageType = DMG_GENERIC):
        self.damager = damagerAvatar
        self.attackID = attackID
        self.damageAmount = damageAmount
        self.damageType = damageType
        self.damagePos = damagePos
        self.damageOrigin = damageOrigin
        self.damageDistance = (self.damagePos - self.damageOrigin).length()
