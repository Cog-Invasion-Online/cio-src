########################################
# Filename: GagManager.py
# Created by: DecodedLogic (07Jul15)
########################################

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.BirthdayCake import BirthdayCake
from src.coginvasion.gags.CreamPieSlice import CreamPieSlice
from src.coginvasion.gags.WholeCreamPie import WholeCreamPie
from src.coginvasion.gags.WholeFruitPie import WholeFruitPie
from src.coginvasion.gags.TNT import TNT
from src.coginvasion.gags.SeltzerBottle import SeltzerBottle
from src.coginvasion.gags.FruitPieSlice import FruitPieSlice
from src.coginvasion.gags.WeddingCake import WeddingCake
from src.coginvasion.gags.GrandPiano import GrandPiano
from src.coginvasion.gags.Safe import Safe
from src.coginvasion.gags.BambooCane import BambooCane
from src.coginvasion.gags.JugglingBalls import JugglingBalls
from src.coginvasion.gags.Megaphone import Megaphone
from src.coginvasion.gags.Cupcake import Cupcake
from src.coginvasion.gags.TrapDoor import TrapDoor
from src.coginvasion.gags.Quicksand import Quicksand
from src.coginvasion.gags.BananaPeel import BananaPeel
from src.coginvasion.gags.Lipstick import Lipstick
from src.coginvasion.gags.Foghorn import Foghorn
from src.coginvasion.gags.Aoogah import Aoogah
from src.coginvasion.gags.ElephantHorn import ElephantHorn
from src.coginvasion.gags.Opera import Opera
from src.coginvasion.gags.BikeHorn import BikeHorn
from src.coginvasion.gags.Whistle import Whistle
from src.coginvasion.gags.Bugle import Bugle
from src.coginvasion.gags.PixieDust import PixieDust
from src.coginvasion.gags.Anvil import Anvil
from src.coginvasion.gags.FlowerPot import FlowerPot
from src.coginvasion.gags.Sandbag import Sandbag
from src.coginvasion.gags.Geyser import Geyser
from src.coginvasion.gags.BigWeight import BigWeight
from src.coginvasion.gags.StormCloud import StormCloud
from src.coginvasion.gags.WaterGlass import WaterGlass
from src.coginvasion.gags.WaterGun import WaterGun
from src.coginvasion.gags.FireHose import FireHose
from src.coginvasion.gags.SquirtingFlower import SquirtingFlower

class GagManager:

    def __init__(self):
        self.gags = {CIGlobals.BirthdayCake : BirthdayCake,
                     CIGlobals.CreamPieSlice : CreamPieSlice,
                     CIGlobals.WholeCreamPie : WholeCreamPie,
                     CIGlobals.TNT : TNT,
                     CIGlobals.SeltzerBottle : SeltzerBottle,
                     CIGlobals.WholeFruitPie : WholeFruitPie,
                     CIGlobals.WeddingCake : WeddingCake,
                     CIGlobals.FruitPieSlice : FruitPieSlice,
                     CIGlobals.GrandPiano : GrandPiano,
                     CIGlobals.Safe : Safe,
                     CIGlobals.BambooCane : BambooCane,
                     CIGlobals.JugglingBalls : JugglingBalls,
                     CIGlobals.Megaphone : Megaphone,
                     CIGlobals.Cupcake : Cupcake,
                     CIGlobals.TrapDoor : TrapDoor,
                     CIGlobals.Quicksand : Quicksand,
                     CIGlobals.BananaPeel : BananaPeel,
                     CIGlobals.Lipstick : Lipstick,
                     CIGlobals.Foghorn : Foghorn,
                     CIGlobals.Aoogah : Aoogah,
                     CIGlobals.ElephantHorn : ElephantHorn,
                     CIGlobals.Opera : Opera,
                     CIGlobals.BikeHorn : BikeHorn,
                     CIGlobals.Whistle : Whistle,
                     CIGlobals.Bugle : Bugle,
                     CIGlobals.PixieDust : PixieDust,
                     CIGlobals.FlowerPot : FlowerPot,
                     CIGlobals.Sandbag : Sandbag,
                     CIGlobals.Anvil : Anvil,
                     CIGlobals.Geyser : Geyser,
                     CIGlobals.BigWeight : BigWeight,
                     CIGlobals.StormCloud : StormCloud,
                     CIGlobals.WaterGlass : WaterGlass,
                     CIGlobals.WaterGun : WaterGun,
                     CIGlobals.FireHose : FireHose,
                     CIGlobals.SquirtFlower : SquirtingFlower}
        
    def getGagNameByType(self, gagType):
        for gName, definedType in self.gags.iteritems():
            if definedType == type(gagType):
                return gName

    def getGagByName(self, name):
        for gName in self.gags.keys():
            if gName == name:
                return self.gags.get(name)()

    def getGags(self):
        return self.gags
