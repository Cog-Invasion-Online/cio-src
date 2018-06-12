"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagGlobals.py
@author Maverick Liberty
@date July 07, 2015

"""

from panda3d.core import VBase4, Point4, Point3
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.GagType import GagType

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from collections import OrderedDict
import types
import math

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

Throw = "Throw"
Squirt = "Squirt"
Drop = "Drop"
Sound = "Sound"
Lure = "Lure"
ToonUp = "Toon-Up"
Trap = "Trap"

# Data that should be able to be quickly picked up by the client and server.
# Values: [default current supply, default max supply, default damage (or health), and, if necessary, toon-up amount.
gagData = {
    CIGlobals.BirthdayCake : {'health': 10,
        'minDamage' : 48, 
        'maxDamage': 100,
        'minMaxSupply' : 3,
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Throw},
    CIGlobals.TNT : {'minDamage' : 90, 
        'maxDamage': 180, 
        'maxSupply': 2, 
        'supply': 2, 
    'track' : Trap},
    CIGlobals.FireHose : {'health': 6,
        'minDamage' : 27,
        'maxDamage' : 30,
        'minMaxSupply' : 3,
        'maxSupply' : 7,
        'supply' : 3,
    'track' : Squirt},
    CIGlobals.Geyser : {'damage': 105, 
        'maxSupply': 1, 
        'supply': 1, 
    'track' : Squirt},
    CIGlobals.BananaPeel : {'minDamage': 10,
        'maxDamage' : 12,
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Trap},
    CIGlobals.Lipstick : {'healRange': (25, 30),
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : ToonUp},
    CIGlobals.Anvil : {'damage': 30,
        'minMaxSupply' : 5,
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Drop},
    CIGlobals.WaterGun : {'health': 2,
        'minDamage' : 10,
        'maxDamage': 12, 
        'minMaxSupply': 5,
        'maxSupply' : 20, 
        'supply': 5, 
    'track' : Squirt},
    CIGlobals.JugglingBalls : {'healRange': (90, 120),
        'maxSupply': 3, 
        'supply': 3, 
    'track' : ToonUp},
    CIGlobals.Safe : {'damage': 60,
        'minMaxSupply' : 3,
        'maxSupply': 7, 
        'supply': 3, 
    'track' : Drop},
    CIGlobals.WholeCreamPie : {'health': 5, 
        'minDamage': 36,
        'maxDamage' : 40, 
        'minMaxSupply': 3,
        'maxSupply' : 7, 
        'supply': 3, 
    'track' : Throw},
    CIGlobals.WholeFruitPie : {'health': 3,
        'minDamage' : 24,
        'damage': 27, 
        'minMaxSupply' : 5,
        'maxSupply': 15, 
        'supply': 5,
    'track' : Throw},
    CIGlobals.SquirtFlower : {'minDamage': 3, 
        'maxDamage' : 4,
        'minMaxSupply' : 10,
        'maxSupply' : 30,
        'supply': 10, 
    'track' : Squirt},
    CIGlobals.BikeHorn : {'minDamage': 3,
        'maxDamage' : 4,
        'minMaxSupply' : 10, 
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Sound},
    CIGlobals.TrapDoor : {'minDamage' : 60,
        'maxDamage': 70, 
        'minMaxSupply' : 3,
        'maxSupply': 5, 
        'supply': 3, 
    'track' : Trap},
    CIGlobals.FlowerPot : {'damage' : 10,
        'minMaxSupply' : 10,
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Drop},
    CIGlobals.Aoogah : {'minDamage': 14,
        'maxDamage' : 16,
        'minMaxSupply' : 5, 
        'maxSupply': 15, 
        'supply': 5, 
    'track' : Sound},
    CIGlobals.Megaphone : {'healRange': (10, 20),
        'minMaxSupply' : 5,
        'maxSupply': 25, 
        'supply': 5, 
    'track' : ToonUp},
    CIGlobals.Opera : {'damage': 90, 
        'maxSupply': 1, 
        'supply': 1, 
    'track' : Sound},
    CIGlobals.BambooCane : {'healRange': (40, 45),
        'minMaxSupply' : 5,
        'maxSupply' : 15,
        'supply': 5, 
    'track' : ToonUp},
    CIGlobals.Cupcake : {'health': 1, 
        'minDamage' : 4, 
        'maxDamage': 6,
        'minMaxSupply' : 10,
        'maxSupply': 30, 
        'supply': 10, 
    'track' : Throw},
    CIGlobals.Bugle : {'minDamage': 9,
        'maxDamage' : 11,
        'minMaxSupply' : 5, 
        'maxSupply': 20,
        'supply': 5, 
    'track' : Sound},
    CIGlobals.Sandbag : {'damage': 18,
        'minMaxSupply' : 5, 
        'maxSupply': 25, 
        'supply': 5, 
    'track' : Drop},
    CIGlobals.WaterGlass : {'health': 2, 
        'minDamage': 6, 
        'maxDamage' : 8,
        'minMaxSupply': 5, 
        'maxSupply': 25, 
        'supply' : 5,
    'track' : Squirt},
    CIGlobals.SeltzerBottle : {'health': 5,
        'minDamage' : 18,
        'maxDamage' : 21,
        'minMaxSupply' : 5,
        'maxSupply' : 15,
        'supply' : 10, 
    'track' : Squirt},
    CIGlobals.PixieDust : {'healRange': (50, 70),
        'minMaxSupply' : 3,
        'maxSupply': 7, 
        'supply': 3, 
    'track' : ToonUp},
    CIGlobals.Foghorn : {'minDamage': 25,
        'maxDamage' : 50, 
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Sound},
    CIGlobals.GrandPiano : {'minDamage': 85,
        'maxDamage' : 170,
        'maxSupply' : 3,
        'supply' : 3, 
    'track' : Drop},
    CIGlobals.StormCloud : {'minDamage': 36,
        'maxDamage' : 80, 
        'maxSupply': 3, 
        'supply': 3,
    'track' : Squirt},
    CIGlobals.WeddingCake : {'health': 25, 
        'damage': 120, 
        'maxSupply': 3, 
        'supply': 3, 
    'track' : Throw},
    CIGlobals.ElephantHorn : {'minDamage': 19,
        'maxDamage' : 21, 
        'minMaxSupply': 3,
        'maxSupply' : 7, 
        'supply': 3, 
    'track' : Sound},
    CIGlobals.Whistle : {'minDamage': 5,
        'maxDamage' : 7,
        'minMaxSupply' : 5,
        'maxSupply' : 25, 
        'supply': 5, 
    'track' : Sound},
    CIGlobals.FruitPieSlice : {'health': 1, 
        'minDamage' : 8, 
        'maxDamage': 10,
        'minMaxSupply' : 5, 
        'maxSupply': 25, 
        'supply': 5, 
    'track' : Throw},
    CIGlobals.Quicksand : {'minDamage': 45, 
        'maxDamage' : 50,
        'minMaxSupply': 3, 
        'maxSupply': 10, 
        'supply' : 3,
    'track' : Trap},
    CIGlobals.CreamPieSlice : {'health': 2,
        'minDamage' : 14,
        'maxDamage': 17,
        'minMaxSupply' : 5, 
        'maxSupply': 20, 
        'supply': 5, 
    'track' : Throw},
    CIGlobals.BigWeight : {'damage': 45,
        'minMaxSupply' : 5,
        'maxSupply' : 15, 
        'supply': 5, 
    'track' : Drop},
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
TrackNameById = OrderedDict({0 : ToonUp, 1 : Trap, 2 : Lure, 3 : Sound, 4 : Throw, 5 : Squirt, 6 : Drop})
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

TrackExperienceAmounts = {
    Throw : [10, 50, 400, 2000, 6000, 10000],
    ToonUp: [20, 200, 800, 2000, 6000], # 10000
    Sound : [40, 200, 1000, 2500, 7500, 10000],
    Drop: [20, 100, 500, 2000, 6000, 10000],
    Trap: [20, 800, 2000, 6000],#100, 800, 2000, 6000, 10000],
    Squirt: [10, 50, 400, 2000, 6000, 10000],
    Lure: [20, 100, 800, 2000, 6000, 10000]
}

def getTrackHighestExperience(track):
    exps = TrackExperienceAmounts[track]
    return exps[len(exps) - 1]

def calculateMaxSupply(avatar, name, data):
    """ This calculates the max supply an avatar can hold with their experience """
    maxSupply = data.get('maxSupply')
    minMaxSupply = maxSupply
    
    if 'minMaxSupply' in data.keys():
        minMaxSupply = data.get('minMaxSupply')
    
    if not avatar is None and minMaxSupply != maxSupply:
        track = data.get('track')
        trackExp = avatar.trackExperience.get(track)
        
        if trackExp == 0:
            return int(minMaxSupply)
        elif trackExp >= MaxedTrackExperiences[track]:
            return int(maxSupply)
        
        trackExperiences = TrackExperienceAmounts.get(track)
        gagIndex = TrackGagNamesByTrackName.get(track).index(name)
        unlockAtExp = float(trackExperiences[gagIndex])
        
        increaseEvery = float(unlockAtExp / maxSupply)
        increaseAmt = (float(trackExp - unlockAtExp) / increaseEvery)
        
        #print '{0} Experience: {1}, Gag Name: {2}, Unlock At Exp: {3}, Max Supply: {4}, Increase Every: {5}, Increase Amount: {6}'.format(
        #    str(track), str(trackExp), name, str(unlockAtExp), str(maxSupply), str(increaseEvery), str(increaseAmt))
        
        if (minMaxSupply + increaseAmt) > maxSupply:
            #print 'Final Value: ' + str(int(maxSupply))
            return int(maxSupply)
        else:
            #print 'Final Value: ' + str(int(minMaxSupply + increaseAmt))
            return int(minMaxSupply + increaseAmt)
    elif minMaxSupply == maxSupply:
        return int(maxSupply)
    else:
        return int(minMaxSupply)

def calculateDamage(avId, name, data):
    """ This calculates the damage a gag will do on a Cog (This is an AI-side method) """
    avatar = base.air.doId2do.get(avId, None)

    baseDmg = 0
    
    if 'damage' in data.keys():
        baseDmg = float(data.get('damage'))
    elif 'minDamage' in data.keys():
        track = data.get('track')
        trackExp = avatar.trackExperience.get(track)
        
        minDamage = float(data.get('minDamage'))
        maxDamage = float(data.get('maxDamage'))
        gagIndex = TrackGagNamesByTrackName.get(track).index(name)
        unlockAtExp = float(TrackExperienceAmounts.get(track)[gagIndex])
        nextGagUnlockExp = unlockAtExp
        
        if (gagIndex + 1) < len(TrackExperienceAmounts.get(track)):
            nextGagUnlockExp = float(TrackExperienceAmounts.get(track)[gagIndex + 1])
        
        scaleDmgEvery = float((nextGagUnlockExp - unlockAtExp) / (maxDamage - minDamage))
        earnedExpSinceUnlock = float(trackExp - unlockAtExp)
        
        if scaleDmgEvery == 0:
            baseDmg = maxDamage
        else:
            dmgAdditions = math.ceil(earnedExpSinceUnlock / scaleDmgEvery)
            
            if (minDamage + dmgAdditions) > maxDamage:
                baseDmg = maxDamage
            else:
                baseDmg = float(minDamage + dmgAdditions)

    dist = data.get('distance', 10)
    ramp = CIGlobals.calcAttackDamage(data.get('distance', 10), baseDmg)

    print "Base damage is", baseDmg
    print "Distance is", dist
    print "Ramp damage is", ramp

    return ramp

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
DEFAULT_DRAW_SFX = "phase_5/audio/sfx/General_device_appear.ogg"

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

# Expecting a dictionary like so:
# TRACK_NAME : EXP
# Returns a blob of the track data.
def trackExperienceToNetString(tracks):
    dg = PyDatagram()
    
    for track, exp in tracks.iteritems():
        dg.addUint8(TrackNameById.values().index(track))
        dg.addInt16(exp)
    dgi = PyDatagramIterator(dg)
    return dgi.getRemainingBytes()

# Expects a TRACK_NAME : EXP dictionary and the backpack that should get updates.
def processTrackData(trackData, backpack):
    for track, exp in trackData.iteritems():
        expAmounts = TrackExperienceAmounts.get(track)
        gags = TrackGagNamesByTrackName.get(track)
        
        for i in range(len(expAmounts)):
            maxEXP = expAmounts[i]
            if exp >= maxEXP:
                gagAtLevel = gags[i]
                gagId = gagIdByName.get(gagAtLevel)
                
                if not backpack.hasGag(gagAtLevel):
                    backpack.addGag(gagId, 1, None)
                
    for gagId in backpack.gags.keys():
        gagName = gagIds.get(gagId)
        maxSupply = calculateMaxSupply(backpack.avatar, gagName, gagData.get(gagName))
        backpack.setMaxSupply(gagId, maxSupply)

def getTrackExperienceFromNetString(netString):
    dg = PyDatagram(netString)
    dgi = PyDatagramIterator(dg)
    
    tracks = {}
    
    for track in TrackNameById.values():
        tracks[track] = 0
    
    while dgi.getRemainingSize() > 0:
        trackId = dgi.getUint8()
        exp = dgi.getInt16()
        
        tracks[TrackNameById.get(trackId)] = exp
    return tracks

def getMaxExperienceValue(exp, track):
    levels = TrackExperienceAmounts[track]
    
    if exp > -1:
        for i in range(len(levels)):
            if exp < levels[i] or (i == (len(levels) - 1) and exp >= levels[i]):
                return levels[i]
    return -1

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

# The idea here is that tracks with a default exp of -1 aren't unlocked yet.
# Throw and squirt fetch the first max exp amount defined in the TrackExperienceAmounts dict.
DefaultTrackExperiences = {
    ToonUp : -1,
    Trap : -1,
    Lure : -1,
    Sound : -1,
    Throw : 0,
    Squirt : 0,
    Drop : -1
}

MaxedTrackExperiences = {
    ToonUp : getTrackHighestExperience(ToonUp),
    Trap   : getTrackHighestExperience(Trap),
    Lure   : -1,
    Sound  : getTrackHighestExperience(Sound),
    Throw  : getTrackHighestExperience(Throw),
    Squirt : getTrackHighestExperience(Squirt),
    Drop   : getTrackHighestExperience(Drop)
}

MaxGagSlots = 4
InitGagSlots = 2

# Cupcake, squirt flower
InitLoadout = [13, 35]

def getDefaultBackpack(isAI = False):
    defaultBackpack = None
    if not isAI:
        from src.coginvasion.gags.backpack.Backpack import Backpack
        defaultBackpack = Backpack(None)
    else:
        from src.coginvasion.gags.backpack.BackpackAI import BackpackAI
        defaultBackpack = BackpackAI(None)
    cupcake = getGagData(13)
    flower = getGagData(35)
    defaultBackpack.addGag(13, cupcake.get('supply'), cupcake.get('maxSupply'))
    defaultBackpack.addGag(35, flower.get('supply'), flower.get('maxSupply'))
    return defaultBackpack
