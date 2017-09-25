"""

  Filename: PickAToon.py
  Created by: blach (??July14)

"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func
from panda3d.core import Point3

from direct.gui.DirectGui import DirectButton, DirectLabel, OnscreenImage
from direct.gui.DirectFrame import DirectFrame

from lib.coginvasion.gui.Dialog import GlobalDialog
from lib.coginvasion.makeatoon.MakeAToon import MakeAToon
from lib.coginvasion.toon.ToonHead import ToonHead
from lib.coginvasion.toon.ToonDNA import ToonDNA
from lib.coginvasion.globals import CIGlobals

from direct.directnotify.DirectNotify import DirectNotify

import sys
import random

notify = DirectNotify().newCategory("PickAToon")

class PickAToon:
    name_hpr = [Point3(0, 0, 352),
        Point3(0, 0, 4),
        Point3(0, 0, 4),
        Point3(0, 0, -4),
        Point3(0, 0, -4),
        Point3(0, 0, 1)]
    name_pos = [Point3(-0.03, 0, 0.22),
        Point3(0, 0, 0.235),
        Point3(0, 0, 0.235),
        Point3(0, 0, 0.24),
        Point3(-0.04, 0, 0.235),
        Point3(0, 0, 0.25)]
    trash_pos = [Point3(0.29, 0, -0.18),
        Point3(0.22, 0, -0.22),
        Point3(0.18, 0, -0.24),
        Point3(0.27, 0, -0.21),
        Point3(0.30, 0, -0.18),
        Point3(0.21, 0, -0.23)]
    BgColor = (0.1450980392156863, 0.3686274509803922, 0.7803921568627451)

    def __init__(self, avChooser):
        self.title = None
        self.avChooser = avChooser
        self.dna = ToonDNA()
        #self.tutorial = Tutorial.Tutorial(self)

    def createGui(self):
        base.cr.renderFrame()

        self.m = loader.loadFont("phase_3/models/fonts/MickeyFont.bam")
        self.bg = loader.loadModel("phase_3/models/gui/tt_m_gui_pat_mainGui.bam")
        self.qtbtn = loader.loadModel("phase_3/models/gui/quit_button.bam")

        self.trash_gui = loader.loadModel("phase_3/models/gui/trashcan_gui.bam")

        self.bg_img = OnscreenImage(image=self.bg.find('**/tt_t_gui_pat_background'))

        self.setTitle("Pick  A  Toon  To  Play")

        base.setBackgroundColor(self.BgColor)

        self.btn1 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squareGreen'), relief=None, pos=(0.012, 0, 0.306), text_wordwrap=6, text_fg=(1,1,1,1))
        self.btn2 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squarePink'), relief=None, pos=(0.01, 0, -0.515), text_wordwrap=6, text_fg=(1,1,1,1))
        self.btn3 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squareRed'), relief=None, pos=(-0.84, 0, 0.36), text_wordwrap=6, text_fg=(1,1,1,1))
        self.btn4 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squareYellow'), relief=None, pos=(0.865, 0, -0.45), text_wordwrap=6, text_fg=(1,1,1,1))
        self.btn5 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squareBlue'), relief=None, pos=(-0.87,0,-0.44), text_wordwrap=6, text_fg=(1,1,1,1))
        self.btn6 = DirectButton(geom=self.bg.find('**/tt_t_gui_pat_squarePurple'), relief=None, pos=(0.873, 0, 0.335), text_wordwrap=6, text_fg=(1,1,1,1))

        self.quit_btn = DirectButton(geom=(self.qtbtn.find('**/QuitBtn_RLVR'),
                                        self.qtbtn.find('**/QuitBtn_RLVR'),
                                        self.qtbtn.find('**/QuitBtn_RLVR')),
                                        relief=None,
                                        text="Quit",
                                        text_font=self.m,
                                        text_scale=0.105,
                                        text_pos=(0, -0.035),
                                        pos=(1.05, 0, -0.9),
                                        text_fg=(1, 0.9, 0.1, 1),
                                        geom1_scale=(1.02, 1, 1),
                                        geom2_scale=(1.02, 1, 1),
                                        command=self.quitGame)

        self.btnList = []
        self.btnList.append(self.btn1)
        self.btnList.append(self.btn2)
        self.btnList.append(self.btn3)
        self.btnList.append(self.btn4)
        self.btnList.append(self.btn5)
        self.btnList.append(self.btn6)

        self.headList = []

        #datafiler = open("toons/data.txt", "r")
        #if datafiler.read() == "-":
        #	for btn in self.btnList:
        #		btn['state'] = DGG.DISABLED
        #	self.quit_btn['state'] = DGG.DISABLED
        #	self.tutorial.askTutorial()
        #	datafilew = open("toons/data.txt", "w")
        #	datafilew.write("+")
        #	datafilew.flush()
        #	datafilew.close()
        #datafiler.close()

        for slot in range(6):
            if self.avChooser.hasToonInSlot(slot):
                notify.info("found existing Toon in slot %s" % (str(slot)))
                frame = DirectFrame(relief=None, parent=self.btnList[slot], pos=(0,0, -0.1))
                headframe = hidden.attachNewNode('head')
                headframe.setPosHprScale(0, 5, -0.1, 180, 0, 0, 0.24, 0.24, 0.24)
                headframe.reparentTo(self.btnList[slot].stateNodePath[0], 20)
                headframe.instanceTo(self.btnList[slot].stateNodePath[1], 20)
                headframe.instanceTo(self.btnList[slot].stateNodePath[2], 20)
                toon = ToonHead(base.cr)
                self.headList.append(toon)
                gender, animal, head, headcolor = self.avChooser.getHeadInfo(slot)
                toon.generateHead(gender, animal, head, 1)
                toon.getGeomNode().setDepthWrite(1)
                toon.getGeomNode().setDepthTest(1)
                toon.startBlink()
                toon.startLookAround()
                toon.reparentTo(headframe)
                toon.setHeadColor(headcolor)
                toon.flattenLight()
                name_lbl = DirectLabel(text=self.avChooser.getNameInSlot(slot), text_scale=0.08, text_fg=(1,1,1,1), text_wordwrap=7, relief=None, text_shadow=(0,0,0,1))
                name_lbl.reparentTo(self.btnList[slot].stateNodePath[0], 20)
                name_lbl.instanceTo(self.btnList[slot].stateNodePath[1], 20)
                name_lbl.instanceTo(self.btnList[slot].stateNodePath[2], 20)
                name_lbl.setPos(self.name_pos[slot])
                name_lbl.setHpr(self.name_hpr[slot])
                self.btnList[slot]['text'] = ("", "Play This Toon", "Play This Toon", "")
                self.btnList[slot]['text_scale'] = 0.1
                self.btnList[slot]['text_pos'] = (0, 0)
                self.btnList[slot]['text_fg'] = (1,0.9,0,1)
                self.btnList[slot]['text_wordwrap'] = 6
                self.btnList[slot]['text_font'] = self.m
                self.btnList[slot]['command'] = self.fadeMenu
                self.btnList[slot]['extraArgs'] = ["playGame", slot]
                delBtn = DirectButton(text=("", "Delete", "Delete", ""), text_scale=0.15, scale=0.5,
                                text_pos=(0, -0.1), text_fg=(1,1,1,1), relief=None, geom=(self.trash_gui.find('**/TrashCan_CLSD'),
                                                        self.trash_gui.find('**/TrashCan_OPEN'),
                                                        self.trash_gui.find('**/TrashCan_RLVR')), pos=self.trash_pos[slot],
                                command=self.deleteToon, extraArgs=[self.avChooser.getAvChoiceBySlot(slot).getAvId()],
                                text_shadow=(0,0,0,1))
                delBtn.reparentTo(self.btnList[slot].stateNodePath[0], 20)
                delBtn.instanceTo(self.btnList[slot].stateNodePath[1], 20)
                delBtn.instanceTo(self.btnList[slot].stateNodePath[2], 20)
            else:
                self.btnList[slot]['text'] = "Make A Toon"
                self.btnList[slot]['text_font'] = self.m
                self.btnList[slot]['text0_scale'] = 0.1
                self.btnList[slot]['text1_scale'] = 0.12
                self.btnList[slot]['text2_scale'] = 0.12
                self.btnList[slot]['text3_scale'] = 0.1
                self.btnList[slot]['text0_fg'] = (0, 1, 0.8, 0.5)
                self.btnList[slot]['text1_fg'] = (0, 1, 0.8, 1)
                self.btnList[slot]['text2_fg'] = (0.3, 1, 0.9, 1)
                self.btnList[slot]['text3_fg'] = (0, 1, 0.8, 0.5)
                self.btnList[slot]['text_font'] = self.m
                self.btnList[slot]['command'] = self.fadeMenu
                self.btnList[slot]['extraArgs'] = ["mat", slot]
                self.btnList[slot]['text_wordwrap'] = 6

    def quitGame(self):
        base.cr.disconnect()
        base.cr.shutdown()
        base.shutdown()
        sys.exit()

    def deleteToon(self, avId):
        notify.warning("deleting Toon with avId %s" % (avId))

        base.transitions.fadeOut(0.3)
        Sequence(Wait(0.31), Func(self.callDeleteToon, avId)).start()

    def callDeleteToon(self, avId):
        self.avChooser.avChooseFSM.request("waitForToonDelResponse", [avId])

    def setTitle(self, title):
        if self.title:
            self.title.destroy()
            self.title = None
        self.title = DirectLabel(text=title, text_font=self.m, text_fg=(1, 0.9, 0.1, 1), relief=None, text_scale=0.13, pos=(0, 0, 0.82))

    def resetMenu(self, task):
        self.removeGui()
        self.createGui()
        return task.done

    def fadeMenu(self, direction, slot):
        base.transitions.fadeOut(0.5)
        self.slot = slot
        if direction == "mat":
            notify.info("Toon selected for creation on slot %s" % (self.slot))
            taskMgr.doMethodLater(0.51, self.enterMAT, "enterMAT")
        elif direction == "playGame":
            notify.info("Playing game as Toon on slot %s" % (self.slot))
            taskMgr.doMethodLater(0.51, self.playGame, "playGame")

    def enterMAT(self, task):
        messenger.send("enterMakeAToon")
        return task.done

    def handleMATUnavailable(self):
        base.transitions.fadeIn(0)
        self.matNAMsg = GlobalDialog(message = CIGlobals.MatNAMsg, doneEvent = "matNAEvent", style = 1)
        self.acceptOnce("matNAEvent", self.removeMatNAMsg)

    def removeMatNAMsg(self, value):
        self.matNAMsg.destroy()
        if value:
            random_gender = random.randint(0, 1)
            if random_gender == 0:
                gender = "boy"
            elif random_gender == 1:
                gender = "girl"
            MAT = MakeAToon(self.slot, self.cr)
            MAT.toonGen.generateToon(gender, 1)
            MAT.exit("finished")
            return
        self.createGui(1)

    def playGame(self, task):
        self.removeGui()
        messenger.send("avChooseDone", [self.avChooser.getAvChoiceBySlot(self.slot)])

    def removeGui(self):
        self.bg.removeNode()
        self.bg_img.destroy()
        self.quit_btn.destroy()
        self.title.destroy()
        for toon in range(len(self.headList) - 1):
            self.headList[toon].delete()
        for button in range(6):
            self.btnList[button].removeNode()
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        base.transitions.fadeIn(0)
