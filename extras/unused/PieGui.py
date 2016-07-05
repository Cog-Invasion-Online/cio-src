# Filename: PieGui.py
# Created by:  blach (06Aug14)

from direct.gui.DirectGui import DirectFrame, OnscreenImage, DirectLabel
from direct.directnotify.DirectNotify import DirectNotify
from direct.interval.SoundInterval import SoundInterval
from direct.showbase.DirectObject import *
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals

class GagGui(DirectObject):
    notify = DirectNotify().newCategory("GagGui")

    def __init__(self, backpack):
        DirectObject.__init__(self)
        self.weapon = backpack.getCurrentGag()
        self.backpack = backpack
        self.prevGag = None
        return

    def createGui(self):
        self.deleteGui()
        gui = loader.loadModel("phase_3.5/models/gui/weapon_gui.bam")
        self.gui_dict = {CIGlobals.WholeCreamPie: {"idle": gui.find('**/tart_idle'),
                            "selected": gui.find('**/tart_selected'),
                            "disabled": gui.find('**/tart_disabled')},
                        CIGlobals.BirthdayCake: {"idle": gui.find('**/cake_idle'),
                            "selected": gui.find('**/cake_selected'),
                            "disabled": gui.find('**/cake_disabled')},
                        CIGlobals.CreamPieSlice: {"idle": gui.find('**/slice_idle'),
                            "selected": gui.find('**/slice_selected'),
                            "disabled": gui.find('**/slice_disabled')},
                        CIGlobals.TNT: {"idle": gui.find('**/tnt_idle'),
                            "selected": gui.find('**/tnt_selected'),
                            "disabled": gui.find('**/tnt_idle')}}
        self.guiPos = {"noTnt": [(0, 0, -0.5),
                                (0, 0, 0),
                                (0, 0, 0.5)],
                    "tnt": [(0, 0, -0.15),
                            (0, 0, 0.15),
                            (0, 0, 0.45),
                            (0, 0, -0.45)]}
        self.guiFrame = DirectFrame(parent=base.a2dRightCenter, pos=(-0.2, 0, 0))
        self.gagOrder = [CIGlobals.BirthdayCake, CIGlobals.WholeCreamPie, CIGlobals.CreamPieSlice, CIGlobals.TNT]
        img1 = OnscreenImage(image=gui.find('**/cake_idle'), pos=(0, 0, -0.5), scale=0.3, parent=self.guiFrame)
        img2 = OnscreenImage(image=gui.find('**/tart_selected'), pos=(0, 0, 0.0), scale=0.3, parent=self.guiFrame)
        img3 = OnscreenImage(image=gui.find('**/slice_idle'), pos=(0, 0, 0.5), scale=0.3, parent=self.guiFrame)
        img4 = OnscreenImage(image=gui.find('**/tnt_idle'), pos=(0, 0, -0.75), scale=0.3, parent=self.guiFrame)
        self.ammo_lbl = DirectLabel(text="Ammo: %s" % self.backpack.getSupply(), text_fg=(1,1,1,1), relief=None, text_shadow=(0,0,0,1), text_scale=0.08, pos=(0.2, 0, 0.35), parent=base.a2dBottomLeft)
        self.gui_list = {CIGlobals.BirthdayCake : img1, CIGlobals.WholeCreamPie : img2, CIGlobals.CreamPieSlice : img3, CIGlobals.TNT : img4}
        self.enableWeaponSwitch()
        gui.remove_node()
        self.update()
        del gui

    def deleteGui(self):
        self.disableWeaponSwitch()
        if hasattr(self, 'gui_list'):
            for gui in self.gui_list:
                img = self.gui_list.get(gui)
                img.destroy()
                img = None
            del self.gui_list
        if hasattr(self, 'ammo_lbl'):
            self.ammo_lbl.destroy()
            del self.ammo_lbl

    def enableWeaponSwitch(self):
        if self.backpack.getSupply(CIGlobals.TNT) > 0:
            self.accept("4", self.setWeapon, [CIGlobals.TNT])
        self.accept("3", self.setWeapon, [CIGlobals.BirthdayCake])
        self.accept("2", self.setWeapon, [CIGlobals.WholeCreamPie])
        self.accept("1", self.setWeapon, [CIGlobals.CreamPieSlice])

    def disableWeaponSwitch(self):
        self.ignore("1")
        self.ignore("2")
        self.ignore("3")
        self.ignore("4")
        self.ignore("wheel_up")
        self.ignore("wheel_down")

    def setWeapon(self, weapon, playSound = True):
        if weapon == CIGlobals.TNT and self.backpack.getSupply(weapon) <= 0: return
        if self.backpack.getSupply(weapon) <= 0: return
        self.prevGag = self.weapon
        base.localAvatar.b_equip(GagGlobals.getIDByName(weapon))
        self.weapon = self.backpack.getGagByIndex(self.backpack.getIndex())
        if playSound:
            sfx = base.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.mp3")
            SoundInterval(sfx).start()
        self.resetScroll()
        self.update()

    def resetScroll(self):
        prevGag = 0
        currGag = -1
        if self.weapon:
            currGag = self.gagOrder.index(self.weapon.getName())
        nextGag = 0
        gap = 1
        if self.backpack.getSupply(CIGlobals.TNT) <= 0: gap = 2
        if currGag == (len(self.gagOrder) - gap):
            nextGag = 0
            prevGag = currGag - 1
        elif currGag == 0:
            nextGag = 1
            prevGag = (len(self.gagOrder) - gap)
        elif currGag == -1:
            nextGag = 0
            prevGag = (len(self.gagOrder) - gap)
        else:
            nextGag = currGag + 1
            prevGag = currGag - 1
        self.accept("wheel_down", self.setWeapon, [self.gagOrder[prevGag]])
        self.accept("wheel_up", self.setWeapon, [self.gagOrder[nextGag]])

    def resetGui(self):
        if hasattr(self, 'gui_list') and hasattr(self, 'gui_dict'):
            for gag in self.backpack.getGags():
                gName = gag.getName()
                pos = self.guiPos['tnt']
                tntSupply = self.backpack.getSupply(CIGlobals.TNT)
                if tntSupply <= 0:
                    pos = self.guiPos['noTnt']
                    self.gui_list[CIGlobals.TNT].hide()
                else:
                    self.gui_list[CIGlobals.TNT].show()
                if tntSupply > 0 or gName != CIGlobals.TNT:
                    self.gui_list[gName].setPos(pos[self.gagOrder.index(gName)])

    def update(self):
        self.resetGui()
        if hasattr(self, 'ammo_lbl') and hasattr(self, 'gui_list'):
            if self.backpack.getSupply(self.weapon) == 0:
                self.weapon = None
                self.resetScroll()
            for gag in self.backpack.getGags():
                gName = gag.getName()
                if gag == self.weapon and self.backpack.getSupply(gName) > 0:
                    self.gui_list[gName]['image'] = self.gui_dict[gName]['selected']
                else:
                    if self.backpack.getSupply(gName) <= 0:
                        self.gui_list[gName]['image'] = self.gui_dict[gName]['disabled']
                        if gName == CIGlobals.TNT: self.gui_list[gName].hide()
                    else:
                        self.gui_list[gName]['image'] = self.gui_dict[gName]['idle']
                        if gName == CIGlobals.TNT: self.gui_list[gName].show()
            self.ammo_lbl['text'] = "Ammo: %s" % self.backpack.getSupply()
            if self.weapon and self.backpack.getSupply(self.weapon) > 0:
                self.ammo_lbl['text_fg'] = (1, 1, 1, 1)
            elif not self.weapon:
                self.ammo_lbl['text_fg'] = (0.9, 0, 0, 1)
            if self.backpack.getCurrentGag():
                self.ammo_lbl.show()
            else:
                self.ammo_lbl.hide()
