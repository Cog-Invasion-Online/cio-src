from src.coginvasion.attack.Attacks import *

from src.coginvasion.gagsnew.WholeCreamPieAI import WholeCreamPieAI
from src.coginvasion.cog.attacks.ClipOnTieAI import ClipOnTieAI
from src.coginvasion.gagsnew.HL2ShotgunAI import HL2ShotgunAI
from src.coginvasion.gagsnew.HL2PistolAI import HL2PistolAI
from src.coginvasion.gagsnew.TNT_AI import TNT_AI
from src.coginvasion.gagsnew.SlapAI import SlapAI
from src.coginvasion.cog.attacks.Bomb_AI import Bomb_AI
from src.coginvasion.gagsnew.GumballBlaster_AI import GumballBlaster_AI
from src.coginvasion.cog.attacks.PickPocket_AI import PickPocket_AI
from src.coginvasion.cog.attacks.FiredAI import FiredAI
from src.coginvasion.gagsnew.FireHoseAI import FireHoseAI
from src.coginvasion.cog.attacks.EvilEyeAI import EvilEyeAI
from src.coginvasion.cog.attacks.WaterCoolerAI import WaterCoolerAI
from src.coginvasion.cog.attacks.RedTapeAI import RedTapeAI
from src.coginvasion.cog.attacks.HalfWindsorAI import HalfWindsorAI
from src.coginvasion.cog.attacks.SackedAI import SackedAI
from src.coginvasion.cog.attacks.HardballAI import HardballAI
from src.coginvasion.cog.attacks.MarketCrashAI import MarketCrashAI
from src.coginvasion.cog.attacks.BiteAI import BiteAI
from src.coginvasion.gagsnew.SoundAI import SoundAI

from AttackManagerShared import AttackManagerShared

class AttackManagerAI(AttackManagerShared):

    AttackClasses = {
        ATTACK_GAG_WHOLECREAMPIE    :   WholeCreamPieAI,
        ATTACK_CLIPONTIE            :   ClipOnTieAI,
        ATTACK_HL2SHOTGUN           :   HL2ShotgunAI,
        ATTACK_HL2PISTOL            :   HL2PistolAI,
        ATTACK_GAG_TNT              :   TNT_AI,
        ATTACK_BOMB                 :   Bomb_AI,
        ATTACK_SLAP                 :   SlapAI,
        ATTACK_GUMBALLBLASTER       :   GumballBlaster_AI,
        ATTACK_PICKPOCKET           :   PickPocket_AI,
        ATTACK_FIRED                :   FiredAI,
        ATTACK_GAG_FIREHOSE         :   FireHoseAI,
        ATTACK_EVIL_EYE             :   EvilEyeAI,
        ATTACK_WATER_COOLER         :   WaterCoolerAI,
        ATTACK_RED_TAPE             :   RedTapeAI,
        ATTACK_HALF_WINDSOR         :   HalfWindsorAI,
        ATTACK_SACKED               :   SackedAI,
        ATTACK_HARDBALL             :   HardballAI,
        ATTACK_MARKET_CRASH         :   MarketCrashAI,
        ATTACK_BITE                 :   BiteAI,
        ATTACK_SOUND                :   SoundAI
    }
