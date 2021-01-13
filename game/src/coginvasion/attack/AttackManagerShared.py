from src.coginvasion.base.Precache import Precacheable
from src.coginvasion.attack.Attacks import ATTACK_NONE

class AttackManagerShared(Precacheable):

    def getAttackClassByID(self, aID):
        return self.AttackClasses.get(aID)

    def getAttackName(self, aID):
        aCls = self.getAttackClassByID(aID)
        if aCls:
            return aCls.Name
        return "Not found"
    
    def getAttackIDByName(self, name):
        """ Fetches an attack ID by its name. Returns ATTACK_NONE if not found. """
        for aID, cls in self.AttackClasses.iteritems():
            if cls.Name == name:
                return aID

        return ATTACK_NONE

    @classmethod
    def doPrecache(cls):
        for aCls in cls.AttackClasses.values():
            aCls.precache()
