from src.coginvasion.attack.Attacks import *

# I don't like this, but it works
if metadata.PROCESS != 'server':
    from src.coginvasion.gagsnew.WholeCreamPie import WholeCreamPie
    from src.coginvasion.cog.attacks.ClipOnTie import ClipOnTie
    from src.coginvasion.gagsnew.HL2Shotgun import HL2Shotgun
    from src.coginvasion.gagsnew.HL2Pistol import HL2Pistol
    from src.coginvasion.gagsnew.TNT import TNT
    from src.coginvasion.gagsnew.Slap import Slap
    from src.coginvasion.cog.attacks.Bomb import Bomb
    from src.coginvasion.gagsnew.GumballBlaster import GumballBlaster
    from src.coginvasion.cog.attacks.PickPocket import PickPocket
else:
    from src.coginvasion.gagsnew.WholeCreamPieAI import WholeCreamPieAI as WholeCreamPie
    from src.coginvasion.cog.attacks.ClipOnTieAI import ClipOnTieAI as ClipOnTie
    from src.coginvasion.gagsnew.HL2ShotgunAI import HL2ShotgunAI as HL2Shotgun
    from src.coginvasion.gagsnew.HL2PistolAI import HL2PistolAI as HL2Pistol
    from src.coginvasion.gagsnew.TNT_AI import TNT_AI as TNT
    from src.coginvasion.gagsnew.SlapAI import SlapAI as Slap
    from src.coginvasion.cog.attacks.Bomb_AI import Bomb_AI as Bomb
    from src.coginvasion.gagsnew.GumballBlaster_AI import GumballBlaster_AI as GumballBlaster
    from src.coginvasion.cog.attacks.PickPocket_AI import PickPocket_AI as PickPocket

from src.coginvasion.base.Precache import Precacheable

class AttackManager(Precacheable):

    AttackClasses = {
        ATTACK_GAG_WHOLECREAMPIE    :   WholeCreamPie,
        ATTACK_CLIPONTIE            :   ClipOnTie,
        ATTACK_HL2SHOTGUN           :   HL2Shotgun,
        ATTACK_HL2PISTOL            :   HL2Pistol,
        ATTACK_GAG_TNT              :   TNT,
        ATTACK_BOMB                 :   Bomb,
        ATTACK_SLAP                 :   Slap,
        ATTACK_GUMBALLBLASTER       :   GumballBlaster,
        ATTACK_PICKPOCKET           :   PickPocket
    }

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
