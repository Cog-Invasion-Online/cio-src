"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagManager.py
@author Maverick Liberty
@date July 07, 2015

"""

from src.coginvasion.gags import GagGlobals
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
from src.coginvasion.gags.HL2Shotgun import HL2Shotgun

class GagManager:
       
    gags = {GagGlobals.BirthdayCake : BirthdayCake,
              GagGlobals.CreamPieSlice : CreamPieSlice,
              GagGlobals.WholeCreamPie : WholeCreamPie,
              GagGlobals.TNT : TNT,
              GagGlobals.SeltzerBottle : SeltzerBottle,
              GagGlobals.WholeFruitPie : WholeFruitPie,
              GagGlobals.WeddingCake : WeddingCake,
              GagGlobals.FruitPieSlice : FruitPieSlice,
              GagGlobals.GrandPiano : GrandPiano,
              GagGlobals.Safe : Safe,
              GagGlobals.BambooCane : BambooCane,
              GagGlobals.JugglingBalls : JugglingBalls,
              GagGlobals.Megaphone : Megaphone,
              GagGlobals.Cupcake : Cupcake,
              GagGlobals.TrapDoor : TrapDoor,
              GagGlobals.Quicksand : Quicksand,
              GagGlobals.BananaPeel : BananaPeel,
              GagGlobals.Lipstick : Lipstick,
              GagGlobals.Foghorn : Foghorn,
              GagGlobals.Aoogah : Aoogah,
              GagGlobals.ElephantHorn : ElephantHorn,
              GagGlobals.Opera : Opera,
              GagGlobals.BikeHorn : BikeHorn,
              GagGlobals.Whistle : Whistle,
              GagGlobals.Bugle : Bugle,
              GagGlobals.PixieDust : PixieDust,
              GagGlobals.FlowerPot : FlowerPot,
              GagGlobals.Sandbag : Sandbag,
              GagGlobals.Anvil : Anvil,
              GagGlobals.Geyser : Geyser,
              GagGlobals.BigWeight : BigWeight,
              GagGlobals.StormCloud : StormCloud,
              GagGlobals.WaterGlass : WaterGlass,
              GagGlobals.WaterGun : WaterGun,
              GagGlobals.FireHose : FireHose,
              GagGlobals.SquirtFlower : SquirtingFlower,
              GagGlobals.HL2Shotgun : HL2Shotgun}
        
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
