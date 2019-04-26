from src.coginvasion.attack.Attacks import *

from src.coginvasion.gagsnew.WholeCreamPie import WholeCreamPie
from src.coginvasion.cog.attacks.ClipOnTie import ClipOnTie
from src.coginvasion.gagsnew.HL2Shotgun import HL2Shotgun
from src.coginvasion.gagsnew.HL2Pistol import HL2Pistol
from src.coginvasion.gagsnew.TNT import TNT
from src.coginvasion.gagsnew.Slap import Slap
from src.coginvasion.cog.attacks.Bomb import Bomb
from src.coginvasion.gagsnew.GumballBlaster import GumballBlaster
from src.coginvasion.cog.attacks.PickPocket import PickPocket
from src.coginvasion.cog.attacks.Fired import Fired
from src.coginvasion.gagsnew.FireHose import FireHose
from src.coginvasion.cog.attacks.EvilEye import EvilEye
from src.coginvasion.cog.attacks.WaterCooler import WaterCooler
from src.coginvasion.cog.attacks.RedTape import RedTape
from src.coginvasion.cog.attacks.HalfWindsor import HalfWindsor
from src.coginvasion.cog.attacks.Sacked import Sacked
from src.coginvasion.cog.attacks.Hardball import Hardball
from src.coginvasion.cog.attacks.MarketCrash import MarketCrash
from src.coginvasion.cog.attacks.Bite import Bite

from AttackManagerShared import AttackManagerShared

class AttackManager(AttackManagerShared):

    AttackClasses = {
        ATTACK_GAG_WHOLECREAMPIE    :   WholeCreamPie,
        ATTACK_CLIPONTIE            :   ClipOnTie,
        ATTACK_HL2SHOTGUN           :   HL2Shotgun,
        ATTACK_HL2PISTOL            :   HL2Pistol,
        ATTACK_GAG_TNT              :   TNT,
        ATTACK_BOMB                 :   Bomb,
        ATTACK_SLAP                 :   Slap,
        ATTACK_GUMBALLBLASTER       :   GumballBlaster,
        ATTACK_PICKPOCKET           :   PickPocket,
        ATTACK_FIRED                :   Fired,
        ATTACK_GAG_FIREHOSE         :   FireHose,
        ATTACK_EVIL_EYE             :   EvilEye,
        ATTACK_WATER_COOLER         :   WaterCooler,
        ATTACK_RED_TAPE             :   RedTape,
        ATTACK_HALF_WINDSOR         :   HalfWindsor,
        ATTACK_SACKED               :   Sacked,
        ATTACK_HARDBALL             :   Hardball,
        ATTACK_MARKET_CRASH         :   MarketCrash,
        ATTACK_BITE                 :   Bite
    }
