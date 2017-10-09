"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonGenerator.py
@author Brian Lach
@date July ??, 2014

"""

from direct.directnotify.DirectNotify import DirectNotify
from src.coginvasion.toon import Toon
from src.coginvasion.toon.ToonDNA import ToonDNA
import random


notify = DirectNotify().newCategory("ToonGenerator")

class ToonGenerator:
    maxShirt = "14"

    maxFemBots = "06"
    maxMaleBots = "07"

    maxAnimal = "08"

    maxColor = "26"

    maxFemTorso = "05"
    minFemTorso = "03"
    maxMaleTorso = "02"
    minMaleTorso = "00"

    maxLeg = "02"

    def __init__(self, mat = None):
        #self.mat = mat
        self.toon = Toon.Toon(base.cr, mat=1)
        self.currentShirtColorIndex = 0
        self.currentBotsColorIndex = 0

    def generateToon(self, gender, matNARandomToon=0):
        genderDNA = self.toon.gender2genderDNA[gender]
        self.random_animal = random.randint(0, 8)
        shortDNA = '00'
        if self.toon.animalDNA2animal["0" + str(self.random_animal)] == "mouse":
            self.random_head = random.randint(0, 1)
        elif self.toon.animalDNA2animal["0" + str(self.random_animal)] == "dog":
            self.random_head = random.randint(4, 7)
        else:
            self.random_head = random.randint(0, 3)
        if gender == "girl":
            self.random_torso = random.randint(3, 5)
            shortDNA = '10'
        else:
            self.random_torso = random.randint(0, 2)
        self.random_legs = random.randint(0, 2)
        self.random_color = random.randint(0, 26)
        animalDNA = '0' + str(self.random_animal)
        headDNA = '0' + str(self.random_head)
        torsoDNA = '0' + str(self.random_torso)
        legsDNA = '0' + str(self.random_legs)
        if self.random_color < 10:
            colorDNA = '0' + str(self.random_color)
        else:
            colorDNA = str(self.random_color)
        dnaStrand = "%s/%s/%s/%s/%s/%s/%s/%s/00/00/27/27/00" % (
                genderDNA, animalDNA, headDNA, colorDNA, torsoDNA,
                colorDNA, legsDNA, colorDNA
                )
        self.toon.setDNAStrand(dnaStrand)
        self.currentAnimFrame = 0
        if not matNARandomToon:
            self.createToon()

    def cleanupToon(self):
        self.toon.deleteCurrentToon()
        self.toon.disable()
        self.toon.delete()
        return

    def isFinalHead(self, headDna, direction):
        if direction == 1:
            return (headDna == '03' and self.toon.animal != "mouse"
                and self.toon.animal != "dog" or
                headDna == '01' and self.toon.animal == "mouse" or
                headDna == '07' and self.toon.animal == "dog")
        elif direction == 0:
            return (headDna == '00' and self.toon.animal != "dog" or
                headDna == '04' and self.toon.animal == "dog")

    def isFinalTorso(self, torsoDna, direction):
        if direction == 1:
            if self.toon.gender == 'girl':
                return (torsoDna == self.maxFemTorso)
            else:
                return (torsoDna == self.maxMaleTorso)
        elif direction == 0:
            if self.toon.gender == 'girl':
                return (torsoDna == self.minFemTorso)
            else:
                return (torsoDna == self.minMaleTorso)

    def isFinalLeg(self, legDna, direction):
        if direction == 1:
            return (legDna == self.maxLeg)
        elif direction == 0:
            return (legDna == '00')

    def isFinalAnimal(self, animalDna, direction):
        if direction == 1:
            return (animalDna == self.maxAnimal)
        elif direction == 0:
            return (animalDna == '00')

    def isFinalTopColor(self, shirtDna, direction):
        if direction == 1:
            if self.toon.gender == 'girl':
                return self.currentShirtColorIndex >= len(ToonDNA.femaleTopDNA2femaleTop[shirtDna][2]) - 1
            else:
                return self.currentShirtColorIndex >= len(ToonDNA.maleTopDNA2maleTop[shirtDna][2]) - 1
        else:
            return self.currentShirtColorIndex == 0

    def isFinalBotColor(self, botDna, direction):
        if direction == 1:
            if self.toon.gender == 'girl':
                return self.currentBotsColorIndex >= len(ToonDNA.femaleBottomDNA2femaleBottom[botDna][1]) - 1
            else:
                return self.currentBotsColorIndex >= len(ToonDNA.maleBottomDNA2maleBottom[botDna][1]) - 1
        else:
            return self.currentBotsColorIndex == 0

    def isFinalColor(self, colorDna, direction):
        if direction == 1:
            return (colorDna == self.maxColor)
        elif direction == 0:
            return (colorDna == '00')

    def isFinalShorts(self, shortDna, direction):
        if direction == 1:
            if self.toon.gender == 'girl':
                return (shortDna == self.maxFemBots)
            else:
                return (shortDna == self.maxMaleBots)
        elif direction == 0:
            return (shortDna == '00')

    def isFinalShirt(self, shirtDna, direction):
        if direction == 1:
            return (shirtDna == self.maxShirt)
        elif direction == 0:
            return (shirtDna == '00')

    def getNextTorso(self):
        if self.isFinalTorso(self.toon.torso2torsoDNA[self.toon.torso], 1):
            if self.toon.getGender() == 'girl':
                return '03'
            else:
                return '00'
        else:
            currentTorso = int(self.toon.torso2torsoDNA[self.toon.torso])
            return '0' + str(currentTorso + 1)

    def getPrevTorso(self):
        if self.isFinalTorso(self.toon.torso2torsoDNA[self.toon.torso], 0):
            if self.toon.getGender() == 'girl':
                return '05'
            else:
                return '02'
        else:
            currentTorso = int(self.toon.torso2torsoDNA[self.toon.torso])
            return '0' + str(currentTorso - 1)

    def getNextLeg(self):
        if self.isFinalLeg(self.toon.leg2legDNA[self.toon.legs], 1):
            return '00'
        else:
            currentLeg = int(self.toon.leg2legDNA[self.toon.legs])
            return '0' + str(currentLeg + 1)

    def getPrevLeg(self):
        if self.isFinalLeg(self.toon.leg2legDNA[self.toon.legs], 0):
            return '02'
        else:
            currentLeg = int(self.toon.leg2legDNA[self.toon.legs])
            return '0' + str(currentLeg - 1)

    def getNextHead(self):
        if self.isFinalHead(self.toon.head2headDNA[self.toon.head], 1):
            if self.getNextAnimal() == '01':
                return '04'
            else:
                return '00'
        else:
            currentHead = int(self.toon.head2headDNA[self.toon.head])
            return '0' + str(currentHead + 1)

    def getNextAnimal(self):
        # Figure out what the next animal will be.
        if self.toon.animal == 'duck' and self.isFinalHead(self.toon.head2headDNA[self.toon.head], 1):
            # This is the final animal and head, just return the first animal now.
            return '00'
        elif not self.isFinalHead(self.toon.head2headDNA[self.toon.head], 1):
            # Return None when there is no next animal.
            return None
        else:
            # Figure out the next animal.
            currentAnimal = int(self.toon.animal2animalDNA[self.toon.animal])
            return '0' + str(currentAnimal + 1)

    def getPrevAnimal(self):
        # Figure out what the prev animal will be.
        if self.toon.animal == 'cat' and self.isFinalHead(self.toon.head2headDNA[self.toon.head], 0):
            # This is the final animal and head, just return the last animal now.
            return '08'
        elif not self.isFinalHead(self.toon.head2headDNA[self.toon.head], 0):
            # Return None if there is no prev animal.
            return None
        else:
            # Figure out the prev animal.
            currentAnimal = int(self.toon.animal2animalDNA[self.toon.animal])
            return '0' + str(currentAnimal - 1)

    def getPrevHead(self):
        if self.isFinalHead(self.toon.head2headDNA[self.toon.head], 0):
            if self.getPrevAnimal() == '07':
                return '01'
            elif self.getPrevAnimal() == '01':
                return '07'
            else:
                return '03'
        else:
            currentHead = int(self.toon.head2headDNA[self.toon.head])
            return '0' + str(currentHead - 1)

    def getNextClothColor(self, part):
        if part == 'bots':
            color = self.toon.shortColor
            if self.toon.gender == 'girl':
                bots = ToonDNA.femaleBottomDNA2femaleBottom
                botsRev = ToonDNA.femaleBottom2femaleBottomDNA
            else:
                bots = ToonDNA.maleBottomDNA2maleBottom
                botsRev = ToonDNA.maleBottom2maleBottomDNA
            dna = botsRev[self.toon.shorts]
            if self.isFinalBotColor(dna, 1):
                self.currentBotsColorIndex = 0
            else:
                self.currentBotsColorIndex += 1
            return bots[dna][1][self.currentBotsColorIndex]

        elif part == 'tops':
            color = self.toon.shirtColor
            if self.toon.gender == 'girl':
                tops = ToonDNA.femaleTopDNA2femaleTop
                topsRev = ToonDNA.femaleTop2femaleTopDNA
            else:
                tops = ToonDNA.maleTopDNA2maleTop
                topsRev = ToonDNA.maleTop2maleTopDNA
            dna = topsRev[self.toon.shirt]
            if self.isFinalTopColor(dna, 1):
                self.currentShirtColorIndex = 0
            else:
                self.currentShirtColorIndex += 1
            return tops[dna][2][self.currentShirtColorIndex]

    def getPrevClothColor(self, part):
        if part == 'bots':
            color = self.toon.shortColor
            if self.toon.gender == 'girl':
                bots = ToonDNA.femaleBottomDNA2femaleBottom
                botsRev = ToonDNA.femaleBottom2femaleBottomDNA
            else:
                bots = ToonDNA.maleBottomDNA2maleBottom
                botsRev = ToonDNA.maleBottom2maleBottomDNA
            dna = botsRev[self.toon.shorts]
            if self.isFinalBotColor(dna, 0):
                self.currentBotsColorIndex = len(bots[dna][1]) - 1
            else:
                self.currentBotsColorIndex -= 1
            return bots[dna][1][self.currentBotsColorIndex]

        elif part == 'tops':
            color = self.toon.shirtColor
            if self.toon.gender == 'girl':
                tops = ToonDNA.femaleTopDNA2femaleTop
                topsRev = ToonDNA.femaleTop2femaleTopDNA
            else:
                tops = ToonDNA.maleTopDNA2maleTop
                topsRev = ToonDNA.maleTop2maleTopDNA
            dna = topsRev[self.toon.shirt]
            if self.isFinalTopColor(dna, 0):
                # Return the dna code for the final top color
                self.currentShirtColorIndex = len(tops[dna][2]) - 1
            else:
                self.currentShirtColorIndex -= 1
            return tops[dna][2][self.currentShirtColorIndex]


    def getNextColor(self, part):
        if part == 'torso':
            color = self.toon.torsocolor
        elif part == 'legs':
            color = self.toon.legcolor
        elif part == 'head' or part == 'all':
            color = self.toon.headcolor
        elif part == 'shirt':
            color = self.toon.shirtColor
        elif part == 'shorts':
            color = self.toon.shortColor
        elif part == 'gloves':
            color = self.toon.gloveColor
        if self.isFinalColor(self.toon.color2colorDNA[color], 1):
            return '00'
        else:
            currentColor = int(self.toon.color2colorDNA[color])
            if currentColor < 9:
                return '0' + str(currentColor + 1)
            else:
                return str(currentColor + 1)

    def getPrevColor(self, part):
        if part == 'torso':
            color = self.toon.torsocolor
        elif part == 'legs':
            color = self.toon.legcolor
        elif part == 'head' or part == 'all':
            color = self.toon.headcolor
        elif part == 'shirt':
            color = self.toon.shirtColor
        elif part == 'shorts':
            color = self.toon.shortColor
        elif part == 'sleeve':
            color = self.toon.sleeveColor
        elif part == 'gloves':
            color = self.toon.gloveColor
        if self.isFinalColor(self.toon.color2colorDNA[color], 0):
            return '26'
        else:
            currentColor = int(self.toon.color2colorDNA[color])
            if currentColor < 11:
                return '0' + str(currentColor - 1)
            else:
                return str(currentColor - 1)

    def getNextShirtAndSleeve(self):
        return [self.getNextShirt(), self.getNextSleeve()]

    def getPrevShirtAndSleeve(self):
        return [self.getPrevShirt(), self.getPrevSleeve()]

    def getNextShirt(self):
        if self.toon.gender == 'girl':
            tops = ToonDNA.femaleTop2femaleTopDNA
        else:
            tops = ToonDNA.maleTop2maleTopDNA

        if self.isFinalTopColor(tops[self.toon.shirt], 1):
            if self.isFinalShirt(tops[self.toon.shirt], 1):
                return '00'
            else:
                currentShirt = int(tops[self.toon.shirt])
                if currentShirt < 9:
                    return '0' + str(currentShirt + 1)
                else:
                    return str(currentShirt + 1)
        else:
            return None

    def getPrevShirt(self):
        if self.toon.gender == 'girl':
            tops = ToonDNA.femaleTop2femaleTopDNA
        else:
            tops = ToonDNA.maleTop2maleTopDNA

        if self.isFinalTopColor(tops[self.toon.shirt], 0):
            if self.isFinalShirt(tops[self.toon.shirt], 0):
                return self.maxShirt
            else:
                currentShirt = int(tops[self.toon.shirt])
                if currentShirt < 11:
                    return '0' + str(currentShirt - 1)
                else:
                    return str(currentShirt - 1)
        else:
            return None

    def getNextSleeve(self):
        if self.getNextColor('sleeve') == '00':
            if self.isFinalSleeve(self.toon.sleeve2sleeveDNA[self.toon.sleeve], 1):
                return '00'
            else:
                currentSleeve = int(self.toon.sleeve2sleeveDNA[self.toon.sleeve])
                if currentSleeve < 9:
                    return '0' + str(currentSleeve + 1)
                else:
                    return str(currentSleeve + 1)
        else:
            return None

    def getPrevSleeve(self):
        if self.getPrevColor('sleeve') == '26':
            if self.isFinalSleeve(self.toon.sleeve2sleeveDNA[self.toon.sleeve], 0):
                return '22'
            else:
                currentSleeve = int(self.toon.sleeve2sleeveDNA[self.toon.sleeve])
                if currentSleeve < 11:
                    return '0' + str(currentSleeve - 1)
                else:
                    return str(currentSleeve - 1)
        else:
            return None

    def getNextShorts(self):
        if self.toon.gender == 'girl':
            bots = ToonDNA.femaleBottom2femaleBottomDNA
        else:
            bots = ToonDNA.maleBottom2maleBottomDNA

        if self.isFinalBotColor(bots[self.toon.shorts], 1):
            if self.isFinalShorts(bots[self.toon.shorts], 1):
                return '00'
            else:
                currentShorts = int(bots[self.toon.shorts])
                if currentShorts < 9:
                    return '0' + str(currentShorts + 1)
                else:
                    return str(currentShorts + 1)
        else:
            return None

    def getPrevShorts(self):
        if self.toon.gender == 'girl':
            bots = ToonDNA.femaleBottom2femaleBottomDNA
        else:
            bots = ToonDNA.maleBottom2maleBottomDNA

        if self.isFinalBotColor(bots[self.toon.shorts],0):
            if self.isFinalShorts(bots[self.toon.shorts], 0):
                return self.maxFemBots if self.toon.gender == 'girl' else self.maxMaleBots
            else:
                currentShorts = int(bots[self.toon.shorts])
                if currentShorts < 11:
                    return '0' + str(currentShorts - 1)
                else:
                    return str(currentShorts - 1)
        else:
            return None

    def generateDNAStrandWithCurrentStyle(self):
        self.currentAnimFrame = self.toon.getCurrentFrame()
        self.toon.generateDNAStrandWithCurrentStyle()
        self.createToon()

    def setToonPosForNameShop(self):
        self.toon.setPos(2.29, -3, 0)
        self.toon.setHpr(138.01, 0, 0)

    def setToonPosForGeneralShop(self):
        self.toon.setPos(0, 0, 0)
        self.toon.setHpr(180, 0, 0)

    def createToon(self):
        self.toon.reparentTo(render)
        if self.currentAnimFrame == 0:
            self.toon.animFSM.request('neutral')
        else:
            self.toon.loopFromFrameToZero('neutral', fromFrame = self.currentAnimFrame)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.toon.setH(180)
        #self.toon.deleteShadow()
