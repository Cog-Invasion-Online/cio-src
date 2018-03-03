"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RemoteAvatar.py
@author Brian Lach
@date April 28, 2015

"""

from panda3d.core import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

class RemoteAvatar:

    notify = directNotify.newCategory("RemoteAvatar")

    def __init__(self, mg, cr, avId):
        self.mg = mg
        self.cr = cr
        self.avId = avId
        self.avatar = None
        self.teamText = None
        self.team = None

        self.ogHeadColor = None
        self.ogTorsoColor = None
        self.ogLegColor = None
        self.ogShirtColor = None
        self.ogSleeveColor = None
        self.ogShortColor = None
        self.ogShirt = None
        self.ogSleeve = None
        self.ogShort = None

        self.dnaWasChanged = False

    def setTeam(self, team):
        self.team = team

        # Make this toon the complete color of the team.
        color = self.mg.getTeamDNAColor(team)
        if color is not None:
            # Store the original style so we can restore it.
            self.ogHeadColor = self.avatar.headcolor
            self.ogTorsoColor = self.avatar.torsocolor
            self.ogLegColor = self.avatar.legcolor
            self.ogShirtColor = self.avatar.shirtColor
            self.ogSleeveColor = self.avatar.sleeveColor
            self.ogShortColor = self.avatar.shortColor
            self.ogShirt = self.avatar.shirt
            self.ogSleeve = self.avatar.sleeve
            self.ogShort = self.avatar.shorts
            
            topsDict = self.avatar.maleTopDNA2maleTop
            btmsDict = self.avatar.maleBottomDNA2maleBottom
            if self.avatar.gender == 'girl':
                topsDict = self.avatar.femaleTopDNA2femaleTop
                btmsDict = self.avatar.femaleBottomDNA2femaleBottom

            self.avatar.headcolor = color
            self.avatar.torsocolor = color
            self.avatar.legcolor = color
            self.avatar.shirtColor = color
            self.avatar.sleeveColor = color
            self.avatar.shortColor = color
            self.avatar.shirt = topsDict['00'][0]
            self.avatar.sleeve = self.avatar.Sleeves[0]
            self.avatar.shorts = btmsDict['00'][0]
            # Generate the new dna strand and regenerate the toon.
            self.avatar.generateDNAStrandWithCurrentStyle()
            self.dnaWasChanged = True

        if self.teamText:
            self.teamText.removeNode()
            self.teamText = None
        textNode = TextNode('teamText')
        textNode.setAlign(TextNode.ACenter)
        textNode.setFont(CIGlobals.getMickeyFont())
        self.teamText = self.avatar.attachNewNode(textNode)
        self.teamText.setBillboardAxis()
        self.teamText.setZ(self.avatar.getNameTag().getZ() + 1.0)
        self.teamText.setScale(5.0)

    def restoreOgDna(self):
        self.avatar.headcolor = self.ogHeadColor
        self.avatar.torsocolor = self.ogTorsoColor
        self.avatar.legcolor = self.ogLegColor
        self.avatar.shirtColor = self.ogShirtColor
        self.avatar.sleeveColor = self.ogSleeveColor
        self.avatar.shortColor = self.ogShortColor
        self.avatar.shirt = self.ogShirt
        self.avatar.sleeve = self.ogSleeve
        self.avatar.shorts = self.ogShort
        # Generate the new dna strand and regenerate the toon.
        self.avatar.generateDNAStrandWithCurrentStyle()

    def getTeam(self):
        return self.team

    def retrieveAvatar(self):
        self.avatar = self.cr.doId2do.get(self.avId, None)
        self.avatar.setPythonTag('player', self.avId)
        if not self.avatar:
            self.notify.warning("Tried to create a " + self.__class__.__name__ + " when the avatar doesn't exist!")
            self.avatar = None

    def cleanup(self):
        if self.dnaWasChanged and (self.avId == base.localAvatar.doId):
            self.restoreOgDna()
        self.dnaWasChanged = None
        self.ogHeadColor = None
        self.ogTorsoColor = None
        self.ogLegColor = None
        self.ogShirtColor = None
        self.ogSleeveColor = None
        self.ogShortColor = None
        self.ogShirt = None
        self.ogSleeve = None
        self.ogShort = None
        del self.avatar
        del self.avId
        del self.cr
        del self.mg
        if self.teamText:
            self.teamText.removeNode()
            self.teamText = None
        del self.team
