"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CharSelection.py
@author Brian Lach
@date September 15, 2015

"""

from panda3d.core import NodePath, Point3, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import (Sequence, Wait, Func, Parallel, LerpPosInterval,
                                            LerpQuatInterval, SoundInterval, ActorInterval, LerpFunc)
from direct.gui.DirectGui import OnscreenText, DirectButton, DGG, DirectScrolledList, DirectLabel, DirectFrame
from direct.showbase.DirectObject import DirectObject

from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.toon import ParticleLoader
from src.coginvasion.toon.Toon import Toon
from src.coginvasion.gui import Dialog
from src.coginvasion.globals import CIGlobals
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.dna.DNALoader import *
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.phys import PhysicsUtils

import sys
import random

HOOD_ID_2_DNA = {
    ZoneUtil.ToontownCentral:      ["phase_4/dna/pickatoon/storage_TT_pickatoon.pdna",
                                     "phase_4/dna/pickatoon/new_ttc_sz_pickatoon.pdna"],

    ZoneUtil.DonaldsDock:          ["phase_6/dna/pickatoon/storage_DD_pickatoon.pdna",
                                     "phase_6/dna/pickatoon/donalds_dock_sz_pickatoon.pdna"],

    ZoneUtil.MinniesMelodyland:    ["phase_6/dna/pickatoon/storage_MM_pickatoon.pdna",
                                     "phase_6/dna/pickatoon/minnies_melody_land_sz_pickatoon.pdna"],

    ZoneUtil.DaisyGardens:         ["phase_8/dna/pickatoon/storage_DG_pickatoon.pdna",
                                     "phase_8/dna/pickatoon/daisys_garden_sz_pickatoon.pdna"],

    ZoneUtil.DonaldsDreamland:     ["phase_8/dna/pickatoon/storage_DL_pickatoon.pdna",
                                     "phase_8/dna/pickatoon/donalds_dreamland_sz_pickatoon.pdna"],
                                     
    ZoneUtil.TheBrrrgh:            ["phase_8/dna/pickatoon/storage_BR_pickatoon.pdna",
                                     "phase_8/dna/pickatoon/the_burrrgh_sz_pickatoon.pdna"]
}

HOOD_STAGE_DATA = {
    #                                   cam start             cam end         toon pos                     toon hpr
    ZoneUtil.ToontownCentral:      [Point3(0, 60, 15), Point3(0, 10, 3), Point3(77, 15, 7.4),          Vec3(90, 0, 0)],
    ZoneUtil.DonaldsDock:          [Point3(0, 60, 15), Point3(0, 10, 3), Point3(-110.4, -37.3, 5.7),   Vec3(-60, 0, 0)],
    ZoneUtil.MinniesMelodyland:    [Point3(0, 60, 15), Point3(0, 10, 3), Point3(-47, 45.23, 6.525),    Vec3(-115, 0, 0)],
    ZoneUtil.DaisyGardens:         [Point3(0, 60, 15), Point3(0, 10, 3), Point3(-0.25, 14, 0.025),     Vec3(0, 0, 0)],
    ZoneUtil.DonaldsDreamland:     [Point3(0, 60, 15), Point3(0, 10, 3), Point3(-6, -90.3, 0.025),     Vec3(0, 0, 0)],
    ZoneUtil.TheBrrrgh:            [Point3(0, 60, 15), Point3(0, 10, 3), Point3(-113, -40.7, 8.55),    Vec3(-69, 0, 0)]
}

ST_RANDOM_ANIMS = ['bow', 'bored', 'shrug', 'read', 'wave', 'win', 'fallf', 'fallb']
ST_ANIM_IVAL = [5, 35]

class CharSelection(DirectObject):
    notify = directNotify.newCategory('CharSelection')

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
        self.title = None
        self.stageToon = None
        self.stageToonRoot = None
        self.deleteConf = None
        self.frame = None
        self.stageFSM = ClassicFSM.ClassicFSM(
            'StageFSM',
            [
                State.State('off', self.enterOff, self.exitOff),
                State.State('loadSZ', self.enterLoadSZ, self.exitLoadSZ),
                State.State('onStage', self.enterOnStage, self.exitOnStage)
            ],
            'off', 'off'
        )
        self.stageFSM.enterInitialState()
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

        self.szGeom = None
        self.olc = None
        self.asyncSZLoadStatus = False
        self.isNewToon = False
        self.newToonSlot = None
        self.camIval = None
        self.stAnimSeq = None
        self.newToonAnnounceSfx = base.loadSfx("phase_4/audio/sfx/King_Crab.ogg")
        self.newToonDrumrollSfx = base.loadSfx("phase_5/audio/sfx/SZ_MM_drumroll.ogg")
        self.newToonRevealSfx = base.loadSfx("phase_5/audio/sfx/SZ_MM_fanfare.ogg")
        
        self.dnaStore = DNAStorage()
        loader.loadDNAFile(self.dnaStore, 'phase_4/dna/pickatoon/storage_pickatoon.pdna')

    def __setupStageToon(self):
        self.stageToonRoot = render.attachNewNode('stageToonRoot')
        self.stageToon = Toon(base.cr)
        self.stageToon.setPosHpr(0, 0, 0, 0, 0, 0)
        self.stageToon.reparentTo(self.stageToonRoot)

    def cleanupStageToon(self):
        if self.stageToon != None:
            self.stageToon.disable()
            self.stageToon.delete()
            self.stageToon = None
        if self.stageToonRoot != None:
            self.stageToonRoot.removeNode()
            self.stageToonRoot = None

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def __async_loadSZTask(self, task = None):
        dnas = HOOD_ID_2_DNA[self.choice.lastHood]
        for i in xrange(len(dnas)):
            dnaFile = dnas[i]
            if i == len(dnas) - 1:
                node = loader.loadDNAFile(self.dnaStore, dnaFile)
                if node.getNumParents() == 1:
                    self.szGeom = NodePath(node.getParent(0))
                    self.szGeom.reparentTo(render)
                else:
                    self.szGeom = render.attachNewNode(node)
                gsg = base.win.getGsg()
                if gsg:
                    self.szGeom.prepareScene(gsg)
            else:
                loader.loadDNAFile(self.dnaStore, dnaFile)

        base.createPhysicsNodes(self.szGeom)
        base.enablePhysicsNodes(self.szGeom)

        self.olc = ZoneUtil.getOutdoorLightingConfig(self.choice.lastHood)
        self.olc.setup()
        self.olc.apply()

        self.asyncSZLoadStatus = True

        if task:
            return task.done

    def enterLoadSZ(self):
        self.loadingDlg = Dialog.GlobalDialog("Loading...")
        self.loadingDlg.show()
        
        base.cr.renderFrame()
        base.cr.renderFrame()

        self.notify.info("Polling for SZ to load")
        self.asyncSZLoadStatus = False
        self.__async_loadSZTask()
        self.stageFSM.request('onStage')

    def exitLoadSZ(self):
        if hasattr(self, 'loadingDlg'):
            self.loadingDlg.cleanup()
            del self.loadingDlg
            
    def __changeCamFOV(self, val):
        base.camLens.setMinFov(val / (4. / 3.))

    def enterOnStage(self):
        dna = self.choice.dna
        name = self.choice.name
        self.stageToon.setName(name)
        self.stageToon.setDNAStrand(dna)
        self.stageToon.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCLocal])
        self.stageToon.nametag.setActive(0)
        self.stageToon.nametag.nametag3d.request('Rollover')
        self.stageToon.nametag.unmanage(base.marginManager)
        self.stageToon.nametag.updateAll()
        self.stageToon.animFSM.request('neutral')
        self.stageToon.startBlink()
        self.stageToon.setPosHpr(0, 0, 0, 10, 0, 0)
        self.stageToon.show()

        dat = HOOD_STAGE_DATA[self.choice.lastHood]

        self.stageToonRoot.setPos(dat[2])
        self.stageToonRoot.setHpr(dat[3])

        camera.reparentTo(self.stageToonRoot)

        camera.setPos(dat[0])
        camera.lookAt(self.stageToonRoot, 0, 0, 3)
        startHpr = camera.getHpr()
        camera.setPos(dat[1])
        camera.lookAt(self.stageToonRoot, 0, 0, 3)
        endHpr = camera.getHpr()

        self.camIval = Parallel(
            LerpPosInterval(camera, 5.0, dat[1] - (1.6, 0, 0), dat[0] - (1.6, 0, 0), blendType = 'easeInOut'),
            LerpQuatInterval(camera, 5.0, hpr = endHpr, startHpr = startHpr, blendType = 'easeInOut'),
            LerpFunc(self.__changeCamFOV, duration = 5.0, fromData = 80.0, toData = CIGlobals.DefaultCameraFov, blendType = 'easeInOut'))
        if self.isNewToon:
            self.camIval.append(
                Sequence(Func(self.stageToon.hide),
                         Func(base.stopMusic),
                         SoundInterval(self.newToonAnnounceSfx, startTime = 1.674, duration = 4.047),
                         SoundInterval(self.newToonDrumrollSfx),
                         Func(self.stageToon.pose, 'tele', self.stageToon.getNumFrames('tele')),
                         Func(self.newToonAppear),
                         Func(self.stageToon.show),
                         SoundInterval(self.newToonRevealSfx),
                         Func(base.cr.playTheme)))
        else:
            self.camIval.append(
                Sequence(Func(self.showActionButtons), Func(self.enableAllCharButtons), Wait(5.0), Func(self.beginRandomAnims)))

        self.camIval.start()
        
    def hideActionButtons(self):
        self.playOrCreateButton.hide()
        self.deleteButton.hide()
        
    def showActionButtons(self):
        self.playOrCreateButton.show()
        self.deleteButton.show()

    def newToonAppear(self):
        self.stopSTAnimSeq()

        self.stAnimSeq = Sequence(Func(self.stageToon.animFSM.request, 'teleportIn'),
                                  Wait(2.0),
                                  ActorInterval(self.stageToon, 'wave'),
                                  Func(self.stageToon.loop, 'neutral'),
                                  Func(self.beginRandomAnims),
                                  Func(self.enableAllCharButtons),
                                  Func(self.showActionButtons))
        self.stAnimSeq.start()

    def stopSTAnimSeq(self):
        if self.stAnimSeq:
            self.stAnimSeq.finish()
            self.stAnimSeq = None
            
    def unloadSZGeom(self):
        if self.szGeom:
            base.disablePhysicsNodes(self.szGeom)
            self.szGeom.removeNode()
            self.szGeom = None
        if self.olc:
            self.olc.cleanup()
            self.olc = None

    def beginRandomAnims(self):
        self.stageToon.startLookAround()
        taskMgr.doMethodLater(random.uniform(*ST_ANIM_IVAL), self.__doRandomSTAnim, "doRandomSTAnim")

    def __doRandomSTAnim(self, task):
        anim = random.choice(ST_RANDOM_ANIMS)

        self.stopSTAnimSeq()
        
        self.stageToon.stopLookAround()
        
        head = self.stageToon.getPart('head')

        if anim == 'read':
            self.stAnimSeq = Sequence(Func(self.stageToon.lerpLookAt, head, (0, -15, 0)),
                                      Func(self.stageToon.animFSM.request, 'openBook'),
                                      Wait(0.5),
                                      Func(self.stageToon.animFSM.request, 'readBook'),
                                      Wait(2.0),
                                      Func(self.stageToon.lerpLookAt, head, (0, 0, 0)),
                                      Func(self.stageToon.animFSM.request, 'closeBook'),
                                      Wait(1.75),
                                      Func(self.stageToon.loop, 'neutral'),
                                      Func(self.stageToon.startLookAround))
        else:
            self.stageToon.lerpLookAt(head, (0, 0, 0))
            self.stAnimSeq = Sequence(ActorInterval(self.stageToon, anim), Func(self.stageToon.loop, 'neutral'),
                                      Func(self.stageToon.startLookAround))

        self.stAnimSeq.start()

        task.delayTime = random.uniform(*ST_ANIM_IVAL)
        return task.again

    def endRandomAnims(self):
        taskMgr.remove("doRandomSTAnim")
        self.stopSTAnimSeq()

    def exitOnStage(self):
        self.isNewToon = False
        if self.camIval:
            self.camIval.finish()
            self.camIval = None
        self.endRandomAnims()
        self.stopSTAnimSeq()
        camera.reparentTo(render)
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        #base.transitions.fadeScreen(1.0)
        self.unloadSZGeom()
        self.stageToon.stopLookAround()
        self.stageToon.stopBlink()
        self.stageToon.hide()

    def enterCharSelected(self):
        self.playOrCreateButton['text'] = self.PLAY
        self.playOrCreateButton['extraArgs'] = ['play']

    def exitCharSelected(self):
        self.playOrCreateButton.hide()
        self.deleteButton.hide()

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
            doFade = False
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
            message = 'This will delete {0} forever.\n\nAre you sure?'.format(self.avChooser.getNameFromAvId(avId)),
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
            self.choice = self.avChooser.getAvChoiceBySlot(slot)
            self.selectionFSM.request('character')
            self.stageFSM.request('loadSZ')
        else:
            self.selectionFSM.request('empty')
            self.stageFSM.request('off')

    def disableAllCharButtons(self):
        for btn in self.charButtons:
            btn['state'] = DGG.DISABLED

    def enableAllCharButtons(self):
        for btn in self.charButtons:
            if not self.choice or btn.getPythonTag('slot') != self.choice.slot:
                btn['state'] = DGG.NORMAL

    def load(self, newToonSlot = None):
        self.isNewToon = newToonSlot is not None
        self.newToonSlot = newToonSlot

        base.transitions.noTransitions()

        base.cr.renderFrame()
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

        self.__setupStageToon()

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

        for slot in range(6):
            if self.avChooser.hasToonInSlot(slot):
                choice = self.avChooser.getAvChoiceBySlot(slot)
                text = choice.name
            else:
                text = self.NO_TOON
            btn = CIGlobals.makeDefaultScrolledListBtn(text = text, text_scale = 0.06, command = self.__handleCharButton, extraArgs = [slot])
            btn.setPythonTag('slot', slot)
            self.charButtons.append(btn)
            btn['state'] = DGG.NORMAL

        self.charList = CIGlobals.makeDefaultScrolledList(pos = (0.75, 0, -0.225), listZorigin = -0.43,
                                                          listFrameSizeZ = 0.51, arrowButtonScale = 0.0, items = self.charButtons,
                                                          parent = self.frame)

        if self.isNewToon:
            self.__handleCharButton(self.newToonSlot)
            self.disableAllCharButtons()

    def unload(self):
        self.selectionFSM.requestFinalState()
        self.stageFSM.requestFinalState()
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
        if self.title:
            self.title.destroy()
            self.title = None
        base.camera.setPos(0, 0, 0)
        base.camera.setHpr(0, 0, 0)
        base.transitions.noTransitions()
        del self.selectionFSM
