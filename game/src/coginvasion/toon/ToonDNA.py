"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonDNA.py
@author Brian Lach
@date November 10, 2014

"""

from panda3d.core import LVecBase4f

from direct.directnotify.DirectNotifyGlobal import directNotify

import types
from pprint import _id

from src.coginvasion.npc.NPCGlobals import NPC_DNA

# Beta outfit shirt: 137, shorts: 59

class ToonDNA:
    notify = directNotify.newCategory("ToonDNA")
    # The length of the strand must be exactly this:
    requiredStrandLength = 0
    """
    colors = [(1.0, 1.0, 1.0, 1.0),
        (0.96875, 0.691406, 0.699219, 1.0),
        (0.933594, 0.265625, 0.28125, 1.0),
        (0.863281, 0.40625, 0.417969, 1.0),
        (0.710938, 0.234375, 0.4375, 1.0),
        (0.570312, 0.449219, 0.164062, 1.0),
        (0.640625, 0.355469, 0.269531, 1.0),
        (0.996094, 0.695312, 0.511719, 1.0),
        (0.832031, 0.5, 0.296875, 1.0),
        (0.992188, 0.480469, 0.167969, 1.0),
        (0.996094, 0.898438, 0.320312, 1.0),
        (0.996094, 0.957031, 0.597656, 1.0),
        (0.855469, 0.933594, 0.492188, 1.0),
        (0.550781, 0.824219, 0.324219, 1.0),
        (0.242188, 0.742188, 0.515625, 1.0),
        (0.304688, 0.96875, 0.402344, 1.0),
        (0.433594, 0.90625, 0.835938, 1.0),
        (0.347656, 0.820312, 0.953125, 1.0),
        (0.191406, 0.5625, 0.773438, 1.0),
        (0.558594, 0.589844, 0.875, 1.0),
        (0.285156, 0.328125, 0.726562, 1.0),
        (0.460938, 0.378906, 0.824219, 1.0),
        (0.546875, 0.28125, 0.75, 1.0),
        (0.726562, 0.472656, 0.859375, 1.0),
        (0.898438, 0.617188, 0.90625, 1.0),
        (0.7, 0.7, 0.8, 1.0),
        (0.3, 0.3, 0.35, 1.0)]
    
    shirtDNA2shirt = {'00': 'phase_3/maps/desat_shirt_1.mat',
                    '01': 'phase_3/maps/desat_shirt_2.mat',
                    '02': 'phase_3/maps/desat_shirt_3.mat',
                    '03': 'phase_3/maps/desat_shirt_4.mat',
                    '04': 'phase_3/maps/desat_shirt_5.mat',
                    '05': 'phase_3/maps/desat_shirt_6.mat',
                    '06': 'phase_3/maps/desat_shirt_7.mat',
                    '07': 'phase_3/maps/desat_shirt_8.mat',
                    '08': 'phase_3/maps/desat_shirt_9.mat',
                    '09': 'phase_3/maps/desat_shirt_10.mat',
                    '10': 'phase_3/maps/desat_shirt_11.mat',
                    '11': 'phase_3/maps/desat_shirt_12.mat',
                    '12': 'phase_3/maps/desat_shirt_13.mat',
                    '13': 'phase_3/maps/desat_shirt_14.mat',
                    '14': 'phase_3/maps/desat_shirt_15.mat',
                    '15': 'phase_3/maps/desat_shirt_16.mat',
                    '16': 'phase_3/maps/desat_shirt_17.mat',
                    '17': 'phase_3/maps/desat_shirt_18.mat',
                    '18': 'phase_3/maps/desat_shirt_19.mat',
                    '19': 'phase_3/maps/desat_shirt_20.mat',
                    '20': 'phase_3/maps/desat_shirt_21.mat',
                    '21': 'phase_3/maps/desat_shirt_22.mat',
                    '22': 'phase_3/maps/desat_shirt_23.mat',
                    '23': 'phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.mat',
                    '24': 'phase_4/maps/tt_t_chr_shirt_scientistA.mat',
                    '25': 'phase_4/maps/tt_t_chr_shirt_scientistB.mat',
                    '26': 'phase_4/maps/tt_t_chr_shirt_scientistC.mat',
                    '27': 'phase_4/maps/tsashirt.mat'}
    sleeveDNA2sleeve = {'00': 'phase_3/maps/desat_sleeve_1.mat',
                        '01': 'phase_3/maps/desat_sleeve_2.mat',
                        '02': 'phase_3/maps/desat_sleeve_3.mat',
                        '03': 'phase_3/maps/desat_sleeve_4.mat',
                        '04': 'phase_3/maps/desat_sleeve_5.mat',
                        '05': 'phase_3/maps/desat_sleeve_6.mat',
                        '06': 'phase_3/maps/desat_sleeve_7.mat',
                        '07': 'phase_3/maps/desat_sleeve_8.mat',
                        '08': 'phase_3/maps/desat_sleeve_9.mat',
                        '09': 'phase_3/maps/desat_sleeve_10.mat',
                        '10': 'phase_3/maps/desat_sleeve_11.mat',
                        '11': 'phase_3/maps/desat_sleeve_12.mat',
                        '12': 'phase_3/maps/desat_sleeve_13.mat',
                        '13': 'phase_3/maps/desat_sleeve_14.mat',
                        '14': 'phase_3/maps/desat_sleeve_15.mat',
                        '15': 'phase_3/maps/desat_sleeve_16.mat',
                        '16': 'phase_3/maps/desat_sleeve_17.mat',
                        '17': 'phase_3/maps/desat_sleeve_18.mat',
                        '18': 'phase_3/maps/desat_sleeve_19.mat',
                        '19': 'phase_3/maps/desat_sleeve_20.mat',
                        '20': 'phase_3/maps/desat_sleeve_21.mat',
                        '21': 'phase_3/maps/desat_sleeve_22.mat',
                        '22': 'phase_3/maps/desat_sleeve_23.mat',
                        '23': 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.mat',
                        '24': 'phase_4/maps/tt_t_chr_shirtSleeve_scientist.mat',
                        '25': 'phase_4/maps/tsasleeve.mat',}
    shortDNA2short = {'00': 'phase_3/maps/desat_shorts_1.mat',
                    '01': 'phase_3/maps/desat_shorts_2.mat',
                    '02': 'phase_3/maps/desat_shorts_3.mat',
                    '03': 'phase_3/maps/desat_shorts_4.mat',
                    '04': 'phase_3/maps/desat_shorts_5.mat',
                    '05': 'phase_3/maps/desat_shorts_6.mat',
                    '06': 'phase_3/maps/desat_shorts_7.mat',
                    '07': 'phase_3/maps/desat_shorts_8.mat',
                    '08': 'phase_3/maps/desat_shorts_9.mat',
                    '09': 'phase_3/maps/desat_shorts_10.mat',
                    '10': 'phase_3/maps/desat_skirt_1.mat',
                    '11': 'phase_3/maps/desat_skirt_2.mat',
                    '12': 'phase_3/maps/desat_skirt_3.mat',
                    '13': 'phase_3/maps/desat_skirt_4.mat',
                    '14': 'phase_3/maps/desat_skirt_5.mat',
                    '15': 'phase_3/maps/desat_skirt_6.mat',
                    '16': 'phase_3/maps/desat_skirt_7.mat',
                    '17': 'phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.mat',
                    '18': 'phase_4/maps/skirtNew5.mat',
                    '19': 'phase_4/maps/tt_t_chr_avt_skirt_winter1.mat',
                    '20': 'phase_4/maps/tt_t_chr_shorts_scientistA.mat',
                    '21': 'phase_4/maps/tt_t_chr_shorts_scientistB.mat',
                    '22': 'phase_4/maps/tt_t_chr_shorts_scientistC.mat',
                    '23': 'phase_3/maps/desat_shorts_11.mat',
                    '24': 'phase_3/maps/desat_shorts_12.mat',
                    '25': 'phase_3/maps/desat_shorts_13.mat',
                    '26': 'phase_3/maps/desat_shorts_14.mat',
                    '27': 'phase_4/maps/tsashorts.mat',
                    '28': 'phase_4/maps/tsaskirt.mat'}
                    
    
    
    gender2genderDNA = {v: k for k, v in genderDNA2gender.items()}
    animal2animalDNA = {v: k for k, v in animalDNA2animal.items()}
    head2headDNA = {v: k for k, v in headDNA2head.items()}
    color2colorDNA = {v: k for k, v in colorDNA2color.items()}
    torso2torsoDNA = {v: k for k, v in torsoDNA2torso.items()}
    leg2legDNA = {v: k for k, v in legDNA2leg.items()}
    shirt2shirtDNA = {v: k for k, v in shirtDNA2shirt.items()}
    sleeve2sleeveDNA = {v: k for k, v in sleeveDNA2sleeve.items()}
    short2shortDNA = {v: k for k, v in shortDNA2short.items()}

    """

    ShortHeads = ['1', '4', 'dgm_skirt', 'dgs_shorts']
    LongHeads = ['2', '3', 'dgm_shorts', 'dgl_shorts']

    genderDNA2gender = {'00': 'boy',
                        '01': 'girl'}
    animalDNA2animal = {'00': 'cat',
                        '01': 'dog',
                        '02': 'bear',
                        '03': 'rabbit',
                        '04': 'monkey',
                        '05': 'horse',
                        '06': 'pig',
                        '07': 'mouse',
                        '08': 'duck'}
    headDNA2head = {'00': '1',
                    '01': '3',
                    '02': '4',
                    '03': '2',
                    '04': 'dgm_skirt',
                    '05': 'dgm_shorts',
                    '06': 'dgl_shorts',
                    '07': 'dgs_shorts'}
    torsoDNA2torso = {'00': 'dgs_shorts',
                    '01': 'dgm_shorts',
                    '02': 'dgl_shorts',
                    '03': 'dgs_skirt',
                    '04': 'dgm_skirt',
                    '05': 'dgl_skirt'}
    legDNA2leg = {'00': 'dgs',
                '01': 'dgm',
                '02': 'dgl'}

    colorDNA2color = {
        '22': LVecBase4f(0.546875, 0.28125, 0.75, 1),
        '02': LVecBase4f(0.933594, 0.265625, 0.28125, 1),
        '03': LVecBase4f(0.863281, 0.40625, 0.417969, 1),
        '00': LVecBase4f(1, 1, 1, 1),
        '01': LVecBase4f(0.96875, 0.691406, 0.699219, 1),
        '06': LVecBase4f(0.640625, 0.355469, 0.269531, 1),
        '07': LVecBase4f(0.996094, 0.695312, 0.511719, 1),
        '04': LVecBase4f(0.710938, 0.234375, 0.4375, 1),
        '05': LVecBase4f(0.570312, 0.449219, 0.164062, 1),
        '08': LVecBase4f(0.832031, 0.5, 0.296875, 1),
        '09': LVecBase4f(0.992188, 0.480469, 0.167969, 1),
        '24': LVecBase4f(0.898438, 0.617188, 0.90625, 1),
        '25': LVecBase4f(0.7, 0.7, 0.8, 1),
        '26': LVecBase4f(0.3, 0.3, 0.35, 1),
        '20': LVecBase4f(0.285156, 0.328125, 0.726562, 1),
        '21': LVecBase4f(0.460938, 0.378906, 0.824219, 1),
        '11': LVecBase4f(0.996094, 0.957031, 0.597656, 1),
        '10': LVecBase4f(0.996094, 0.898438, 0.320312, 1),
        '13': LVecBase4f(0.550781, 0.824219, 0.324219, 1),
        '12': LVecBase4f(0.855469, 0.933594, 0.492188, 1),
        '15': LVecBase4f(0.304688, 0.96875, 0.402344, 1),
        '14': LVecBase4f(0.242188, 0.742188, 0.515625, 1),
        '17': LVecBase4f(0.347656, 0.820312, 0.953125, 1),
        '16': LVecBase4f(0.433594, 0.90625, 0.835938, 1),
        '19': LVecBase4f(0.558594, 0.589844, 0.875, 1),
        '18': LVecBase4f(0.191406, 0.5625, 0.773438, 1),
        '23': LVecBase4f(0.726562, 0.472656, 0.859375, 1)}

    clothesColorDNA2clothesColor = {
        '30': LVecBase4f(0.447058, 0, 0.90196, 1),
        '22': LVecBase4f(0.996094, 0.957031, 0.597656, 1),
        '02': LVecBase4f(0.710938, 0.234375, 0.4375, 1),
        '03': LVecBase4f(0.992188, 0.480469, 0.167969, 1),
        '00': LVecBase4f(0.933594, 0.265625, 0.28125, 1),
        '01': LVecBase4f(0.863281, 0.40625, 0.417969, 1),
        '06': LVecBase4f(0.242188, 0.742188, 0.515625, 1),
        '07': LVecBase4f(0.433594, 0.90625, 0.835938, 1),
        '04': LVecBase4f(0.996094, 0.898438, 0.320312, 1),
        '05': LVecBase4f(0.550781, 0.824219, 0.324219, 1),
        '08': LVecBase4f(0.347656, 0.820312, 0.953125, 1),
        '09': LVecBase4f(0.191406, 0.5625, 0.773438, 1),
        '28': LVecBase4f(0, 0.2, 0.956862, 1),
        '29': LVecBase4f(0.972549, 0.094117, 0.094117, 1),
        '24': LVecBase4f(0.558594, 0.589844, 0.875, 1),
        '25': LVecBase4f(0.726562, 0.472656, 0.859375, 1),
        '26': LVecBase4f(0.898438, 0.617188, 0.90625, 1),
        '27': LVecBase4f(1, 1, 1, 1),
        '20': LVecBase4f(0.347656, 0.820312, 0.953125, 1),
        '21': LVecBase4f(0.96875, 0.691406, 0.699219, 1),
        '11': LVecBase4f(0.460938, 0.378906, 0.824219, 1),
        '10': LVecBase4f(0.285156, 0.328125, 0.726562, 1),
        '13': LVecBase4f(0.570312, 0.449219, 0.164062, 1),
        '12': LVecBase4f(0.546875, 0.28125, 0.75, 1),
        '15': LVecBase4f(0.996094, 0.695312, 0.511719, 1),
        '14': LVecBase4f(0.640625, 0.355469, 0.269531, 1),
        '17': LVecBase4f(0.992188, 0.480469, 0.167969, 1),
        '16': LVecBase4f(0.832031, 0.5, 0.296875, 1),
        '19': LVecBase4f(0.433594, 0.90625, 0.835938, 1),
        '18': LVecBase4f(0.550781, 0.824219, 0.324219, 1),
        '31': LVecBase4f(0.3, 0.3, 0.35, 1),
        '23': LVecBase4f(0.855469, 0.933594, 0.492188, 1)}

    Sleeves = ['phase_3/maps/desat_sleeve_1.mat',
         'phase_3/maps/desat_sleeve_2.mat',
         'phase_3/maps/desat_sleeve_3.mat',
         'phase_3/maps/desat_sleeve_4.mat',
         'phase_3/maps/desat_sleeve_5.mat',
         'phase_3/maps/desat_sleeve_6.mat',
         'phase_3/maps/desat_sleeve_7.mat',
         'phase_3/maps/desat_sleeve_8.mat',
         'phase_3/maps/desat_sleeve_9.mat',
         'phase_3/maps/desat_sleeve_10.mat',
         'phase_3/maps/desat_sleeve_15.mat',
         'phase_3/maps/desat_sleeve_16.mat',
         'phase_3/maps/desat_sleeve_19.mat',
         'phase_3/maps/desat_sleeve_20.mat',
         'phase_4/maps/female_sleeve1b.mat',
         'phase_4/maps/female_sleeve2.mat',
         'phase_4/maps/female_sleeve3.mat',
         'phase_4/maps/male_sleeve1.mat',
         'phase_4/maps/male_sleeve2_palm.mat',
         'phase_4/maps/male_sleeve3c.mat',
         'phase_4/maps/shirt_Sleeve_ghost.mat',
         'phase_4/maps/shirt_Sleeve_pumkin.mat',
         'phase_4/maps/holidaySleeve1.mat',
         'phase_4/maps/holidaySleeve3.mat',
         'phase_4/maps/female_sleeve1b.mat',
         'phase_4/maps/female_sleeve5New.mat',
         'phase_4/maps/male_sleeve4New.mat',
         'phase_4/maps/sleeve6New.mat',
         'phase_4/maps/SleeveMaleNew7.mat',
         'phase_4/maps/female_sleeveNew6.mat',
         'phase_4/maps/Vday5Sleeve.mat',
         'phase_4/maps/Vda6Sleeve.mat',
         'phase_4/maps/Vday_shirt4sleeve.mat',
         'phase_4/maps/Vday2cSleeve.mat',
         'phase_4/maps/sleeveTieDye.mat',
         'phase_4/maps/male_sleeve1.mat',
         'phase_4/maps/StPats_sleeve.mat',
         'phase_4/maps/StPats_sleeve2.mat',
         'phase_4/maps/ContestfishingVestSleeve1.mat',
         'phase_4/maps/ContestFishtankSleeve1.mat',
         'phase_4/maps/ContestPawSleeve1.mat',
         'phase_4/maps/CowboySleeve1.mat',
         'phase_4/maps/CowboySleeve2.mat',
         'phase_4/maps/CowboySleeve3.mat',
         'phase_4/maps/CowboySleeve4.mat',
         'phase_4/maps/CowboySleeve5.mat',
         'phase_4/maps/CowboySleeve6.mat',
         'phase_4/maps/4thJulySleeve1.mat',
         'phase_4/maps/4thJulySleeve2.mat',
         'phase_4/maps/shirt_sleeveCat7_01.mat',
         'phase_4/maps/shirt_sleeveCat7_02.mat',
         'phase_4/maps/contest_backpack_sleeve.mat',
         'phase_4/maps/Contest_leder_sleeve.mat',
         'phase_4/maps/contest_mellon_sleeve2.mat',
         'phase_4/maps/contest_race_sleeve.mat',
         'phase_4/maps/PJSleeveBlue.mat',
         'phase_4/maps/PJSleeveRed.mat',
         'phase_4/maps/PJSleevePurple.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_desat4.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_party1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_party2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_marathon1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley2.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween3.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween4.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine3.mat',
         'phase_4/maps/tt_t_chr_shirtSleeve_scientist.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mailbox.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trashcan.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_loonyLabs.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_hydrant.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_whistle.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_cogbuster.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated01.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty01.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty02.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotIcon.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotVPIcon.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_jellyBeans.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_doodle.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween5.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloweenTurtle.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_greentoon1.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_getConnectedMoverShaker.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racingGrandPrix.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_bee.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_pirate.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_supertoon.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_vampire.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_dinosaur.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing04.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf03.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated02.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing03.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding3.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley03.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing05.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf04.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween06.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter03.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween07.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter02.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing06.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing07.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf05.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing04.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing05.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated03.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated04.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley04.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley05.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding4.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding05.mat',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_anniversary.mat',
         'phase_4/maps/tsasleeve.mat',
         'phase_4/maps/tsasleeve_dev.mat',
         'phase_14/maps/tt_t_chr_avt_shirtSleeve_betaoutfit.mat']

    maleTopDNA2maleTop = {
        "00": [
            "phase_3/maps/desat_shirt_1.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "01": [
            "phase_3/maps/desat_shirt_2.mat", 
            1, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "02": [
            "phase_3/maps/desat_shirt_3.mat", 
            2, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "03": [
            "phase_3/maps/desat_shirt_4.mat", 
            3, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "04": [
            "phase_3/maps/desat_shirt_5.mat", 
            4, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "05": [
            "phase_3/maps/desat_shirt_6.mat", 
            5, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "06": [
            "phase_3/maps/desat_shirt_9.mat", 
            8, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "20", 
                "09", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "07": [
            "phase_3/maps/desat_shirt_10.mat", 
            9, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "08": [
            "phase_3/maps/desat_shirt_11.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "09": [
            "phase_3/maps/desat_shirt_12.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "10": [
            "phase_3/maps/desat_shirt_15.mat", 
            10, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "100": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween5.mat", 
            101, 
            [
                "27"
            ]
        ], 
        "101": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.mat", 
            102, 
            [
                "27"
            ]
        ], 
        "102": [
            "phase_4/maps/tt_t_chr_avt_shirt_greentoon1.mat", 
            103, 
            [
                "27"
            ]
        ], 
        "103": [
            "phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.mat", 
            104, 
            [
                "27"
            ]
        ], 
        "104": [
            "phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.mat", 
            105, 
            [
                "27"
            ]
        ], 
        "105": [
            "phase_4/maps/tt_t_chr_avt_shirt_bee.mat", 
            106, 
            [
                "27"
            ]
        ], 
        "106": [
            "phase_4/maps/tt_t_chr_avt_shirt_pirate.mat", 
            107, 
            [
                "27"
            ]
        ], 
        "107": [
            "phase_4/maps/tt_t_chr_avt_shirt_supertoon.mat", 
            108, 
            [
                "27"
            ]
        ], 
        "108": [
            "phase_4/maps/tt_t_chr_avt_shirt_vampire.mat", 
            109, 
            [
                "27"
            ]
        ], 
        "109": [
            "phase_4/maps/tt_t_chr_avt_shirt_dinosaur.mat", 
            110, 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_3/maps/desat_shirt_17.mat", 
            0, 
            [
                "27"
            ]
        ], 
        "110": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing04.mat", 
            111, 
            [
                "27"
            ]
        ], 
        "111": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf03.mat", 
            112, 
            [
                "27"
            ]
        ], 
        "112": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.mat", 
            113, 
            [
                "27"
            ]
        ], 
        "113": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing03.mat", 
            114, 
            [
                "27"
            ]
        ], 
        "114": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.mat", 
            115, 
            [
                "27"
            ]
        ], 
        "115": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley03.mat", 
            116, 
            [
                "27"
            ]
        ], 
        "116": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing05.mat", 
            117, 
            [
                "27"
            ]
        ], 
        "117": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf04.mat", 
            118, 
            [
                "27"
            ]
        ], 
        "118": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween06.mat", 
            119, 
            [
                "27"
            ]
        ], 
        "119": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter03.mat", 
            120, 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_3/maps/desat_shirt_18.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12"
            ]
        ], 
        "120": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween07.mat", 
            121, 
            [
                "27"
            ]
        ], 
        "121": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter02.mat", 
            122, 
            [
                "27"
            ]
        ], 
        "122": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing06.mat", 
            123, 
            [
                "27"
            ]
        ], 
        "123": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing07.mat", 
            124, 
            [
                "27"
            ]
        ], 
        "124": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf05.mat", 
            125, 
            [
                "27"
            ]
        ], 
        "125": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing04.mat", 
            126, 
            [
                "27"
            ]
        ], 
        "126": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing05.mat", 
            127, 
            [
                "27"
            ]
        ], 
        "127": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.mat", 
            128, 
            [
                "27"
            ]
        ], 
        "128": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.mat", 
            129, 
            [
                "27"
            ]
        ], 
        "129": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley04.mat", 
            130, 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_3/maps/desat_shirt_19.mat", 
            12, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "20", 
                "09", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "130": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley05.mat", 
            116, 
            [
                "27"
            ]
        ], 
        "131": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.mat", 
            131, 
            [
                "27"
            ]
        ], 
        "132": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.mat", 
            133, 
            [
                "27"
            ]
        ], 
        "133": [
            "phase_4/maps/tt_t_chr_avt_shirt_anniversary.mat", 
            134, 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_3/maps/desat_shirt_20.mat", 
            13, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "27"
            ]
        ], 
        "15": [
            "phase_4/maps/female_shirt3.mat", 
            16, 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/male_shirt1.mat", 
            17, 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/male_shirt2_palm.mat", 
            18, 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/male_shirt3c.mat", 
            19, 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/shirt_ghost.mat", 
            20, 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/shirt_pumkin.mat", 
            21, 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/holiday_shirt1.mat", 
            22, 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/holiday_shirt2b.mat", 
            22, 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/holidayShirt3b.mat", 
            23, 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/holidayShirt4.mat", 
            23, 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/shirtMale4B.mat", 
            26, 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/shirt6New.mat", 
            27, 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/shirtMaleNew7.mat", 
            28, 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/Vday1Shirt5.mat", 
            30, 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/Vday1Shirt6SHD.mat", 
            31, 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/Vday1Shirt4.mat", 
            32, 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/Vday_shirt2c.mat", 
            33, 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/shirtTieDyeNew.mat", 
            34, 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/StPats_shirt1.mat", 
            36, 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/StPats_shirt2.mat", 
            37, 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/ContestfishingVestShirt2.mat", 
            38, 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/ContestFishtankShirt1.mat", 
            39, 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/ContestPawShirt1.mat", 
            40, 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/CowboyShirt1.mat", 
            41, 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/CowboyShirt2.mat", 
            42, 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/CowboyShirt3.mat", 
            43, 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/CowboyShirt4.mat", 
            44, 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/CowboyShirt5.mat", 
            45, 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/CowboyShirt6.mat", 
            46, 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/4thJulyShirt1.mat", 
            47, 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/4thJulyShirt2.mat", 
            48, 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/shirt_Cat7_01.mat", 
            49, 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/shirt_Cat7_02.mat", 
            50, 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/contest_backpack3.mat", 
            51, 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/contest_leder.mat", 
            52, 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/contest_mellon2.mat", 
            53, 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/contest_race2.mat", 
            54, 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/PJBlueBanana2.mat", 
            55, 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/PJRedHorn2.mat", 
            56, 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/PJGlasses2.mat", 
            57, 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine1.mat", 
            58, 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine2.mat", 
            59, 
            [
                "27"
            ]
        ], 
        "57": [
            "phase_4/maps/tt_t_chr_avt_shirt_desat4.mat", 
            60, 
            [
                "27"
            ]
        ], 
        "58": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing1.mat", 
            61, 
            [
                "27"
            ]
        ], 
        "59": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing2.mat", 
            62, 
            [
                "27"
            ]
        ], 
        "60": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening1.mat", 
            63, 
            [
                "27"
            ]
        ], 
        "61": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening2.mat", 
            64, 
            [
                "27"
            ]
        ], 
        "62": [
            "phase_4/maps/tt_t_chr_avt_shirt_party1.mat", 
            65, 
            [
                "27"
            ]
        ], 
        "63": [
            "phase_4/maps/tt_t_chr_avt_shirt_party2.mat", 
            66, 
            [
                "27"
            ]
        ], 
        "64": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing1.mat", 
            67, 
            [
                "27"
            ]
        ], 
        "65": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing2.mat", 
            68, 
            [
                "27"
            ]
        ], 
        "66": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer1.mat", 
            69, 
            [
                "27"
            ]
        ], 
        "67": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer2.mat", 
            70, 
            [
                "27"
            ]
        ], 
        "68": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf1.mat", 
            71, 
            [
                "27"
            ]
        ], 
        "69": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf2.mat", 
            72, 
            [
                "27"
            ]
        ], 
        "70": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween1.mat", 
            73, 
            [
                "27"
            ]
        ], 
        "71": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween2.mat", 
            74, 
            [
                "27"
            ]
        ], 
        "72": [
            "phase_4/maps/tt_t_chr_avt_shirt_marathon1.mat", 
            75, 
            [
                "27"
            ]
        ], 
        "73": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.mat", 
            76, 
            [
                "27"
            ]
        ], 
        "74": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.mat", 
            77, 
            [
                "27"
            ]
        ], 
        "75": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask1.mat", 
            78, 
            [
                "27"
            ]
        ], 
        "76": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask2.mat", 
            79, 
            [
                "27"
            ]
        ], 
        "77": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley1.mat", 
            80, 
            [
                "27"
            ]
        ], 
        "78": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley2.mat", 
            81, 
            [
                "27"
            ]
        ], 
        "79": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter1.mat", 
            82, 
            [
                "27"
            ]
        ], 
        "80": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween3.mat", 
            83, 
            [
                "27"
            ]
        ], 
        "81": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween4.mat", 
            84, 
            [
                "27"
            ]
        ], 
        "82": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine3.mat", 
            85, 
            [
                "27"
            ]
        ], 
        "83": [
            "phase_4/maps/tt_t_chr_shirt_scientistC.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "84": [
            "phase_4/maps/tt_t_chr_shirt_scientistA.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "85": [
            "phase_4/maps/tt_t_chr_shirt_scientistB.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "86": [
            "phase_4/maps/tt_t_chr_avt_shirt_mailbox.mat", 
            87, 
            [
                "27"
            ]
        ], 
        "87": [
            "phase_4/maps/tt_t_chr_avt_shirt_trashcan.mat", 
            88, 
            [
                "27"
            ]
        ], 
        "88": [
            "phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.mat", 
            89, 
            [
                "27"
            ]
        ], 
        "89": [
            "phase_4/maps/tt_t_chr_avt_shirt_hydrant.mat", 
            90, 
            [
                "27"
            ]
        ], 
        "90": [
            "phase_4/maps/tt_t_chr_avt_shirt_whistle.mat", 
            91, 
            [
                "27"
            ]
        ], 
        "91": [
            "phase_4/maps/tt_t_chr_avt_shirt_cogbuster.mat", 
            92, 
            [
                "27"
            ]
        ], 
        "92": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.mat", 
            93, 
            [
                "27"
            ]
        ], 
        "93": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.mat", 
            94, 
            [
                "27"
            ]
        ], 
        "94": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.mat", 
            95, 
            [
                "27"
            ]
        ], 
        "95": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.mat", 
            96, 
            [
                "27"
            ]
        ], 
        "96": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.mat", 
            97, 
            [
                "27"
            ]
        ], 
        "97": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.mat", 
            98, 
            [
                "27"
            ]
        ], 
        "98": [
            "phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.mat", 
            99, 
            [
                "27"
            ]
        ], 
        "99": [
            "phase_4/maps/tt_t_chr_avt_shirt_doodle.mat", 
            100, 
            [
                "27"
            ]
        ],
        "135": [
            "phase_4/maps/tsashirt.mat",
            135,
            [
                "27"
            ]
        ],
        "136": [
            "phase_4/maps/tsashirt_dev.mat",
            136,
            [
                "27"
            ]
        ],
        "137": [
            "phase_14/maps/tt_t_chr_avt_shirt_betaoutfit.mat",
            137,
            [
                "27"
            ]
        ]
    }

    femaleTopDNA2femaleTop = {
        "00": [
            "phase_3/maps/desat_shirt_1.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26", 
                "27"
            ]
        ], 
        "01": [
            "phase_3/maps/desat_shirt_2.mat", 
            1, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "02": [
            "phase_3/maps/desat_shirt_3.mat", 
            2, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "03": [
            "phase_3/maps/desat_shirt_4.mat", 
            3, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "04": [
            "phase_3/maps/desat_shirt_6.mat", 
            5, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "05": [
            "phase_3/maps/desat_shirt_7.mat", 
            6, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "06": [
            "phase_3/maps/desat_shirt_8.mat", 
            7, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "07": [
            "phase_3/maps/desat_shirt_10.mat", 
            9, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "08": [
            "phase_3/maps/desat_shirt_13.mat", 
            0, 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_3/maps/desat_shirt_14.mat", 
            11, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "10": [
            "phase_3/maps/desat_shirt_16.mat", 
            11, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "100": [
            "phase_4/maps/tt_t_chr_avt_shirt_doodle.mat", 
            100, 
            [
                "27"
            ]
        ], 
        "101": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween5.mat", 
            101, 
            [
                "27"
            ]
        ], 
        "102": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.mat", 
            102, 
            [
                "27"
            ]
        ], 
        "103": [
            "phase_4/maps/tt_t_chr_avt_shirt_greentoon1.mat", 
            103, 
            [
                "27"
            ]
        ], 
        "104": [
            "phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.mat", 
            104, 
            [
                "27"
            ]
        ], 
        "105": [
            "phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.mat", 
            105, 
            [
                "27"
            ]
        ], 
        "106": [
            "phase_4/maps/tt_t_chr_avt_shirt_bee.mat", 
            106, 
            [
                "27"
            ]
        ], 
        "107": [
            "phase_4/maps/tt_t_chr_avt_shirt_pirate.mat", 
            107, 
            [
                "27"
            ]
        ], 
        "108": [
            "phase_4/maps/tt_t_chr_avt_shirt_supertoon.mat", 
            108, 
            [
                "27"
            ]
        ], 
        "109": [
            "phase_4/maps/tt_t_chr_avt_shirt_vampire.mat", 
            109, 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_3/maps/desat_shirt_17.mat", 
            0, 
            [
                "27"
            ]
        ], 
        "110": [
            "phase_4/maps/tt_t_chr_avt_shirt_dinosaur.mat", 
            110, 
            [
                "27"
            ]
        ], 
        "111": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing04.mat", 
            111, 
            [
                "27"
            ]
        ], 
        "112": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf03.mat", 
            112, 
            [
                "27"
            ]
        ], 
        "113": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.mat", 
            113, 
            [
                "27"
            ]
        ], 
        "114": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing03.mat", 
            114, 
            [
                "27"
            ]
        ], 
        "115": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.mat", 
            115, 
            [
                "27"
            ]
        ], 
        "116": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley03.mat", 
            116, 
            [
                "27"
            ]
        ], 
        "117": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing05.mat", 
            117, 
            [
                "27"
            ]
        ], 
        "118": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf04.mat", 
            118, 
            [
                "27"
            ]
        ], 
        "119": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween06.mat", 
            119, 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_3/maps/desat_shirt_21.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "120": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter03.mat", 
            120, 
            [
                "27"
            ]
        ], 
        "121": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween07.mat", 
            121, 
            [
                "27"
            ]
        ], 
        "122": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter02.mat", 
            122, 
            [
                "27"
            ]
        ], 
        "123": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing06.mat", 
            123, 
            [
                "27"
            ]
        ], 
        "124": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing07.mat", 
            124, 
            [
                "27"
            ]
        ], 
        "125": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf05.mat", 
            125, 
            [
                "27"
            ]
        ], 
        "126": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing04.mat", 
            126, 
            [
                "27"
            ]
        ], 
        "127": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing05.mat", 
            127, 
            [
                "27"
            ]
        ], 
        "128": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.mat", 
            128, 
            [
                "27"
            ]
        ], 
        "129": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.mat", 
            129, 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_3/maps/desat_shirt_22.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "130": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley04.mat", 
            130, 
            [
                "27"
            ]
        ], 
        "131": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley05.mat", 
            116, 
            [
                "27"
            ]
        ], 
        "132": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.mat", 
            131, 
            [
                "27"
            ]
        ], 
        "133": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.mat", 
            133, 
            [
                "27"
            ]
        ], 
        "134": [
            "phase_4/maps/tt_t_chr_avt_shirt_anniversary.mat", 
            134, 
            [
                "27"
            ]
        ],
        "135": [
            "phase_4/maps/tsashirt.mat",
            135,
            [
                "27"
            ]
        ],
        "136": [
            "phase_4/maps/tsashirt_dev.mat",
            136,
            [
                "27"
            ]
        ],
        "137": [
            "phase_14/maps/tt_t_chr_avt_shirt_betaoutfit.mat",
            137,
            [
                "27"
            ]
        ],
        "14": [
            "phase_3/maps/desat_shirt_23.mat", 
            0, 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "10", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "15": [
            "phase_4/maps/female_shirt1b.mat", 
            24, 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/female_shirt2.mat", 
            15, 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/female_shirt3.mat", 
            16, 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/male_shirt1.mat", 
            35, 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/male_shirt2_palm.mat", 
            18, 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/shirt_ghost.mat", 
            20, 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/shirt_pumkin.mat", 
            21, 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/holiday_shirt1.mat", 
            22, 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/holiday_shirt2b.mat", 
            22, 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/holidayShirt3b.mat", 
            23, 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/holidayShirt4.mat", 
            23, 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/female_shirt5New.mat", 
            25, 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/shirt6New.mat", 
            27, 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/femaleShirtNew6.mat", 
            29, 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/Vday1Shirt5.mat", 
            30, 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/Vday1Shirt6SHD.mat", 
            31, 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/Vday1Shirt4.mat", 
            32, 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/Vday_shirt2c.mat", 
            33, 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/shirtTieDyeNew.mat", 
            34, 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/StPats_shirt1.mat", 
            36, 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/StPats_shirt2.mat", 
            37, 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/ContestfishingVestShirt2.mat", 
            38, 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/ContestFishtankShirt1.mat", 
            39, 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/ContestPawShirt1.mat", 
            40, 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/CowboyShirt1.mat", 
            41, 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/CowboyShirt2.mat", 
            42, 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/CowboyShirt3.mat", 
            43, 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/CowboyShirt4.mat", 
            44, 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/CowboyShirt5.mat", 
            45, 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/CowboyShirt6.mat", 
            46, 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/4thJulyShirt1.mat", 
            47, 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/4thJulyShirt2.mat", 
            48, 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/shirt_Cat7_01.mat", 
            49, 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/shirt_Cat7_02.mat", 
            50, 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/contest_backpack3.mat", 
            51, 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/contest_leder.mat", 
            52, 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/contest_mellon2.mat", 
            53, 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/contest_race2.mat", 
            54, 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/PJBlueBanana2.mat", 
            55, 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/PJRedHorn2.mat", 
            56, 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/PJGlasses2.mat", 
            57, 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine1.mat", 
            58, 
            [
                "27"
            ]
        ], 
        "57": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine2.mat", 
            59, 
            [
                "27"
            ]
        ], 
        "58": [
            "phase_4/maps/tt_t_chr_avt_shirt_desat4.mat", 
            60, 
            [
                "27"
            ]
        ], 
        "59": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing1.mat", 
            61, 
            [
                "27"
            ]
        ], 
        "60": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing2.mat", 
            62, 
            [
                "27"
            ]
        ], 
        "61": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening1.mat", 
            63, 
            [
                "27"
            ]
        ], 
        "62": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening2.mat", 
            64, 
            [
                "27"
            ]
        ], 
        "63": [
            "phase_4/maps/tt_t_chr_avt_shirt_party1.mat", 
            65, 
            [
                "27"
            ]
        ], 
        "64": [
            "phase_4/maps/tt_t_chr_avt_shirt_party2.mat", 
            66, 
            [
                "27"
            ]
        ], 
        "65": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing1.mat", 
            67, 
            [
                "27"
            ]
        ], 
        "66": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing2.mat", 
            68, 
            [
                "27"
            ]
        ], 
        "67": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer1.mat", 
            69, 
            [
                "27"
            ]
        ], 
        "68": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer2.mat", 
            70, 
            [
                "27"
            ]
        ], 
        "69": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf1.mat", 
            71, 
            [
                "27"
            ]
        ], 
        "70": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf2.mat", 
            72, 
            [
                "27"
            ]
        ], 
        "71": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween1.mat", 
            73, 
            [
                "27"
            ]
        ], 
        "72": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween2.mat", 
            74, 
            [
                "27"
            ]
        ], 
        "73": [
            "phase_4/maps/tt_t_chr_avt_shirt_marathon1.mat", 
            75, 
            [
                "27"
            ]
        ], 
        "74": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.mat", 
            76, 
            [
                "27"
            ]
        ], 
        "75": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.mat", 
            77, 
            [
                "27"
            ]
        ], 
        "76": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask1.mat", 
            78, 
            [
                "27"
            ]
        ], 
        "77": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask2.mat", 
            79, 
            [
                "27"
            ]
        ], 
        "78": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley1.mat", 
            80, 
            [
                "27"
            ]
        ], 
        "79": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley2.mat", 
            81, 
            [
                "27"
            ]
        ], 
        "80": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter1.mat", 
            82, 
            [
                "27"
            ]
        ], 
        "81": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween3.mat", 
            83, 
            [
                "27"
            ]
        ], 
        "82": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween4.mat", 
            84, 
            [
                "27"
            ]
        ], 
        "83": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine3.mat", 
            85, 
            [
                "27"
            ]
        ], 
        "84": [
            "phase_4/maps/tt_t_chr_shirt_scientistC.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "85": [
            "phase_4/maps/tt_t_chr_shirt_scientistA.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "86": [
            "phase_4/maps/tt_t_chr_shirt_scientistB.mat", 
            86, 
            [
                "27"
            ]
        ], 
        "87": [
            "phase_4/maps/tt_t_chr_avt_shirt_mailbox.mat", 
            87, 
            [
                "27"
            ]
        ], 
        "88": [
            "phase_4/maps/tt_t_chr_avt_shirt_trashcan.mat", 
            88, 
            [
                "27"
            ]
        ], 
        "89": [
            "phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.mat", 
            89, 
            [
                "27"
            ]
        ], 
        "90": [
            "phase_4/maps/tt_t_chr_avt_shirt_hydrant.mat", 
            90, 
            [
                "27"
            ]
        ], 
        "91": [
            "phase_4/maps/tt_t_chr_avt_shirt_whistle.mat", 
            91, 
            [
                "27"
            ]
        ], 
        "92": [
            "phase_4/maps/tt_t_chr_avt_shirt_cogbuster.mat", 
            92, 
            [
                "27"
            ]
        ], 
        "93": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.mat", 
            93, 
            [
                "27"
            ]
        ], 
        "94": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.mat", 
            94, 
            [
                "27"
            ]
        ], 
        "95": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.mat", 
            95, 
            [
                "27"
            ]
        ], 
        "96": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.mat", 
            96, 
            [
                "27"
            ]
        ], 
        "97": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.mat", 
            97, 
            [
                "27"
            ]
        ], 
        "98": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.mat", 
            98, 
            [
                "27"
            ]
        ], 
        "99": [
            "phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.mat", 
            99, 
            [
                "27"
            ]
        ]
    }

    femaleBottomDNA2femaleBottom = {
        "00": [
            "phase_3/maps/desat_skirt_1.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26", 
                "27"
            ]
        ], 
        "01": [
            "phase_3/maps/desat_skirt_2.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "02": [
            "phase_3/maps/desat_skirt_3.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "03": [
            "phase_3/maps/desat_skirt_4.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "04": [
            "phase_3/maps/desat_skirt_5.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26"
            ]
        ], 
        "05": [
            "phase_3/maps/desat_skirt_6.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26", 
                "27"
            ]
        ], 
        "06": [
            "phase_3/maps/desat_skirt_7.mat", 
            [
                "00", 
                "01", 
                "02", 
                "17", 
                "04", 
                "18", 
                "06", 
                "19", 
                "20", 
                "09", 
                "11", 
                "12", 
                "21", 
                "22", 
                "23", 
                "24", 
                "25", 
                "26", 
                "27"
            ]
        ], 
        "07": [
            "phase_4/maps/female_skirt1.mat", 
            [
                "27"
            ]
        ], 
        "08": [
            "phase_4/maps/female_skirt2.mat", 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_4/maps/female_skirt3.mat", 
            [
                "27"
            ]
        ], 
        "10": [
            "phase_4/maps/VdaySkirt1.mat", 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_4/maps/skirtNew5.mat", 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_4/maps/CowboySkirt1.mat", 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_4/maps/CowboySkirt2.mat", 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_4/maps/4thJulySkirt1.mat", 
            [
                "27"
            ]
        ], 
        "15": [
            "phase_4/maps/skirtCat7_01.mat", 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter1.mat", 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter2.mat", 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter3.mat", 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter4.mat", 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/tt_t_chr_avt_skirt_valentine1.mat", 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/tt_t_chr_avt_skirt_valentine2.mat", 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/tt_t_chr_avt_skirt_fishing1.mat", 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/tt_t_chr_avt_skirt_gardening1.mat", 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/tt_t_chr_avt_skirt_party1.mat", 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing1.mat", 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/tt_t_chr_avt_skirt_summer1.mat", 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf1.mat", 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween1.mat", 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween2.mat", 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/tt_t_chr_avt_skirt_saveBuilding1.mat", 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/tt_t_chr_avt_skirt_trolley1.mat", 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween3.mat", 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween4.mat", 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/tt_t_chr_avt_skirt_greentoon1.mat", 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/tt_t_chr_avt_skirt_racingGrandPrix.mat", 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/tt_t_chr_avt_skirt_pirate.mat", 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf02.mat", 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing03.mat", 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf03.mat", 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf04.mat", 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing04.mat", 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing05.mat", 
            [
                "27"
            ]
        ],
        "43": [
            "phase_4/maps/tsaskirt.mat",
            [
                "27"
            ]
        ],
        "44": [
            "phase_4/maps/tsaskirt_dev.mat",
            [
                "27"
            ]
        ]
    }

    maleBottomDNA2maleBottom = {
        "00": [
            "phase_3/maps/desat_shorts_1.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20"
            ]
        ], 
        "01": [
            "phase_3/maps/desat_shorts_2.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20"
            ]
        ], 
        "02": [
            "phase_3/maps/desat_shorts_4.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20"
            ]
        ], 
        "03": [
            "phase_3/maps/desat_shorts_6.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "20", 
                "09", 
                "11", 
                "12", 
                "13", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "27"
            ]
        ], 
        "04": [
            "phase_3/maps/desat_shorts_7.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20"
            ]
        ], 
        "05": [
            "phase_3/maps/desat_shorts_8.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20", 
                "27"
            ]
        ], 
        "06": [
            "phase_3/maps/desat_shorts_9.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "20", 
                "27"
            ]
        ], 
        "07": [
            "phase_3/maps/desat_shorts_10.mat", 
            [
                "00", 
                "01", 
                "02", 
                "04", 
                "06", 
                "09", 
                "10", 
                "11", 
                "12", 
                "13", 
                "14", 
                "15", 
                "16", 
                "17", 
                "18", 
                "19", 
                "20", 
                "27"
            ]
        ], 
        "08": [
            "phase_4/maps/VdayShorts2.mat", 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_4/maps/shorts4.mat", 
            [
                "27"
            ]
        ], 
        "10": [
            "phase_4/maps/shorts1.mat", 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_4/maps/shorts5.mat", 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_4/maps/CowboyShorts1.mat", 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_4/maps/CowboyShorts2.mat", 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_4/maps/4thJulyShorts1.mat", 
            [
                "27"
            ]
        ], 
        "15": [
            "phase_4/maps/shortsCat7_01.mat", 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/Blue_shorts_1.mat", 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/Red_shorts_1.mat", 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/Purple_shorts_1.mat", 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter1.mat", 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter2.mat", 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter3.mat", 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter4.mat", 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/tt_t_chr_avt_shorts_valentine1.mat", 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/tt_t_chr_avt_shorts_valentine2.mat", 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/tt_t_chr_avt_shorts_fishing1.mat", 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/tt_t_chr_avt_shorts_gardening1.mat", 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/tt_t_chr_avt_shorts_party1.mat", 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing1.mat", 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/tt_t_chr_avt_shorts_summer1.mat", 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf1.mat", 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween1.mat", 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween2.mat", 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/tt_t_chr_avt_shorts_saveBuilding1.mat", 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/tt_t_chr_avt_shorts_trolley1.mat", 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween4.mat", 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween3.mat", 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/tt_t_chr_shorts_scientistA.mat", 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/tt_t_chr_shorts_scientistB.mat", 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/tt_t_chr_shorts_scientistC.mat", 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/tt_t_chr_avt_shorts_cogbuster.mat", 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.mat", 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween5.mat", 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.mat", 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/tt_t_chr_avt_shorts_greentoon1.mat", 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/tt_t_chr_avt_shorts_racingGrandPrix.mat", 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/tt_t_chr_avt_shorts_bee.mat", 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/tt_t_chr_avt_shorts_pirate.mat", 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/tt_t_chr_avt_shorts_supertoon.mat", 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/tt_t_chr_avt_shorts_vampire.mat", 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/tt_t_chr_avt_shorts_dinosaur.mat", 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf03.mat", 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing03.mat", 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf04.mat", 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf05.mat", 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing04.mat", 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing05.mat", 
            [
                "27"
            ]
        ],
        "57": [
            "phase_4/maps/tsashorts.mat",
            [
                "27"
            ]
        ],
        "58": [
            "phase_4/maps/tsashorts_dev.mat",
            [
                "27"
            ]
        ],
        "59": [
            "phase_14/maps/tt_t_chr_avt_shorts_betaoutfit.mat",
            [
                "27"
            ]
        ]
    }

    gender2genderDNA = {v: k for k, v in genderDNA2gender.items()}
    animal2animalDNA = {v: k for k, v in animalDNA2animal.items()}
    head2headDNA = {v: k for k, v in headDNA2head.items()}
    torso2torsoDNA = {v: k for k, v in torsoDNA2torso.items()}
    leg2legDNA = {v: k for k, v in legDNA2leg.items()}

    maleTop2maleTopDNA = {v[0]: k for k, v in maleTopDNA2maleTop.items()}
    femaleTop2femaleTopDNA = {v[0]: k for k, v in femaleTopDNA2femaleTop.items()}
    maleBottom2maleBottomDNA = {v[0]: k for k, v in maleBottomDNA2maleBottom.items()}
    femaleBottom2femaleBottomDNA = {v[0]: k for k, v in femaleBottomDNA2femaleBottom.items()}

    clothesColor2clothesColorDNA = {v: k for k, v in clothesColorDNA2clothesColor.items()}
    color2colorDNA = {v: k for k, v in colorDNA2color.items()}

    def __init__(self):
        self.dnaStrand = "00/00/00/00/00/00/00/00/00/00/00/00/00"
        self.gender = ""
        self.animal = ""
        self.head = ""
        self.headcolor = None
        self.headLength = ""
        self.torso = ""
        self.torsocolor = None
        self.legs = ""
        self.legcolor = None
        self.shirt = ""
        self.sleeve = ""
        self.shorts = ""
        self.shirtColor = None
        self.sleeveColor = None
        self.shortColor = None
        self.gloveColor = None
        self.parseDNAStrand(self.dnaStrand)
        return
        
    def hasTSASuit(self):
        return False

    def getColorByName(self, name):
        name = name.lower()
        color = None
        if name in self.colorName2DNAcolor.keys():
            color = self.colorName2DNAcolor[name]
        return color

    def getDNAIDFromColor(self, color):
        dnaID = None
        for _id, dnaColor in self.colorDNA2color.iteritems():
            if dnaColor == color:
                dnaID = _id
        return dnaID

    def getAnimal(self):
        return self.animal

    def getGender(self):
        return self.gender

    def getHead(self):
        return self.head

    def getHeadColor(self):
        return self.headcolor

    def getHeadStyle(self):
        return [self.head, self.headcolor]
        
    def getHeadLength(self):
        return self.headLength

    def getTorso(self):
        return self.torso

    def getTorsoColor(self):
        return self.torsocolor

    def getTorsoStyle(self):
        return [self.torso, self.torsocolor]

    def getLegs(self):
        return self.legs

    def getLegColor(self):
        return self.legcolor

    def getLegStyle(self):
        return [self.legs, self.legcolor]

    def getShirt(self):
        return self.shirt

    def getShirtColor(self):
        return self.shirtColor

    def getShirtStyle(self):
        return [self.shirt, self.shirtColor]

    def getSleeve(self):
        return self.sleeve

    def getSleeveColor(self):
        return self.sleeveColor

    def getSleeveStyle(self):
        return [self.sleeve, self.sleeveColor]

    def getShorts(self):
        return self.shorts

    def getShortColor(self):
        return self.shortColor

    def getShortStyle(self):
        return [self.shorts, self.shortColor]

    def getGloveColor(self):
        return self.gloveColor

    def setDNAStrand(self, dnaStrand):
        self.dnaStrand = dnaStrand
        self.parseDNAStrand(dnaStrand)

    def getDNAStrand(self):
        return self.dnaStrand

    def isCoach(self):
        return self.getDNAStrand() == "00/06/02/15/00/15/00/15/97/41/27/27/00"

    def getToonAnimalNoise(self, noise):
        if self.isCoach():
            return 'phase_3/audio/dial/coach.ogg'
        return 'phase_3.5/audio/dial/AV_' + self.getAnimal() + '_' + noise + '.ogg'

    def generateDNAStrandWithCurrentStyle(self):
        gender = self.gender2genderDNA[self.gender]
        animal = self.animal2animalDNA[self.animal]
        head = self.head2headDNA[self.head]
        headcolor = self.color2colorDNA[self.headcolor]
        torso = self.torso2torsoDNA[self.torso]
        torsocolor = self.color2colorDNA[self.torsocolor]
        legs = self.leg2legDNA[self.legs]
        legcolor = self.color2colorDNA[self.legcolor]

        if self.gender == 'girl':
            tops = self.femaleTop2femaleTopDNA
            bots = self.femaleBottom2femaleBottomDNA
        else:
            tops = self.maleTop2maleTopDNA
            bots = self.maleBottom2maleBottomDNA

        shirt = tops[self.shirt]
        shorts = bots[self.shorts]
        shirtColor = self.clothesColor2clothesColorDNA[self.shirtColor]
        shortColor = self.clothesColor2clothesColorDNA[self.shortColor]
        gloveColor = self.color2colorDNA[self.gloveColor]
        strand = "%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s" % (
            gender, animal, head, headcolor, torso,
            torsocolor, legs, legcolor, shirt,
            shorts, shirtColor, shortColor, gloveColor
            )
        self.setDNAStrand(strand)

    def parseDNAStrand(self, dnaStrand):
        dnaParts = dnaStrand.split('/')
        strandLength = len(dnaParts) * 2
        isString = type(dnaStrand) is types.StringType
        if (strandLength >= self.requiredStrandLength and isString):
            self.gender = self.genderDNA2gender[dnaParts[0]]
            self.animal = self.animalDNA2animal[dnaParts[1]]
            self.head = self.headDNA2head[dnaParts[2]]
            
            if self.head in self.LongHeads:
                self.headLength = 'l'
            elif self.head in self.ShortHeads:
                self.headLength = 's'

            if self.gender == 'girl':
                tops = self.femaleTopDNA2femaleTop
                bots = self.femaleBottomDNA2femaleBottom
            elif self.gender == 'boy':
                tops = self.maleTopDNA2maleTop
                bots = self.maleBottomDNA2maleBottom
                
            self.headcolor = self.colorDNA2color[dnaParts[3]]
            self.torso = self.torsoDNA2torso[dnaParts[4]]
            self.torsocolor = self.colorDNA2color[dnaParts[5]]
            self.legs = self.legDNA2leg[dnaParts[6]]
            self.legcolor = self.colorDNA2color[dnaParts[7]]
            self.shirt = tops[dnaParts[8]][0]
            self.sleeve = self.Sleeves[tops[dnaParts[8]][1]]
            self.shorts = bots[dnaParts[9]][0]
            self.shirtColor = self.clothesColorDNA2clothesColor[dnaParts[10]]
            self.sleeveColor = self.shirtColor
            self.shortColor = self.clothesColorDNA2clothesColor[dnaParts[11]]
            self.gloveColor = self.colorDNA2color[dnaParts[12]]
        else:
            self.notify.error("The DNA strand %s is formatted incorrectly." % dnaStrand)
