"""

  Filename: ToonDNA.py
  Created by: blach (10Nov14)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import types
from pprint import _id

from lib.coginvasion.npc.NPCGlobals import NPC_DNA
from panda3d.core import VBase4, LVecBase4f
import random

class ToonDNA:
    notify = directNotify.newCategory("ToonDNA")
    # The length of the strand must be exactly this:
    requiredStrandLength = 30
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
    clothesColors = [
        VBase4(0.933594, 0.265625, 0.28125, 1.0),
        VBase4(0.863281, 0.40625, 0.417969, 1.0),
        VBase4(0.710938, 0.234375, 0.4375, 1.0),
        VBase4(0.992188, 0.480469, 0.167969, 1.0),
        VBase4(0.996094, 0.898438, 0.320312, 1.0),
        VBase4(0.550781, 0.824219, 0.324219, 1.0),
        VBase4(0.242188, 0.742188, 0.515625, 1.0),
        VBase4(0.433594, 0.90625, 0.835938, 1.0),
        VBase4(0.347656, 0.820312, 0.953125, 1.0),
        VBase4(0.191406, 0.5625, 0.773438, 1.0),
        VBase4(0.285156, 0.328125, 0.726562, 1.0),
        VBase4(0.460938, 0.378906, 0.824219, 1.0),
        VBase4(0.546875, 0.28125, 0.75, 1.0),
        VBase4(0.570312, 0.449219, 0.164062, 1.0),
        VBase4(0.640625, 0.355469, 0.269531, 1.0),
        VBase4(0.996094, 0.695312, 0.511719, 1.0),
        VBase4(0.832031, 0.5, 0.296875, 1.0),
        VBase4(0.992188, 0.480469, 0.167969, 1.0),
        VBase4(0.550781, 0.824219, 0.324219, 1.0),
        VBase4(0.433594, 0.90625, 0.835938, 1.0),
        VBase4(0.347656, 0.820312, 0.953125, 1.0),
        VBase4(0.96875, 0.691406, 0.699219, 1.0),
        VBase4(0.996094, 0.957031, 0.597656, 1.0),
        VBase4(0.855469, 0.933594, 0.492188, 1.0),
        VBase4(0.558594, 0.589844, 0.875, 1.0),
        VBase4(0.726562, 0.472656, 0.859375, 1.0),
        VBase4(0.898438, 0.617188, 0.90625, 1.0),
        VBase4(1.0, 1.0, 1.0, 1.0),
        VBase4(0.0, 0.2, 0.956862, 1.0),
        VBase4(0.972549, 0.094117, 0.094117, 1.0),
        VBase4(0.447058, 0.0, 0.90196, 1.0),
        VBase4(0.3, 0.3, 0.35, 1.0)
    ]
    clothesColorDNA2clothesColor = {
       '00' : LVecBase4f(0.933594, 0.265625, 0.28125, 1),
       '01' : LVecBase4f(0.863281, 0.40625, 0.417969, 1),
       '02' : LVecBase4f(0.710938, 0.234375, 0.4375, 1),
       '03' : LVecBase4f(0.992188, 0.480469, 0.167969, 1),
       '04' : LVecBase4f(0.996094, 0.898438, 0.320312, 1),
       '05' : LVecBase4f(0.550781, 0.824219, 0.324219, 1),
       '06' : LVecBase4f(0.242188, 0.742188, 0.515625, 1),
       '07' : LVecBase4f(0.433594, 0.90625, 0.835938, 1),
       '08' : LVecBase4f(0.347656, 0.820312, 0.953125, 1),
       '09' : LVecBase4f(0.191406, 0.5625, 0.773438, 1),
       '10' : LVecBase4f(0.285156, 0.328125, 0.726562, 1),
       '11' : LVecBase4f(0.460938, 0.378906, 0.824219, 1),
       '12' : LVecBase4f(0.546875, 0.28125, 0.75, 1),
       '13' : LVecBase4f(0.570312, 0.449219, 0.164062, 1),
       '14' : LVecBase4f(0.640625, 0.355469, 0.269531, 1),
       '15' : LVecBase4f(0.996094, 0.695312, 0.511719, 1),
       '16' : LVecBase4f(0.832031, 0.5, 0.296875, 1),
       '17' : LVecBase4f(0.992188, 0.480469, 0.167969, 1),
       '18' : LVecBase4f(0.550781, 0.824219, 0.324219, 1),
       '19' : LVecBase4f(0.433594, 0.90625, 0.835938, 1),
       '20' : LVecBase4f(0.347656, 0.820312, 0.953125, 1),
       '21' : LVecBase4f(0.96875, 0.691406, 0.699219, 1),
       '22' : LVecBase4f(0.996094, 0.957031, 0.597656, 1),
       '23' : LVecBase4f(0.855469, 0.933594, 0.492188, 1),
       '24' : LVecBase4f(0.558594, 0.589844, 0.875, 1),
       '25' : LVecBase4f(0.726562, 0.472656, 0.859375, 1),
       '26' : LVecBase4f(0.898438, 0.617188, 0.90625, 1),
       '27' : LVecBase4f(1, 1, 1, 1),
       '28' : LVecBase4f(0, 0.2, 0.956862, 1),
       '29' : LVecBase4f(0.972549, 0.094117, 0.094117, 1),
       '30' : LVecBase4f(0.447058, 0, 0.90196, 1),
       '31' : LVecBase4f(0.3, 0.3, 0.35, 1)
    }
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
    colorName2DNAcolor = {'white' : colors[0],
                          'peach' : colors[1],
                          'bright red' : colors[2],
                          'red' : colors[3],
                          'maroon' : colors[4],
                          'sienna' : colors[5],
                          'brown' : colors[6],
                          'tan' : colors[7],
                          'coral' : colors[8],
                          'orange' : colors[9],
                          'yellow' : colors[10],
                          'cream' : colors[11],
                          'citrine' : colors[12],
                          'lime green' : colors[13],
                          'sea green' : colors[14],
                          'green' : colors[15],
                          'light blue' : colors[16],
                          'aqua' : colors[17],
                          'blue' : colors[18],
                          'periwinkle' : colors[19],
                          'royal blue' : colors[20],
                          'slate blue' : colors[21],
                          'purple' : colors[22],
                          'lavender' : colors[23],
                          'pink' : colors[24],
                          'gray' : colors[25],
                          'black' : colors[26]
                          }
    colorDNA2color = {'00': colors[0],
                    '01': colors[1],
                    '02': colors[2],
                    '03': colors[3],
                    '04': colors[4],
                    '05': colors[5],
                    '06': colors[6],
                    '07': colors[7],
                    '08': colors[8],
                    '09': colors[9],
                    '10': colors[10],
                    '11': colors[11],
                    '12': colors[12],
                    '13': colors[13],
                    '14': colors[14],
                    '15': colors[15],
                    '16': colors[16],
                    '17': colors[17],
                    '18': colors[18],
                    '19': colors[19],
                    '20': colors[20],
                    '21': colors[21],
                    '22': colors[22],
                    '23': colors[23],
                    '24': colors[24],
                    '25': colors[25],
                    '26': colors[26]}
    torsoDNA2torso = {'00': 'dgs_shorts',
                    '01': 'dgm_shorts',
                    '02': 'dgl_shorts',
                    '03': 'dgs_skirt',
                    '04': 'dgm_skirt',
                    '05': 'dgl_skirt'}
    legDNA2leg = {'00': 'dgs',
                '01': 'dgm',
                '02': 'dgl'}
    shirtDNA2shirt = {
       '00' : 'phase_3/maps/desat_shirt_1.jpg',
       '01' : 'phase_3/maps/desat_shirt_2.jpg',
       '02' : 'phase_3/maps/desat_shirt_3.jpg',
       '03' : 'phase_3/maps/desat_shirt_4.jpg',
       '04' : 'phase_3/maps/desat_shirt_5.jpg',
       '05' : 'phase_3/maps/desat_shirt_6.jpg',
       '06' : 'phase_3/maps/desat_shirt_7.jpg',
       '07' : 'phase_3/maps/desat_shirt_8.jpg',
       '08' : 'phase_3/maps/desat_shirt_9.jpg',
       '09' : 'phase_3/maps/desat_shirt_10.jpg',
       '10' : 'phase_3/maps/desat_shirt_11.jpg',
       '11' : 'phase_3/maps/desat_shirt_12.jpg',
       '12' : 'phase_3/maps/desat_shirt_13.jpg',
       '13' : 'phase_3/maps/desat_shirt_14.jpg',
       '14' : 'phase_3/maps/desat_shirt_15.jpg',
       '15' : 'phase_3/maps/desat_shirt_16.jpg',
       '16' : 'phase_3/maps/desat_shirt_17.jpg',
       '17' : 'phase_3/maps/desat_shirt_18.jpg',
       '18' : 'phase_3/maps/desat_shirt_19.jpg',
       '19' : 'phase_3/maps/desat_shirt_20.jpg',
       '20' : 'phase_3/maps/desat_shirt_21.jpg',
       '21' : 'phase_3/maps/desat_shirt_22.jpg',
       '22' : 'phase_3/maps/desat_shirt_23.jpg',
       '23' : 'phase_4/maps/female_shirt1b.jpg',
       '24' : 'phase_4/maps/female_shirt2.jpg',
       '25' : 'phase_4/maps/female_shirt3.jpg',
       '26' : 'phase_4/maps/male_shirt1.jpg',
       '27' : 'phase_4/maps/male_shirt2_palm.jpg',
       '28' : 'phase_4/maps/male_shirt3c.jpg',
       '29' : 'phase_4/maps/shirt_ghost.jpg',
       '30' : 'phase_4/maps/shirt_pumkin.jpg',
       '31' : 'phase_4/maps/holiday_shirt1.jpg',
       '32' : 'phase_4/maps/holiday_shirt2b.jpg',
       '33' : 'phase_4/maps/holidayShirt3b.jpg',
       '34' : 'phase_4/maps/holidayShirt4.jpg',
       '35' : 'phase_4/maps/female_shirt1b.jpg',
       '36' : 'phase_4/maps/female_shirt5New.jpg',
       '37' : 'phase_4/maps/shirtMale4B.jpg',
       '38' : 'phase_4/maps/shirt6New.jpg',
       '39' : 'phase_4/maps/shirtMaleNew7.jpg',
       '40' : 'phase_4/maps/femaleShirtNew6.jpg',
       '41' : 'phase_4/maps/Vday1Shirt5.jpg',
       '42' : 'phase_4/maps/Vday1Shirt6SHD.jpg',
       '43' : 'phase_4/maps/Vday1Shirt4.jpg',
       '44' : 'phase_4/maps/Vday_shirt2c.jpg',
       '45' : 'phase_4/maps/shirtTieDyeNew.jpg',
       '46' : 'phase_4/maps/male_shirt1.jpg',
       '47' : 'phase_4/maps/StPats_shirt1.jpg',
       '48' : 'phase_4/maps/StPats_shirt2.jpg',
       '49' : 'phase_4/maps/ContestfishingVestShirt2.jpg',
       '50' : 'phase_4/maps/ContestFishtankShirt1.jpg',
       '51' : 'phase_4/maps/ContestPawShirt1.jpg',
       '52' : 'phase_4/maps/CowboyShirt1.jpg',
       '53' : 'phase_4/maps/CowboyShirt2.jpg',
       '54' : 'phase_4/maps/CowboyShirt3.jpg',
       '55' : 'phase_4/maps/CowboyShirt4.jpg',
       '56' : 'phase_4/maps/CowboyShirt5.jpg',
       '57' : 'phase_4/maps/CowboyShirt6.jpg',
       '58' : 'phase_4/maps/4thJulyShirt1.jpg',
       '59' : 'phase_4/maps/4thJulyShirt2.jpg',
       '60' : 'phase_4/maps/shirt_Cat7_01.jpg',
       '61' : 'phase_4/maps/shirt_Cat7_02.jpg',
       '62' : 'phase_4/maps/contest_backpack3.jpg',
       '63' : 'phase_4/maps/contest_leder.jpg',
       '64' : 'phase_4/maps/contest_mellon2.jpg',
       '65' : 'phase_4/maps/contest_race2.jpg',
       '66' : 'phase_4/maps/PJBlueBanana2.jpg',
       '67' : 'phase_4/maps/PJRedHorn2.jpg',
       '68' : 'phase_4/maps/PJGlasses2.jpg',
       '69' : 'phase_4/maps/tt_t_chr_avt_shirt_valentine1.jpg',
       '70' : 'phase_4/maps/tt_t_chr_avt_shirt_valentine2.jpg',
       '71' : 'phase_4/maps/tt_t_chr_avt_shirt_desat4.jpg',
       '72' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing1.jpg',
       '73' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing2.jpg',
       '74' : 'phase_4/maps/tt_t_chr_avt_shirt_gardening1.jpg',
       '75' : 'phase_4/maps/tt_t_chr_avt_shirt_gardening2.jpg',
       '76' : 'phase_4/maps/tt_t_chr_avt_shirt_party1.jpg',
       '77' : 'phase_4/maps/tt_t_chr_avt_shirt_party2.jpg',
       '78' : 'phase_4/maps/tt_t_chr_avt_shirt_racing1.jpg',
       '79' : 'phase_4/maps/tt_t_chr_avt_shirt_racing2.jpg',
       '80' : 'phase_4/maps/tt_t_chr_avt_shirt_summer1.jpg',
       '81' : 'phase_4/maps/tt_t_chr_avt_shirt_summer2.jpg',
       '82' : 'phase_4/maps/tt_t_chr_avt_shirt_golf1.jpg',
       '83' : 'phase_4/maps/tt_t_chr_avt_shirt_golf2.jpg',
       '84' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween1.jpg',
       '85' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween2.jpg',
       '86' : 'phase_4/maps/tt_t_chr_avt_shirt_marathon1.jpg',
       '87' : 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.jpg',
       '88' : 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.jpg',
       '89' : 'phase_4/maps/tt_t_chr_avt_shirt_toonTask1.jpg',
       '90' : 'phase_4/maps/tt_t_chr_avt_shirt_toonTask2.jpg',
       '91' : 'phase_4/maps/tt_t_chr_avt_shirt_trolley1.jpg',
       '92' : 'phase_4/maps/tt_t_chr_avt_shirt_trolley2.jpg',
       '93' : 'phase_4/maps/tt_t_chr_avt_shirt_winter1.jpg',
       '94' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween3.jpg',
       '95' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween4.jpg',
       '96' : 'phase_4/maps/tt_t_chr_avt_shirt_valentine3.jpg',
       '97' : 'phase_4/maps/tt_t_chr_shirt_scientistC.jpg',
       '98' : 'phase_4/maps/tt_t_chr_shirt_scientistA.jpg',
       '99' : 'phase_4/maps/tt_t_chr_shirt_scientistB.jpg',
       '100' : 'phase_4/maps/tt_t_chr_avt_shirt_mailbox.jpg',
       '101' : 'phase_4/maps/tt_t_chr_avt_shirt_trashcan.jpg',
       '102' : 'phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.jpg',
       '103' : 'phase_4/maps/tt_t_chr_avt_shirt_hydrant.jpg',
       '104' : 'phase_4/maps/tt_t_chr_avt_shirt_whistle.jpg',
       '105' : 'phase_4/maps/tt_t_chr_avt_shirt_cogbuster.jpg',
       '106' : 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.jpg',
       '107' : 'phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.jpg',
       '108' : 'phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.jpg',
       '109' : 'phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.jpg',
       '110' : 'phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.jpg',
       '111' : 'phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.jpg',
       '112' : 'phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.jpg',
       '113' : 'phase_4/maps/tt_t_chr_avt_shirt_doodle.jpg',
       '114' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween5.jpg',
       '115' : 'phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.jpg',
       '116' : 'phase_4/maps/tt_t_chr_avt_shirt_greentoon1.jpg',
       '117' : 'phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.jpg',
       '118' : 'phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.jpg',
       '119' : 'phase_4/maps/tt_t_chr_avt_shirt_bee.jpg',
       '120' : 'phase_4/maps/tt_t_chr_avt_shirt_pirate.jpg',
       '121' : 'phase_4/maps/tt_t_chr_avt_shirt_supertoon.jpg',
       '122' : 'phase_4/maps/tt_t_chr_avt_shirt_vampire.jpg',
       '123' : 'phase_4/maps/tt_t_chr_avt_shirt_dinosaur.jpg',
       '124' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing04.jpg',
       '125' : 'phase_4/maps/tt_t_chr_avt_shirt_golf03.jpg',
       '126' : 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.jpg',
       '127' : 'phase_4/maps/tt_t_chr_avt_shirt_racing03.jpg',
       '128' : 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.jpg',
       '129' : 'phase_4/maps/tt_t_chr_avt_shirt_trolley03.jpg',
       '130' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing05.jpg',
       '131' : 'phase_4/maps/tt_t_chr_avt_shirt_golf04.jpg',
       '132' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween06.jpg',
       '133' : 'phase_4/maps/tt_t_chr_avt_shirt_winter03.jpg',
       '134' : 'phase_4/maps/tt_t_chr_avt_shirt_halloween07.jpg',
       '135' : 'phase_4/maps/tt_t_chr_avt_shirt_winter02.jpg',
       '136' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing06.jpg',
       '137' : 'phase_4/maps/tt_t_chr_avt_shirt_fishing07.jpg',
       '138' : 'phase_4/maps/tt_t_chr_avt_shirt_golf05.jpg',
       '139' : 'phase_4/maps/tt_t_chr_avt_shirt_racing04.jpg',
       '140' : 'phase_4/maps/tt_t_chr_avt_shirt_racing05.jpg',
       '141' : 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.jpg',
       '142' : 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.jpg',
       '143' : 'phase_4/maps/tt_t_chr_avt_shirt_trolley04.jpg',
       '144' : 'phase_4/maps/tt_t_chr_avt_shirt_trolley05.jpg',
       '145' : 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.jpg',
       '146' : 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.jpg',
       '147' : 'phase_4/maps/tt_t_chr_avt_shirt_anniversary.jpg'
    }
    sleeveDNA2sleeve = {
       '00' : 'phase_3/maps/desat_sleeve_1.jpg',
       '01' : 'phase_3/maps/desat_sleeve_2.jpg',
       '02' : 'phase_3/maps/desat_sleeve_3.jpg',
       '03' : 'phase_3/maps/desat_sleeve_4.jpg',
       '04' : 'phase_3/maps/desat_sleeve_5.jpg',
       '05' : 'phase_3/maps/desat_sleeve_6.jpg',
       '06' : 'phase_3/maps/desat_sleeve_7.jpg',
       '07' : 'phase_3/maps/desat_sleeve_8.jpg',
       '08' : 'phase_3/maps/desat_sleeve_9.jpg',
       '09' : 'phase_3/maps/desat_sleeve_10.jpg',
       '10' : 'phase_3/maps/desat_sleeve_15.jpg',
       '11' : 'phase_3/maps/desat_sleeve_16.jpg',
       '12' : 'phase_3/maps/desat_sleeve_19.jpg',
       '13' : 'phase_3/maps/desat_sleeve_20.jpg',
       '14' : 'phase_4/maps/female_sleeve1b.jpg',
       '15' : 'phase_4/maps/female_sleeve2.jpg',
       '16' : 'phase_4/maps/female_sleeve3.jpg',
       '17' : 'phase_4/maps/male_sleeve1.jpg',
       '18' : 'phase_4/maps/male_sleeve2_palm.jpg',
       '19' : 'phase_4/maps/male_sleeve3c.jpg',
       '20' : 'phase_4/maps/shirt_Sleeve_ghost.jpg',
       '21' : 'phase_4/maps/shirt_Sleeve_pumkin.jpg',
       '22' : 'phase_4/maps/holidaySleeve1.jpg',
       '23' : 'phase_4/maps/holidaySleeve3.jpg',
       '24' : 'phase_4/maps/female_sleeve1b.jpg',
       '25' : 'phase_4/maps/female_sleeve5New.jpg',
       '26' : 'phase_4/maps/male_sleeve4New.jpg',
       '27' : 'phase_4/maps/sleeve6New.jpg',
       '28' : 'phase_4/maps/SleeveMaleNew7.jpg',
       '29' : 'phase_4/maps/female_sleeveNew6.jpg',
       '30' : 'phase_4/maps/Vday5Sleeve.jpg',
       '31' : 'phase_4/maps/Vda6Sleeve.jpg',
       '32' : 'phase_4/maps/Vday_shirt4sleeve.jpg',
       '33' : 'phase_4/maps/Vday2cSleeve.jpg',
       '34' : 'phase_4/maps/sleeveTieDye.jpg',
       '35' : 'phase_4/maps/male_sleeve1.jpg',
       '36' : 'phase_4/maps/StPats_sleeve.jpg',
       '37' : 'phase_4/maps/StPats_sleeve2.jpg',
       '38' : 'phase_4/maps/ContestfishingVestSleeve1.jpg',
       '39' : 'phase_4/maps/ContestFishtankSleeve1.jpg',
       '40' : 'phase_4/maps/ContestPawSleeve1.jpg',
       '41' : 'phase_4/maps/CowboySleeve1.jpg',
       '42' : 'phase_4/maps/CowboySleeve2.jpg',
       '43' : 'phase_4/maps/CowboySleeve3.jpg',
       '44' : 'phase_4/maps/CowboySleeve4.jpg',
       '45' : 'phase_4/maps/CowboySleeve5.jpg',
       '46' : 'phase_4/maps/CowboySleeve6.jpg',
       '47' : 'phase_4/maps/4thJulySleeve1.jpg',
       '48' : 'phase_4/maps/4thJulySleeve2.jpg',
       '49' : 'phase_4/maps/shirt_sleeveCat7_01.jpg',
       '50' : 'phase_4/maps/shirt_sleeveCat7_02.jpg',
       '51' : 'phase_4/maps/contest_backpack_sleeve.jpg',
       '52' : 'phase_4/maps/Contest_leder_sleeve.jpg',
       '53' : 'phase_4/maps/contest_mellon_sleeve2.jpg',
       '54' : 'phase_4/maps/contest_race_sleeve.jpg',
       '55' : 'phase_4/maps/PJSleeveBlue.jpg',
       '56' : 'phase_4/maps/PJSleeveRed.jpg',
       '57' : 'phase_4/maps/PJSleevePurple.jpg',
       '58' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine1.jpg',
       '59' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine2.jpg',
       '60' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_desat4.jpg',
       '61' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing1.jpg',
       '62' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing2.jpg',
       '63' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening1.jpg',
       '64' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening2.jpg',
       '65' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_party1.jpg',
       '66' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_party2.jpg',
       '67' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing1.jpg',
       '68' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing2.jpg',
       '69' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer1.jpg',
       '70' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer2.jpg',
       '71' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf1.jpg',
       '72' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf2.jpg',
       '73' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween1.jpg',
       '74' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween2.jpg',
       '75' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_marathon1.jpg',
       '76' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding1.jpg',
       '77' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding2.jpg',
       '78' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask1.jpg',
       '79' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask2.jpg',
       '80' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley1.jpg',
       '81' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley2.jpg',
       '82' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter1.jpg',
       '83' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween3.jpg',
       '84' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween4.jpg',
       '85' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine3.jpg',
       '86' : 'phase_4/maps/tt_t_chr_shirtSleeve_scientist.jpg',
       '87' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mailbox.jpg',
       '88' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trashcan.jpg',
       '89' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_loonyLabs.jpg',
       '90' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_hydrant.jpg',
       '91' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_whistle.jpg',
       '92' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_cogbuster.jpg',
       '93' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated01.jpg',
       '94' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty01.jpg',
       '95' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty02.jpg',
       '96' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotIcon.jpg',
       '97' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotVPIcon.jpg',
       '98' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.jpg',
       '99' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_jellyBeans.jpg',
       '100' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_doodle.jpg',
       '101' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween5.jpg',
       '102' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloweenTurtle.jpg',
       '103' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_greentoon1.jpg',
       '104' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_getConnectedMoverShaker.jpg',
       '105' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racingGrandPrix.jpg',
       '106' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_bee.jpg',
       '107' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_pirate.jpg',
       '108' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_supertoon.jpg',
       '109' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_vampire.jpg',
       '110' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_dinosaur.jpg',
       '111' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing04.jpg',
       '112' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf03.jpg',
       '113' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated02.jpg',
       '114' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing03.jpg',
       '115' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding3.jpg',
       '116' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley03.jpg',
       '117' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing05.jpg',
       '118' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf04.jpg',
       '119' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween06.jpg',
       '120' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter03.jpg',
       '121' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween07.jpg',
       '122' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter02.jpg',
       '123' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing06.jpg',
       '124' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing07.jpg',
       '125' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf05.jpg',
       '126' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing04.jpg',
       '127' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing05.jpg',
       '128' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated03.jpg',
       '129' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated04.jpg',
       '130' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley04.jpg',
       '131' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley05.jpg',
       '132' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding4.jpg',
       '133' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding05.jpg',
       '134' : 'phase_4/maps/tt_t_chr_avt_shirtSleeve_anniversary.jpg'
    }
    shortDNA2short = {
       '00' : 'phase_3/maps/desat_shorts_1.jpg',
       '01' : 'phase_3/maps/desat_shorts_2.jpg',
       '02' : 'phase_3/maps/desat_shorts_4.jpg',
       '03' : 'phase_3/maps/desat_shorts_6.jpg',
       '04' : 'phase_3/maps/desat_shorts_7.jpg',
       '05' : 'phase_3/maps/desat_shorts_8.jpg',
       '06' : 'phase_3/maps/desat_shorts_9.jpg',
       '07' : 'phase_3/maps/desat_shorts_10.jpg',
       '08' : 'phase_4/maps/VdayShorts2.jpg',
       '09' : 'phase_4/maps/shorts4.jpg',
       '10' : 'phase_4/maps/shorts1.jpg',
       '11' : 'phase_4/maps/shorts5.jpg',
       '12' : 'phase_4/maps/CowboyShorts1.jpg',
       '13' : 'phase_4/maps/CowboyShorts2.jpg',
       '14' : 'phase_4/maps/4thJulyShorts1.jpg',
       '15' : 'phase_4/maps/shortsCat7_01.jpg',
       '16' : 'phase_4/maps/Blue_shorts_1.jpg',
       '17' : 'phase_4/maps/Red_shorts_1.jpg',
       '18' : 'phase_4/maps/Purple_shorts_1.jpg',
       '19' : 'phase_4/maps/tt_t_chr_avt_shorts_winter1.jpg',
       '20' : 'phase_4/maps/tt_t_chr_avt_shorts_winter2.jpg',
       '21' : 'phase_4/maps/tt_t_chr_avt_shorts_winter3.jpg',
       '22' : 'phase_4/maps/tt_t_chr_avt_shorts_winter4.jpg',
       '23' : 'phase_4/maps/tt_t_chr_avt_shorts_valentine1.jpg',
       '24' : 'phase_4/maps/tt_t_chr_avt_shorts_valentine2.jpg',
       '25' : 'phase_4/maps/tt_t_chr_avt_shorts_fishing1.jpg',
       '26' : 'phase_4/maps/tt_t_chr_avt_shorts_gardening1.jpg',
       '27' : 'phase_4/maps/tt_t_chr_avt_shorts_party1.jpg',
       '28' : 'phase_4/maps/tt_t_chr_avt_shorts_racing1.jpg',
       '29' : 'phase_4/maps/tt_t_chr_avt_shorts_summer1.jpg',
       '30' : 'phase_4/maps/tt_t_chr_avt_shorts_golf1.jpg',
       '31' : 'phase_4/maps/tt_t_chr_avt_shorts_halloween1.jpg',
       '32' : 'phase_4/maps/tt_t_chr_avt_shorts_halloween2.jpg',
       '33' : 'phase_4/maps/tt_t_chr_avt_shorts_saveBuilding1.jpg',
       '34' : 'phase_4/maps/tt_t_chr_avt_shorts_trolley1.jpg',
       '35' : 'phase_4/maps/tt_t_chr_avt_shorts_halloween4.jpg',
       '36' : 'phase_4/maps/tt_t_chr_avt_shorts_halloween3.jpg',
       '37' : 'phase_4/maps/tt_t_chr_shorts_scientistA.jpg',
       '38' : 'phase_4/maps/tt_t_chr_shorts_scientistB.jpg',
       '39' : 'phase_4/maps/tt_t_chr_shorts_scientistC.jpg',
       '40' : 'phase_4/maps/tt_t_chr_avt_shorts_cogbuster.jpg',
       '41' : 'phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg',
       '42' : 'phase_4/maps/tt_t_chr_avt_shorts_halloween5.jpg',
       '43' : 'phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.jpg',
       '44' : 'phase_4/maps/tt_t_chr_avt_shorts_greentoon1.jpg',
       '45' : 'phase_4/maps/tt_t_chr_avt_shorts_racingGrandPrix.jpg',
       '46' : 'phase_4/maps/tt_t_chr_avt_shorts_bee.jpg',
       '47' : 'phase_4/maps/tt_t_chr_avt_shorts_pirate.jpg',
       '48' : 'phase_4/maps/tt_t_chr_avt_shorts_supertoon.jpg',
       '49' : 'phase_4/maps/tt_t_chr_avt_shorts_vampire.jpg',
       '50' : 'phase_4/maps/tt_t_chr_avt_shorts_dinosaur.jpg',
       '51' : 'phase_4/maps/tt_t_chr_avt_shorts_golf03.jpg',
       '52' : 'phase_4/maps/tt_t_chr_avt_shorts_racing03.jpg',
       '53' : 'phase_4/maps/tt_t_chr_avt_shorts_golf04.jpg',
       '54' : 'phase_4/maps/tt_t_chr_avt_shorts_golf05.jpg',
       '55' : 'phase_4/maps/tt_t_chr_avt_shorts_racing04.jpg',
       '56' : 'phase_4/maps/tt_t_chr_avt_shorts_racing05.jpg',
    }
    skirtDNA2skirt = {
        '00' : ('phase_3/maps/desat_skirt_1.jpg', 1),
        '01' : ('phase_3/maps/desat_skirt_2.jpg', 1),
        '02' : ('phase_3/maps/desat_skirt_3.jpg', 1),
        '03' : ('phase_3/maps/desat_skirt_4.jpg', 1),
        '04' : ('phase_3/maps/desat_skirt_5.jpg', 1),
        '05' : ('phase_3/maps/desat_shorts_1.jpg', 0),
        '06' : ('phase_3/maps/desat_shorts_5.jpg', 0),
        '07' : ('phase_3/maps/desat_skirt_6.jpg', 1),
        '08' : ('phase_3/maps/desat_skirt_7.jpg', 1),
        '09' : ('phase_3/maps/desat_shorts_10.jpg', 0),
        '10' : ('phase_4/maps/female_skirt1.jpg', 1),
        '11' : ('phase_4/maps/female_skirt2.jpg', 1),
        '12' : ('phase_4/maps/female_skirt3.jpg', 1),
        '13' : ('phase_4/maps/VdaySkirt1.jpg', 1),
        '14' : ('phase_4/maps/skirtNew5.jpg', 1),
        '15' : ('phase_4/maps/shorts5.jpg', 0),
        '16' : ('phase_4/maps/CowboySkirt1.jpg', 1),
        '17' : ('phase_4/maps/CowboySkirt2.jpg', 1),
        '18' : ('phase_4/maps/4thJulySkirt1.jpg', 1),
        '19' : ('phase_4/maps/skirtCat7_01.jpg', 1),
        '20' : ('phase_4/maps/Blue_shorts_1.jpg', 0),
        '21' : ('phase_4/maps/Red_shorts_1.jpg', 0),
        '22' : ('phase_4/maps/Purple_shorts_1.jpg', 0),
        '23' : ('phase_4/maps/tt_t_chr_avt_skirt_winter1.jpg', 1),
        '24' : ('phase_4/maps/tt_t_chr_avt_skirt_winter2.jpg', 1),
        '25' : ('phase_4/maps/tt_t_chr_avt_skirt_winter3.jpg', 1),
        '26' : ('phase_4/maps/tt_t_chr_avt_skirt_winter4.jpg', 1),
        '27' : ('phase_4/maps/tt_t_chr_avt_skirt_valentine1.jpg', 1),
        '28' : ('phase_4/maps/tt_t_chr_avt_skirt_valentine2.jpg', 1),
        '29' : ('phase_4/maps/tt_t_chr_avt_skirt_fishing1.jpg', 1),
        '30' : ('phase_4/maps/tt_t_chr_avt_skirt_gardening1.jpg', 1),
        '31' : ('phase_4/maps/tt_t_chr_avt_skirt_party1.jpg', 1),
        '32' : ('phase_4/maps/tt_t_chr_avt_skirt_racing1.jpg', 1),
        '33' : ('phase_4/maps/tt_t_chr_avt_skirt_summer1.jpg', 1),
        '34' : ('phase_4/maps/tt_t_chr_avt_skirt_golf1.jpg', 1),
        '35' : ('phase_4/maps/tt_t_chr_avt_skirt_halloween1.jpg', 1),
        '36' : ('phase_4/maps/tt_t_chr_avt_skirt_halloween2.jpg', 1),
        '37' : ('phase_4/maps/tt_t_chr_avt_skirt_saveBuilding1.jpg', 1),
        '38' : ('phase_4/maps/tt_t_chr_avt_skirt_trolley1.jpg', 1),
        '39' : ('phase_4/maps/tt_t_chr_avt_skirt_halloween3.jpg', 1),
        '40' : ('phase_4/maps/tt_t_chr_avt_skirt_halloween4.jpg', 1),
        '41' : ('phase_4/maps/tt_t_chr_shorts_scientistA.jpg', 0),
        '42' : ('phase_4/maps/tt_t_chr_shorts_scientistB.jpg', 0),
        '43' : ('phase_4/maps/tt_t_chr_shorts_scientistC.jpg', 0),
        '44' : ('phase_4/maps/tt_t_chr_avt_shorts_cogbuster.jpg', 0),
        '45' : ('phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg', 0),
        '46' : ('phase_4/maps/tt_t_chr_avt_shorts_halloween5.jpg', 0),
        '47' : ('phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.jpg', 0),
        '48' : ('phase_4/maps/tt_t_chr_avt_skirt_greentoon1.jpg', 1),
        '49' : ('phase_4/maps/tt_t_chr_avt_skirt_racingGrandPrix.jpg', 1),
        '50' : ('phase_4/maps/tt_t_chr_avt_shorts_bee.jpg', 0),
        '51' : ('phase_4/maps/tt_t_chr_avt_shorts_pirate.jpg', 0),
        '52' : ('phase_4/maps/tt_t_chr_avt_skirt_pirate.jpg', 1),
        '53' : ('phase_4/maps/tt_t_chr_avt_shorts_supertoon.jpg', 0),
        '54' : ('phase_4/maps/tt_t_chr_avt_shorts_vampire.jpg', 0),
        '55' : ('phase_4/maps/tt_t_chr_avt_shorts_dinosaur.jpg', 0),
        '56' : ('phase_4/maps/tt_t_chr_avt_skirt_golf02.jpg', 1),
        '57' : ('phase_4/maps/tt_t_chr_avt_skirt_racing03.jpg', 1),
        '58' : ('phase_4/maps/tt_t_chr_avt_skirt_golf03.jpg', 1),
        '59' : ('phase_4/maps/tt_t_chr_avt_skirt_golf04.jpg', 1),
        '60' : ('phase_4/maps/tt_t_chr_avt_skirt_racing04.jpg', 1),
        '61' : ('phase_4/maps/tt_t_chr_avt_skirt_racing05.jpg', 1)
    }
    BoyShorts = ['phase_3/maps/desat_shorts_1.jpg',
     'phase_3/maps/desat_shorts_2.jpg',
     'phase_3/maps/desat_shorts_4.jpg',
     'phase_3/maps/desat_shorts_6.jpg',
     'phase_3/maps/desat_shorts_7.jpg',
     'phase_3/maps/desat_shorts_8.jpg',
     'phase_3/maps/desat_shorts_9.jpg',
     'phase_3/maps/desat_shorts_10.jpg',
     'phase_4/maps/VdayShorts2.jpg',
     'phase_4/maps/shorts4.jpg',
     'phase_4/maps/shorts1.jpg',
     'phase_4/maps/shorts5.jpg',
     'phase_4/maps/CowboyShorts1.jpg',
     'phase_4/maps/CowboyShorts2.jpg',
     'phase_4/maps/4thJulyShorts1.jpg',
     'phase_4/maps/shortsCat7_01.jpg',
     'phase_4/maps/Blue_shorts_1.jpg',
     'phase_4/maps/Red_shorts_1.jpg',
     'phase_4/maps/Purple_shorts_1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_winter1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_winter2.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_winter3.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_winter4.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_valentine1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_valentine2.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_fishing1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_gardening1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_party1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_racing1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_summer1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_golf1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloween1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloween2.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_saveBuilding1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_trolley1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloween4.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloween3.jpg',
     'phase_4/maps/tt_t_chr_shorts_scientistA.jpg',
     'phase_4/maps/tt_t_chr_shorts_scientistB.jpg',
     'phase_4/maps/tt_t_chr_shorts_scientistC.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_cogbuster.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloween5.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_greentoon1.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_racingGrandPrix.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_lawbotCrusher.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_bee.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_pirate.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_supertoon.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_vampire.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_dinosaur.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_golf03.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_racing03.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_golf04.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_golf05.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_racing04.jpg',
     'phase_4/maps/tt_t_chr_avt_shorts_racing05.jpg']
    SHORTS = 0
    SKIRT = 1
    GirlBottoms = [
     ('phase_3/maps/desat_skirt_1.jpg', SKIRT),
     ('phase_3/maps/desat_skirt_2.jpg', SKIRT),
     ('phase_3/maps/desat_skirt_3.jpg', SKIRT),
     ('phase_3/maps/desat_skirt_4.jpg', SKIRT),
     ('phase_3/maps/desat_skirt_5.jpg', SKIRT),
     ('phase_3/maps/desat_shorts_1.jpg', SHORTS),
     ('phase_3/maps/desat_shorts_5.jpg', SHORTS),
     ('phase_3/maps/desat_skirt_6.jpg', SKIRT),
     ('phase_3/maps/desat_skirt_7.jpg', SKIRT),
     ('phase_3/maps/desat_shorts_10.jpg', SHORTS),
     ('phase_4/maps/female_skirt1.jpg', SKIRT),
     ('phase_4/maps/female_skirt2.jpg', SKIRT),
     ('phase_4/maps/female_skirt3.jpg', SKIRT),
     ('phase_4/maps/VdaySkirt1.jpg', SKIRT),
     ('phase_4/maps/skirtNew5.jpg', SKIRT),
     ('phase_4/maps/shorts5.jpg', SHORTS),
     ('phase_4/maps/CowboySkirt1.jpg', SKIRT),
     ('phase_4/maps/CowboySkirt2.jpg', SKIRT),
     ('phase_4/maps/4thJulySkirt1.jpg', SKIRT),
     ('phase_4/maps/skirtCat7_01.jpg', SKIRT),
     ('phase_4/maps/Blue_shorts_1.jpg', SHORTS),
     ('phase_4/maps/Red_shorts_1.jpg', SHORTS),
     ('phase_4/maps/Purple_shorts_1.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_skirt_winter1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_winter2.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_winter3.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_winter4.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_valentine1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_valentine2.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_fishing1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_gardening1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_party1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_racing1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_summer1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_golf1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_halloween1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_halloween2.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_saveBuilding1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_trolley1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_halloween3.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_halloween4.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_shorts_scientistA.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_shorts_scientistB.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_shorts_scientistC.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_cogbuster.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_halloween5.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_skirt_greentoon1.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_racingGrandPrix.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_shorts_bee.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_pirate.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_skirt_pirate.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_shorts_supertoon.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_vampire.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_shorts_dinosaur.jpg', SHORTS),
     ('phase_4/maps/tt_t_chr_avt_skirt_golf02.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_racing03.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_golf03.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_golf04.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_racing04.jpg', SKIRT),
     ('phase_4/maps/tt_t_chr_avt_skirt_racing05.jpg', SKIRT)]
    BottomStyles = {'bbs1': [0, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              19,
              20]],
    'bbs2': [1, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              19,
              20]],
    'bbs3': [2, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              19,
              20]],
    'bbs4': [3, [0,
              1,
              2,
              4,
              6,
              8,
              9,
              11,
              12,
              13,
              15,
              16,
              17,
              18,
              19,
              20,
              27]],
    'bbs5': [4, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              19,
              20]],
    'bbs6': [5, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              14,
              15,
              16,
              17,
              18,
              19,
              20,
              27]],
    'bbs7': [6, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              20,
              27]],
    'bbs8': [7, [0,
              1,
              2,
              4,
              6,
              9,
              10,
              11,
              12,
              13,
              14,
              15,
              16,
              17,
              18,
              19,
              20,
              27]],
    'vd_bs1': [8, [27]],
    'vd_bs2': [23, [27]],
    'vd_bs3': [24, [27]],
    'c_bs1': [9, [27]],
    'c_bs2': [10, [27]],
    'c_bs5': [15, [27]],
    'sd_bs1': [11, [27]],
    'sd_bs2': [44, [27]],
    'pj_bs1': [16, [27]],
    'pj_bs2': [17, [27]],
    'pj_bs3': [18, [27]],
    'wh_bs1': [19, [27]],
    'wh_bs2': [20, [27]],
    'wh_bs3': [21, [27]],
    'wh_bs4': [22, [27]],
    'hw_bs1': [47, [27]],
    'hw_bs2': [48, [27]],
    'hw_bs5': [49, [27]],
    'hw_bs6': [50, [27]],
    'hw_bs7': [51, [27]],
    'gsk1': [0, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'gsk2': [1, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26]],
    'gsk3': [2, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26]],
    'gsk4': [3, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26]],
    'gsk5': [4, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26]],
    'gsk6': [7, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'gsk7': [8, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'gsh1': [5, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'gsh2': [6, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'gsh3': [9, [0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              11,
              12,
              21,
              22,
              23,
              24,
              25,
              26,
              27]],
    'c_gsk1': [10, [27]],
    'c_gsk2': [11, [27]],
    'c_gsk3': [12, [27]],
    'vd_gs1': [13, [27]],
    'vd_gs2': [27, [27]],
    'vd_gs3': [28, [27]],
    'c_gsk4': [14, [27]],
    'sd_gs1': [15, [27]],
    'sd_gs2': [48, [27]],
    'c_gsk5': [16, [27]],
    'c_gsk6': [17, [27]],
    'c_bs3': [12, [27]],
    'c_bs4': [13, [27]],
    'j4_bs1': [14, [27]],
    'j4_gs1': [18, [27]],
    'c_gsk7': [19, [27]],
    'pj_gs1': [20, [27]],
    'pj_gs2': [21, [27]],
    'pj_gs3': [22, [27]],
    'wh_gsk1': [23, [27]],
    'wh_gsk2': [24, [27]],
    'wh_gsk3': [25, [27]],
    'wh_gsk4': [26, [27]],
    'sa_bs1': [25, [27]],
    'sa_bs2': [26, [27]],
    'sa_bs3': [27, [27]],
    'sa_bs4': [28, [27]],
    'sa_bs5': [29, [27]],
    'sa_bs6': [30, [27]],
    'sa_bs7': [31, [27]],
    'sa_bs8': [32, [27]],
    'sa_bs9': [33, [27]],
    'sa_bs10': [34, [27]],
    'sa_bs11': [35, [27]],
    'sa_bs12': [36, [27]],
    'sa_bs13': [41, [27]],
    'sa_bs14': [46, [27]],
    'sa_bs15': [45, [27]],
    'sa_bs16': [52, [27]],
    'sa_bs17': [53, [27]],
    'sa_bs18': [54, [27]],
    'sa_bs19': [55, [27]],
    'sa_bs20': [56, [27]],
    'sa_bs21': [57, [27]],
    'sa_gs1': [29, [27]],
    'sa_gs2': [30, [27]],
    'sa_gs3': [31, [27]],
    'sa_gs4': [32, [27]],
    'sa_gs5': [33, [27]],
    'sa_gs6': [34, [27]],
    'sa_gs7': [35, [27]],
    'sa_gs8': [36, [27]],
    'sa_gs9': [37, [27]],
    'sa_gs10': [38, [27]],
    'sa_gs11': [39, [27]],
    'sa_gs12': [40, [27]],
    'sa_gs13': [45, [27]],
    'sa_gs14': [50, [27]],
    'sa_gs15': [49, [27]],
    'sa_gs16': [57, [27]],
    'sa_gs17': [58, [27]],
    'sa_gs18': [59, [27]],
    'sa_gs19': [60, [27]],
    'sa_gs20': [61, [27]],
    'sa_gs21': [62, [27]],
    'sc_bs1': [37, [27]],
    'sc_bs2': [38, [27]],
    'sc_bs3': [39, [27]],
    'sc_gs1': [41, [27]],
    'sc_gs2': [42, [27]],
    'sc_gs3': [43, [27]],
    'sil_bs1': [40, [27]],
    'sil_gs1': [44, [27]],
    'hw_bs3': [42, [27]],
    'hw_gs3': [46, [27]],
    'hw_bs4': [43, [27]],
    'hw_gs4': [47, [27]],
    'hw_gs1': [51, [27]],
    'hw_gs2': [52, [27]],
    'hw_gs5': [54, [27]],
    'hw_gs6': [55, [27]],
    'hw_gs7': [56, [27]],
    'hw_gsk1': [53, [27]]}
    MAKE_A_TOON = 1
    TAMMY_TAILOR = 2004
    LONGJOHN_LEROY = 1007
    TAILOR_HARMONY = 4008
    BONNIE_BLOSSOM = 5007
    WARREN_BUNDLES = 3008
    WORNOUT_WAYLON = 9010
    BOY_SHORTS = 2
    GIRL_BOTTOMS = 3
    TailorCollections = {MAKE_A_TOON: [['bss1', 'bss2'],
                   ['gss1', 'gss2'],
                   ['bbs1', 'bbs2'],
                   ['gsk1', 'gsh1']],
     TAMMY_TAILOR: [['bss1', 'bss2'],
                    ['gss1', 'gss2'],
                    ['bbs1', 'bbs2'],
                    ['gsk1', 'gsh1']],
     LONGJOHN_LEROY: [['bss3', 'bss4', 'bss14'],
                      ['gss3', 'gss4', 'gss14'],
                      ['bbs3', 'bbs4'],
                      ['gsk2', 'gsh2']],
     TAILOR_HARMONY: [['bss5', 'bss6', 'bss10'],
                      ['gss5', 'gss6', 'gss9'],
                      ['bbs5'],
                      ['gsk3', 'gsh3']],
     BONNIE_BLOSSOM: [['bss7', 'bss8', 'bss12'],
                      ['gss8', 'gss10', 'gss12'],
                      ['bbs6'],
                      ['gsk4', 'gsk5']],
     WARREN_BUNDLES: [['bss9', 'bss13'],
                      ['gss7', 'gss11'],
                      ['bbs7'],
                      ['gsk6']],
     WORNOUT_WAYLON: [['bss11', 'bss15'],
                      ['gss13', 'gss15'],
                      ['bbs8'],
                      ['gsk7']]}

    gender2genderDNA = {v: k for k, v in genderDNA2gender.items()}
    animal2animalDNA = {v: k for k, v in animalDNA2animal.items()}
    head2headDNA = {v: k for k, v in headDNA2head.items()}
    color2colorDNA = {v: k for k, v in colorDNA2color.items()}
    torso2torsoDNA = {v: k for k, v in torsoDNA2torso.items()}
    leg2legDNA = {v: k for k, v in legDNA2leg.items()}
    shirt2shirtDNA = {v: k for k, v in shirtDNA2shirt.items()}
    sleeve2sleeveDNA = {v: k for k, v in sleeveDNA2sleeve.items()}
    short2shortDNA = {v: k for k, v in shortDNA2short.items()}
    skirt2skirtDNA = {}
    for k, v in skirtDNA2skirt.items():
        skirt2skirtDNA[v[0]] = k

    clothesColor2clothesColorDNA = {v: k for k, v in clothesColorDNA2clothesColor.items()}

    def getRandomBottom(self, gender, tailorId = MAKE_A_TOON, generator = None, girlBottomType = None):
        if generator == None:
            generator = random
        collection = self.TailorCollections[tailorId]
        if gender == 'm':
            style = generator.choice(collection[self.BOY_SHORTS])
        elif girlBottomType is None:
            style = generator.choice(collection[self.GIRL_BOTTOMS])
        elif girlBottomType == self.SKIRT:
            skirtCollection = filter(lambda style: self.GirlBottoms[self.BottomStyles[style][0]][1] == self.SKIRT, collection[self.GIRL_BOTTOMS])
            style = generator.choice(skirtCollection)
        elif girlBottomType == self.SHORTS:
            shortsCollection = filter(lambda style: self.GirlBottoms[self.BottomStyles[style][0]][1] == self.SHORTS, collection[self.GIRL_BOTTOMS])
            style = generator.choice(shortsCollection)
        else:
            self.notify.error('Bad girlBottomType: %s' % girlBottomType)
        styleList = self.BottomStyles[style]
        color = generator.choice(styleList[1])
        return (styleList[0], color)

    def getBottomFromTexture(self, bottomTex, skirt = None):
        texIndex = 0
        if skirt == True:
            for tex, isShorts in self.skirtDNA2skirt.values():
                if tex == bottomTex:
                    texIndex = self.skirtDNA2skirt.values().index((tex, isShorts))
        elif skirt == False:
            texIndex = self.BoyShorts.index(bottomTex)
        else:
            bottom = self.getBottom(bottomTex)
            if len(bottom) == 2:
                texIndex = self.skirtDNA2skirt.values().index(bottom)
            else:
                texIndex = self.BoyShorts.index(bottomTex)
        for key, values in self.BottomStyles.iteritems():
            tex = values[0]
            if tex == texIndex:
                return key

    def getBottom(self, bottomTex):
        print bottomTex

        skirtValues = self.skirtDNA2skirt.values()
        if isinstance(skirtValues[0], tuple):
            return self.skirt2skirtDNA[bottomTex]
        else:
            return self.short2shortDNA[bottomTex]

    def __init__(self):
        self.dnaStrand = "00/00/00/00/00/00/00/00/00/00/00/00/00/00/00"
        self.gender = ""
        self.animal = ""
        self.head = ""
        self.headcolor = None
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

    def parseClothesColorIndexToString(self, index):
        if index < 10:
            index = '0' + str(index)
        index = str(index)
        return index

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
        shirt = self.shirt2shirtDNA[self.shirt]
        sleeve = self.sleeve2sleeveDNA[self.sleeve]
        if gender == 'boy':
            shorts = self.short2shortDNA[self.shorts]
            print 'Using dict'
        else:
            shorts = self.getBottom(self.shorts)
            print 'Using getBottom'
        print shorts
        shirtColorIndex = self.clothesColor2clothesColorDNA[self.shirtColor]
        sleeveColorIndex = self.clothesColor2clothesColorDNA[self.sleeveColor]
        shortColorIndex = self.clothesColor2clothesColorDNA[self.shortColor]
        shirtColor = self.parseClothesColorIndexToString(shirtColorIndex)
        sleeveColor = self.parseClothesColorIndexToString(sleeveColorIndex)
        shortColor = self.parseClothesColorIndexToString(shortColorIndex)
        gloveColor = "00"
        strand = "%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s" % (
            gender, animal, head, headcolor, torso,
            torsocolor, legs, legcolor, shirt, sleeve,
            shorts, shirtColor, sleeveColor, shortColor, gloveColor
            )
        print strand
        self.setDNAStrand(strand)

    def canBeInteger(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def parseDNAStrand(self, dnaStrand):
        dnaParts = dnaStrand.split('/')
        strandLength = len(dnaParts) * 2
        isString = type(dnaStrand) is types.StringType
        if (strandLength == self.requiredStrandLength and isString):
            self.gender = self.genderDNA2gender[dnaParts[0]]
            self.animal = self.animalDNA2animal[dnaParts[1]]
            self.head = self.headDNA2head[dnaParts[2]]
            self.headcolor = self.colorDNA2color[dnaParts[3]]
            self.torso = self.torsoDNA2torso[dnaParts[4]]
            self.torsocolor = self.colorDNA2color[dnaParts[5]]
            self.legs = self.legDNA2leg[dnaParts[6]]
            self.legcolor = self.colorDNA2color[dnaParts[7]]
            self.shirt = self.shirtDNA2shirt[dnaParts[8]]
            self.sleeve = self.sleeveDNA2sleeve[dnaParts[9]]
            if dnaParts[0] == '00':
                self.shorts = self.shortDNA2short[dnaParts[10]]
            else:
                self.shorts = self.skirtDNA2skirt[dnaParts[10]][0]
            self.shirtColor = self.clothesColorDNA2clothesColor[dnaParts[11]]
            self.sleeveColor = self.clothesColorDNA2clothesColor[dnaParts[12]]
            self.shortColor = self.clothesColorDNA2clothesColor[dnaParts[13]]
            self.gloveColor = self.colorDNA2color[dnaParts[14]]
        else:
            self.notify.error("The DNA strand %s is formatted incorrectly." % dnaStrand)
