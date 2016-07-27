########################################
# Filename: DistrictsPage.py
# Created by: DecodedLogic (18Jun16)
########################################

from panda3d.core import Vec4, TextNode

from direct.gui.DirectGui import DirectScrolledList, DirectFrame
from direct.gui.DirectGui import DirectButton, OnscreenText
from direct.gui.DirectGui import DGG

from lib.coginvasion.book_new.BookPage import BookPage

textRolloverColor = Vec4(1, 1, 0, 1)
textDownColor = Vec4(0.5, 0.9, 1, 1)
textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)

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
            btn = DirectButton(
                relief=None, text=shardName, text_scale=0.07,
                text_align=TextNode.ALeft, text1_bg=textDownColor, text2_bg=textRolloverColor,
                text3_fg=textDisabledColor, textMayChange=0, command=self.__handleShardButton,
                extraArgs=[shardId], text_pos = (0, 0, 0.0), parent = self
            )
            if shardId == base.localAvatar.parentId:
                btn['state'] = DGG.DISABLED
            else:
                btn['state'] = DGG.NORMAL
            self.shardButtons.append(btn)

        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        listXorigin = -0.02
        listFrameSizeX = 0.625
        listZorigin = -0.96
        listFrameSizeZ = 1.04
        arrowButtonScale = 1.3
        itemFrameXorigin = -0.237
        itemFrameZorigin = 0.365
        buttonXstart = itemFrameXorigin + 0.293

        self.districtList = DirectScrolledList(
            relief=None,
            pos=(-0.54, 0, 0.08),
            incButton_image=(gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            incButton_relief=None,
            incButton_scale=(arrowButtonScale, arrowButtonScale, -arrowButtonScale),
            incButton_pos=(buttonXstart, 0, itemFrameZorigin - 0.999),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),
            decButton_image=(gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            decButton_relief=None,
            decButton_scale=(arrowButtonScale, arrowButtonScale, arrowButtonScale),
            decButton_pos=(buttonXstart, 0, itemFrameZorigin + 0.125),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),
            itemFrame_pos=(itemFrameXorigin, 0, itemFrameZorigin),
            itemFrame_scale=1.0,
            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(listXorigin,
                listXorigin + listFrameSizeX,
                listZorigin,
                listZorigin + listFrameSizeZ),
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.01, 0.01),
            numItemsVisible=15,
            forceHeight=0.075,
            items=self.shardButtons, parent = self
        )

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
