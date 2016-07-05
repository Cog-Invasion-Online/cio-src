########################################
# Filename: GagGlobals.py
# Created by: DecodedLogic (07Jul15)
########################################

from panda3d.core import VBase4, Point4, Point3
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags.GagType import GagType
import types

# These ids are sent on the wire to capture gags.
gagIds = {0 : CIGlobals.WholeCreamPie, 1 : CIGlobals.CreamPieSlice, 2 : CIGlobals.BirthdayCake, 3 : CIGlobals.TNT,
          4 : CIGlobals.SeltzerBottle, 5 : CIGlobals.WholeFruitPie, 6 : CIGlobals.WeddingCake,
          7 : CIGlobals.FruitPieSlice, 8 : CIGlobals.GrandPiano, 9 : CIGlobals.Safe, 10 : CIGlobals.BambooCane,
          11 : CIGlobals.JugglingBalls, 12 : CIGlobals.Megaphone, 13 : CIGlobals.Cupcake, 14 : CIGlobals.TrapDoor,
          15 : CIGlobals.Quicksand, 16 : CIGlobals.BananaPeel, 17 : CIGlobals.Lipstick, 18 : CIGlobals.Foghorn,
          19 : CIGlobals.Aoogah, 20 : CIGlobals.ElephantHorn, 21 : CIGlobals.Opera, 22 : CIGlobals.BikeHorn,
          23 : CIGlobals.Whistle, 24 : CIGlobals.Bugle, 25 : CIGlobals.PixieDust, 26 : CIGlobals.FlowerPot,
          27 : CIGlobals.Sandbag, 28 : CIGlobals.Anvil, 29 : CIGlobals.Geyser, 30 : CIGlobals.BigWeight,
          31 : CIGlobals.StormCloud, 32 : CIGlobals.WaterGlass, 33 : CIGlobals.WaterGun, 34 : CIGlobals.FireHose,
          35 : CIGlobals.SquirtFlower}
gagIdByName = {v: k for k, v in gagIds.items()}

# Data that should be able to be quickly picked up by the client and server.
# Values: [default current supply, default max supply, default damage (or health), and, if necessary, toon-up amount.
gagData = {
    CIGlobals.BirthdayCake : {'health': 10, 'damage': 75, 'maxSupply': 3, 'supply': 3},
    CIGlobals.TNT : {'damage': 180, 'maxSupply': 3, 'supply': 3},
    CIGlobals.FireHose : {'health': 6, 'damage': 30, 'maxSupply': 5, 'supply': 5},
    CIGlobals.Geyser : {'damage': 105, 'maxSupply': 1, 'supply': 1},
    CIGlobals.BananaPeel : {'damage': 10, 'maxSupply': 10, 'supply': 10},
    CIGlobals.Lipstick : {'healRange': (25, 30), 'maxSupply': 5, 'supply': 5},
    CIGlobals.Anvil : {'damage': 30, 'maxSupply': 8, 'supply': 8},
    CIGlobals.WaterGun : {'health': 2, 'damage': 12, 'maxSupply': 7, 'supply': 7},
    CIGlobals.JugglingBalls : {'healRange': (90, 120), 'maxSupply': 3, 'supply': 3},
    CIGlobals.Safe : {'damage': 60, 'maxSupply': 7, 'supply': 7},
    CIGlobals.WholeCreamPie : {'health': 5, 'damage': 36, 'maxSupply': 7, 'supply': 7},
    CIGlobals.WholeFruitPie : {'health': 3, 'damage': 28, 'maxSupply': 10, 'supply': 10},
    CIGlobals.SquirtFlower : {'damage': 3, 'maxSupply': 15, 'supply': 15},
    CIGlobals.BikeHorn : {'damage': 5, 'maxSupply': 15, 'supply': 15},
    CIGlobals.TrapDoor : {'damage': 70, 'maxSupply': 7, 'supply': 7},
    CIGlobals.FlowerPot : {'damage': 10, 'maxSupply': 12, 'supply': 12},
    CIGlobals.Aoogah : {'damage': 16, 'maxSupply': 7, 'supply': 7},
    CIGlobals.Megaphone : {'healRange': (10, 20), 'maxSupply': 7, 'supply': 7},
    CIGlobals.Opera : {'damage': 90, 'maxSupply': 1, 'supply': 1},
    CIGlobals.BambooCane : {'healRange': (40, 45), 'maxSupply': 4, 'supply': 4},
    CIGlobals.Cupcake : {'health': 1, 'damage': 6, 'maxSupply': 15, 'supply': 15},
    CIGlobals.Bugle : {'damage': 11, 'maxSupply': 10, 'supply': 10},
    CIGlobals.Sandbag : {'damage': 18, 'maxSupply': 10, 'supply': 10},
    CIGlobals.WaterGlass : {'health': 2, 'damage': 8, 'maxSupply': 10, 'supply': 10},
    CIGlobals.SeltzerBottle : {'health': 5, 'damage': 21, 'maxSupply': 10, 'supply': 10},
    CIGlobals.PixieDust : {'healRange': (50, 70), 'maxSupply': 5, 'supply': 5},
    CIGlobals.Foghorn : {'damage': 50, 'maxSupply': 3, 'supply': 3},
    CIGlobals.GrandPiano : {'damage': 170, 'maxSupply': 3, 'supply': 3},
    CIGlobals.StormCloud : {'damage': 60, 'maxSupply': 3, 'supply': 3},
    CIGlobals.WeddingCake : {'health': 25, 'damage': 120, 'maxSupply': 3, 'supply': 3},
    CIGlobals.ElephantHorn : {'damage': 21, 'maxSupply': 5, 'supply': 5},
    CIGlobals.Whistle : {'damage': 7, 'maxSupply': 10, 'supply': 10},
    CIGlobals.FruitPieSlice : {'health': 1, 'damage': 10, 'maxSupply': 10, 'supply': 10},
    CIGlobals.Quicksand : {'damage': 50, 'maxSupply': 7, 'supply': 7},
    CIGlobals.CreamPieSlice : {'health': 2, 'damage': 17, 'maxSupply': 10, 'supply': 10},
    CIGlobals.BigWeight : {'damage': 45, 'maxSupply': 7, 'supply': 7},
}

InventoryIconByName = {CIGlobals.WholeCreamPie : '**/inventory_creampie',
 CIGlobals.BirthdayCake : '**/inventory_cake',
 CIGlobals.CreamPieSlice : '**/inventory_cream_pie_slice',
 CIGlobals.TNT : '**/inventory_tnt',
 CIGlobals.SeltzerBottle : '**/inventory_seltzer_bottle',
 CIGlobals.WholeFruitPie : '**/inventory_fruitpie',
 CIGlobals.WeddingCake : '**/inventory_wedding',
 CIGlobals.FruitPieSlice : '**/inventory_fruit_pie_slice',
 CIGlobals.GrandPiano : '**/inventory_piano',
 CIGlobals.BambooCane : '**/inventory_bamboo_cane',
 CIGlobals.JugglingBalls : '**/inventory_juggling_cubes',
 CIGlobals.Safe : '**/inventory_safe_box',
 CIGlobals.Megaphone : '**/inventory_megaphone',
 CIGlobals.Cupcake : '**/inventory_tart',
 CIGlobals.TrapDoor : '**/inventory_trapdoor',
 CIGlobals.Quicksand : '**/inventory_quicksand_icon',
 CIGlobals.Lipstick : '**/inventory_lipstick',
 CIGlobals.Foghorn : '**/inventory_fog_horn',
 CIGlobals.Aoogah : '**/inventory_aoogah',
 CIGlobals.ElephantHorn : '**/inventory_elephant',
 CIGlobals.Opera : '**/inventory_opera_singer',
 CIGlobals.BikeHorn : '**/inventory_bikehorn',
 CIGlobals.Whistle : '**/inventory_whistle',
 CIGlobals.Bugle : '**/inventory_bugle',
 CIGlobals.PixieDust : '**/inventory_pixiedust',
 CIGlobals.Anvil : '**/inventory_anvil',
 CIGlobals.FlowerPot : '**/inventory_flower_pot',
 CIGlobals.Sandbag : '**/inventory_sandbag',
 CIGlobals.Geyser : '**/inventory_geyser',
 CIGlobals.BigWeight : '**/inventory_weight',
 CIGlobals.StormCloud : '**/inventory_storm_cloud',
 CIGlobals.BananaPeel : '**/inventory_bannana_peel',
 CIGlobals.WaterGlass : '**/inventory_glass_of_water',
 CIGlobals.WaterGun : '**/inventory_water_gun',
 CIGlobals.FireHose : '**/inventory_firehose',
 CIGlobals.SquirtFlower : '**/inventory_squirt_flower'}

Throw = "Throw"
Squirt = "Squirt"
Drop = "Drop"
Sound = "Sound"
Lure = "Lure"
ToonUp = "Toon-Up"
Trap = "Trap"
TrackIdByName = {Throw : GagType.THROW,
                 Squirt : GagType.SQUIRT,
                 Drop : GagType.DROP,
                 Sound : GagType.SOUND,
                 Lure : GagType.LURE,
                 ToonUp : GagType.TOON_UP,
                 Trap : GagType.TRAP}
TrackColorByName = {ToonUp : (211 / 255.0, 148 / 255.0, 255 / 255.0),
 Trap : (249 / 255.0, 255 / 255.0, 93 / 255.0),
 Lure : (79 / 255.0, 190 / 255.0, 76 / 255.0),
 Sound : (93 / 255.0, 108 / 255.0, 239 / 255.0),
 Throw : (255 / 255.0, 145 / 255.0, 66 / 255.0),
 Squirt : (255 / 255.0, 65 / 255.0, 199 / 255.0),
 Drop : (67 / 255.0, 243 / 255.0, 255 / 255.0)}
Type2TrackName = {GagType.TOON_UP : 0, GagType.TRAP : 1, GagType.SOUND : 3, GagType.THROW : 4, GagType.SQUIRT : 5, GagType.DROP : 6}
TrackNameById = {0 : ToonUp, 1 : Trap, 2 : Lure, 3 : Sound, 4 : Throw, 5 : Squirt, 6 : Drop}
TrackGagNamesByTrackName = {Throw : [CIGlobals.Cupcake,
  CIGlobals.FruitPieSlice,
  CIGlobals.CreamPieSlice,
  CIGlobals.WholeFruitPie,
  CIGlobals.WholeCreamPie,
  CIGlobals.BirthdayCake,
  CIGlobals.WeddingCake],
 ToonUp : [CIGlobals.Megaphone,
  CIGlobals.Lipstick,
  CIGlobals.BambooCane,
  CIGlobals.PixieDust,
  CIGlobals.JugglingBalls],
 Sound : [CIGlobals.BikeHorn,
  CIGlobals.Whistle,
  CIGlobals.Bugle,
  CIGlobals.Aoogah,
  CIGlobals.ElephantHorn,
  CIGlobals.Foghorn,
  CIGlobals.Opera],
 Drop : [CIGlobals.FlowerPot,
  CIGlobals.Sandbag,
  CIGlobals.Anvil,
  CIGlobals.BigWeight,
  CIGlobals.Safe,
  CIGlobals.GrandPiano],
 Squirt : [CIGlobals.SquirtFlower,
  CIGlobals.WaterGlass,
  CIGlobals.WaterGun,
  CIGlobals.SeltzerBottle,
  CIGlobals.FireHose,
  CIGlobals.StormCloud,
  CIGlobals.Geyser],
 Trap : [CIGlobals.BananaPeel,
  CIGlobals.Quicksand,
  CIGlobals.TrapDoor,
  CIGlobals.TNT],
 Lure : []}

# These are the splat scales
splatSizes = {
    CIGlobals.WholeCreamPie: 0.5, CIGlobals.WholeFruitPie: 0.45,
    CIGlobals.CreamPieSlice: 0.35, CIGlobals.BirthdayCake: 0.6,
    CIGlobals.WeddingCake: 0.7, CIGlobals.FruitPieSlice: 0.35,
    CIGlobals.SeltzerBottle: 0.6, CIGlobals.Cupcake: 0.25,
    CIGlobals.WaterGlass: 0.35, CIGlobals.WaterGun : 0.35,
    CIGlobals.FireHose: 0.6, CIGlobals.SquirtFlower: 0.2
}

# Let's define some gag sounds.
WHOLE_PIE_SPLAT_SFX = "phase_4/audio/sfx/AA_wholepie_only.ogg"
SLICE_SPLAT_SFX = "phase_5/audio/sfx/AA_slice_only.ogg"
TART_SPLAT_SFX = "phase_3.5/audio/sfx/AA_tart_only.ogg"
PIE_WOOSH_SFX = "phase_3.5/audio/sfx/AA_pie_throw_only.ogg"
WEDDING_SPLAT_SFX = "phase_5/audio/sfx/AA_throw_wedding_cake_cog.ogg"
SELTZER_SPRAY_SFX = "phase_5/audio/sfx/AA_squirt_seltzer.ogg"
SELTZER_HIT_SFX = "phase_4/audio/sfx/Seltzer_squirt_2dgame_hit.ogg"
SELTZER_MISS_SFX = "phase_4/audio/sfx/AA_squirt_seltzer_miss.ogg"
PIANO_DROP_SFX = "phase_5/audio/sfx/AA_drop_piano.ogg"
PIANO_MISS_SFX = "phase_5/audio/sfx/AA_drop_piano_miss.ogg"
SAFE_DROP_SFX = "phase_5/audio/sfx/AA_drop_safe.ogg"
SAFE_MISS_SFX = "phase_5/audio/sfx/AA_drop_safe_miss.ogg"
WEIGHT_DROP_SFX = "phase_5/audio/sfx/AA_drop_bigweight.ogg"
WEIGHT_MISS_SFX = "phase_5/audio/sfx/AA_drop_bigweight_miss.ogg"
ANVIL_DROP_SFX = "phase_5/audio/sfx/AA_drop_anvil.ogg"
ANVIL_MISS_SFX = "phase_4/audio/sfx/AA_drop_anvil_miss.ogg"
BAG_DROP_SFX = "phase_5/audio/sfx/AA_drop_sandbag.ogg"
BAG_MISS_SFX = "phase_5/audio/sfx/AA_drop_sandbag_miss.ogg"
POT_DROP_SFX = "phase_5/audio/sfx/AA_drop_flowerpot.ogg"
POT_MISS_SFX = "phase_5/audio/sfx/AA_drop_flowerpot_miss.ogg"
BAMBOO_CANE_SFX = "phase_5/audio/sfx/AA_heal_happydance.ogg"
JUGGLE_SFX = "phase_5/audio/sfx/AA_heal_juggle.ogg"
SMOOCH_SFX = "phase_5/audio/sfx/AA_heal_smooch.ogg"
TELLJOKE_SFX = "phase_5/audio/sfx/AA_heal_telljoke.ogg"
TRAP_DOOR_SFX = "phase_5/audio/sfx/TL_trap_door.ogg"
QUICKSAND_SFX = "phase_5/audio/sfx/TL_quicksand.ogg"
BANANA_SFX = "phase_5/audio/sfx/TL_banana.ogg"
FALL_SFX = "phase_5/audio/sfx/Toon_bodyfall_synergy.ogg"
FOG_APPEAR_SFX = "phase_5/audio/sfx/mailbox_full_wobble.ogg"
FOG_SFX = "phase_5/audio/sfx/SZ_DD_foghorn.ogg"
ELEPHANT_APPEAR_SFX = "phase_5/audio/sfx/toonbldg_grow.ogg"
ELEPHANT_SFX = "phase_5/audio/sfx/AA_sound_elephant.ogg"
AOOGAH_APPEAR_SFX = "phase_5/audio/sfx/TL_step_on_rake.ogg"
AOOGAH_SFX = "phase_5/audio/sfx/AA_sound_aoogah.ogg"
OPERA_SFX = "phase_5/audio/sfx/AA_sound_Opera_Singer.ogg"
OPERA_HIT_SFX = "phase_5/audio/sfx/AA_sound_Opera_Singer_Cog_Glass.ogg"
BIKE_HORN_APPEAR_SFX = "phase_5/audio/sfx/MG_tag_1.ogg"
BIKE_HORN_SFX = "phase_5/audio/sfx/AA_sound_bikehorn.ogg"
WHISTLE_APPEAR_SFX = "phase_5/audio/sfx/LB_receive_evidence.ogg"
WHISTLE_SFX = "phase_4/audio/sfx/AA_sound_whistle.ogg"
BUGLE_APPEAR_SFX = "phase_4/audio/sfx/m_match_trumpet.ogg"
BUGLE_SFX = "phase_5/audio/sfx/AA_sound_bugle.ogg"
PIXIE_DUST_SFX = "phase_5/audio/sfx/AA_heal_pixiedust.ogg"
GEYSER_HIT_SFX = "phase_5/audio/sfx/AA_squirt_Geyser.ogg"
CLOUD_HIT_SFX = "phase_5/audio/sfx/AA_throw_stormcloud.ogg"
CLOUD_MISS_SFX = "phase_5/audio/sfx/AA_throw_stormcloud_miss.ogg"
SPIT_SFX = "phase_5/audio/sfx/AA_squirt_glasswater.ogg"
WATERGUN_SFX = "phase_5/audio/sfx/AA_squirt_neonwatergun.ogg"
FIREHOSE_SFX = "phase_5/audio/sfx/firehose_spray.ogg"
FLOWER_HIT_SFX = "phase_3.5/audio/sfx/AA_squirt_flowersquirt.ogg"
FLOWER_MISS_SFX = "phase_5/audio/sfx/AA_squirt_flowersquirt_miss.ogg"
NULL_SFX = "phase_3/audio/sfx/null.ogg"

# These are globals for splats.
SPLAT_MDL = "phase_3.5/models/props/splat-mod.bam"
SPLAT_CHAN = "phase_3.5/models/props/splat-chan.bam"
SPRAY_MDL = "phase_3.5/models/props/spray.bam"
SPRAY_LEN = 1.5

# These are all the different colors for splats.
TART_SPLAT_COLOR = VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
CREAM_SPLAT_COLOR = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
CAKE_SPLAT_COLOR = VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
WATER_SPRAY_COLOR = Point4(0.75, 0.75, 1.0, 0.8)

PNT3NEAR0 = Point3(0.01, 0.01, 0.01)
PNT3NORMAL = Point3(1, 1, 1)

# The range these gags extend.
TNT_RANGE = 35
SELTZER_RANGE = 25

# How much gags heal.
WEDDING_HEAL = 25
BDCAKE_HEAL = 10
CREAM_PIE_HEAL = 5
FRUIT_PIE_HEAL = 3
CREAM_PIE_SLICE_HEAL = 2
FRUIT_PIE_SLICE_HEAL = 1
CUPCAKE_HEAL = 1
SELTZER_HEAL = 5
WATERGLASS_HEAL = 2
WATERGUN_HEAL = 4
FIREHOSE_HEAL = 6

# Scales of gags.
CUPCAKE_SCALE = 0.5

def loadProp(phase, name):
    return loader.loadModel('phase_%s/models/props/%s.bam' % (str(phase), name))

def getProp(phase, name):
    return 'phase_%s/models/props/%s.bam' % (str(phase), name)

def getGagByID(gId):
    return gagIds.get(gId)

def getIDByName(name):
    for gId, gName in gagIds.iteritems():
        if gName == name:
            return gId

def getGagData(gagId):
    return gagData.get(getGagByID(gagId))

def getTrackOfGag(arg, getId = False):
    if type(arg) == types.IntType:

        # This is a gag id.
        for trackName, gagList in TrackGagNamesByTrackName.items():

            if getGagByID(arg) in gagList:

                if not getId:
                    # Return the name of the track as a string
                    return trackName
                else:
                    # Return the int ID of the track
                    return TrackIdByName[trackName]

    elif type(arg) == types.StringType:

        # This is a gag name.
        for trackName, gagList in TrackGagNamesByTrackName.items():

            if arg in gagList:

                if not getId:
                    # Return the name of the track as a string
                    return trackName
                else:
                    # Return the int ID of the track
                    return TrackIdByName[trackName]
