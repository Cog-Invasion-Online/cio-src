########################################
# Filename: MakeAToon.py
# Created by:  blach (??July14)
########################################

from pandac.PandaModules import Vec4, TextNode

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry
from direct.gui.DirectGui import OnscreenImage, DirectLabel, DGG
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals
from src.coginvasion.makeatoon.ToonGenerator import ToonGenerator
from src.coginvasion.gui import Dialog

it = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf")

nextShops = {"gender": "body",
            "body": "color",
            "color": "cloth",
            "cloth": "name"}
prevShops = {"body": "gender",
            "color": "body",
            "cloth": "color",
            "name": "cloth"}

class MakeAToon:
    MSG_BADNAME = 'Sorry, that name will not work.'
    MSG_NAMEPENDING = 'Great! Until your name is accepted by Toon Council, your name will be %s.'

    def __init__(self):
        self.toonMade = 0
        self.slot = -1
        self.currentShop = None
        self.currentHead = 0
        self.currentTorso = 0
        self.currentLeg = 0
        self.currentShirt = 0
        self.currentShorts = 0
        self.shirt1Path = "phase_3/maps/desat_shirt_1.jpg"
        self.shirt2Path = "phase_3/maps/desat_shirt_2.jpg"
        self.sleeve1Path = "phase_3/maps/desat_sleeve_1.jpg"
        self.sleeve2Path = "phase_3/maps/desat_sleeve_2.jpg"
        self.skirt1Path = "phase_3/maps/desat_skirt_1.jpg"
        self.short1Path = "phase_3/maps/desat_shorts_1.jpg"
        self.short2Path = "phase_3/maps/desat_shorts_2.jpg"
        self.currentShirtTex = self.shirt1Path
        self.currentSleeveTex = self.sleeve1Path
        self.currentShortTex = self.short1Path
        self.toonName = None
        self.matFSM = ClassicFSM('MakeAToon',
                        [State('off',
                        self.enterOff,
                        self.exitOff),

                        State('genderShop',
                        self.enterGenderShop,
                        self.exitGenderShop,
                        ['exit',
                        'off',
                        'bodyShop']),

                        State('bodyShop',
                        self.enterBodyShop,
                        self.exitBodyShop,
                        ['exit',
                        'off',
                        'genderShop',
                        'colorShop']),

                        State('colorShop',
                        self.enterColorShop,
                        self.exitColorShop,
                        ['exit',
                        'off',
                        'bodyShop',
                        'clothShop']),

                        State('clothShop',
                        self.enterClothShop,
                        self.exitClothShop,
                        ['exit',
                        'off',
                        'colorShop',
                        'nameShop']),

                        State('nameShop',
                        self.enterNameShop,
                        self.exitNameShop,
                        ['exit',
                        'off',
                        'clothShop',
                        'done']),

                        State('exit',
                        self.enterExit,
                        self.exitExit)],

                        'off',
                        'off')
        self.matFSM.enterInitialState()
        return

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def loadEnviron(self):
        base.camLens.setFov(CIGlobals.OriginalCameraFov)
        camera.setPos(-4.77, -17.47, 3.30)
        camera.setH(344.05)
        self.mat_gui = loader.loadModel("phase_3/models/gui/tt_m_gui_mat_mainGui.bam")
        self.cat_gui = loader.loadModel("phase_3/models/gui/create_a_toon_gui.bam")
        self.nameGui = loader.loadModel("phase_3/models/gui/nameshop_gui.bam")
        self.namePanel = self.nameGui.find('**/typeNamePanel')
        self.namePanel.reparentTo(hidden)
        self.namePanel.setScale(0.6)
        self.room = loader.loadModel("phase_3/models/makeatoon/tt_m_ara_mat_room.bam")
        self.floor = self.room.find('**/floor')
        self.floor.reparentTo(render)
        self.bg = self.room.find('**/background')
        self.bg.reparentTo(render)
        self.bg.setY(1.625)
        self.genderRoom = self.room.find('**/genderAll')
        self.genderRoom.reparentTo(hidden)
        self.bodyRoom = self.room.find('**/bodyAll')
        self.bodyRoom.reparentTo(hidden)
        self.colorRoom = self.room.find('**/colorAll')
        self.colorRoom.reparentTo(hidden)
        self.clothRoom = self.room.find('**/cothAll')
        self.clothRoom.reparentTo(hidden)
        self.nameRoom = self.room.find('**/nameAll')
        self.nameRoom.reparentTo(hidden)
        self.desatShirt1 = loader.loadTexture(self.shirt1Path)
        self.desatShirt2 = loader.loadTexture(self.shirt2Path)
        self.desatSleeve1 = loader.loadTexture(self.sleeve1Path)
        self.desatSleeve2 = loader.loadTexture(self.sleeve2Path)
        self.desatSkirt1 = loader.loadTexture(self.skirt1Path)
        self.desatShorts1 = loader.loadTexture(self.short1Path)
        self.desatShorts2 = loader.loadTexture(self.short2Path)
        self.spotlight = loader.loadModel("phase_3/models/gui/tt_m_gui_mat_spotlight.bam")
        self.spotlight.setR(90)
        self.spotlight.setScale(0.6, 0.8, 0.8)
        self.spotlight.setColor(1,1,1,0.3)
        self.spotlight_img = OnscreenImage(image=self.spotlight)
        #self.light = render.attachNewNode(Spotlight('light'))
        #self.light.node().setColor(Vec4(1, 1, 1, 1))
        #light.node().setAttenuation(Point3(1, 1, 1))
        #self.light.node().setShadowCaster(True, 2000, 2000)
        #self.light.setPos(0, -27.11, 20)
        #self.light.node().getLens().setFov(54)
        #self.light.node().getLens().setNearFar(40,300)
        #self.light.lookAt(0, 0, 3)
        #self.light.node().setExponent( 0.0 )
        #render.setLight(self.light)
        #self.light.node().showFrustum()
        #self.amb = render.attachNewNode(AmbientLight('amblight'))
        #self.amb.node().setColor(Vec4(0.5, 0.5, 0.5, 1))
        #render.setLight(self.amb)
        #render.setAttrib(LightRampAttrib.makeDefault())
        #render.setShaderAuto()
        #render.flattenStrong()
        #render.setTwoSided(True)
        self.toonGen = ToonGenerator(self)
        #self.toonGen.toon.flattenStrong()
        self.music = base.loadMusic("phase_3/audio/bgm/create_a_toon.mid")
        base.playMusic(self.music, volume=0.5, looping=1)
        #base.enableMouse()
        #base.oobe()
        #self.light.place()

    def setSlot(self, slot):
        self.slot = slot

    def getSlot(self):
        return self.slot

    def __handleNextShop(self):
        self.okBtn.hide()
        self.nextBtn.hide()
        self.exitBtn.hide()
        self.backBtn.hide()
        self.nextBtn.hide()
        self.setNextShop(nextShops[self.currentShop])

    def __handlePrevShop(self):
        self.okBtn.hide()
        self.nextBtn.hide()
        self.exitBtn.hide()
        self.backBtn.hide()
        self.nextBtn.hide()
        self.setPrevShop(prevShops[self.currentShop])

    def __handleExit(self, direction):
        self.okBtn.hide()
        self.nextBtn.hide()
        self.exitBtn.hide()
        self.backBtn.hide()
        self.nextBtn.hide()
        base.transitions.fadeOut(0.5)
        Sequence(Wait(0.51), Func(self.exitMakeAToon, direction)).start()

    def exitMakeAToon(self, direction):
        self.matFSM.request("exit", enterArgList = [direction])

    def finishedMakeAToon(self, textEntered = None):
        self.toonName = self.nameEntry.get()
        if self.toonName.isspace() or len(self.toonName) == 0:
            self.badNameDialog = Dialog.GlobalDialog(message = self.MSG_BADNAME,
                doneEvent = 'badNameAck', style = Dialog.Ok)
            base.acceptOnce('badNameAck', self.__handleBadNameAck)
            self.badNameDialog.show()
            return
        else:
            dialogMsg = self.MSG_NAMEPENDING
            toon = self.toonGen.toon
            headColor = toon.getHeadColor()
            requestedName = self.toonName

            # We need to get the name of the head color.
            #for colorName, color in toon.colorName2DNAcolor.iteritems():
            #    if headColor == color:
            #        colorName = colorName.title()
            #        self.toonName = "%s %s" % (colorName, toon.getAnimal().title())
            #        dialogMsg = dialogMsg % self.toonName
            #        break

            #self.nameInfoDialog = Dialog.GlobalDialog(message = dialogMsg,
            #    doneEvent = 'nameInfoAck', style = Dialog.Ok)
            #base.acceptOnce('nameInfoAck', self.__handleNameInfoAck, [requestedName])
            #base.cr.requestedName = requestedName
            #self.nameInfoDialog.show()
            self.__handleExit('finished')

    def __handleNameInfoAck(self, requestedName):
        self.__handleExit('finished')
        self.nameInfoDialog.cleanup()
        del self.nameInfoDialog

    def __handleBadNameAck(self):
        self.badNameDialog.cleanup()
        del self.badNameDialog

    def isAvailable(self):
        return True

    def setNextShop(self, shop):
        if shop == "body":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'bodyShop')).start()
        elif shop == "color":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'colorShop')).start()
        elif shop == "cloth":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'clothShop')).start()
        elif shop == "name":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'nameShop')).start()
        self.fade()

    def setPrevShop(self, shop):
        if shop == "gender":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'genderShop')).start()
        elif shop == "body":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'bodyShop')).start()
        elif shop == "color":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'colorShop')).start()
        elif shop == "cloth":
            Sequence(Wait(0.21), Func(self.matFSM.request, 'clothShop')).start()
        self.fade()


    def exitColorShop(self):
        self.nextAllColorBtn.destroy()
        self.prevAllColorBtn.destroy()
        self.nextHeadColorBtn.destroy()
        self.prevHeadColorBtn.destroy()
        self.nextTorsoColorBtn.destroy()
        self.prevTorsoColorBtn.destroy()
        self.nextLegColorBtn.destroy()
        self.prevLegColorBtn.destroy()
        self.colorRoom.reparentTo(hidden)
        del self.nextAllColorBtn
        del self.prevAllColorBtn
        del self.nextHeadColorBtn
        del self.prevHeadColorBtn
        del self.nextTorsoColorBtn
        del self.prevTorsoColorBtn
        del self.nextLegColorBtn
        del self.prevLegColorBtn

    def load(self):
        self.exitBtn = DirectButton(text=("", "Exit", "Exit", ""),
                                text_scale=0.08,
                                text_shadow=(0,0,0,1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.115),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_closeUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_closeDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_closeUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_closeUp')),
                                geom3_color=(0.6, 0.6, 0.6, 0.6),
                                relief=None,
                                pos=(0.2, 0.2, 0.2),
                                geom0_scale=0.6,
                                geom1_scale=0.65,
                                geom2_scale=0.65,
                                geom3_scale=0.6,
                                command=self.__handleExit,
                                extraArgs=["quit"],
                                parent=base.a2dBottomLeft)
        self.exitBtn.setBin('gui-popup', 60)
        self.okBtn = DirectButton(text=("", "Ready", "Ready", ""),
                                text_scale=0.08,
                                text_shadow=(0,0,0,1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.115),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_okUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_okDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_okUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_okUp')),
                                geom3_color=(0.6, 0.6, 0.6, 0.6),
                                relief=None,
                                pos=(-0.2, 0.2, 0.2),
                                geom0_scale=0.6,
                                geom1_scale=0.65,
                                geom2_scale=0.65,
                                geom3_scale=0.6,
                                command=self.finishedMakeAToon,
                                parent=base.a2dBottomRight)
        self.okBtn.hide()
        self.okBtn.setBin('gui-popup', 60)
        self.nextBtn = DirectButton(text=("", "Next", "Next", ""),
                                text_scale=0.08,
                                text_shadow=(0,0,0,1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.115),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_nextUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextDisabled')),
                                relief=None,
                                pos=(-0.2, 0.2, 0.2),
                                geom0_scale=0.3,
                                geom1_scale=0.35,
                                geom2_scale=0.35,
                                geom3_scale=0.3,
                                command=self.__handleNextShop,
                                parent=base.a2dBottomRight)
        self.nextBtn.setBin('gui-popup', 60)
        self.backBtn = DirectButton(text=("", "Back", "Back", ""),
                                text_scale=0.08,
                                text_shadow=(0,0,0,1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.115),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_nextUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_nextDisabled')),
                                relief=None,
                                pos=(-0.4, 0.2, 0.2),
                                geom3_color=Vec4(0.5, 0.5, 0.5, 0.75),
                                geom0_scale=(-0.3, 0.3, 0.3),
                                geom1_scale=(-0.35, 0.35, 0.35),
                                geom2_scale=(-0.35, 0.35, 0.35),
                                geom3_scale=(-0.3, 0.3, 0.3),
                                command=self.__handlePrevShop,
                                parent=base.a2dBottomRight)
        self.backBtn.setBin('gui-popup', 60)

    def enterNameShop(self):
        self.okBtn.show()
        self.backBtn.show()
        self.exitBtn.show()
        base.transitions.fadeIn(0)
        self.currentShop = "name"
        self.nameRoom.reparentTo(render)
        self.setTitle("Choose Your Name", "yellow")
        self.spotlight_img.setX(0.55)
        self.spotlight_img.setZ(-0.08)
        self.namePanelFrame = DirectFrame(pos = (-0.4, 0, 0))
        self.namePanel.reparentTo(self.namePanelFrame)
        self.nameEntry = DirectEntry(parent = self.namePanelFrame, pos = (0.013, 0, 0.26),
                    width = 10, numLines = 2, scale = 0.05, text_align = TextNode.ACenter,
                    relief = None, focus = 1, command = self.finishedMakeAToon)
        self.toonGen.setToonPosForNameShop()

    def exitNameShop(self):
        self.nameRoom.reparentTo(hidden)
        self.namePanel.setX(0)
        self.namePanel.reparentTo(hidden)
        #self.spotlight_img.setX(0)
        #self.spotlight_img.setZ(0)
        self.nameEntry.destroy()
        del self.nameEntry
        self.toonGen.setToonPosForGeneralShop()
        if hasattr(self, 'badNameDialog'):
            self.badNameDialog.cleanup()
            del self.badNameDialog

    def enterGenderShop(self):
        self.nextBtn.show()
        self.exitBtn.show()
        self.backBtn.show()
        base.transitions.fadeIn(0)
        self.currentShop = "gender"

        self.genderRoom.reparentTo(render)

        self.setTitle("Choose Boy Or Girl", "yellow")

        self.boyBtn = DirectButton(text=("", "Boy", "Boy", ""),
                                text_scale=0.08,
                                text_shadow=(0, 0, 0, 1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.19),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_boyUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_boyDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_boyUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_boyDown')),
                                relief=None,
                                pos=(-0.45, -0.8, -0.8),
                                geom0_scale=0.6,
                                geom1_scale=0.7,
                                geom2_scale=0.7,
                                geom3_scale=0.6,
                                command=self.generateToon,
                                extraArgs=["boy"])
        self.girlBtn = DirectButton(text=("", "Girl", "Girl", ""),
                                text_scale=0.08,
                                text_shadow=(0, 0, 0, 1),
                                text_fg=(1,1,1,1),
                                text_pos=(0, 0.19),
                                geom=(self.mat_gui.find('**/tt_t_gui_mat_girlUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_girlDown'),
                                    self.mat_gui.find('**/tt_t_gui_mat_girlUp'),
                                    self.mat_gui.find('**/tt_t_gui_mat_girlDown')),
                                relief=None,
                                pos=(0.45, -0.8, -0.8),
                                geom0_scale=0.6,
                                geom1_scale=0.7,
                                geom2_scale=0.7,
                                geom3_scale=0.6,
                                command=self.generateToon,
                                extraArgs=["girl"])
        if not self.toonMade:
            self.nextBtn['state'] = DGG.DISABLED
        self.backBtn['state'] = DGG.DISABLED

    def exitGenderShop(self):
        self.boyBtn.destroy()
        self.girlBtn.destroy()
        self.genderRoom.reparentTo(hidden)
        del self.boyBtn
        del self.girlBtn

    def enterBodyShop(self):
        self.nextBtn.show()
        self.exitBtn.show()
        self.backBtn.show()
        base.transitions.fadeIn(0)
        self.currentShop = "body"

        self.bodyRoom.reparentTo(render)

        self.setTitle("Choose Your Type", "sea-green")

        self.nextHeadBtn = DirectButton(text="Head",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, 0.1, 0.1),
                                    command=self.nextHead)
        self.prevHeadBtn = DirectButton(text="Head",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, 0.1, 0.1),
                                    command=self.prevHead)
        self.nextTorsoBtn = DirectButton(text="Body",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.2, -0.2),
                                    command=self.nextTorso)
        self.prevTorsoBtn = DirectButton(text="Body",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.2, -0.2),
                                    command=self.prevTorso)
        self.nextLegBtn = DirectButton(text="Legs",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.5, -0.5),
                                    command=self.nextLeg)
        self.prevLegBtn = DirectButton(text="Legs",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.5, -0.5),
                                    command=self.prevLeg)

        self.currentHead = self.toonGen.toon.head
        self.currentTorso = self.toonGen.toon.torso
        self.currentLeg = self.toonGen.toon.legs

        self.updateBodyShopButtons()

    def updateBodyShopButtons(self):
        if self.currentHead == '2' and self.toonGen.toon.animal == 'cat':
            self.prevHeadBtn['state'] = DGG.NORMAL
        elif self.currentHead == '4' and self.toonGen.toon.animal == 'duck':
            self.nextHeadBtn['state'] = DGG.DISABLED
        elif self.currentHead == '1' and self.toonGen.toon.animal == 'cat':
            self.prevHeadBtn['state'] = DGG.DISABLED
        elif self.currentHead == '3' and self.toonGen.toon.animal == 'duck':
            self.nextHeadBtn['state'] = DGG.NORMAL

        if (self.currentTorso == 'dgm_shorts' and self.toonGen.toon.gender == 'boy'
            or self.currentTorso == 'dgm_skirt' and self.toonGen.toon.gender == 'girl'):
            self.prevTorsoBtn['state'] = DGG.NORMAL
        elif (self.currentTorso == 'dgl_shorts' and self.toonGen.toon.gender == 'boy'
            or self.currentTorso == 'dgl_skirt' and self.toonGen.toon.gender == 'girl'):
            self.nextTorsoBtn['state'] = DGG.DISABLED
        elif (self.currentTorso == 'dgs_shorts' and self.toonGen.toon.gender == 'boy'
            or self.currentTorso == 'dgs_skirt' and self.toonGen.toon.gender == 'girl'):
            self.prevTorsoBtn['state'] = DGG.DISABLED
        elif (self.currentTorso == 'dgm_shorts' and self.toonGen.toon.gender == 'boy'
            or self.currentTorso == 'dgm_skirt' and self.toonGen.toon.gender == 'girl'):
            self.nextTorsoBtn['state'] = DGG.NORMAL

        if self.currentLeg == 'dgm':
            self.prevLegBtn['state'] = DGG.NORMAL
        elif self.currentLeg == 'dgl':
            self.nextLegBtn['state'] = DGG.DISABLED
        elif self.currentLeg == 'dgs':
            self.prevLegBtn['state'] = DGG.DISABLED
        elif self.currentLeg == 'dgm':
            self.nextLegBtn['state'] = DGG.NORMAL

        self.backBtn['state'] = DGG.NORMAL

    def nextHead(self):
        head = self.toonGen.getNextHead()
        print head
        newAnimal = None
        # NOTE: head = what the head of the next animal would be.
        # NOTE: self.toonGen.toon.animal = what the current animal is.
        if (self.toonGen.toon.animal == "dog" and head == '00' or
            self.toonGen.toon.animal == "cat" and head == '04' or
            self.toonGen.toon.animal != "dog" and head == '00'):
            newAnimal = self.toonGen.getNextAnimal()
            if newAnimal == '00':
                # When we click next, the animal dna doesn't go down!
                self.nextHeadBtn['state'] = DGG.DISABLED
                return
        self.prevHeadBtn['state'] = DGG.NORMAL
        self.toonGen.toon.head = self.toonGen.toon.headDNA2head[head]
        if newAnimal != None:
            self.toonGen.toon.animal = self.toonGen.toon.animalDNA2animal[newAnimal]
        self.toonGen.generateDNAStrandWithCurrentStyle()

    def prevHead(self):
        head = self.toonGen.getPrevHead()
        newAnimal = None
        # NOTE: head = what the head of the next animal would be.
        # NOTE: self.toonGen.toon.animal = what the current animal is.
        if (self.toonGen.toon.animal == "duck" and head == '01' or
            self.toonGen.toon.animal == "bear" and head == '07' or
            self.toonGen.toon.animal == "dog" and head == '03' or
            self.toonGen.toon.animal != "dog" and head == '03'):
            newAnimal = self.toonGen.getPrevAnimal()
            if newAnimal == '08':
                # When we click next, the animal dna doesn't go down!
                self.prevHeadBtn['state'] = DGG.DISABLED
                return
        self.nextHeadBtn['state'] = DGG.NORMAL
        self.toonGen.toon.head = self.toonGen.toon.headDNA2head[head]
        if newAnimal != None:
            self.toonGen.toon.animal = self.toonGen.toon.animalDNA2animal[newAnimal]
        self.toonGen.generateDNAStrandWithCurrentStyle()

    def nextTorso(self):
        newTorso = self.toonGen.getNextTorso()
        self.toonGen.toon.torso = self.toonGen.toon.torsoDNA2torso[newTorso]
        self.toonGen.generateDNAStrandWithCurrentStyle()
        self.updateTorsoButtons(1)

    def updateTorsoButtons(self, direction):
        gender = self.toonGen.toon.getGender()
        if direction == 1:
            nextNewTorso = self.toonGen.getNextTorso()
            if (nextNewTorso == '00' and gender == 'boy' or
                nextNewTorso == '03' and gender == 'girl'):
                self.nextTorsoBtn['state'] = DGG.DISABLED
            self.prevTorsoBtn['state'] = DGG.NORMAL
        elif direction == 0:
            nextNewTorso = self.toonGen.getPrevTorso()
            if (nextNewTorso == '02' and gender == 'boy' or
                nextNewTorso == '05' and gender == 'girl'):
                self.prevTorsoBtn['state'] = DGG.DISABLED
            self.nextTorsoBtn['state'] = DGG.NORMAL

    def prevTorso(self):
        newTorso = self.toonGen.getPrevTorso()
        self.toonGen.toon.torso = self.toonGen.toon.torsoDNA2torso[newTorso]
        self.toonGen.generateDNAStrandWithCurrentStyle()
        self.updateTorsoButtons(0)

    def nextLeg(self):
        newLegs = self.toonGen.getNextLeg()
        self.toonGen.toon.legs = self.toonGen.toon.legDNA2leg[newLegs]
        self.toonGen.generateDNAStrandWithCurrentStyle()
        self.updateLegButtons(1)

    def updateLegButtons(self, direction):
        if direction == 1:
            nextNewLeg = self.toonGen.getNextLeg()
            if nextNewLeg == '00':
                self.nextLegBtn['state'] = DGG.DISABLED
            self.prevLegBtn['state'] = DGG.NORMAL
        elif direction == 0:
            nextNewLeg = self.toonGen.getPrevLeg()
            if nextNewLeg == '02':
                self.prevLegBtn['state'] = DGG.DISABLED
            self.nextLegBtn['state'] = DGG.NORMAL

    def prevLeg(self):
        newLegs = self.toonGen.getPrevLeg()
        self.toonGen.toon.legs = self.toonGen.toon.legDNA2leg[newLegs]
        self.toonGen.generateDNAStrandWithCurrentStyle()
        self.updateLegButtons(0)

    def exitBodyShop(self):
        self.nextHeadBtn.destroy()
        self.prevHeadBtn.destroy()
        self.nextTorsoBtn.destroy()
        self.prevTorsoBtn.destroy()
        self.nextLegBtn.destroy()
        self.prevLegBtn.destroy()
        self.bodyRoom.reparentTo(hidden)
        del self.nextHeadBtn
        del self.prevHeadBtn
        del self.nextTorsoBtn
        del self.prevTorsoBtn
        del self.nextLegBtn
        del self.prevLegBtn

    def enterColorShop(self):
        self.nextBtn.show()
        self.exitBtn.show()
        self.backBtn.show()
        base.transitions.fadeIn(0)

        self.currentShop = "color"

        self.colorRoom.reparentTo(render)

        self.setTitle("Choose Your Color", "light-blue")

        self.nextAllColorBtn = DirectButton(text="Toon",
                                text_scale=0.06,
                                text_fg=(1,0,0,1),
                                text_pos=(-0.03, 0.005),
                                geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                geom_scale=(1, 1, 1),
                                geom3_color=(0.6, 0.6, 0.6, 0.6),
                                relief=None,
                                scale=1.3,
                                pos=(0.45, 0.5, 0.5),
                                command=self.nextAllColor)
        self.prevAllColorBtn = DirectButton(text="Toon",
                                text_scale=0.06,
                                text_fg=(1,0,0,1),
                                text_pos=(0.03, 0.005),
                                geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                    self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                geom_scale=(-1, 1, 1),
                                geom3_color=(0.6, 0.6, 0.6, 0.6),
                                relief=None,
                                scale=1.3,
                                pos=(-0.5, 0.5, 0.5),
                                command=self.prevAllColor)
        self.nextHeadColorBtn = DirectButton(text="Head",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, 0.1, 0.1),
                                    command=self.nextHeadColor)
        self.prevHeadColorBtn = DirectButton(text="Head",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, 0.1, 0.1),
                                    command=self.prevHeadColor)
        self.nextTorsoColorBtn = DirectButton(text="Body",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.2, -0.2),
                                    command=self.nextTorsoColor)
        self.prevTorsoColorBtn = DirectButton(text="Body",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.2, -0.2),
                                    command=self.prevTorsoColor)
        self.nextLegColorBtn = DirectButton(text="Legs",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.5, -0.5),
                                    command=self.nextLegColor)
        self.prevLegColorBtn = DirectButton(text="Legs",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.5, -0.5),
                                    command=self.prevLegColor)
        self.currentColor = self.toonGen.toon.headcolor
        self.currentHeadColor = self.toonGen.toon.headcolor
        self.currentTorsoColor = self.toonGen.toon.torsocolor
        self.currentLegColor = self.toonGen.toon.legcolor
        self.updateColorShopButtons()

    def setColorShopButtonsNormal(self):
        self.prevAllColorBtn['state'] = DGG.NORMAL
        self.prevHeadColorBtn['state'] = DGG.NORMAL
        self.prevTorsoColorBtn['state'] = DGG.NORMAL
        self.prevLegColorBtn['state'] = DGG.NORMAL
        self.nextAllColorBtn['state'] = DGG.NORMAL
        self.nextHeadColorBtn['state'] = DGG.NORMAL
        self.nextTorsoColorBtn['state'] = DGG.NORMAL
        self.nextLegColorBtn['state'] = DGG.NORMAL

    def updateColorShopButtons(self):
        self.setColorShopButtonsNormal()
        if self.toonGen.toon.color2colorDNA[self.currentColor] == '01':
            self.prevAllColorBtn['state'] = DGG.NORMAL
            self.prevHeadColorBtn['state'] = DGG.NORMAL
            self.prevTorsoColorBtn['state'] = DGG.NORMAL
            self.prevLegColorBtn['state'] = DGG.NORMAL
        elif self.toonGen.toon.color2colorDNA[self.currentColor] == '26':
            self.nextAllColorBtn['state'] = DGG.DISABLED
            self.nextHeadColorBtn['state'] = DGG.DISABLED
            self.nextTorsoColorBtn['state'] = DGG.DISABLED
            self.nextLegColorBtn['state'] = DGG.DISABLED
        elif self.toonGen.toon.color2colorDNA[self.currentColor] == '00':
            self.prevAllColorBtn['state'] = DGG.DISABLED
            self.prevHeadColorBtn['state'] = DGG.DISABLED
            self.prevTorsoColorBtn['state'] = DGG.DISABLED
            self.prevLegColorBtn['state'] = DGG.DISABLED
        elif self.toonGen.toon.color2colorDNA[self.currentColor] == '25':
            self.nextAllColorBtn['state'] = DGG.NORMAL
            self.nextHeadColorBtn['state'] = DGG.NORMAL
            self.nextTorsoColorBtn['state'] = DGG.NORMAL
            self.nextLegColorBtn['state'] = DGG.NORMAL

    def updateColorShopButtonsDir(self, direction):
        self.setColorShopButtonsNormal()
        if direction == 1:
            nextNewHColor = self.toonGen.getNextColor('head')
            nextNewTColor = self.toonGen.getNextColor('torso')
            nextNewLColor = self.toonGen.getNextColor('legs')
            if nextNewHColor == '00':
                self.nextAllColorBtn['state'] = DGG.DISABLED
                self.nextHeadColorBtn['state'] = DGG.DISABLED
            if nextNewTColor == '00':
                self.nextTorsoColorBtn['state'] = DGG.DISABLED
            if nextNewLColor == '00':
                self.nextLegColorBtn['state'] = DGG.DISABLED
        elif direction == 0:
            nextNewHColor = self.toonGen.getPrevColor('head')
            nextNewTColor = self.toonGen.getPrevColor('torso')
            nextNewLColor = self.toonGen.getPrevColor('legs')
            if nextNewHColor == '26':
                self.prevAllColorBtn['state'] = DGG.DISABLED
                self.prevHeadColorBtn['state'] = DGG.DISABLED
            if nextNewTColor == '26':
                self.prevTorsoColorBtn['state'] = DGG.DISABLED
            if nextNewLColor == '26':
                self.prevLegColorBtn['state'] = DGG.DISABLED

    def nextAllColor(self):
        color = self.toonGen.getNextColor('all')
        self.toonGen.toon.headcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.torsocolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.legcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(1)

    def prevAllColor(self):
        color = self.toonGen.getPrevColor('all')
        self.toonGen.toon.headcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.torsocolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.legcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(0)

    def nextHeadColor(self):
        color = self.toonGen.getNextColor('head')
        self.toonGen.toon.headcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(1)

    def prevHeadColor(self):
        color = self.toonGen.getPrevColor('head')
        self.toonGen.toon.headcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(0)

    def nextTorsoColor(self):
        color = self.toonGen.getNextColor('torso')
        self.toonGen.toon.torsocolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(1)

    def prevTorsoColor(self):
        color = self.toonGen.getPrevColor('torso')
        self.toonGen.toon.torsocolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(0)

    def nextLegColor(self):
        color = self.toonGen.getNextColor('legs')
        self.toonGen.toon.legcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(1)

    def prevLegColor(self):
        color = self.toonGen.getPrevColor('legs')
        self.toonGen.toon.legcolor = self.toonGen.toon.colorDNA2color[color]
        self.toonGen.toon.setToonColor()
        self.updateColorShopButtonsDir(0)

    def nextShirt(self):
        newShirt, newSleeve = self.toonGen.getNextShirtAndSleeve()
        newColor = self.toonGen.getNextColor('shirt')
        self.toonGen.toon.shirtColor = self.toonGen.toon.colorDNA2color[newColor]
        self.toonGen.toon.sleeveColor = self.toonGen.toon.colorDNA2color[newColor]
        if newShirt != None and newSleeve != None:
            self.toonGen.toon.shirt = self.toonGen.toon.shirtDNA2shirt[newShirt]
            self.toonGen.toon.sleeve = self.toonGen.toon.sleeveDNA2sleeve[newSleeve]
        self.toonGen.toon.setClothes()
        self.updateClothShopButtonsDir(1)

    def prevShirt(self):
        newShirt, newSleeve = self.toonGen.getPrevShirtAndSleeve()
        newColor = self.toonGen.getPrevColor('shirt')
        self.toonGen.toon.shirtColor = self.toonGen.toon.colorDNA2color[newColor]
        self.toonGen.toon.sleeveColor = self.toonGen.toon.colorDNA2color[newColor]
        if newShirt != None and newSleeve != None:
            self.toonGen.toon.shirt = self.toonGen.toon.shirtDNA2shirt[newShirt]
            self.toonGen.toon.sleeve = self.toonGen.toon.sleeveDNA2sleeve[newSleeve]
        self.toonGen.toon.setClothes()
        self.updateClothShopButtonsDir(1)

    def updateClothShopButtonsDir(self, direction):
        self.nextShirtBtn['state'] = DGG.NORMAL
        self.prevShirtBtn['state'] = DGG.NORMAL
        self.nextShortsBtn['state'] = DGG.NORMAL
        self.prevShortsBtn['state'] = DGG.NORMAL
        if direction == 1:
            if self.toonGen.getNextShirt() == '00':
                self.nextShirtBtn['state'] = DGG.DISABLED
            if self.toonGen.getNextShorts() == '00':
                self.nextShortsBtn['state'] = DGG.DISABLED
            if self.toonGen.getPrevShirt() == '22':
                self.prevShirtBtn['state'] = DGG.DISABLED
            if self.toonGen.getPrevShorts() == '16':
                self.prevShortsBtn['state'] = DGG.DISABLED

    def nextShorts(self):
        newShorts = self.toonGen.getNextShorts()
        newColor = self.toonGen.getNextColor('shorts')
        self.toonGen.toon.shortColor = self.toonGen.toon.colorDNA2color[newColor]
        if newShorts != None:
            self.toonGen.toon.shorts = self.toonGen.toon.shortDNA2short[newShorts]
        self.toonGen.toon.setClothes()
        self.updateClothShopButtonsDir(1)

    def prevShorts(self):
        newShorts = self.toonGen.getPrevShorts()
        newColor = self.toonGen.getPrevColor('shorts')
        self.toonGen.toon.shortColor = self.toonGen.toon.colorDNA2color[newColor]
        if newShorts != None:
            self.toonGen.toon.shorts = self.toonGen.toon.shortDNA2short[newShorts]
        self.toonGen.toon.setClothes()
        self.updateClothShopButtonsDir(1)

    def updateClothes(self):
        if self.currentShirt > 26:
            self.currentShirtTex = self.shirt2Path
            self.currentSleeveTex = self.sleeve2Path
        else:
            self.currentShirtTex = self.shirt1Path
            self.currentSleeveTex = self.sleeve1Path
        if self.gender == "boy":
            if self.currentShorts > 26:
                self.currentShortTex = self.short2Path
            else:
                self.currentShortTex = self.short1Path
        elif self.gender == "girl":
            self.currentShortTex = self.skirt1Path

    def getToonColors(self):
        hr, hg, hb, ha = toonColors[self.currentHeadColor]
        tr, tg, tb, ta = toonColors[self.currentTorsoColor]
        lr, lg, lb, la = toonColors[self.currentLegColor]
        return tuple((hr, hg, hb, tr, tg, tb, lr, lg, lb))

    def enterClothShop(self):
        self.nextBtn.show()
        self.exitBtn.show()
        self.backBtn.show()
        base.transitions.fadeIn(0)

        self.currentShop = "cloth"

        self.clothRoom.reparentTo(render)

        self.setTitle("Choose Your Clothes", "light-blue")

        self.nextShirtBtn = DirectButton(text="Shirt",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.2, -0.2),
                                    command=self.nextShirt)
        self.prevShirtBtn = DirectButton(text="Shirt",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.2, -0.2),
                                    command=self.prevShirt)

        self.nextShortsBtn = DirectButton(text="Shorts",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(-0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(0.45, -0.5, -0.5),
                                    command=self.nextShorts)
        self.prevShortsBtn = DirectButton(text="Shorts",
                                    text_scale=0.06,
                                    text_fg=(1,0,0,1),
                                    text_pos=(0.03, 0.005),
                                    geom=(self.cat_gui.find('**/CrtATn_R_Arrow_UP'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_DN'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_RLVR'),
                                        self.cat_gui.find('**/CrtATn_R_Arrow_UP')),
                                    geom_scale=(-1, 1, 1),
                                    geom3_color=(0.6, 0.6, 0.6, 0.6),
                                    relief=None,
                                    pos=(-0.5, -0.5, -0.5),
                                    command=self.prevShorts)
        self.updateClothes()

        if self.currentShirt == 0:
            self.nextShirtBtn['state'] = DGG.NORMAL
            self.prevShirtBtn['state'] = DGG.DISABLED
        elif self.currentShirt == 26:
            self.nextShirtBtn['state'] = DGG.DISABLED
            self.prevShirtBtn['state'] = DGG.NORMAL
        if self.currentShorts == 0:
            self.nextShortsBtn['state'] = DGG.NORMAL
            self.prevShortsBtn['state'] = DGG.DISABLED
        if self.gender == "boy":
            if self.currentShorts == 53:
                self.nextShortsBtn['state'] = DGG.DISABLED
                self.prevShortsBtn['state'] = DGG.NORMAL
        elif self.gender == "girl":
            if self.currentShorts == 26:
                self.nextShortsBtn['state'] = DGG.DISABLED
                self.prevShortsBtn['state'] = DGG.NORMAL

    def deleteClothShopTask(self, task):
        self.deleteClothShop()

    def exitClothShop(self):
        self.nextShirtBtn.destroy()
        self.prevShirtBtn.destroy()
        self.nextShortsBtn.destroy()
        self.prevShortsBtn.destroy()
        self.clothRoom.reparentTo(hidden)
        del self.nextShirtBtn
        del self.prevShirtBtn
        del self.nextShortsBtn
        del self.prevShortsBtn

    def generateToon(self, gender):
        self.gender = gender
        self.toonGen.generateToon(gender)
        self.toonMade = 1
        self.nextBtn['state'] = DGG.NORMAL

    def fade(self):
        base.transitions.fadeOut(0.2)

    def enterExit(self, direction):
        if direction == "finished":
            # Generate a dna strand because changing the clothes and color doesn't
            # change the dna strand, only the style. I'll call this so it can
            # generate a new dna strand with the current style, so the colors and
            # clothes picked are updated in the strand.
            self.toonGen.generateDNAStrandWithCurrentStyle()
            base.transitions.noTransitions()
            messenger.send("createAToonFinished", [self.toonGen.toon.dnaStrand,
                                self.getSlot(),
                                self.toonName])

            return
        elif direction == "quit":
            base.transitions.noTransitions()
            messenger.send("quitCreateAToon")
            return
        #render.clearLight(self.light)
        #del self.light
        #render.clearLight(self.amb)
        #del self.amb
        self.mat_gui.remove()
        self.cat_gui.remove()
        self.nameGui.removeNode()
        self.room.remove()
        if self.toonMade:
            self.toonGen.cleanupToon()
        if self.currentShop is not None:
            self.backBtn.destroy()
            self.exitBtn.destroy()
        if self.currentShop is not None:
            self.okBtn.destroy()
            self.nextBtn.destroy()
            self.title_lbl.destroy()
            del self.exitBtn
            del self.nextBtn
            del self.backBtn
            del self.okBtn
            del self.title_lbl
        self.spotlight_img.destroy()
        self.spotlight.remove()
        self.genderRoom.remove()
        self.bodyRoom.remove()
        self.colorRoom.remove()
        self.floor.remove()
        self.bg.remove()
        del self.genderRoom
        del self.bodyRoom
        del self.colorRoom
        del self.floor
        del self.bg
        del self.mat_gui
        del self.cat_gui
        del self.room
        del self.spotlight_img
        del self.spotlight
        del self.nameGui
        self.toonName = None
        self.toonMade = 0
        self.music.stop()
        del self.music
        del self.toonGen
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        return

    def exitExit(self):
        pass

    def setTitle(self, title, color):
        try:
            self.title_lbl.destroy()
        except:
            pass
        self.title_lbl = DirectLabel(text=title, relief=None, text_scale=0.16, text_font=loader.loadFont("phase_3/models/fonts/MickeyFont.bam"), pos=(0, 0.85, 0.85))
        if color == "yellow":
            self.title_lbl['text_fg'] = (1,1,0,1)
        elif color == "sea-green":
            self.title_lbl['text_fg'] = (0, 0.8509803921568627, 0.4784313725490196, 1)
        elif color == "light-blue":
            self.title_lbl['text_fg'] = (0, 0.8901960784313725, 1, 1)
