"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MapPage.py
@author Maverick Liberty
@date June 17, 2016

@desc HAPPY BIRTHDAY COG INVASION ONLINE!!!
             2 YEAR ANNIVERSARY

"""

from panda3d.core import Vec4, TextNode

from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui.DirectLabel import DirectLabel

from src.coginvasion.globals import CIGlobals
from src.coginvasion.book.BookPage import BookPage
from src.coginvasion.hood import ZoneUtil

class MapPage(BookPage, DirectFrame):

    def __init__(self, book):
        BookPage.__init__(self, book, 'Map', wantHeader = False)
        DirectFrame.__init__(self, parent = book, relief = None,
            pos = (0, 0, 0.0775), image_scale = (1.8, 1, 1.35),
        scale = 0.97)

        self['image'] = loader.loadModel('phase_3.5/models/gui/toontown_map.bam')

        self.initialiseoptions(MapPage)
        self.hide()

        self.cloudPos = [[(-0.61, 0, 0.18), (0.55, 0.25, 0.37), (180, 0, 0)],
                    [(-0.54, 0, 0.34), (0.76, 0.4, 0.55), (180, 0, 0)],
                    [(-0.55, 0, -0.09), (0.72, 0.4, 0.55), (0, 0, 0)],
                    [(-0.67, 0, -0.51),  (0.5, 0.29, 0.38), (180, 0, 0)],
                    [(-0.67, 0, 0.51), (0.50, 0.29, 0.38), (0, 0, 0)],
                    [(0.67, 0, 0.51), (0.5, 0.29, 0.38), (0, 0, 0)],
                    [(0.35, 0, -0.46),  (0.63, 0.35, 0.45), (0, 0, 0)],
                    [(0.18, 0, -0.45),  (0.52, 0.27, 0.32), (0, 0, 0)],
                    [(0.67, 0, -0.44),  (0.63, 0.35, 0.48), (180, 0, 0)]]

        self.hoodClouds = [#[(0.02, 0, -0.17),  (0.63, 0.35, 0.48), (180, 0, 0), ZoneUtil.ToontownCentral],
                      [(0.63, 0, -0.13),  (0.63, 0.35, 0.40), (0, 0, 0), ZoneUtil.DonaldsDock],
                      [(0.51, 0, 0.25),  (0.57, 0.35, 0.40), (0, 0, 0), ZoneUtil.TheBrrrgh],
                      [(0.03, 0, 0.19),  (0.63, 0.35, 0.40), (180, 0, 0), ZoneUtil.MinniesMelodyland],
                      [(-0.08, 0, 0.46),  (0.54, 0.35, 0.40), (0, 0, 0), ZoneUtil.DonaldsDreamland],
                      [(-0.28, 0, -0.49),  (0.60, 0.35, 0.45), (0, 0, 0), ZoneUtil.DaisyGardens]]

        self.labelData = [[(0, 0, -0.2), ZoneUtil.ToontownCentral],
                     [(0.65, 0, -0.125), ZoneUtil.DonaldsDock],
                     [(0.07, 0, 0.18), ZoneUtil.MinniesMelodyland],
                     [(-0.1, 0, 0.45), ZoneUtil.DonaldsDreamland],
                     [(0.5, 0, 0.25), ZoneUtil.TheBrrrgh],
                     [(-0.37, 0, -0.525), ZoneUtil.DaisyGardens]]

        # The buttons
        self.infoLabel = None
        self.BTPButton = None
        self.MGAButton = None

        self.clouds = []
        self.labels = []

    def enter(self):
        BookPage.enter(self)
        self.show()

    def exit(self):
        BookPage.exit(self)
        self.hide()

    def load(self):
        BookPage.load(self)
        # Let's load up the clouds.
        for pos, scale, hpr in self.cloudPos:
            cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
            cloud.reparentTo(self)
            cloud.setPos(pos)
            cloud.setScale(scale)
            cloud.setHpr(hpr)
            self.clouds.append(cloud)

        for pos, scale, hpr, hood in self.hoodClouds:
            if not base.localAvatar.hasDiscoveredHood(ZoneUtil.getZoneId(hood)):
                cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
                cloud.reparentTo(self)
                cloud.setPos(pos)
                cloud.setScale(scale)
                cloud.setHpr(hpr)
                self.clouds.append(cloud)

        for pos, name in self.labelData:
            if base.localAvatar.hasDiscoveredHood(ZoneUtil.getZoneId(name)):
                text = name
                if base.localAvatar.hasTeleportAccess(ZoneUtil.getZoneId(name)):
                    text = 'Go To\n' + text
                label = DirectButton(
                    parent = self,
                    relief = None,
                    pos = pos,
                    pad = (0.2, 0.16),
                    text = ('', text, text, ''),
                    text_bg = Vec4(1, 1, 1, 0.4),
                    text_scale = 0.055,
                    text_wordwrap = 8,
                    rolloverSound = None,
                    clickSound = None,
                    pressEffect = 0,
                    sortOrder = 1,
                    text_font = CIGlobals.getToonFont())
                if base.localAvatar.hasTeleportAccess(ZoneUtil.getZoneId(name)):
                    label['command'] = self.book.finished
                    label['extraArgs'] = [ZoneUtil.getZoneId(name)]
                label.resetFrameSize()
                self.labels.append(label)

        currHoodName = base.cr.playGame.hood.id
        currLocation = ''
        if base.localAvatar.zoneId == ZoneUtil.MinigameAreaId or base.localAvatar.getMyBattle() is not None:
            currLocation = ''
        elif ZoneUtil.getWhereName(base.localAvatar.zoneId) == 'playground':
            currLocation = 'Playground'
        elif ZoneUtil.getWhereName(base.localAvatar.zoneId) in ['street', 'interior']:
            currLocation = ZoneUtil.BranchZone2StreetName[ZoneUtil.getBranchZone(base.localAvatar.zoneId)]
        self.infoLabel = DirectLabel(relief = None, text = 'You are in: {0}\n{1}'.format(currHoodName, currLocation),
                                     scale = 0.06, pos = (-0.4, 0, -0.74), parent = self, text_align = TextNode.ACenter)

        if currHoodName in [ZoneUtil.MinigameArea, ZoneUtil.BattleTTC]:
            currHoodName = base.cr.playGame.lastHood
        btpText = 'Back to Playground'
        btpEA = [ZoneUtil.getZoneId(currHoodName)]
        self.BTPButton = DirectButton(relief = None, text = btpText, geom = CIGlobals.getDefaultBtnGeom(),
            text_pos = (0, -0.018), geom_scale = (1.3, 1.11, 1.11), text_scale = 0.06, parent = self,
            text_font = CIGlobals.getToonFont(), pos = (0.25, 0, -0.75), command = self.book.finished,
        extraArgs = btpEA, scale = 0.7)
        if base.localAvatar.zoneId != ZoneUtil.MinigameAreaId:
            self.MGAButton = DirectButton(relief = None, text = ZoneUtil.MinigameArea, geom = CIGlobals.getDefaultBtnGeom(),
                text_pos = (0, -0.018), geom_scale = (1, 1.11, 1.11), text_scale = 0.06, parent = self,
                text_font = CIGlobals.getToonFont(), pos = (0.625, 0, -0.75), command = self.book.finished,
            extraArgs = [ZoneUtil.MinigameAreaId], scale = 0.7)

        icons = loader.loadModel('phase_3.5/models/gui/sos_textures.bam')
        self.icon = icons.find('**/teleportIcon')
        icons.detachNode()

    def unload(self):
        BookPage.unload(self)

        # Destroy the GUI elements.
        self.infoLabel.destroy()
        self.BTPButton.destroy()

        if self.MGAButton:
            self.MGAButton.destroy()
        self.destroy()

        # Destroy the labels.
        for label in self.labels:
            label.destroy()

        # Destroy the clouds.
        for cloud in self.clouds:
            cloud.removeNode()
            self.clouds.remove(cloud)

        del self.labels
        del self.clouds
        del self.infoLabel
        del self.BTPButton
        del self.MGAButton
