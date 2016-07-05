"""

  Filename: ToonDNA.py
  Created by: blach (10Nov14)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import types
from pprint import _id

from lib.coginvasion.npc.NPCGlobals import NPC_DNA

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
                    '26': 'phase_4/maps/tt_t_chr_shirt_scientistC.jpg'}
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
                        '24': 'phase_4/maps/tt_t_chr_shirtSleeve_scientist.jpg'}
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
                    '26': 'phase_3/maps/desat_shorts_14.jpg'}
    gender2genderDNA = {v: k for k, v in genderDNA2gender.items()}
    animal2animalDNA = {v: k for k, v in animalDNA2animal.items()}
    head2headDNA = {v: k for k, v in headDNA2head.items()}
    color2colorDNA = {v: k for k, v in colorDNA2color.items()}
    torso2torsoDNA = {v: k for k, v in torsoDNA2torso.items()}
    leg2legDNA = {v: k for k, v in legDNA2leg.items()}
    shirt2shirtDNA = {v: k for k, v in shirtDNA2shirt.items()}
    sleeve2sleeveDNA = {v: k for k, v in sleeveDNA2sleeve.items()}
    short2shortDNA = {v: k for k, v in shortDNA2short.items()}

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
        shorts = self.short2shortDNA[self.shorts]
        shirtColor = self.color2colorDNA[self.shirtColor]
        sleeveColor = self.color2colorDNA[self.sleeveColor]
        shortColor = self.color2colorDNA[self.shortColor]
        gloveColor = self.color2colorDNA[self.gloveColor]
        strand = "%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s" % (
            gender, animal, head, headcolor, torso,
            torsocolor, legs, legcolor, shirt, sleeve,
            shorts, shirtColor, sleeveColor, shortColor, gloveColor
            )
        self.setDNAStrand(strand)

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
            self.shorts = self.shortDNA2short[dnaParts[10]]
            self.shirtColor = self.colorDNA2color[dnaParts[11]]
            self.sleeveColor = self.colorDNA2color[dnaParts[12]]
            self.shortColor = self.colorDNA2color[dnaParts[13]]
            self.gloveColor = self.colorDNA2color[dnaParts[14]]
        else:
            self.notify.error("The DNA strand %s is formatted incorrectly." % dnaStrand)
