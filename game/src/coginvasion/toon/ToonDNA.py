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
    
    shirtDNA2shirt = {'00': 'phase_3/maps/desat_shirt_1.jpg',
                    '01': 'phase_3/maps/desat_shirt_2.jpg',
                    '02': 'phase_3/maps/desat_shirt_3.jpg',
                    '03': 'phase_3/maps/desat_shirt_4.jpg',
                    '04': 'phase_3/maps/desat_shirt_5.jpg',
                    '05': 'phase_3/maps/desat_shirt_6.jpg',
                    '06': 'phase_3/maps/desat_shirt_7.jpg',
                    '07': 'phase_3/maps/desat_shirt_8.jpg',
                    '08': 'phase_3/maps/desat_shirt_9.jpg',
                    '09': 'phase_3/maps/desat_shirt_10.jpg',
                    '10': 'phase_3/maps/desat_shirt_11.jpg',
                    '11': 'phase_3/maps/desat_shirt_12.jpg',
                    '12': 'phase_3/maps/desat_shirt_13.jpg',
                    '13': 'phase_3/maps/desat_shirt_14.jpg',
                    '14': 'phase_3/maps/desat_shirt_15.jpg',
                    '15': 'phase_3/maps/desat_shirt_16.jpg',
                    '16': 'phase_3/maps/desat_shirt_17.jpg',
                    '17': 'phase_3/maps/desat_shirt_18.jpg',
                    '18': 'phase_3/maps/desat_shirt_19.jpg',
                    '19': 'phase_3/maps/desat_shirt_20.jpg',
                    '20': 'phase_3/maps/desat_shirt_21.jpg',
                    '21': 'phase_3/maps/desat_shirt_22.jpg',
                    '22': 'phase_3/maps/desat_shirt_23.jpg',
                    '23': 'phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.jpg',
                    '24': 'phase_4/maps/tt_t_chr_shirt_scientistA.jpg',
                    '25': 'phase_4/maps/tt_t_chr_shirt_scientistB.jpg',
                    '26': 'phase_4/maps/tt_t_chr_shirt_scientistC.jpg',
                    '27': 'phase_4/maps/tsashirt.jpg'}
    sleeveDNA2sleeve = {'00': 'phase_3/maps/desat_sleeve_1.jpg',
                        '01': 'phase_3/maps/desat_sleeve_2.jpg',
                        '02': 'phase_3/maps/desat_sleeve_3.jpg',
                        '03': 'phase_3/maps/desat_sleeve_4.jpg',
                        '04': 'phase_3/maps/desat_sleeve_5.jpg',
                        '05': 'phase_3/maps/desat_sleeve_6.jpg',
                        '06': 'phase_3/maps/desat_sleeve_7.jpg',
                        '07': 'phase_3/maps/desat_sleeve_8.jpg',
                        '08': 'phase_3/maps/desat_sleeve_9.jpg',
                        '09': 'phase_3/maps/desat_sleeve_10.jpg',
                        '10': 'phase_3/maps/desat_sleeve_11.jpg',
                        '11': 'phase_3/maps/desat_sleeve_12.jpg',
                        '12': 'phase_3/maps/desat_sleeve_13.jpg',
                        '13': 'phase_3/maps/desat_sleeve_14.jpg',
                        '14': 'phase_3/maps/desat_sleeve_15.jpg',
                        '15': 'phase_3/maps/desat_sleeve_16.jpg',
                        '16': 'phase_3/maps/desat_sleeve_17.jpg',
                        '17': 'phase_3/maps/desat_sleeve_18.jpg',
                        '18': 'phase_3/maps/desat_sleeve_19.jpg',
                        '19': 'phase_3/maps/desat_sleeve_20.jpg',
                        '20': 'phase_3/maps/desat_sleeve_21.jpg',
                        '21': 'phase_3/maps/desat_sleeve_22.jpg',
                        '22': 'phase_3/maps/desat_sleeve_23.jpg',
                        '23': 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.jpg',
                        '24': 'phase_4/maps/tt_t_chr_shirtSleeve_scientist.jpg',
                        '25': 'phase_4/maps/tsasleeve.jpg',}
    shortDNA2short = {'00': 'phase_3/maps/desat_shorts_1.jpg',
                    '01': 'phase_3/maps/desat_shorts_2.jpg',
                    '02': 'phase_3/maps/desat_shorts_3.jpg',
                    '03': 'phase_3/maps/desat_shorts_4.jpg',
                    '04': 'phase_3/maps/desat_shorts_5.jpg',
                    '05': 'phase_3/maps/desat_shorts_6.jpg',
                    '06': 'phase_3/maps/desat_shorts_7.jpg',
                    '07': 'phase_3/maps/desat_shorts_8.jpg',
                    '08': 'phase_3/maps/desat_shorts_9.jpg',
                    '09': 'phase_3/maps/desat_shorts_10.jpg',
                    '10': 'phase_3/maps/desat_skirt_1.jpg',
                    '11': 'phase_3/maps/desat_skirt_2.jpg',
                    '12': 'phase_3/maps/desat_skirt_3.jpg',
                    '13': 'phase_3/maps/desat_skirt_4.jpg',
                    '14': 'phase_3/maps/desat_skirt_5.jpg',
                    '15': 'phase_3/maps/desat_skirt_6.jpg',
                    '16': 'phase_3/maps/desat_skirt_7.jpg',
                    '17': 'phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg',
                    '18': 'phase_4/maps/skirtNew5.jpg',
                    '19': 'phase_4/maps/tt_t_chr_avt_skirt_winter1.jpg',
                    '20': 'phase_4/maps/tt_t_chr_shorts_scientistA.jpg',
                    '21': 'phase_4/maps/tt_t_chr_shorts_scientistB.jpg',
                    '22': 'phase_4/maps/tt_t_chr_shorts_scientistC.jpg',
                    '23': 'phase_3/maps/desat_shorts_11.jpg',
                    '24': 'phase_3/maps/desat_shorts_12.jpg',
                    '25': 'phase_3/maps/desat_shorts_13.jpg',
                    '26': 'phase_3/maps/desat_shorts_14.jpg',
                    '27': 'phase_4/maps/tsashorts.jpg',
                    '28': 'phase_4/maps/tsaskirt.jpg'}
                    
    
    
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

    Sleeves = ['phase_3/maps/desat_sleeve_1.jpg',
         'phase_3/maps/desat_sleeve_2.jpg',
         'phase_3/maps/desat_sleeve_3.jpg',
         'phase_3/maps/desat_sleeve_4.jpg',
         'phase_3/maps/desat_sleeve_5.jpg',
         'phase_3/maps/desat_sleeve_6.jpg',
         'phase_3/maps/desat_sleeve_7.jpg',
         'phase_3/maps/desat_sleeve_8.jpg',
         'phase_3/maps/desat_sleeve_9.jpg',
         'phase_3/maps/desat_sleeve_10.jpg',
         'phase_3/maps/desat_sleeve_15.jpg',
         'phase_3/maps/desat_sleeve_16.jpg',
         'phase_3/maps/desat_sleeve_19.jpg',
         'phase_3/maps/desat_sleeve_20.jpg',
         'phase_4/maps/female_sleeve1b.jpg',
         'phase_4/maps/female_sleeve2.jpg',
         'phase_4/maps/female_sleeve3.jpg',
         'phase_4/maps/male_sleeve1.jpg',
         'phase_4/maps/male_sleeve2_palm.jpg',
         'phase_4/maps/male_sleeve3c.jpg',
         'phase_4/maps/shirt_Sleeve_ghost.jpg',
         'phase_4/maps/shirt_Sleeve_pumkin.jpg',
         'phase_4/maps/holidaySleeve1.jpg',
         'phase_4/maps/holidaySleeve3.jpg',
         'phase_4/maps/female_sleeve1b.jpg',
         'phase_4/maps/female_sleeve5New.jpg',
         'phase_4/maps/male_sleeve4New.jpg',
         'phase_4/maps/sleeve6New.jpg',
         'phase_4/maps/SleeveMaleNew7.jpg',
         'phase_4/maps/female_sleeveNew6.jpg',
         'phase_4/maps/Vday5Sleeve.jpg',
         'phase_4/maps/Vda6Sleeve.jpg',
         'phase_4/maps/Vday_shirt4sleeve.jpg',
         'phase_4/maps/Vday2cSleeve.jpg',
         'phase_4/maps/sleeveTieDye.jpg',
         'phase_4/maps/male_sleeve1.jpg',
         'phase_4/maps/StPats_sleeve.jpg',
         'phase_4/maps/StPats_sleeve2.jpg',
         'phase_4/maps/ContestfishingVestSleeve1.jpg',
         'phase_4/maps/ContestFishtankSleeve1.jpg',
         'phase_4/maps/ContestPawSleeve1.jpg',
         'phase_4/maps/CowboySleeve1.jpg',
         'phase_4/maps/CowboySleeve2.jpg',
         'phase_4/maps/CowboySleeve3.jpg',
         'phase_4/maps/CowboySleeve4.jpg',
         'phase_4/maps/CowboySleeve5.jpg',
         'phase_4/maps/CowboySleeve6.jpg',
         'phase_4/maps/4thJulySleeve1.jpg',
         'phase_4/maps/4thJulySleeve2.jpg',
         'phase_4/maps/shirt_sleeveCat7_01.jpg',
         'phase_4/maps/shirt_sleeveCat7_02.jpg',
         'phase_4/maps/contest_backpack_sleeve.jpg',
         'phase_4/maps/Contest_leder_sleeve.jpg',
         'phase_4/maps/contest_mellon_sleeve2.jpg',
         'phase_4/maps/contest_race_sleeve.jpg',
         'phase_4/maps/PJSleeveBlue.jpg',
         'phase_4/maps/PJSleeveRed.jpg',
         'phase_4/maps/PJSleevePurple.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_desat4.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_party1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_party2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_marathon1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley2.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween3.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween4.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine3.jpg',
         'phase_4/maps/tt_t_chr_shirtSleeve_scientist.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mailbox.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trashcan.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_loonyLabs.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_hydrant.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_whistle.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_cogbuster.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated01.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty01.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty02.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotIcon.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotVPIcon.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_jellyBeans.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_doodle.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween5.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloweenTurtle.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_greentoon1.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_getConnectedMoverShaker.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racingGrandPrix.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_bee.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_pirate.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_supertoon.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_vampire.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_dinosaur.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing04.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf03.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated02.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing03.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding3.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley03.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing05.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf04.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween06.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter03.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween07.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter02.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing06.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing07.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf05.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing04.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing05.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated03.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated04.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley04.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley05.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding4.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding05.jpg',
         'phase_4/maps/tt_t_chr_avt_shirtSleeve_anniversary.jpg',
         'phase_4/maps/tsasleeve.jpg',
         'phase_4/maps/tsasleeve_dev.jpg']

    maleTopDNA2maleTop = {
        "00": [
            "phase_3/maps/desat_shirt_1.jpg", 
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
            "phase_3/maps/desat_shirt_2.jpg", 
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
            "phase_3/maps/desat_shirt_3.jpg", 
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
            "phase_3/maps/desat_shirt_4.jpg", 
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
            "phase_3/maps/desat_shirt_5.jpg", 
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
            "phase_3/maps/desat_shirt_6.jpg", 
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
            "phase_3/maps/desat_shirt_9.jpg", 
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
            "phase_3/maps/desat_shirt_10.jpg", 
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
            "phase_3/maps/desat_shirt_11.jpg", 
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
            "phase_3/maps/desat_shirt_12.jpg", 
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
            "phase_3/maps/desat_shirt_15.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_halloween5.jpg", 
            101, 
            [
                "27"
            ]
        ], 
        "101": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.jpg", 
            102, 
            [
                "27"
            ]
        ], 
        "102": [
            "phase_4/maps/tt_t_chr_avt_shirt_greentoon1.jpg", 
            103, 
            [
                "27"
            ]
        ], 
        "103": [
            "phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.jpg", 
            104, 
            [
                "27"
            ]
        ], 
        "104": [
            "phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.jpg", 
            105, 
            [
                "27"
            ]
        ], 
        "105": [
            "phase_4/maps/tt_t_chr_avt_shirt_bee.jpg", 
            106, 
            [
                "27"
            ]
        ], 
        "106": [
            "phase_4/maps/tt_t_chr_avt_shirt_pirate.jpg", 
            107, 
            [
                "27"
            ]
        ], 
        "107": [
            "phase_4/maps/tt_t_chr_avt_shirt_supertoon.jpg", 
            108, 
            [
                "27"
            ]
        ], 
        "108": [
            "phase_4/maps/tt_t_chr_avt_shirt_vampire.jpg", 
            109, 
            [
                "27"
            ]
        ], 
        "109": [
            "phase_4/maps/tt_t_chr_avt_shirt_dinosaur.jpg", 
            110, 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_3/maps/desat_shirt_17.jpg", 
            0, 
            [
                "27"
            ]
        ], 
        "110": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing04.jpg", 
            111, 
            [
                "27"
            ]
        ], 
        "111": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf03.jpg", 
            112, 
            [
                "27"
            ]
        ], 
        "112": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.jpg", 
            113, 
            [
                "27"
            ]
        ], 
        "113": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing03.jpg", 
            114, 
            [
                "27"
            ]
        ], 
        "114": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.jpg", 
            115, 
            [
                "27"
            ]
        ], 
        "115": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley03.jpg", 
            116, 
            [
                "27"
            ]
        ], 
        "116": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing05.jpg", 
            117, 
            [
                "27"
            ]
        ], 
        "117": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf04.jpg", 
            118, 
            [
                "27"
            ]
        ], 
        "118": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween06.jpg", 
            119, 
            [
                "27"
            ]
        ], 
        "119": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter03.jpg", 
            120, 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_3/maps/desat_shirt_18.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_halloween07.jpg", 
            121, 
            [
                "27"
            ]
        ], 
        "121": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter02.jpg", 
            122, 
            [
                "27"
            ]
        ], 
        "122": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing06.jpg", 
            123, 
            [
                "27"
            ]
        ], 
        "123": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing07.jpg", 
            124, 
            [
                "27"
            ]
        ], 
        "124": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf05.jpg", 
            125, 
            [
                "27"
            ]
        ], 
        "125": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing04.jpg", 
            126, 
            [
                "27"
            ]
        ], 
        "126": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing05.jpg", 
            127, 
            [
                "27"
            ]
        ], 
        "127": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.jpg", 
            128, 
            [
                "27"
            ]
        ], 
        "128": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.jpg", 
            129, 
            [
                "27"
            ]
        ], 
        "129": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley04.jpg", 
            130, 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_3/maps/desat_shirt_19.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_trolley05.jpg", 
            116, 
            [
                "27"
            ]
        ], 
        "131": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.jpg", 
            131, 
            [
                "27"
            ]
        ], 
        "132": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.jpg", 
            133, 
            [
                "27"
            ]
        ], 
        "133": [
            "phase_4/maps/tt_t_chr_avt_shirt_anniversary.jpg", 
            134, 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_3/maps/desat_shirt_20.jpg", 
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
            "phase_4/maps/female_shirt3.jpg", 
            16, 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/male_shirt1.jpg", 
            17, 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/male_shirt2_palm.jpg", 
            18, 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/male_shirt3c.jpg", 
            19, 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/shirt_ghost.jpg", 
            20, 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/shirt_pumkin.jpg", 
            21, 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/holiday_shirt1.jpg", 
            22, 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/holiday_shirt2b.jpg", 
            22, 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/holidayShirt3b.jpg", 
            23, 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/holidayShirt4.jpg", 
            23, 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/shirtMale4B.jpg", 
            26, 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/shirt6New.jpg", 
            27, 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/shirtMaleNew7.jpg", 
            28, 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/Vday1Shirt5.jpg", 
            30, 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/Vday1Shirt6SHD.jpg", 
            31, 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/Vday1Shirt4.jpg", 
            32, 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/Vday_shirt2c.jpg", 
            33, 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/shirtTieDyeNew.jpg", 
            34, 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/StPats_shirt1.jpg", 
            36, 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/StPats_shirt2.jpg", 
            37, 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/ContestfishingVestShirt2.jpg", 
            38, 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/ContestFishtankShirt1.jpg", 
            39, 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/ContestPawShirt1.jpg", 
            40, 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/CowboyShirt1.jpg", 
            41, 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/CowboyShirt2.jpg", 
            42, 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/CowboyShirt3.jpg", 
            43, 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/CowboyShirt4.jpg", 
            44, 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/CowboyShirt5.jpg", 
            45, 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/CowboyShirt6.jpg", 
            46, 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/4thJulyShirt1.jpg", 
            47, 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/4thJulyShirt2.jpg", 
            48, 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/shirt_Cat7_01.jpg", 
            49, 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/shirt_Cat7_02.jpg", 
            50, 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/contest_backpack3.jpg", 
            51, 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/contest_leder.jpg", 
            52, 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/contest_mellon2.jpg", 
            53, 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/contest_race2.jpg", 
            54, 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/PJBlueBanana2.jpg", 
            55, 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/PJRedHorn2.jpg", 
            56, 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/PJGlasses2.jpg", 
            57, 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine1.jpg", 
            58, 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine2.jpg", 
            59, 
            [
                "27"
            ]
        ], 
        "57": [
            "phase_4/maps/tt_t_chr_avt_shirt_desat4.jpg", 
            60, 
            [
                "27"
            ]
        ], 
        "58": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing1.jpg", 
            61, 
            [
                "27"
            ]
        ], 
        "59": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing2.jpg", 
            62, 
            [
                "27"
            ]
        ], 
        "60": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening1.jpg", 
            63, 
            [
                "27"
            ]
        ], 
        "61": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening2.jpg", 
            64, 
            [
                "27"
            ]
        ], 
        "62": [
            "phase_4/maps/tt_t_chr_avt_shirt_party1.jpg", 
            65, 
            [
                "27"
            ]
        ], 
        "63": [
            "phase_4/maps/tt_t_chr_avt_shirt_party2.jpg", 
            66, 
            [
                "27"
            ]
        ], 
        "64": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing1.jpg", 
            67, 
            [
                "27"
            ]
        ], 
        "65": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing2.jpg", 
            68, 
            [
                "27"
            ]
        ], 
        "66": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer1.jpg", 
            69, 
            [
                "27"
            ]
        ], 
        "67": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer2.jpg", 
            70, 
            [
                "27"
            ]
        ], 
        "68": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf1.jpg", 
            71, 
            [
                "27"
            ]
        ], 
        "69": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf2.jpg", 
            72, 
            [
                "27"
            ]
        ], 
        "70": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween1.jpg", 
            73, 
            [
                "27"
            ]
        ], 
        "71": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween2.jpg", 
            74, 
            [
                "27"
            ]
        ], 
        "72": [
            "phase_4/maps/tt_t_chr_avt_shirt_marathon1.jpg", 
            75, 
            [
                "27"
            ]
        ], 
        "73": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.jpg", 
            76, 
            [
                "27"
            ]
        ], 
        "74": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.jpg", 
            77, 
            [
                "27"
            ]
        ], 
        "75": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask1.jpg", 
            78, 
            [
                "27"
            ]
        ], 
        "76": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask2.jpg", 
            79, 
            [
                "27"
            ]
        ], 
        "77": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley1.jpg", 
            80, 
            [
                "27"
            ]
        ], 
        "78": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley2.jpg", 
            81, 
            [
                "27"
            ]
        ], 
        "79": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter1.jpg", 
            82, 
            [
                "27"
            ]
        ], 
        "80": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween3.jpg", 
            83, 
            [
                "27"
            ]
        ], 
        "81": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween4.jpg", 
            84, 
            [
                "27"
            ]
        ], 
        "82": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine3.jpg", 
            85, 
            [
                "27"
            ]
        ], 
        "83": [
            "phase_4/maps/tt_t_chr_shirt_scientistC.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "84": [
            "phase_4/maps/tt_t_chr_shirt_scientistA.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "85": [
            "phase_4/maps/tt_t_chr_shirt_scientistB.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "86": [
            "phase_4/maps/tt_t_chr_avt_shirt_mailbox.jpg", 
            87, 
            [
                "27"
            ]
        ], 
        "87": [
            "phase_4/maps/tt_t_chr_avt_shirt_trashcan.jpg", 
            88, 
            [
                "27"
            ]
        ], 
        "88": [
            "phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.jpg", 
            89, 
            [
                "27"
            ]
        ], 
        "89": [
            "phase_4/maps/tt_t_chr_avt_shirt_hydrant.jpg", 
            90, 
            [
                "27"
            ]
        ], 
        "90": [
            "phase_4/maps/tt_t_chr_avt_shirt_whistle.jpg", 
            91, 
            [
                "27"
            ]
        ], 
        "91": [
            "phase_4/maps/tt_t_chr_avt_shirt_cogbuster.jpg", 
            92, 
            [
                "27"
            ]
        ], 
        "92": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.jpg", 
            93, 
            [
                "27"
            ]
        ], 
        "93": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.jpg", 
            94, 
            [
                "27"
            ]
        ], 
        "94": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.jpg", 
            95, 
            [
                "27"
            ]
        ], 
        "95": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.jpg", 
            96, 
            [
                "27"
            ]
        ], 
        "96": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.jpg", 
            97, 
            [
                "27"
            ]
        ], 
        "97": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.jpg", 
            98, 
            [
                "27"
            ]
        ], 
        "98": [
            "phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.jpg", 
            99, 
            [
                "27"
            ]
        ], 
        "99": [
            "phase_4/maps/tt_t_chr_avt_shirt_doodle.jpg", 
            100, 
            [
                "27"
            ]
        ],
        "135": [
            "phase_4/maps/tsashirt.jpg",
            135,
            [
                "27"
            ]
        ],
        "136": [
            "phase_4/maps/tsashirt_dev.jpg",
            136,
            [
                "27"
            ]
        ]
    }

    femaleTopDNA2femaleTop = {
        "00": [
            "phase_3/maps/desat_shirt_1.jpg", 
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
            "phase_3/maps/desat_shirt_2.jpg", 
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
            "phase_3/maps/desat_shirt_3.jpg", 
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
            "phase_3/maps/desat_shirt_4.jpg", 
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
            "phase_3/maps/desat_shirt_6.jpg", 
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
            "phase_3/maps/desat_shirt_7.jpg", 
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
            "phase_3/maps/desat_shirt_8.jpg", 
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
            "phase_3/maps/desat_shirt_10.jpg", 
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
            "phase_3/maps/desat_shirt_13.jpg", 
            0, 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_3/maps/desat_shirt_14.jpg", 
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
            "phase_3/maps/desat_shirt_16.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_doodle.jpg", 
            100, 
            [
                "27"
            ]
        ], 
        "101": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween5.jpg", 
            101, 
            [
                "27"
            ]
        ], 
        "102": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.jpg", 
            102, 
            [
                "27"
            ]
        ], 
        "103": [
            "phase_4/maps/tt_t_chr_avt_shirt_greentoon1.jpg", 
            103, 
            [
                "27"
            ]
        ], 
        "104": [
            "phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.jpg", 
            104, 
            [
                "27"
            ]
        ], 
        "105": [
            "phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.jpg", 
            105, 
            [
                "27"
            ]
        ], 
        "106": [
            "phase_4/maps/tt_t_chr_avt_shirt_bee.jpg", 
            106, 
            [
                "27"
            ]
        ], 
        "107": [
            "phase_4/maps/tt_t_chr_avt_shirt_pirate.jpg", 
            107, 
            [
                "27"
            ]
        ], 
        "108": [
            "phase_4/maps/tt_t_chr_avt_shirt_supertoon.jpg", 
            108, 
            [
                "27"
            ]
        ], 
        "109": [
            "phase_4/maps/tt_t_chr_avt_shirt_vampire.jpg", 
            109, 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_3/maps/desat_shirt_17.jpg", 
            0, 
            [
                "27"
            ]
        ], 
        "110": [
            "phase_4/maps/tt_t_chr_avt_shirt_dinosaur.jpg", 
            110, 
            [
                "27"
            ]
        ], 
        "111": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing04.jpg", 
            111, 
            [
                "27"
            ]
        ], 
        "112": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf03.jpg", 
            112, 
            [
                "27"
            ]
        ], 
        "113": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.jpg", 
            113, 
            [
                "27"
            ]
        ], 
        "114": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing03.jpg", 
            114, 
            [
                "27"
            ]
        ], 
        "115": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.jpg", 
            115, 
            [
                "27"
            ]
        ], 
        "116": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley03.jpg", 
            116, 
            [
                "27"
            ]
        ], 
        "117": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing05.jpg", 
            117, 
            [
                "27"
            ]
        ], 
        "118": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf04.jpg", 
            118, 
            [
                "27"
            ]
        ], 
        "119": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween06.jpg", 
            119, 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_3/maps/desat_shirt_21.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_winter03.jpg", 
            120, 
            [
                "27"
            ]
        ], 
        "121": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween07.jpg", 
            121, 
            [
                "27"
            ]
        ], 
        "122": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter02.jpg", 
            122, 
            [
                "27"
            ]
        ], 
        "123": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing06.jpg", 
            123, 
            [
                "27"
            ]
        ], 
        "124": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing07.jpg", 
            124, 
            [
                "27"
            ]
        ], 
        "125": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf05.jpg", 
            125, 
            [
                "27"
            ]
        ], 
        "126": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing04.jpg", 
            126, 
            [
                "27"
            ]
        ], 
        "127": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing05.jpg", 
            127, 
            [
                "27"
            ]
        ], 
        "128": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.jpg", 
            128, 
            [
                "27"
            ]
        ], 
        "129": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.jpg", 
            129, 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_3/maps/desat_shirt_22.jpg", 
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
            "phase_4/maps/tt_t_chr_avt_shirt_trolley04.jpg", 
            130, 
            [
                "27"
            ]
        ], 
        "131": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley05.jpg", 
            116, 
            [
                "27"
            ]
        ], 
        "132": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.jpg", 
            131, 
            [
                "27"
            ]
        ], 
        "133": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.jpg", 
            133, 
            [
                "27"
            ]
        ], 
        "134": [
            "phase_4/maps/tt_t_chr_avt_shirt_anniversary.jpg", 
            134, 
            [
                "27"
            ]
        ],
        "135": [
            "phase_4/maps/tsashirt.jpg",
            135,
            [
                "27"
            ]
        ],
        "136": [
            "phase_4/maps/tsashirt_dev.jpg",
            136,
            [
                "27"
            ]
        ],
        "14": [
            "phase_3/maps/desat_shirt_23.jpg", 
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
            "phase_4/maps/female_shirt1b.jpg", 
            24, 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/female_shirt2.jpg", 
            15, 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/female_shirt3.jpg", 
            16, 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/male_shirt1.jpg", 
            35, 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/male_shirt2_palm.jpg", 
            18, 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/shirt_ghost.jpg", 
            20, 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/shirt_pumkin.jpg", 
            21, 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/holiday_shirt1.jpg", 
            22, 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/holiday_shirt2b.jpg", 
            22, 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/holidayShirt3b.jpg", 
            23, 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/holidayShirt4.jpg", 
            23, 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/female_shirt5New.jpg", 
            25, 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/shirt6New.jpg", 
            27, 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/femaleShirtNew6.jpg", 
            29, 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/Vday1Shirt5.jpg", 
            30, 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/Vday1Shirt6SHD.jpg", 
            31, 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/Vday1Shirt4.jpg", 
            32, 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/Vday_shirt2c.jpg", 
            33, 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/shirtTieDyeNew.jpg", 
            34, 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/StPats_shirt1.jpg", 
            36, 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/StPats_shirt2.jpg", 
            37, 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/ContestfishingVestShirt2.jpg", 
            38, 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/ContestFishtankShirt1.jpg", 
            39, 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/ContestPawShirt1.jpg", 
            40, 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/CowboyShirt1.jpg", 
            41, 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/CowboyShirt2.jpg", 
            42, 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/CowboyShirt3.jpg", 
            43, 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/CowboyShirt4.jpg", 
            44, 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/CowboyShirt5.jpg", 
            45, 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/CowboyShirt6.jpg", 
            46, 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/4thJulyShirt1.jpg", 
            47, 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/4thJulyShirt2.jpg", 
            48, 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/shirt_Cat7_01.jpg", 
            49, 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/shirt_Cat7_02.jpg", 
            50, 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/contest_backpack3.jpg", 
            51, 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/contest_leder.jpg", 
            52, 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/contest_mellon2.jpg", 
            53, 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/contest_race2.jpg", 
            54, 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/PJBlueBanana2.jpg", 
            55, 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/PJRedHorn2.jpg", 
            56, 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/PJGlasses2.jpg", 
            57, 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine1.jpg", 
            58, 
            [
                "27"
            ]
        ], 
        "57": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine2.jpg", 
            59, 
            [
                "27"
            ]
        ], 
        "58": [
            "phase_4/maps/tt_t_chr_avt_shirt_desat4.jpg", 
            60, 
            [
                "27"
            ]
        ], 
        "59": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing1.jpg", 
            61, 
            [
                "27"
            ]
        ], 
        "60": [
            "phase_4/maps/tt_t_chr_avt_shirt_fishing2.jpg", 
            62, 
            [
                "27"
            ]
        ], 
        "61": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening1.jpg", 
            63, 
            [
                "27"
            ]
        ], 
        "62": [
            "phase_4/maps/tt_t_chr_avt_shirt_gardening2.jpg", 
            64, 
            [
                "27"
            ]
        ], 
        "63": [
            "phase_4/maps/tt_t_chr_avt_shirt_party1.jpg", 
            65, 
            [
                "27"
            ]
        ], 
        "64": [
            "phase_4/maps/tt_t_chr_avt_shirt_party2.jpg", 
            66, 
            [
                "27"
            ]
        ], 
        "65": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing1.jpg", 
            67, 
            [
                "27"
            ]
        ], 
        "66": [
            "phase_4/maps/tt_t_chr_avt_shirt_racing2.jpg", 
            68, 
            [
                "27"
            ]
        ], 
        "67": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer1.jpg", 
            69, 
            [
                "27"
            ]
        ], 
        "68": [
            "phase_4/maps/tt_t_chr_avt_shirt_summer2.jpg", 
            70, 
            [
                "27"
            ]
        ], 
        "69": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf1.jpg", 
            71, 
            [
                "27"
            ]
        ], 
        "70": [
            "phase_4/maps/tt_t_chr_avt_shirt_golf2.jpg", 
            72, 
            [
                "27"
            ]
        ], 
        "71": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween1.jpg", 
            73, 
            [
                "27"
            ]
        ], 
        "72": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween2.jpg", 
            74, 
            [
                "27"
            ]
        ], 
        "73": [
            "phase_4/maps/tt_t_chr_avt_shirt_marathon1.jpg", 
            75, 
            [
                "27"
            ]
        ], 
        "74": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.jpg", 
            76, 
            [
                "27"
            ]
        ], 
        "75": [
            "phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.jpg", 
            77, 
            [
                "27"
            ]
        ], 
        "76": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask1.jpg", 
            78, 
            [
                "27"
            ]
        ], 
        "77": [
            "phase_4/maps/tt_t_chr_avt_shirt_toonTask2.jpg", 
            79, 
            [
                "27"
            ]
        ], 
        "78": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley1.jpg", 
            80, 
            [
                "27"
            ]
        ], 
        "79": [
            "phase_4/maps/tt_t_chr_avt_shirt_trolley2.jpg", 
            81, 
            [
                "27"
            ]
        ], 
        "80": [
            "phase_4/maps/tt_t_chr_avt_shirt_winter1.jpg", 
            82, 
            [
                "27"
            ]
        ], 
        "81": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween3.jpg", 
            83, 
            [
                "27"
            ]
        ], 
        "82": [
            "phase_4/maps/tt_t_chr_avt_shirt_halloween4.jpg", 
            84, 
            [
                "27"
            ]
        ], 
        "83": [
            "phase_4/maps/tt_t_chr_avt_shirt_valentine3.jpg", 
            85, 
            [
                "27"
            ]
        ], 
        "84": [
            "phase_4/maps/tt_t_chr_shirt_scientistC.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "85": [
            "phase_4/maps/tt_t_chr_shirt_scientistA.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "86": [
            "phase_4/maps/tt_t_chr_shirt_scientistB.jpg", 
            86, 
            [
                "27"
            ]
        ], 
        "87": [
            "phase_4/maps/tt_t_chr_avt_shirt_mailbox.jpg", 
            87, 
            [
                "27"
            ]
        ], 
        "88": [
            "phase_4/maps/tt_t_chr_avt_shirt_trashcan.jpg", 
            88, 
            [
                "27"
            ]
        ], 
        "89": [
            "phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.jpg", 
            89, 
            [
                "27"
            ]
        ], 
        "90": [
            "phase_4/maps/tt_t_chr_avt_shirt_hydrant.jpg", 
            90, 
            [
                "27"
            ]
        ], 
        "91": [
            "phase_4/maps/tt_t_chr_avt_shirt_whistle.jpg", 
            91, 
            [
                "27"
            ]
        ], 
        "92": [
            "phase_4/maps/tt_t_chr_avt_shirt_cogbuster.jpg", 
            92, 
            [
                "27"
            ]
        ], 
        "93": [
            "phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.jpg", 
            93, 
            [
                "27"
            ]
        ], 
        "94": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.jpg", 
            94, 
            [
                "27"
            ]
        ], 
        "95": [
            "phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.jpg", 
            95, 
            [
                "27"
            ]
        ], 
        "96": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.jpg", 
            96, 
            [
                "27"
            ]
        ], 
        "97": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.jpg", 
            97, 
            [
                "27"
            ]
        ], 
        "98": [
            "phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.jpg", 
            98, 
            [
                "27"
            ]
        ], 
        "99": [
            "phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.jpg", 
            99, 
            [
                "27"
            ]
        ]
    }

    femaleBottomDNA2femaleBottom = {
        "00": [
            "phase_3/maps/desat_skirt_1.jpg", 
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
            "phase_3/maps/desat_skirt_2.jpg", 
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
            "phase_3/maps/desat_skirt_3.jpg", 
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
            "phase_3/maps/desat_skirt_4.jpg", 
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
            "phase_3/maps/desat_skirt_5.jpg", 
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
            "phase_3/maps/desat_skirt_6.jpg", 
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
            "phase_3/maps/desat_skirt_7.jpg", 
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
            "phase_4/maps/female_skirt1.jpg", 
            [
                "27"
            ]
        ], 
        "08": [
            "phase_4/maps/female_skirt2.jpg", 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_4/maps/female_skirt3.jpg", 
            [
                "27"
            ]
        ], 
        "10": [
            "phase_4/maps/VdaySkirt1.jpg", 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_4/maps/skirtNew5.jpg", 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_4/maps/CowboySkirt1.jpg", 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_4/maps/CowboySkirt2.jpg", 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_4/maps/4thJulySkirt1.jpg", 
            [
                "27"
            ]
        ], 
        "15": [
            "phase_4/maps/skirtCat7_01.jpg", 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter1.jpg", 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter2.jpg", 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter3.jpg", 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/tt_t_chr_avt_skirt_winter4.jpg", 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/tt_t_chr_avt_skirt_valentine1.jpg", 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/tt_t_chr_avt_skirt_valentine2.jpg", 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/tt_t_chr_avt_skirt_fishing1.jpg", 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/tt_t_chr_avt_skirt_gardening1.jpg", 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/tt_t_chr_avt_skirt_party1.jpg", 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing1.jpg", 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/tt_t_chr_avt_skirt_summer1.jpg", 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf1.jpg", 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween1.jpg", 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween2.jpg", 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/tt_t_chr_avt_skirt_saveBuilding1.jpg", 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/tt_t_chr_avt_skirt_trolley1.jpg", 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween3.jpg", 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/tt_t_chr_avt_skirt_halloween4.jpg", 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/tt_t_chr_avt_skirt_greentoon1.jpg", 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/tt_t_chr_avt_skirt_racingGrandPrix.jpg", 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/tt_t_chr_avt_skirt_pirate.jpg", 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf02.jpg", 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing03.jpg", 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf03.jpg", 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/tt_t_chr_avt_skirt_golf04.jpg", 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing04.jpg", 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/tt_t_chr_avt_skirt_racing05.jpg", 
            [
                "27"
            ]
        ],
        "43": [
            "phase_4/maps/tsaskirt.jpg",
            [
                "27"
            ]
        ],
        "44": [
            "phase_4/maps/tsaskirt_dev.jpg",
            [
                "27"
            ]
        ]
    }

    maleBottomDNA2maleBottom = {
        "00": [
            "phase_3/maps/desat_shorts_1.jpg", 
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
            "phase_3/maps/desat_shorts_2.jpg", 
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
            "phase_3/maps/desat_shorts_4.jpg", 
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
            "phase_3/maps/desat_shorts_6.jpg", 
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
            "phase_3/maps/desat_shorts_7.jpg", 
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
            "phase_3/maps/desat_shorts_8.jpg", 
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
            "phase_3/maps/desat_shorts_9.jpg", 
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
            "phase_3/maps/desat_shorts_10.jpg", 
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
            "phase_4/maps/VdayShorts2.jpg", 
            [
                "27"
            ]
        ], 
        "09": [
            "phase_4/maps/shorts4.jpg", 
            [
                "27"
            ]
        ], 
        "10": [
            "phase_4/maps/shorts1.jpg", 
            [
                "27"
            ]
        ], 
        "11": [
            "phase_4/maps/shorts5.jpg", 
            [
                "27"
            ]
        ], 
        "12": [
            "phase_4/maps/CowboyShorts1.jpg", 
            [
                "27"
            ]
        ], 
        "13": [
            "phase_4/maps/CowboyShorts2.jpg", 
            [
                "27"
            ]
        ], 
        "14": [
            "phase_4/maps/4thJulyShorts1.jpg", 
            [
                "27"
            ]
        ], 
        "15": [
            "phase_4/maps/shortsCat7_01.jpg", 
            [
                "27"
            ]
        ], 
        "16": [
            "phase_4/maps/Blue_shorts_1.jpg", 
            [
                "27"
            ]
        ], 
        "17": [
            "phase_4/maps/Red_shorts_1.jpg", 
            [
                "27"
            ]
        ], 
        "18": [
            "phase_4/maps/Purple_shorts_1.jpg", 
            [
                "27"
            ]
        ], 
        "19": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter1.jpg", 
            [
                "27"
            ]
        ], 
        "20": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter2.jpg", 
            [
                "27"
            ]
        ], 
        "21": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter3.jpg", 
            [
                "27"
            ]
        ], 
        "22": [
            "phase_4/maps/tt_t_chr_avt_shorts_winter4.jpg", 
            [
                "27"
            ]
        ], 
        "23": [
            "phase_4/maps/tt_t_chr_avt_shorts_valentine1.jpg", 
            [
                "27"
            ]
        ], 
        "24": [
            "phase_4/maps/tt_t_chr_avt_shorts_valentine2.jpg", 
            [
                "27"
            ]
        ], 
        "25": [
            "phase_4/maps/tt_t_chr_avt_shorts_fishing1.jpg", 
            [
                "27"
            ]
        ], 
        "26": [
            "phase_4/maps/tt_t_chr_avt_shorts_gardening1.jpg", 
            [
                "27"
            ]
        ], 
        "27": [
            "phase_4/maps/tt_t_chr_avt_shorts_party1.jpg", 
            [
                "27"
            ]
        ], 
        "28": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing1.jpg", 
            [
                "27"
            ]
        ], 
        "29": [
            "phase_4/maps/tt_t_chr_avt_shorts_summer1.jpg", 
            [
                "27"
            ]
        ], 
        "30": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf1.jpg", 
            [
                "27"
            ]
        ], 
        "31": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween1.jpg", 
            [
                "27"
            ]
        ], 
        "32": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween2.jpg", 
            [
                "27"
            ]
        ], 
        "33": [
            "phase_4/maps/tt_t_chr_avt_shorts_saveBuilding1.jpg", 
            [
                "27"
            ]
        ], 
        "34": [
            "phase_4/maps/tt_t_chr_avt_shorts_trolley1.jpg", 
            [
                "27"
            ]
        ], 
        "35": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween4.jpg", 
            [
                "27"
            ]
        ], 
        "36": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween3.jpg", 
            [
                "27"
            ]
        ], 
        "37": [
            "phase_4/maps/tt_t_chr_shorts_scientistA.jpg", 
            [
                "27"
            ]
        ], 
        "38": [
            "phase_4/maps/tt_t_chr_shorts_scientistB.jpg", 
            [
                "27"
            ]
        ], 
        "39": [
            "phase_4/maps/tt_t_chr_shorts_scientistC.jpg", 
            [
                "27"
            ]
        ], 
        "40": [
            "phase_4/maps/tt_t_chr_avt_shorts_cogbuster.jpg", 
            [
                "27"
            ]
        ], 
        "41": [
            "phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg", 
            [
                "27"
            ]
        ], 
        "42": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloween5.jpg", 
            [
                "27"
            ]
        ], 
        "43": [
            "phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.jpg", 
            [
                "27"
            ]
        ], 
        "44": [
            "phase_4/maps/tt_t_chr_avt_shorts_greentoon1.jpg", 
            [
                "27"
            ]
        ], 
        "45": [
            "phase_4/maps/tt_t_chr_avt_shorts_racingGrandPrix.jpg", 
            [
                "27"
            ]
        ], 
        "46": [
            "phase_4/maps/tt_t_chr_avt_shorts_bee.jpg", 
            [
                "27"
            ]
        ], 
        "47": [
            "phase_4/maps/tt_t_chr_avt_shorts_pirate.jpg", 
            [
                "27"
            ]
        ], 
        "48": [
            "phase_4/maps/tt_t_chr_avt_shorts_supertoon.jpg", 
            [
                "27"
            ]
        ], 
        "49": [
            "phase_4/maps/tt_t_chr_avt_shorts_vampire.jpg", 
            [
                "27"
            ]
        ], 
        "50": [
            "phase_4/maps/tt_t_chr_avt_shorts_dinosaur.jpg", 
            [
                "27"
            ]
        ], 
        "51": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf03.jpg", 
            [
                "27"
            ]
        ], 
        "52": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing03.jpg", 
            [
                "27"
            ]
        ], 
        "53": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf04.jpg", 
            [
                "27"
            ]
        ], 
        "54": [
            "phase_4/maps/tt_t_chr_avt_shorts_golf05.jpg", 
            [
                "27"
            ]
        ], 
        "55": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing04.jpg", 
            [
                "27"
            ]
        ], 
        "56": [
            "phase_4/maps/tt_t_chr_avt_shorts_racing05.jpg", 
            [
                "27"
            ]
        ],
        "57": [
            "phase_4/maps/tsashorts.jpg",
            [
                "27"
            ]
        ],
        "58": [
            "phase_4/maps/tsashorts_dev.jpg",
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
        return self.getDNAStrand() == NPC_DNA['Coach']

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
