########################################
# Filename: ShtickerBook.py
# Created by:  blach (20Jun14)
########################################

from lib.coginvasion.globals import CIGlobals
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.fsm.StateData import StateData
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM
from lib.coginvasion.hood import ZoneUtil
from lib.coginvasion.gui.BackpackGUI import BackpackGUI

from OptionPage import OptionPage
from AdminPage import AdminPage
from lib.coginvasion.book.NamePage import NamePage
from lib.coginvasion.quest.QuestPoster import QuestPoster

qt_btn = loader.loadModel("phase_3/models/gui/quit_button.bam")

class ShtickerBook(StateData):

    def __init__(self, parentFSM, doneEvent):
        self.parentFSM = parentFSM
        StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM('ShtickerBook', [State('off', self.enterOff, self.exitOff),
         State('optionPage', self.enterOptionPage, self.exitOptionPage, ['districtPage', 'off']),
         State('districtPage', self.enterDistrictPage, self.exitDistrictPage, ['optionPage', 'questPage', 'off']),
         State('questPage', self.enterQuestPage, self.exitQuestPage, ['inventoryPage', 'districtPage', 'off']),
         State('inventoryPage', self.enterInventoryPage, self.exitInventoryPage, ['mapPage', 'questPage', 'off']),
         State('mapPage', self.enterMapPage, self.exitMapPage, ['inventoryPage', 'off']),
         State('releaseNotesPage', self.enterReleaseNotesPage, self.exitReleaseNotesPage, ['mapPage', 'off']),
         State('adminPage', self.enterAdminPage, self.exitAdminPage, ['mapPage', 'namePage', 'off']),
         State('namePage', self.enterNamePage, self.exitNamePage, ['adminPage', 'off'])],
        'off', 'off')
        if base.localAvatar.getAdminToken() > -1:
            self.fsm.getStateNamed('mapPage').addTransition('adminPage')
        self.fsm.enterInitialState()
        self.entered = 0
        self.parentFSM.getStateNamed('shtickerBook').addChild(self.fsm)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def load(self):
        StateData.load(self)
        self.book_contents = loader.loadModel("phase_3.5/models/gui/stickerbook_gui.bam")
        self.book_texture = self.book_contents.find('**/big_book')
        self.book_open = loader.loadSfx("phase_3.5/audio/sfx/GUI_stickerbook_open.ogg")
        self.book_close = loader.loadSfx("phase_3.5/audio/sfx/GUI_stickerbook_delete.ogg")
        self.book_turn = loader.loadSfx("phase_3.5/audio/sfx/GUI_stickerbook_turn.ogg")

    def unload(self):
        self.book_texture.removeNode()
        del self.book_texture
        self.book_contents.removeNode()
        del self.book_contents
        loader.unloadSfx(self.book_open)
        del self.book_open
        loader.unloadSfx(self.book_close)
        del self.book_close
        loader.unloadSfx(self.book_turn)
        del self.book_turn
        del self.fsm
        del self.parentFSM
        del self.entered
        StateData.unload(self)

    def enter(self, page):
        if self.entered:
            return
        self.entered = 1
        StateData.enter(self)
        render.hide()
        base.setBackgroundColor(0.05, 0.15, 0.4)
        self.book_img = OnscreenImage(image=self.book_texture, scale=(2, 1, 1.5))
        self.book_open.play()
        if base.localAvatar.getAdminToken() > -1:
            self.fsm.request('adminPage')
        else:
            self.fsm.request(page)

    def exit(self):
        if not self.entered:
            return
        self.entered = 0
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        render.show()
        self.book_img.destroy()
        del self.book_img
        self.book_close.play()
        self.fsm.request('off')
        StateData.exit(self)

    def enterDistrictPage(self):
        self.createPageButtons('optionPage', 'questPage')
        self.setTitle("Districts")

        currDistrictName = base.cr.myDistrict.getDistrictName()
        if not currDistrictName.isalpha():
            currDistrictName = currDistrictName[:-1]
        self.infoLbl = OnscreenText(
            text = 'Each District is a copy of the Cog Invasion world.\n'
                '\n\nYou are currently in the "%s" District' % currDistrictName,
            pos = (0.05, 0.3), align = TextNode.ALeft, wordwrap = 12)
        self.populationLbl = OnscreenText(text = "Population: %d" % base.cr.myDistrict.getPopulation(),
            pos = (0.44, -0.3), align = TextNode.ACenter)

        textRolloverColor = Vec4(1, 1, 0, 1)
        textDownColor = Vec4(0.5, 0.9, 1, 1)
        textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)

        self.shardButtons = []
        for shard in base.cr.activeDistricts.values():
            shardName = shard.getDistrictName()
            shardId = shard.doId
            btn = DirectButton(
                relief=None, text=shardName, text_scale=0.07,
                text_align=TextNode.ALeft, text1_bg=textDownColor, text2_bg=textRolloverColor,
                text3_fg=textDisabledColor, textMayChange=0, command=self.__handleShardButton,
                extraArgs=[shardId], text_pos = (0, 0, 0.0)
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
            items=self.shardButtons
        )
        base.taskMgr.add(self.__updateDistrictPopTask, "SB.updateDistrictPopTask")

    def __handleShardButton(self, shardId):
        self.finished("switchShard", shardId)

    def __updateDistrictPopTask(self, task):
        population = base.cr.myDistrict.getPopulation()
        self.populationLbl.setText('Population: %d' % population)
        task.delayTime = 5.0
        return task.again

    def exitDistrictPage(self):
        base.taskMgr.remove('SB.updateDistrictPopTask')
        for btn in self.shardButtons:
            btn.destroy()
        del self.shardButtons
        self.districtList.destroy()
        del self.districtList
        self.infoLbl.destroy()
        del self.infoLbl
        self.populationLbl.destroy()
        del self.populationLbl
        self.deletePageButtons(True, True)
        self.clearTitle()

    def enterNamePage(self):
        self.namePageStateData = NamePage(self, self.fsm)
        self.namePageStateData.load()
        self.namePageStateData.enter()

    def exitNamePage(self):
        self.namePageStateData.exit()
        self.namePageStateData.unload()
        del self.namePageStateData

    def enterQuestPage(self):
        self.createPageButtons('districtPage', 'inventoryPage')
        self.setTitle("Quests")
        
        """
        self.notes = base.localAvatar.questManager.makeQuestNotes()
        for note in self.notes:
            note.show()
        """
        
        self.posters = []
        for quest in base.localAvatar.questManager.getQuests(): 
            poster = QuestPoster(quest)
            poster.update()
            self.posters.append(poster)

        self.infoText = OnscreenText(text = "Return completed Quests to an HQ Officer at any Toon HQ building.",
            pos = (0, -0.6), scale = 0.045)

    def exitQuestPage(self):
        self.infoText.destroy()
        del self.infoText
        for poster in self.posters:
            poster.destroy()
        """
        for note in self.notes:
            note.destroy()
        """
        self.deletePageButtons(True, True)
        self.clearTitle()

    def enterInventoryPage(self):
        self.createPageButtons('questPage', 'mapPage')
        self.setTitle('Gags')
        self.gui = BackpackGUI()
        self.gui.createGUI()

    def exitInventoryPage(self):
        self.gui.deleteGUI()
        del self.gui
        self.deletePageButtons(True, True)
        self.clearTitle()

    def enterMapPage(self):
        if base.localAvatar.getAdminToken() > -1:
            self.createPageButtons('inventoryPage', 'adminPage')
        else:
            self.createPageButtons('inventoryPage', None)
        self.setTitle("")

        themap = loader.loadModel('phase_3.5/models/gui/toontown_map.bam')
        self.frame = DirectFrame(parent=aspect2d, relief=None, image=themap, image_scale=(1.8, 1, 1.35), scale=0.97, pos=(0, 0, 0.0775))
        cloudpos = [[(-0.61, 0, 0.18), (0.55, 0.25, 0.37), (180, 0, 0)],
                    [(-0.54, 0, 0.34), (0.76, 0.4, 0.55), (180, 0, 0)],
                    [(-0.55, 0, -0.09), (0.72, 0.4, 0.55), (0, 0, 0)],
                    [(-0.67, 0, -0.51),  (0.5, 0.29, 0.38), (180, 0, 0)],
                    [(-0.67, 0, 0.51), (0.50, 0.29, 0.38), (0, 0, 0)],
                    [(0.67, 0, 0.51), (0.5, 0.29, 0.38), (0, 0, 0)],
                    [(0.35, 0, -0.46),  (0.63, 0.35, 0.45), (0, 0, 0)],
                    [(0.18, 0, -0.45),  (0.52, 0.27, 0.32), (0, 0, 0)],
                    [(0.67, 0, -0.44),  (0.63, 0.35, 0.48), (180, 0, 0)]]
        hoodclouds = [#[(0.02, 0, -0.17),  (0.63, 0.35, 0.48), (180, 0, 0), CIGlobals.ToontownCentral],
                      [(0.63, 0, -0.13),  (0.63, 0.35, 0.40), (0, 0, 0), CIGlobals.DonaldsDock],
                      [(0.51, 0, 0.25),  (0.57, 0.35, 0.40), (0, 0, 0), CIGlobals.TheBrrrgh],
                      [(0.03, 0, 0.19),  (0.63, 0.35, 0.40), (180, 0, 0), CIGlobals.MinniesMelodyland],
                      [(-0.08, 0, 0.46),  (0.54, 0.35, 0.40), (0, 0, 0), CIGlobals.DonaldsDreamland],
                      [(-0.28, 0, -0.49),  (0.60, 0.35, 0.45), (0, 0, 0), CIGlobals.DaisyGardens]]
        self.clouds = []
        self.labels = []

        for pos, scale, hpr in cloudpos:
            cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
            cloud.reparentTo(self.frame)
            cloud.setPos(pos)
            cloud.setScale(scale)
            cloud.setHpr(hpr)
            self.clouds.append(cloud)

        for pos, scale, hpr, hood in hoodclouds:
            if not base.localAvatar.hasDiscoveredHood(ZoneUtil.getZoneId(hood)):
                cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
                cloud.reparentTo(self.frame)
                cloud.setPos(pos)
                cloud.setScale(scale)
                cloud.setHpr(hpr)
                self.clouds.append(cloud)

        labeldata = [[(0, 0, -0.2), CIGlobals.ToontownCentral],
                     [(0.65, 0, -0.125), CIGlobals.DonaldsDock],
                     [(0.07, 0, 0.18), CIGlobals.MinniesMelodyland],
                     [(-0.1, 0, 0.45), CIGlobals.DonaldsDreamland],
                     [(0.5, 0, 0.25), CIGlobals.TheBrrrgh],
                     [(-0.37, 0, -0.525), CIGlobals.DaisyGardens]]

        for pos, name in labeldata:
            if base.localAvatar.hasDiscoveredHood(ZoneUtil.getZoneId(name)):
                text = name
                if base.localAvatar.hasTeleportAccess(ZoneUtil.getZoneId(name)):
                    text = 'Go To\n' + text
                label = DirectButton(
                    parent=self.frame,
                    relief=None,
                    pos=pos,
                    pad=(0.2, 0.16),
                    text=('', text, text, ''),
                    text_bg=Vec4(1, 1, 1, 0.4),
                    text_scale=0.055,
                    text_wordwrap=8,
                    rolloverSound=None,
                    clickSound=None,
                    pressEffect=0,
                    sortOrder=1,
                    text_font = CIGlobals.getToonFont())
                if base.localAvatar.hasTeleportAccess(ZoneUtil.getZoneId(name)):
                    label['command'] = self.finished
                    label['extraArgs'] = [ZoneUtil.getZoneId(name)]
                label.resetFrameSize()
                self.labels.append(label)

        currHoodName = base.cr.playGame.hood.id
        currLocation = ''
        if base.localAvatar.zoneId == CIGlobals.MinigameAreaId or base.localAvatar.getMyBattle() is not None:
            currLocation = ''
        elif ZoneUtil.getWhereName(base.localAvatar.zoneId) == 'playground':
            currLocation = 'Playground'
        elif ZoneUtil.getWhereName(base.localAvatar.zoneId) in ['street', 'interior']:
            currLocation = CIGlobals.BranchZone2StreetName[ZoneUtil.getBranchZone(base.localAvatar.zoneId)]
        self.infoLabel = DirectLabel(relief = None, text = 'You are in: {0}\n{1}'.format(currHoodName, currLocation),
                                     scale = 0.06, pos = (-0.4, 0, -0.74), parent = self.frame, text_align = TextNode.ACenter)

        if currHoodName in [CIGlobals.MinigameArea, CIGlobals.BattleTTC]:
            currHoodName = base.cr.playGame.lastHood
        btpText = "Back to Playground"
        btpEA = [ZoneUtil.getZoneId(currHoodName)]
        self.BTPButton = DirectButton(relief = None, text = btpText, geom = CIGlobals.getDefaultBtnGeom(),
                                      text_pos = (0, -0.018), geom_scale = (1.3, 1.11, 1.11), text_scale = 0.06, parent = self.frame,
                                      text_font = CIGlobals.getToonFont(), pos = (0.25, 0, -0.75), command = self.finished,
                                      extraArgs = btpEA, scale = 0.7)
        if base.localAvatar.zoneId != CIGlobals.MinigameAreaId:
            self.MGAButton = DirectButton(relief = None, text = "Minigame Area", geom = CIGlobals.getDefaultBtnGeom(),
                                          text_pos = (0, -0.018), geom_scale = (1, 1.11, 1.11), text_scale = 0.06, parent = self.frame,
                                          text_font = CIGlobals.getToonFont(), pos = (0.625, 0, -0.75), command = self.finished,
                                          extraArgs = [CIGlobals.MinigameAreaId], scale = 0.7)

    def exitMapPage(self):
        for label in self.labels:
            label.destroy()
        del self.labels
        for cloud in self.clouds:
            cloud.removeNode()
        del self.clouds
        self.frame.destroy()
        del self.frame
        self.infoLabel.destroy()
        del self.infoLabel
        self.BTPButton.destroy()
        del self.BTPButton
        if hasattr(self, 'MGAButton'):
            self.MGAButton.destroy()
            del self.MGAButton
        if base.localAvatar.getAdminToken() > -1:
            self.deletePageButtons(True, True)
        else:
            self.deletePageButtons(True, False)
        self.clearTitle()

    def enterZonePage(self):
        self.createPageButtons('inventoryPage', 'releaseNotesPage')
        self.setTitle("Places")
        #self.home_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
        #									qt_btn.find('**/QuitBtn_DN'),
        #									qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.055, text=CIGlobals.Estate, command=self.setHood, extraArgs=[10], pos=(-0.45, 0.55, 0.55))
        self.ttc_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
                                            qt_btn.find('**/QuitBtn_DN'),
                                            qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.045, text=CIGlobals.ToontownCentral, command=self.finished, extraArgs=[CIGlobals.ToontownCentralId], pos=(-0.45, 0.15, 0.5), text_pos = (0, -0.01))
        self.tbr_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
                                            qt_btn.find('**/QuitBtn_DN'),
                                            qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.055, text=CIGlobals.TheBrrrgh, command=self.finished, extraArgs=[CIGlobals.TheBrrrghId], pos=(-0.45, 0.15, 0.38), text_pos = (0, -0.01))
        self.ddl_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
                                            qt_btn.find('**/QuitBtn_DN'),
                                            qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.044, text=CIGlobals.DonaldsDreamland, command=self.finished, extraArgs=[CIGlobals.DonaldsDreamlandId], pos=(-0.45, 0.15, 0.26), text_pos = (0, -0.01))
        self.mml_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
        									qt_btn.find('**/QuitBtn_DN'),
        									qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.0425, text=CIGlobals.MinniesMelodyland, command=self.finished, extraArgs=[CIGlobals.MinniesMelodylandId], pos=(-0.45, 0.35, 0.14), text_pos = (0, -0.01))
        self.dg_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
        									qt_btn.find('**/QuitBtn_DN'),
        									qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.045, text=CIGlobals.DaisyGardens, command=self.finished, extraArgs=[CIGlobals.DaisyGardensId], pos=(-0.45, 0.35, 0.02), text_pos = (0, -0.01))
        self.dd_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
        									qt_btn.find('**/QuitBtn_DN'),
        									qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.045, text=CIGlobals.DonaldsDock, command=self.finished, extraArgs=[CIGlobals.DonaldsDockId], pos=(-0.45, 0.35, -0.1), text_pos = (0, -0.01))
        self.minigame_btn = DirectButton(geom=(qt_btn.find('**/QuitBtn_UP'),
                                            qt_btn.find('**/QuitBtn_DN'),
                                            qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.055, text=CIGlobals.MinigameArea, command=self.finished, extraArgs=[CIGlobals.MinigameAreaId], pos=(-0.45, 0.35, -0.34), text_pos = (0, -0.01))
        #self.populationLbl = OnscreenText(text = "", pos = (0.45, 0.1), align = TextNode.ACenter)
        #self.popRecordLbl = OnscreenText(text = "", pos = (0.45, -0.1), align = TextNode.ACenter, scale = 0.05)
        #taskMgr.add(self.__updateGamePopulation, "ShtickerBook-updateGamePopulation")

    def __updateGamePopulation(self, task):
        population = 0
        for district in base.cr.activeDistricts.values():
            population += district.getPopulation()
        self.populationLbl.setText("Game Population:\n" + str(population))
        recordPopulation = base.cr.myDistrict.getPopRecord()
        self.popRecordLbl.setText("Record Population:\n" + str(recordPopulation))
        task.delayTime = 5.0
        return task.again

    def exitZonePage(self):
        #taskMgr.remove("ShtickerBook-updateGamePopulation")
        #self.popRecordLbl.destroy()
        #del self.popRecordLbl
        #self.populationLbl.destroy()
        #del self.populationLbl
        self.dd_btn.destroy()
        del self.dd_btn
        self.ddl_btn.destroy()
        del self.ddl_btn
        self.ttc_btn.destroy()
        del self.ttc_btn
        self.tbr_btn.destroy()
        del self.tbr_btn
        self.minigame_btn.destroy()
        del self.minigame_btn
        self.mml_btn.destroy()
        del self.mml_btn
        self.dg_btn.destroy()
        del self.dg_btn
        self.deletePageButtons(True, True)
        self.clearTitle()

    def createPageButtons(self, back, fwd):
        if back:
            self.btn_prev = DirectButton(geom=(self.book_contents.find('**/arrow_button'),
                                        self.book_contents.find('**/arrow_down'),
                                        self.book_contents.find('**/arrow_rollover')), relief=None, pos=(-0.838, 0, -0.661), scale=(-0.1, 0.1, 0.1), command=self.pageDone, extraArgs = [back])
            self.acceptOnce('arrow_left-up', self.pageDone, [back])
        if fwd:
            self.btn_next = DirectButton(geom=(self.book_contents.find('**/arrow_button'),
                                        self.book_contents.find('**/arrow_down'),
                                        self.book_contents.find('**/arrow_rollover')), relief=None, pos=(0.838, 0, -0.661), scale=(0.1, 0.1, 0.1), command=self.pageDone, extraArgs = [fwd])
            self.acceptOnce('arrow_right-up', self.pageDone, [fwd])

    def deletePageButtons(self, back, fwd):
        if back:
            self.ignore('arrow_left-up')
            self.btn_prev.destroy()
            del self.btn_prev
        if fwd:
            self.ignore('arrow_right-up')
            self.btn_next.destroy()
            del self.btn_next

    def setTitle(self, title):
        self.page_title = OnscreenText(text=title, pos=(0, 0.62, 0), scale=0.12)

    def clearTitle(self):
        self.page_title.destroy()
        del self.page_title

    def enterReleaseNotesPage(self):
        if base.localAvatar.getAdminToken() > -1:
            self.createPageButtons('mapPage', 'adminPage')
        else:
            self.createPageButtons('mapPage', None)
        self.setTitle("Release Notes")
        self.frame = DirectScrolledFrame(canvasSize = (-1, 1, -3.5, 1), frameSize = (-1, 1, -0.6, 0.6))
        self.frame.setPos(0, 0, 0)
        self.frame.setScale(0.8)
        self.release_notes = DirectLabel(text=open("release_notes.txt", "r").read(), text_align = TextNode.ALeft, pos=(-0.955, 0, 0.93), relief=None,
            text_fg=(0,0,0,1), text_wordwrap=37.0, text_scale=0.05, parent = self.frame.getCanvas())

    def exitReleaseNotesPage(self):
        self.frame.destroy()
        del self.frame
        self.release_notes.destroy()
        del self.release_notes
        self.clearTitle()
        if base.localAvatar.getAdminToken() > -1:
            self.deletePageButtons(True, True)
        else:
            self.deletePageButtons(True, False)

    def enterAdminPage(self):
        self.adminPageStateData = AdminPage(self, self.fsm)
        self.adminPageStateData.load()
        self.adminPageStateData.enter()

    def exitAdminPage(self):
        self.adminPageStateData.exit()
        self.adminPageStateData.unload()
        del self.adminPageStateData

    def pageDone(self, nextPage):
        base.cr.playGame.getPlace().lastBookPage = nextPage
        if hasattr(self, 'fsm'):
            self.fsm.request(nextPage)
        self.book_turn.play()

    def enterOptionPage(self):
        self.optionPageStateData = OptionPage(self, self.fsm)
        #self.acceptOnce(self.optionPageStateData.doneEvent, self.pageDone)
        self.optionPageStateData.load()
        self.optionPageStateData.enter()

    def exitOptionPage(self):
        #self.ignore(self.optionPageStateData.doneEvent)
        self.optionPageStateData.exit()
        self.optionPageStateData.unload()
        del self.optionPageStateData

    def prevPage(self, currentPage):
        self.clearCurrentPage()
        if self.currentPage == 2:
            self.optionPage()
        elif self.currentPage == 3:
            self.zonePage()
        elif self.currentPage == 4:
            self.releaseNotesPage()

    def nextPage(self, currentPage):
        self.clearCurrentPage()
        if self.currentPage == 1:
            self.zonePage()
        elif self.currentPage == 2:
            self.releaseNotesPage()
        elif self.currentPage == 3:
            self.adminPage()

    def clearCurrentPage(self):
        self.book_turn.play()
        for m in base.bookpgnode.getChildren():
            m.removeNode()

    def finished(self, zone, shardId = None):
        if base.localAvatar.getHealth() < 1 and type(zone) == type(1):
            return
        doneStatus = {}
        if zone in [CIGlobals.ToontownCentralId, CIGlobals.MinigameAreaId,
        CIGlobals.TheBrrrghId, CIGlobals.DonaldsDreamlandId, CIGlobals.MinniesMelodylandId,
        CIGlobals.DaisyGardensId, CIGlobals.DonaldsDockId]:
            doneStatus["mode"] = 'teleport'
            doneStatus["zoneId"] = zone
            doneStatus["hoodId"] = ZoneUtil.getHoodId(zone)
            doneStatus["where"] = ZoneUtil.getWhereName(zone)
            doneStatus["how"] = 'teleportIn'
            doneStatus["avId"] = base.localAvatar.doId
            doneStatus["shardId"] = None
            doneStatus["loader"] = ZoneUtil.getLoaderName(zone)
        else:
            doneStatus["mode"] = zone
            if zone == "switchShard":
                doneStatus["shardId"] = shardId
        self.doneStatus = doneStatus
        messenger.send(self.doneEvent)

    def closeBook(self):
        self.book_close.play()
        base.bookpgnode.removeNode()
        base.booknode.removeNode()
