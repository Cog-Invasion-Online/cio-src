"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BackpackGUI.py
@author Maverick Liberty
@date July 12, 2015

"""

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import DirectFrame, OnscreenImage, OnscreenText, DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval

from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags import GagGlobals

from panda3d.core import TransparencyAttrib, TextNode

import types

class Slot(DirectFrame):
    
    RechargeCompleteCooldown = 0.30

    def __init__(self, baseGui, index, pos, parent):
        DirectFrame.__init__(self, pos = pos, parent = parent, image = loader.loadTexture('phase_3.5/maps/slot_%s_%s.png' % (str(index), 'idle')), scale = 0.15,
            frameSize = (-1, 1, -1, 1), frameColor = (0, 0, 0, 0), sortOrder = 0)
        self.initialiseoptions(Slot)
        self.gui = baseGui
        self.index = index
        self.hoverObj = None
        self.gagImage = None
        self.gag = None
        self.rechargeCompleteTrack = None
        self.mouseRlvrSfx = base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg')
        self.soundRecharged = base.loadSfx('phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.ogg')
        self.switchUnavailableSfx = base.loadSfx("phase_4/audio/sfx/ring_miss.ogg")

        # The recharging text.
        self.infoText = OnscreenText(text = "", fg = (1, 0, 0, 1), parent = self,
                                       scale = 0.5, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, 0.1))
        self.infoText.setBin('unsorted', 100)
        self.infoText.hide()

        # Text in the bottom left corner that shows the gags remaining.
        self.grText = OnscreenText(text = "", fg = (1, 1, 1, 1), parent = self,
                                   scale = 0.4, shadow = (0, 0, 0, 1), align = TextNode.ALeft,
                                   pos = (-0.87, -0.87))

        # The recharging progress bar.
        self.rechargeBar = DirectWaitBar(value = 0, range = 100, frameColor = (1, 1, 1, 1),
                                        barColor = (0.286, 0.901, 1, 1), relief = DGG.RAISED,
                                        borderWidth = (0.04, 0.04), pos = (-1.25, 0, 0),
                                        hpr = (0, 0, -90), parent = self, frameSize = (-0.85, 0.85, -0.12, 0.12))
        self.rechargeBar.setBin('fixed', 60)
        self.rechargeBar.hide()

        # The gag label underneath the gag icon.
        self.gagLabel = OnscreenText(text = "Birthday Cake", fg = (1, 1, 1, 1), parent = self,
                                       scale = 0.25, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, -0.9), mayChange = 1)
        self.gagLabel.setBin('fixed', 50)
        self.gagLabel.hide()

        # The left arrow for moving to the gag before this one in the sequence.
        battleGui = loader.loadModel('phase_3.5/models/gui/battle_gui.bam')
        arrow = battleGui.find('**/PckMn_BackBtn')
        arrowRlvr = battleGui.find('**/PckMn_BackBtn_Rlvr')
        arrowDn = battleGui.find('**/PckMn_BackBtn_Dn')
        self.leftArrow = DirectButton(geom = (arrow, arrowDn, arrowRlvr, arrow),
            parent = self, pos = (-0.925, -2.0, -1.02), relief = None, scale = 2,
            command = self.updateLoadout, extraArgs = [0], geom3_color = (0.5, 0.5, 0.5, 1.0))
        self.leftArrow.setBin('fixed', 60)
        self.rightArrow = DirectButton(geom = (arrow, arrowDn, arrowRlvr, arrow),
            parent = self, pos = (0.925, -2.0, -1.02), hpr = (180, 0, 0), relief = None, scale = 2,
            command = self.updateLoadout, extraArgs = [1], geom3_color = (0.5, 0.5, 0.5, 1.0))
        self.rightArrow.setBin('fixed', 60)

        if base.localAvatar.GTAControls:
            # no arrows in gta controls
            self.leftArrow.hide()
            self.rightArrow.hide()

        self.hoverObj = DirectButton(relief = None, parent = self, frameSize = self['frameSize'])

        self.setBin('gui-popup', 100)
        self.setOutlineImage('idle')
        self.setDepthWrite(False)

        if not base.localAvatar.GTAControls:
            # Let's handle mouse entering and leaving.
            self.hoverObj.guiItem.setActive(True)
            self.hoverObj.bind(DGG.WITHIN, self.mouseEntered)
            self.hoverObj.bind(DGG.WITHOUT, self.mouseExited)
            self.hoverObj.bind(DGG.B1CLICK, self.gui.click_setWeapon, [self])

    def toggleArrows(self, left, right):
        if left:
            self.leftArrow['state'] = DGG.NORMAL
        else:
            self.leftArrow['state'] = DGG.DISABLED

        if right:
            self.rightArrow['state'] = DGG.NORMAL
        else:
            self.rightArrow['state'] = DGG.DISABLED

    def updateArrows(self):
        if not self.gag:
            self.toggleArrows(False, False)
        else:
            track = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.getTrackOfGag(self.gag.getID()))
            index = None

            useTrack = []

            for name in track:
                gag = self.gui.backpack.getGagByID(GagGlobals.getIDByName(name))
                if gag == self.gag or (not gag in self.gui.backpack.getLoadout()):
                    useTrack.append(name)

            index = useTrack.index(self.gag.getName())

            if index == 0:
                self.toggleArrows(False, True)

            elif(index > 0 and index < (len(useTrack) - 1)):
                gagId = GagGlobals.getIDByName(useTrack[index + 1])
                if not self.gui.backpack.hasGag(gagId):
                    self.toggleArrows(True, False)

            elif(index == (len(useTrack) - 1)):
                self.toggleArrows(True, False)

            else:
                self.toggleArrows(True, True)

    def updateLoadout(self, forward):
        if self.gag and self.gag.getState() in [GagState.RECHARGING, GagState.LOADED]:
            track = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.getTrackOfGag(self.gag.getID()))
            index = None

            useTrack = []

            for name in track:
                gag = self.gui.backpack.getGagByID(GagGlobals.getIDByName(name))
                if gag == self.gag or (not gag in self.gui.backpack.getLoadout()):
                    useTrack.append(name)

            index = useTrack.index(self.gag.getName())

            if forward == 1:
                nextGagIndex = index + 1
            else:
                nextGagIndex = index - 1

            if nextGagIndex < 0 or nextGagIndex >= len(useTrack):
                base.playSfx(self.switchUnavailableSfx)
                return

            gagId = GagGlobals.getIDByName(useTrack[nextGagIndex])
            loadout = self.gui.backpack.getLoadout()
            if self.gui.backpack.hasGag(gagId) and self.gag in loadout:
                self.hideInfoText()

                if not self.gag in loadout:
                    return
                
                newGag = self.gui.backpack.getGagByID(gagId)
                loadout[loadout.index(self.gag)] = newGag
                self.gui.backpack.setLoadout(loadout, andResetGui = False)
                
                if self.gui.activeSlot == self and newGag.getState() == GagState.LOADED:
                    self.setGag(newGag)
                    self.gui.update()
                    self.gui.setWeapon(self)

    def makeGrTextRed(self):
        self.grText['fg'] = (1, 0, 0, 1)

    def makeGrTextWhite(self):
        self.grText['fg'] = (1, 1, 1, 1)

    def showNoAmmo(self):
        #self.infoText['text'] = ""
        #self.infoText['scale'] = 0.5
        #self.infoText['fg'] = (1, 0, 0, 1)
        #self.infoText['pos'] = (0, 0.1)
        #self.infoText.show()

        self.grText['fg'] = (1, 0, 0, 1)

        if self.gag and self.gag.getState() == GagState.RECHARGING:
            self.rechargeBar.show()

    def showRecharging(self):
        self.infoText['text'] = "Recharging..."
        self.infoText['scale'] = 0.315
        self.infoText['fg'] = (0.286, 0.901, 1, 1)
        self.infoText['pos'] = (0, 0)
        self.infoText.show()

        self.rechargeBar.show()

    def __tickRecharge(self):
        if not self.gag:
            self.ignoreAll()
        else:
            elapsedTime = float(self.gag.getRechargeElapsedTime())
            totalTime = float(self.gag.getRechargeTime())
            barValue = int(float(elapsedTime / totalTime) * self.rechargeBar['range'])
            self.rechargeBar['value'] = barValue

            if barValue == 0:
                self.showRecharging()
            elif barValue >= 100:
                slotImage = 'idle'
                self.rechargeCompleteTrack = Sequence(Wait(self.RechargeCompleteCooldown), Func(base.playSfx, self.soundRecharged))
                if base.localAvatar.getBackpack().getSupply(self.gag.getID()) <= 0:
                    slotImage = 'no_ammo'
                elif self.gui.getActiveSlot() == self:
                    slotImage = 'selected'
                    self.rechargeCompleteTrack.append(Func(self.gui.setWeapon, self, True))
                self.rechargeCompleteTrack.append(Func(self.setOutlineImage, slotImage))
                self.rechargeCompleteTrack.start()

    def hideInfoText(self):
        self.infoText.hide()
        self.rechargeBar.hide()

    def setSlotImage(self, gagImage):
        if self.gagImage:
            self.gagImage.destroy()
            self.gagImage = None
        self.gagImage = OnscreenImage(image = gagImage, parent = self)
        self.gagImage.setTransparency(TransparencyAttrib.MAlpha)

    def setOutline(self):
        self.setTransparency(TransparencyAttrib.MAlpha)

    def setOutlineImage(self, image):
        phase = 'phase_3.5/maps/'

        if hasattr(self, '_optionInfo'):
            self['image'] = loader.loadTexture(phase + 'slot_%s_%s.png' % (str(self.index), image))
            self.setOutline()

            if image != 'no_ammo':
                if self.gag and base.localAvatar.getBackpack().getSupply(self.gag.getID()) == 0 or self.gag and self.gag.getState() == GagState.RECHARGING:
                    image = 'no_ammo'

            if image == 'no_ammo':
                if self.gag and self.gag.getState() == GagState.RECHARGING:
                    # Show the recharge text.
                    self.showRecharging()
                else:
                    # Show the no ammo text.
                    self.makeGrTextRed()
                    self.rechargeBar.hide()
                # When we have no ammo, render the frame in front of the gag image.
                self.setBin('fixed', 40)

                if self.gagImage:
                    self.gagImage.setBin('transparent', 30)
            else:
                # Hide the no ammo text if we're not out of ammo.
                self.makeGrTextWhite()
                self.hideInfoText()
                # Render the gag image in front of the frame.
                if self.gagImage:
                    self.gagImage.setBin('fixed', 40)
                self.setBin('transparent', 30)

    def getOutline(self):
        return self.outline

    def mouseEntered(self, _):
        if self.gag:
            self.gagLabel.show()
            self.mouseRlvrSfx.play()

    def mouseExited(self, _):
        self.gagLabel.hide()

    def setGag(self, gag):
        if type(gag) == types.IntType:
            gag = self.gui.backpack.getGagByID(gag)
        self.ignoreAll()
        self.gag = gag
        if gag:
            self.show()
            self.setSlotImage(self.gag.getImage())
            self.gagLabel['text'] = self.gag.getName()
            self.accept('%s-Recharge-Tick' % (str(self.gag.getID())), self.__tickRecharge)
        else:
            self.hide()
            self.gagLabel['text'] = ''
        self.updateArrows()

    def getGag(self):
        return self.gag
    
    def destroy(self):
        if self.rechargeCompleteTrack:
            self.rechargeCompleteTrack.finish()
            self.rechargeCompleteTrack = None
        if self.gui:
            self.gui = None
        if self.index:
            self.index = None
        if self.gagImage:
            self.gagImage.destroy()
            self.gagImage = None
        if self.gagLabel:
            self.gagLabel.destroy()
            self.gagLabel = None
        if self.hoverObj:
            self.hoverObj.destroy()
            self.hoverObj = None
        if self.infoText:
            self.infoText.destroy()
        if self.grText:
            self.grText.destroy()
        if self.rechargeBar:
            self.rechargeBar.destroy()
        if self.mouseRlvrSfx:
            self.mouseRlvrSfx = None
        if self.soundRecharged:
            self.soundRecharged = None
        if self.switchUnavailableSfx:
            self.switchUnavailableSfx = None
        del self.gui
        del self.index
        del self.gagImage
        del self.gagLabel
        del self.hoverObj
        del self.infoText
        del self.rechargeBar
        del self.mouseRlvrSfx
        del self.soundRecharged
        del self.switchUnavailableSfx
        del self.rechargeCompleteTrack
        del self.grText
        DirectFrame.destroy(self)

class InventoryGui(DirectObject):
    directNotify = DirectNotify().newCategory('InventoryGui')

    HiddenPos = (0.2, 0, 0)
    VisiblePos = (-0.1725, 0, 0)
    SwitchTime = 0.3
    AutoShowTime = 1.5

    DELETED = False
    Enabled = False

    def __init__(self):
        DirectObject.__init__(self)
        self.backpack = base.localAvatar.backpack

        if not self.backpack:
            return
        self.backpack.loadoutGUI = self

        self.oneSlotPos = [(0, 0, 0)]
        self.twoSlotsPos = [(0, 0, 0.30), (0, 0, -0.2)]
        self.threeSlotsPos = [(0, 0, 0.5), (0, 0, 0), (0, 0, -0.5)]
        self.fourSlotPos = [(0, 0, 0.5), (0, 0, 0.15), (0, 0, -0.2), (0, 0, -0.55)]
        self.availableSlot = 0
        self.slots = []
        self.activeSlot = None
        self.defaultSlots = 3
        self.prevSlot = None

        self.inventoryFrame = DirectFrame(parent = base.a2dRightCenter, pos = (-0.1725, 0, 0))
        self.moveIval = None

        self.switchSound = True
        self.switchSoundSfx = base.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.ogg")
        self.switchUnavailableSfx = base.loadSfx("phase_4/audio/sfx/ring_miss.ogg")

        self.visibilityFSM = ClassicFSM('InventoryGui-VisibilityFSM',
                                        [State('off', self.enterOff, self.exitOff),
                                         State('hidden', self.enterHidden, self.exitHidden),
                                         State('hidden2visible', self.enterHidden2Visible, self.exitHidden2Visible),
                                         State('visible', self.enterVisible, self.exitVisible),
                                         State('visible2hidden', self.enterVisible2Hidden, self.exitVisible2Hidden)],
                                        'off', 'off')
        self.visibilityFSM.setInitialState('hidden')
        self.visibilityFSM.enterInitialState()
        
        # Variables having to do with making the gui remain on the screen.
        self.keepVisibleSfx = base.loadSfx('phase_5/audio/sfx/General_device_appear.ogg')
        self.keepVisibleSfx.setVolume(0.5)
        self.disableKeepVisibleSfx = self.keepVisibleSfx#base.loadSfx('phase_5/audio/sfx/GUI_battleselect.ogg')
        self.slotsVisible = False
        self.slotsForceShown = False
        self.disable(True)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterHidden(self):
        self.inventoryFrame.setPos(InventoryGui.HiddenPos)
        self.inventoryFrame.hide()
        self.slotsVisible = False

    def exitHidden(self):
        pass

    def enterVisible(self, autoShow = False):
        self.inventoryFrame.setPos(InventoryGui.VisiblePos)
        self.inventoryFrame.show()

        if autoShow is False and self.slotsForceShown is False:
            # our mouse is no longer in the visibility button.
            self.visibilityFSM.request('visible2hidden')
        self.slotsVisible = True
        
    def exitVisible(self):
        pass

    def enterHidden2Visible(self, autoShow = False):
        self.inventoryFrame.show()
        self.moveIval = LerpPosInterval(self.inventoryFrame, duration = InventoryGui.SwitchTime,
                                        pos = InventoryGui.VisiblePos, startPos = InventoryGui.HiddenPos)
        self.moveIval.setDoneEvent("hidden2visible")
        self.acceptOnce("hidden2visible", self.visibilityFSM.request, ["visible", [autoShow]])
        self.moveIval.start()
        #base.playSfx(self.keepVisibleSfx)

    def exitHidden2Visible(self):
        self.ignore("hidden2visible")
        
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None

    def enterVisible2Hidden(self):
        if not self.slotsForceShown and self.slotsVisible:
            self.moveIval = LerpPosInterval(self.inventoryFrame, duration = InventoryGui.SwitchTime,
                                            pos = InventoryGui.HiddenPos, startPos = InventoryGui.VisiblePos)
            self.moveIval.setDoneEvent("visible2hidden")
            self.acceptOnce("visible2hidden", self.visibilityFSM.request, ["hidden"])
            self.moveIval.start()

    def exitVisible2Hidden(self):
        self.ignore("visible2hidden")

        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        
    def __toggleForcedVisibility(self):
        if self.slotsForceShown and self.slotsVisible:
            self.slotsForceShown = False
            
            self.__autoVisExit()
            
            # If we want switch sounds, we most likely want all sfx based on this GUI.
            if self.switchSound:
                base.playSfx(self.disableKeepVisibleSfx)
        elif not self.slotsForceShown and not self.slotsVisible:
            self.slotsForceShown = True

            self.__autoVisEnter()
            self.ignore('visible2hidden')
            
            # If we want switch sounds, we most likely want all sfx based on this GUI.
            if self.switchSound:
                base.playSfx(self.keepVisibleSfx)

    def click_setWeapon(self, slot, _):
        self.setWeapon(slot, playSound = False)
        
    def __switchTrackGag(self, forward):
        if self.activeSlot:
            self.activeSlot.updateLoadout(forward)
        
    def __hasSupplyRemaining(self, gag):
        return self.backpack.getSupply(gag) > 0

    def setWeapon(self, slot, playSound = True, showUpIfHidden = False):
        if self.activeSlot and slot != self.activeSlot:
            self.activeSlot.setOutlineImage('idle')
            self.prevSlot = self.activeSlot
        if slot.getGag():
            if self.activeSlot != slot or (self.activeSlot == slot and self.backpack.currentGag != slot.getGag().getID()):
                gagId = slot.getGag().getID()

                base.localAvatar.needsToSwitchToGag = gagId
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_equip(gagId)
                    base.localAvatar.enableGagKeys()
                
                slot.setOutlineImage('selected')
                self.activeSlot = slot
            else:
                base.localAvatar.needsToSwitchToGag = 'unequip'
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_unEquip()
                    base.localAvatar.enableGagKeys()
            if self.switchSound and playSound:
                base.playSfx(self.switchSoundSfx)
        else:
            # If we want the switch sound, we'll assume we want the switch unavailable sound too.
            if self.switchSound:
                base.playSfx(self.switchUnavailableSfx)
        self.update()

        if showUpIfHidden and not self.slotsForceShown:
            base.taskMgr.remove("showUpIfHidden")
            self.__autoVisEnter()
            base.taskMgr.doMethodLater(InventoryGui.AutoShowTime, self.__autoVisExitTask, "showUpIfHidden")

    def __autoVisExitTask(self, task):
        if not self.slotsForceShown:
            self.__handleVisExit(None)
        return task.done

    def __autoVisEnter(self):
        self.__handleVisEnter(None, True)

    def __handleVisEnter(self, _, autoShow = False):
        if self.visibilityFSM.getCurrentState().getName() == 'hidden':
            self.visibilityFSM.request('hidden2visible', [autoShow])
        elif self.visibilityFSM.getCurrentState().getName() == 'visible2hidden':
            self.visibilityFSM.request('visible')
            
    def __autoVisExit(self):
        self.__handleVisExit(None)

    def __handleVisExit(self, _):
        base.taskMgr.remove("showUpIfHidden")
        if self.visibilityFSM.getCurrentState().getName() == 'visible':
            self.visibilityFSM.request('visible2hidden')

    def createGui(self):
        posGroup = self.threeSlotsPos
        if self.defaultSlots == 4:
            posGroup = self.fourSlotPos
        for slot in range(len(posGroup) + 1):
            if slot == 3:
                posGroup = self.fourSlotPos
            slotObj = Slot(self, slot + 1, posGroup[slot], self.inventoryFrame)
            self.slots.append(slotObj)
            if slot == 3:
                slotObj.hide()
        
    def enable(self):
        self.Enabled = True
        self.enableWeaponSwitch()
        self.resetScroll()
        self.updateLoadout()

    def deleteGui(self):
        self.disable(quietly = True)
        for slot in self.slots:
            slot.destroy()
        self.slots = []
        if self.inventoryFrame:
            self.inventoryFrame.destroy()
            self.inventoryFrame = None
        if self.backpack:
            self.backpack = None
        if self.oneSlotPos:
            self.oneSlotPos = None
        if self.twoSlotsPos:
            self.twoSlotsPos = None
        if self.threeSlotsPos:
            self.threeSlotsPos = None
        if self.fourSlotPos:
            self.fourSlotPos = None
        if self.availableSlot:
            self.availableSlot = None
        if self.defaultSlots:
            self.defaultSlots = None
        if self.prevSlot:
            self.prevSlot = None
        if self.switchSound:
            self.switchSound = None
        if self.switchSoundSfx:
            self.switchSoundSfx = None
        if self.switchUnavailableSfx:
            self.switchUnavailableSfx = None
        if self.visibilityFSM:
            self.visibilityFSM = None
        if self.keepVisibleSfx:
            self.keepVisibleSfx = None
        if self.disableKeepVisibleSfx:
            self.disableKeepVisibleSfx = None
        del self.slots
        del self.inventoryFrame
        del self.backpack
        del self.oneSlotPos
        del self.twoSlotsPos
        del self.threeSlotsPos
        del self.fourSlotPos
        del self.availableSlot
        del self.defaultSlots
        del self.prevSlot
        del self.switchSound
        del self.switchSoundSfx
        del self.switchUnavailableSfx
        del self.visibilityFSM
        del self.keepVisibleSfx
        del self.disableKeepVisibleSfx
        self.DELETED = True
        
    def disable(self, quietly = False):
        self.Enabled = False
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.disableWeaponSwitch()
        self.activeSlot = None
        self.slotsForceShown = False
        
        if quietly is False:
            self.__autoVisExit()
        self.slotsVisible = False
        self.ignoreAll()

    def resetScroll(self):
        nextGag = 0
        prevGag = -1
        curGag = -1
        if self.prevSlot:
            prevGag = self.slots.index(self.prevSlot)
        if self.activeSlot:
            curGag = self.slots.index(self.activeSlot)
        if curGag == (len(self.slots) - 1):
            nextGag = 0
            prevGag = curGag - 1
        elif curGag == 0:
            nextGag = 1
            prevGag = (len(self.slots) - 1)
        elif curGag == -1:
            prevGag = (len(self.slots) - 1)
        else:
            nextGag = curGag + 1
            prevGag = curGag - 1
        self.accept('wheel_down', self.setWeapon, extraArgs = [self.slots[nextGag], True, True])
        self.accept('wheel_up', self.setWeapon, extraArgs = [self.slots[prevGag], True, True])

    def update(self):
        if not self.backpack or not self.inventoryFrame:
            return

        updateSlots = list(self.slots)

        for slot in self.slots:
            gag = slot.getGag()
            if not gag:
                updateSlots.remove(slot)
                slot.hide()
                continue

            supply = self.backpack.getSupply(gag.getID())
            index = self.slots.index(slot)

            if not gag and len(self.backpack.getGags()) - 1 >= index:
                gag = self.backpack.getGagByIndex(index)
                slot.setGag(gag)

                if supply > 0 and not gag.getState() == GagState.RECHARGING:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')
                    
                if slot == self.activeSlot:
                    self.activeSlot = None
            else:

                if slot == self.activeSlot:
                    slot.setOutlineImage('selected')
                elif self.__hasSupplyRemaining(slot.getGag().getID()) > 0:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')

                if supply < 1:
                    slot.makeGrTextRed()
                else:
                    slot.makeGrTextWhite()
                slot.grText.setText(str(supply))

        numSlots = len(updateSlots)
        posGroup = {1 : self.oneSlotPos, 2 : self.twoSlotsPos, 3 : self.threeSlotsPos, 4 : self.fourSlotPos}.get(numSlots)

        for i in xrange(len(updateSlots)):
            updateSlots[i].setPos(posGroup[i])
            updateSlots[i].show()
        self.resetScroll()

    def setBackpack(self, backpack):
        self.backpack = backpack

    def updateLoadout(self):
        if self.backpack:
            loadout = self.backpack.getLoadout()
            if len(loadout) <= 3:
                self.reseatSlots()
            elif len(loadout) == 4:
                self.reseatSlots(slots = 4)
            for i in range(len(self.slots)):
                slot = self.slots[i]
                if i < len(loadout):
                    slot.setGag(loadout[i])
                else:
                    slot.setGag(None)
            
            # Let's only update the GUI when it's enabled.
            if self.Enabled:
                self.update()

    def reseatSlots(self, slots = 3):
        for slot in range(len(self.slots) - 1):
            if slots == 4:
                self.slots[slot].setPos(self.fourSlotPos[slot])
            else: self.slots[slot].setPos(self.threeSlotsPos[slot])

    def enableWeaponSwitch(self):
        for index in range(len(self.slots)):
            self.accept(str(index + 1), self.setWeapon, extraArgs = [self.slots[index], True, True])
        self.slotsForceShown = False
        self.slotsVisible = False
        self.accept(base.inputStore.ToggleLoadoutVisibility, self.__toggleForcedVisibility)
        self.accept(base.inputStore.PreviousTrackGag, self.__switchTrackGag, [0])
        self.accept(base.inputStore.NextTrackGag, self.__switchTrackGag, [1])

    def disableWeaponSwitch(self):
        ctrls = base.inputStore
        for key in ['1', '2', '3', '4', 'wheel_down', 'wheel_up', 
                    ctrls.ToggleLoadoutVisibility, 
                    ctrls.PreviousTrackGag, 
                    ctrls.NextTrackGag]:
            self.ignore(key)

    def getSlots(self):
        return self.slots

    def getActiveSlot(self):
        return self.activeSlot

    def isDeleted(self):
        return self.DELETED
