########################################
# Filename: GagManager.py
# Created by: DecodedLogic (07Jul15)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags.BirthdayCake import BirthdayCake
from lib.coginvasion.gags.CreamPieSlice import CreamPieSlice
from lib.coginvasion.gags.WholeCreamPie import WholeCreamPie
from lib.coginvasion.gags.WholeFruitPie import WholeFruitPie
from lib.coginvasion.gags.TNT import TNT
from lib.coginvasion.gags.SeltzerBottle import SeltzerBottle
from lib.coginvasion.gags.FruitPieSlice import FruitPieSlice
from lib.coginvasion.gags.WeddingCake import WeddingCake
from lib.coginvasion.gags.GrandPiano import GrandPiano
from lib.coginvasion.gags.Safe import Safe
from lib.coginvasion.gags.BambooCane import BambooCane
from lib.coginvasion.gags.JugglingBalls import JugglingBalls
from lib.coginvasion.gags.Megaphone import Megaphone
from lib.coginvasion.gags.Cupcake import Cupcake
from lib.coginvasion.gags.TrapDoor import TrapDoor
from lib.coginvasion.gags.Quicksand import Quicksand
from lib.coginvasion.gags.BananaPeel import BananaPeel
from lib.coginvasion.gags.Lipstick import Lipstick
from lib.coginvasion.gags.Foghorn import Foghorn
from lib.coginvasion.gags.Aoogah import Aoogah
from lib.coginvasion.gags.ElephantHorn import ElephantHorn
from lib.coginvasion.gags.Opera import Opera
from lib.coginvasion.gags.BikeHorn import BikeHorn
from lib.coginvasion.gags.Whistle import Whistle
from lib.coginvasion.gags.Bugle import Bugle
from lib.coginvasion.gags.PixieDust import PixieDust
from lib.coginvasion.gags.Anvil import Anvil
from lib.coginvasion.gags.FlowerPot import FlowerPot
from lib.coginvasion.gags.Sandbag import Sandbag
from lib.coginvasion.gags.Geyser import Geyser
from lib.coginvasion.gags.BigWeight import BigWeight
from lib.coginvasion.gags.StormCloud import StormCloud
from lib.coginvasion.gags.WaterGlass import WaterGlass
from lib.coginvasion.gags.WaterGun import WaterGun
from lib.coginvasion.gags.FireHose import FireHose
from lib.coginvasion.gags.SquirtingFlower import SquirtingFlower

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
