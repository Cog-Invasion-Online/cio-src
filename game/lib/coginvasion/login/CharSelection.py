# Filename: CharSelection.py
# Created by:  blach (05Sep15)

from panda3d.core import Vec4, TextNode, Fog

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.gui.DirectGui import OnscreenText, DirectButton, DGG, DirectScrolledList, DirectLabel, DirectFrame
from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.holiday.HolidayManager import HolidayType
from lib.coginvasion.toon import ParticleLoader
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.gui import Dialog
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.nametag import NametagGlobals

import sys

class CharSelection(DirectObject):
    notify = directNotify.newCategory('CharSelection')

    STAGE_TOON_POS = (66.4, 74.47, -25)
    STAGE_TOON_HPR = (227.73, 0, 0)

    NO_TOON = "Empty Slot"
    PLAY = "Play"
    CREATE = "Create"
    TITLE = "Pick  A  Toon  To  Play"

    def __init__(self, avChooser):
        self.avChooser = avChooser
        self.choice = None
        self.charList = None
        self.charNameLabel = None
        self.charButtons = []
        self.playOrCreateButton = None
        self.deleteButton = None
        self.quitButton = None
        self.world = None
        self.sky = None
        self.fog = None
        self.title = None
        self.stageToon = None
        self.deleteConf = None
        self.frame = None
        self.selectionFSM = ClassicFSM.ClassicFSM(
            'CharSelection',
            [
                State.State('off', self.enterOff, self.exitOff),
                State.State('character', self.enterCharSelected, self.exitCharSelected),
                State.State('empty', self.enterEmptySelected, self.exitEmptySelected)
            ],
            'off', 'off'
        )
        self.selectionFSM.enterInitialState()

    def __setupStageToon(self):
        self.stageToon = Toon(base.cr)
        self.stageToon.setPos(self.STAGE_TOON_POS)
        self.stageToon.setHpr(self.STAGE_TOON_HPR)

    def cleanupStageToon(self):
        if self.stageToon != None:
            self.stageToon.disable()
            self.stageToon.delete()
            self.stageToon = None

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterCharSelected(self, slot):
        self.choice = self.avChooser.getAvChoiceBySlot(slot)
        dna = self.choice.dna
        name = self.choice.name
        self.stageToon.setName(name)
        self.stageToon.setDNAStrand(dna)
        self.stageToon.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCLocal])
        self.stageToon.nametag.setActive(0)
        self.stageToon.nametag.updateAll()
        self.stageToon.nametag.nametag3d.request('Rollover')
        self.stageToon.animFSM.request('neutral')
        self.stageToon.reparentTo(base.render)
        self.charNameLabel.setText(name)
        self.playOrCreateButton['text'] = self.PLAY
        self.playOrCreateButton['extraArgs'] = ['play']
        self.playOrCreateButton.show()
        self.deleteButton.show()

    def exitCharSelected(self):
        self.stageToon.animFSM.requestFinalState()
        self.stageToon.deleteCurrentToon()
        self.stageToon.reparentTo(base.hidden)
        self.playOrCreateButton.hide()
        self.deleteButton.hide()
        self.choice = None

    def enterEmptySelected(self):
        self.charNameLabel.setText(self.NO_TOON)
        self.playOrCreateButton['text'] = self.CREATE
        self.playOrCreateButton['extraArgs'] = ['create']
        self.playOrCreateButton.show()

    def exitEmptySelected(self):
        self.playOrCreateButton.hide()

    def __action(self, action):
        for btn in self.charButtons:
            if btn['state'] == DGG.DISABLED:
                self.slot = btn.getPythonTag('slot')
                break
        func = None
        arg = None
        doFade = True
        if action == 'delete':
            func = self.deleteToon
            arg = self.choice.avId
            doFade = False
        elif action == 'play':
            func = self.playGame
            arg = self.choice.slot
        elif action == 'create':
            func = self.enterMAT
        elif action == 'quit':
            func = sys.exit
        if doFade:
            base.transitions.fadeOut(0.3)
            if arg != None:
                Sequence(Wait(0.31), Func(func, arg)).start()
            else:
                Sequence(Wait(0.31), Func(func)).start()
        else:
            if arg != None:
                func(arg)
            else:
                func()

    def playGame(self, slot):
        messenger.send("avChooseDone", [self.avChooser.getAvChoiceBySlot(slot)])

    def enterMAT(self):
        messenger.send("enterMakeAToon", [self.slot])

    def deleteToon(self, avId):
        # Show a confirmation message
        self.deleteConf = Dialog.GlobalDialog(
            message = 'This will delete {0} forever. Are you sure?'.format(self.avChooser.getNameFromAvId(avId)),
            style = Dialog.YesNo, doneEvent = 'deleteConfResponse', extraArgs = [avId])
        self.acceptOnce('deleteConfResponse', self.__handleDeleteConfResponse)
        self.deleteConf.show()

    def __handleDeleteConfResponse(self, avId):
        doneStatus = self.deleteConf.getValue()
        if doneStatus:
            # Alright, they pressed yes. No complaining to us.
            self.avChooser.avChooseFSM.request("waitForToonDelResponse", [avId])
        else:
            self.deleteConf.cleanup()
            self.deleteConf = None

    def __handleCharButton(self, slot):
        for btn in self.charButtons:
            if btn.getPythonTag('slot') == slot:
                btn['state'] = DGG.DISABLED
            else:
                btn['state'] = DGG.NORMAL
        if self.avChooser.hasToonInSlot(slot):
            self.selectionFSM.request('character', [slot])
        else:
            self.selectionFSM.request('empty')

    def load(self):
        base.cr.renderFrame()
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

        self.__setupStageToon()
        holidayMgr = base.cr.holidayManager

        self.props = []
        self.world = loader.loadModel('phase_9/models/cogHQ/SellbotHQExterior.bam')
        self.world.reparentTo(base.render)
        self.world.setPos(0, 227.09, -25.36)
        self.sky = loader.loadModel('phase_9/models/cogHQ/cog_sky.bam')
        self.sky.setScale(1)
        self.sky.reparentTo(base.render)
        self.sky.find('**/InnerGroup').removeNode()
        self.fog = Fog('charSelectFog')
        self.fog.setColor(0.2, 0.2, 0.2)
        self.fog.setExpDensity(0.003)
        base.render.setFog(self.fog)
        
        # Let's fix the flickering doors.
        doors = self.world.find('**/doors').getChildren()
        
        for door in doors:
            for frameHole in door.findAllMatches('**/doorFrameHole*'): frameHole.removeNode()

        if holidayMgr.getHoliday() == HolidayType.CHRISTMAS:
            piles = {
                'half' : {'pos' : (57.28, 86.47, -25.00), 'hpr' : (46.79, 0, 0)},
                'full' : {'pos' : (71.23, 85.2, -25.00), 'hpr' : (290.82, 0, 0)},
                'half_2' : {'pos' : (-15, 128.69, -25), 'hpr' : (60.26, 0, 0)}
            }

            for pileType, info in piles.items():
                if '_' in pileType:
                    pileType = pileType[:-2]
                pile = loader.loadModel('phase_8/models/props/snow_pile_%s.bam' % (pileType))
                pile.reparentTo(render)
                pile.setPos(info['pos'])
                pile.setHpr(info['hpr'])
                self.props.append(pile)

            self.world.find('**/TopRocks').removeNode()

            snowTxt = loader.loadTexture('winter/maps/sbhq_snow.png')
            self.world.find('**/Ground').setTexture(snowTxt, 1)

            self.particles = ParticleLoader.loadParticleEffect('phase_8/etc/snowdisk.ptf')
            self.particles.setPos(0, 0, 5)
            self.particlesRender = self.world.attachNewNode('snowRender')
            self.particlesRender.setDepthWrite(0)
            self.particlesRender.setBin('fixed', 1)
            self.particles.start(parent = camera, renderParent = self.particlesRender)
            self.fog.setColor(0.486, 0.784, 1)
            self.fog.setExpDensity(0.006)
            base.render.setFog(self.fog)


        self.title = DirectLabel(text=self.TITLE, text_font=CIGlobals.getMickeyFont(), text_fg=(1, 0.9, 0.1, 1),
                                relief=None, text_scale=0.13, pos=(0, 0, 0.82))
        self.charNameLabel = OnscreenText(text = "", font = CIGlobals.getMickeyFont(),
                                        pos = (-0.25, 0.5, 0), fg = (1, 0.9, 0.1, 1.0))
        self.charNameLabel.hide()
        self.frame = DirectFrame()
        self.frame['image'] = DGG.getDefaultDialogGeom()
        self.frame['image_color'] = CIGlobals.DialogColor
        self.frame['image_scale'] = (-0.9, -0.9, 0.8)
        self.frame['image_pos'] = (0.82, 0, -0.125)
        self.playOrCreateButton = DirectButton(text = "", pos = (0.8125, 0, -0.35), command = self.__action,
                                            geom = CIGlobals.getDefaultBtnGeom(), text_scale = 0.06,
                                            relief = None, text_pos = (0, -0.01))
        self.playOrCreateButton.hide()
        self.deleteButton = DirectButton(text = "Delete", pos = (0.8125, 0, -0.45),
                                        command = self.__action, extraArgs = ['delete'],
                                        geom = CIGlobals.getDefaultBtnGeom(), text_scale = 0.06,
                                        relief = None, text_pos = (0, -0.01))
        self.deleteButton.hide()
        self.quitButton = DirectButton(text = "Quit", pos = (-1.10, 0, -0.925), command = self.__action,
                                    extraArgs = ['quit'], text_scale = 0.06, geom = CIGlobals.getDefaultBtnGeom(),
                                    relief = None, text_pos = (0, -0.01))

        textRolloverColor = Vec4(1, 1, 0, 1)
        textDownColor = Vec4(0.5, 0.9, 1, 1)
        textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)

        for slot in range(6):
            if self.avChooser.hasToonInSlot(slot):
                choice = self.avChooser.getAvChoiceBySlot(slot)
                text = choice.name
            else:
                text = self.NO_TOON
            btn = DirectButton(
                relief=None, text = text, text_scale=0.06,
                text_align=TextNode.ALeft, text1_bg=textDownColor, text2_bg=textRolloverColor,
                text3_fg=textDisabledColor, textMayChange=0, command=self.__handleCharButton,
                extraArgs=[slot], text_pos = (0, 0, 0.0)
            )
            btn.setPythonTag('slot', slot)
            self.charButtons.append(btn)
            btn['state'] = DGG.NORMAL

        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        listXorigin = -0.02
        listFrameSizeX = 0.625
        listZorigin = -0.43
        listFrameSizeZ = 0.51
        arrowButtonScale = 0.0
        itemFrameXorigin = -0.237
        itemFrameZorigin = 0.365
        buttonXstart = itemFrameXorigin + 0.293

        self.charList = DirectScrolledList(
            relief=None,
            pos=(0.75, 0, -0.225),
            incButton_image=None,
            #incButton_relief=None,
            incButton_scale=(arrowButtonScale, arrowButtonScale, -arrowButtonScale),
            #incButton_pos=(buttonXstart, 0, itemFrameZorigin - 0.999),
            #incButton_image3_color=Vec4(1, 1, 1, 0.2),
            decButton_image=None,
            #decButton_relief=None,
            decButton_scale=(arrowButtonScale, arrowButtonScale, arrowButtonScale),
            #decButton_pos=(buttonXstart, 0, itemFrameZorigin + 0.125),
            #decButton_image3_color=Vec4(1, 1, 1, 0.2),
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
            items=self.charButtons,
            parent = self.frame
        )

        base.camera.setPos(75.12, 63.22, -23)
        base.camera.setHpr(26.57, 9.62, 0)

    def unload(self):
        self.selectionFSM.requestFinalState()
        self.cleanupStageToon()
        self.choice = None
        if self.frame:
            self.frame.destroy()
            self.frame = None
        if self.charButtons:
            for btn in self.charButtons:
                btn.destroy()
            self.charButtons = None
        if self.deleteConf:
            self.deleteConf.cleanup()
            self.deleteConf = None
        if self.charList:
            self.charList.destroy()
            self.charList = None
        if self.charNameLabel:
            self.charNameLabel.destroy()
            self.charNameLabel = None
        if self.playOrCreateButton:
            self.playOrCreateButton.destroy()
            self.playOrCreateButton = None
        if self.deleteButton:
            self.deleteButton.destroy()
            self.deleteButton = None
        if self.quitButton:
            self.quitButton.destroy()
            self.quitButton = None
        if self.sky:
            self.sky.removeNode()
            self.sky = None
        if self.world:
            self.world.removeNode()
            self.world = None
        if self.title:
            self.title.destroy()
            self.title = None
        for prop in self.props:
            if not prop.isEmpty():
                prop.removeNode()
        self.props = None
        if hasattr(self, 'particles'):
            self.particles.cleanup()
            self.particlesRender.removeNode()
            self.particles = None
            del self.particlesRender
        base.render.clearFog()
        self.fog = None
        base.camera.setPos(0, 0, 0)
        base.camera.setHpr(0, 0, 0)
        base.transitions.noTransitions()
        del self.selectionFSM
