"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistrictsPage.py
@author Maverick Liberty
@date June 18, 2016

"""

from panda3d.core import Vec4, TextNode

from direct.gui.DirectGui import DirectScrolledList, DirectFrame
from direct.gui.DirectGui import DirectButton, OnscreenText
from direct.gui.DirectGui import DGG

from src.coginvasion.globals import CIGlobals
from src.coginvasion.book.BookPage import BookPage

class DistrictsPage(BookPage, DirectFrame):

    def __init__(self, book):
        BookPage.__init__(self, book, 'Districts')
        DirectFrame.__init__(self, parent = book)
        self.initialiseoptions(DistrictsPage)

        # GUI elements
        self.infoLbl = None
        self.populationLbl = None
        self.shardButtons = []
        self.districtList = None

        self.hide()

    def __updateDistrictPopTask(self, task):
        population = base.cr.myDistrict.getPopulation()
        self.populationLbl.setText('Population: %d' % population)
        task.delayTime = 5.0
        return task.again

    def enter(self):
        BookPage.enter(self)
        self.show()
        base.taskMgr.add(self.__updateDistrictPopTask, 'SB.updateDistrictPopTask')

    def __handleShardButton(self, shardId):
        self.book.finished('switchShard', shardId)

    def exit(self):
        BookPage.exit(self)
        base.taskMgr.remove('SB.updateDistrictPopTask')
        self.hide()

    def load(self):
        BookPage.load(self)
        icons = loader.loadModel('phase_3.5/models/gui/sos_textures.bam')
        self.icon = icons.find('**/district')
        icons.detachNode()

        currDistrictName = base.cr.myDistrict.getDistrictName()
        if not currDistrictName.isalpha():
            currDistrictName = currDistrictName[:-1]
        self.infoLbl = OnscreenText(
            text = 'Each District is a copy of the Cog Invasion world.\n'
                '\n\nYou are currently in the "%s" District' % currDistrictName,
            pos = (0.05, 0.3), parent = self, align = TextNode.ALeft, wordwrap = 12)
        self.populationLbl = OnscreenText(text = "Population: %d" % base.cr.myDistrict.getPopulation(),
            pos = (0.44, -0.3), parent = self, align = TextNode.ACenter)

        self.shardButtons = []
        for shard in base.cr.activeDistricts.values():
            shardName = shard.getDistrictName()
            shardId = shard.doId
            btn = CIGlobals.makeDefaultScrolledListBtn(text = shardName, parent = self, command = self.__handleShardButton, extraArgs = [shardId])
            if shardId == base.localAvatar.parentId:
                btn['state'] = DGG.DISABLED
            else:
                btn['state'] = DGG.NORMAL
            self.shardButtons.append(btn)

        self.districtList = CIGlobals.makeDefaultScrolledList(items = self.shardButtons, parent = self, pos = (-0.54, 0, 0.08))

    def unload(self):
        BookPage.unload(self)

        # Delete GUI elements.
        for btn in self.shardButtons:
            btn.destroy()
            self.shardButtons.remove(btn)

        self.districtList.destroy()
        self.infoLbl.destroy()
        self.populationLbl.destroy()
        self.destroy()

        del self.shardButtons
        del self.districtList
        del self.infoLbl
        del self.populationLbl
        del textDisabledColor
        del textDownColor
        del textRolloverColor
