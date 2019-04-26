"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagSelectionGui.py
@author Brian Lach
@date June 13, 2018

@desc Amazing gag gui created by fatigue/baru/baja/taijitu.

"""

from panda3d.core import TransparencyAttrib, Vec3, TextNode

from direct.showutil import Effects
from direct.gui.DirectGui import DirectFrame, DirectButton, OnscreenImage, OnscreenText, OnscreenGeom, DGG
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, LerpScaleInterval
from direct.fsm.FSM import FSM

from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

FRAME_OFFSET = 0.04
FRAME_SORT_BEGIN = 100
FRAME_SORT_DISTANCE = 50
FRAME_FRONT_SORT = 500

GAG_BTN_OFFSET = 0.23
GAG_BTN_START = -0.53

class GagWidget(DirectButton):

    Idle = (0, 115 / 255.0, 194 / 255.0, 1)
    Selected = (0, 115 / 255.0 * 1.5, 194 / 255.0 * 1.5, 1)
    
    NoAmmoIdle = (0, 115 / 255.0 / 1.75, 194 / 255.0 / 1.75, 1)
    NoAmmoSelected = (0, 115 / 255.0 / 1.75, 194 / 255.0 / 1.75, 1)

    LockedIdle = (0.5, 0.5, 0.5, 1.0)
    LockedSelected = (0.5, 0.5, 0.5, 1.0)

    def __init__(self, track, gagId):
        self.track = track
        self.gagId = gagId
        self.gagName = base.cr.attackMgr.getAttackName(gagId)

        self.lastScale = 1.0
        self.goalScale = 1.0
        self.scaleLerpTask = taskMgr.add(self.__scaleLerp, "scaleLerp")

        self.locked = False

        DirectButton.__init__(self, scale = 1, relief = None, pressEffect = False,
                              rolloverSound = None, clickSound = None,
                              command = self.track.gsg.selectCurrentGag)
        self['image'] = 'phase_14/maps/gag_box.png'
        self['image_scale'] = (0.115, 0, 0.114)
        self.bind(DGG.ENTER, self.mouseEnter)
        self.bind(DGG.EXIT, self.mouseExit)

        self.lockedImg = OnscreenImage(image = 'phase_14/maps/lock.png', scale = (0.061, 0, 0.089),
                                       parent = self, color = (1, 1, 1, 0.5))

        invIcons = loader.loadModel("phase_3.5/models/gui/inventory_icons.bam")
        self.gagImg = OnscreenGeom(geom = invIcons.find(GagGlobals.InventoryIconByName[self.gagName]),
                                   scale = 0.85, parent = self)
        invIcons.removeNode()
        del invIcons

        self.initialiseoptions(GagWidget)

    def mouseEnter(self, foo = None, bar = None):
        if self.track.gsg.getCurrentOrNextState() == 'Select':
            self.track.gsg.ignoreSelectionClick()
        self.track.gsg.resetTimeout()
        self.select()

    def mouseExit(self, foo = None, bar = None):
        if self.track.gsg.getCurrentOrNextState() == 'Select':
            self.track.gsg.acceptSelectionClick()
        self.track.gsg.resetTimeout()
        self.deselect()

    def cleanup(self):
        if self.scaleLerpTask:
            self.scaleLerpTask.remove()
            self.scaleLerpTask = None

        self.lastScale = None
        self.goalScale = None
        self.locked = None
        self.gagId = None
        self.gagName = None
        
        if self.lockedImg:
            self.lockedImg.destroy()
            self.lockedImg = None
        if self.gagImg:
            self.gagImg.destroy()
            self.gagImg = None

        self.destroy()

    def __scaleLerp(self, task):
        if self.lastScale == self.goalScale:
            return task.cont

        self.lastScale = CIGlobals.lerpWithRatio(self.goalScale, self.lastScale, 0.8)
        self.setScale(self.lastScale)

        return task.cont

    def stash(self):
        self.scaleLerpTask.remove()
        DirectButton.stash(self)

    def unstash(self):
        taskMgr.add(self.scaleLerpTask)
        DirectButton.unstash(self)

    def select(self):
        if self.locked:
            self['image_color'] = self.LockedSelected
        elif not self.hasAmmo():
            self['image_color'] = self.NoAmmoSelected
        else:
            self['image_color'] = self.Selected

        self.goalScale = 1.15

        if self.track.gsg.currentGag != self:
            if self.track.gsg.currentGag is not None:
                self.track.gsg.currentGag.deselect()
            self.track.gsg.currentGag = self
            self.track.gsg.update()
            
    def hasAmmo(self):
        if not base.localAvatar.hasAttackId(self.gagId):
            return False
            
        return base.localAvatar.getAttack(self.gagId).hasAmmo()

    def deselect(self):
        if self.locked:
            self['image_color'] = self.LockedIdle
        elif not self.hasAmmo():
            self['image_color'] = self.NoAmmoIdle
        else:
            self['image_color'] = self.Idle
        self.goalScale = 1.0

        if self.track.gsg.currentGag == self:
            self.track.gsg.currentGag = None

    def setLocked(self, flag):
        self.locked = flag
        if flag:
            self.lockedImg.show()
            self.gagImg.hide()
            self['image_color'] = self.LockedIdle
            self['state'] = DGG.DISABLED
        else:
            self.lockedImg.hide()
            self.gagImg.show()
            self['image_color'] = self.Idle
            self['state'] = DGG.NORMAL

class GagTrack(DirectFrame):

    def __init__(self, gsg, trackId):
        DirectFrame.__init__(self)
        self.gsg = gsg
        self.trackId = trackId
        self.trackName = GagGlobals.TrackNameById[trackId]
        self['image'] = 'phase_14/maps/track_bar.png'
        self['image_scale'] = (1.119, 0, 0.152)
        self['relief'] = None
        color = GagGlobals.TrackColorByName[self.trackName]
        self['image_color'] = (color[0], color[1], color[2], 1)

        self.trackText = OnscreenText(text = self.trackName.upper(), fg = (0, 0, 0, 0.65), shadow = (0, 0, 0, 0),
                                      pos = (-0.825, -0.022), scale = 0.12 * (3.0/4.0), align = TextNode.ACenter, parent = self)
        self.gagBtns = []

        self.currentGag = 0

    def cleanup(self):
        self.gsg = None
        self.trackId = None
        self.trackName = None
        self.currentGag = None
        if self.trackText:
            self.trackText.destroy()
            self.trackText = None

        if self.gagBtns:
            for btn in self.gagBtns:
                btn.cleanup()
        self.gagBtns = None

        self.destroy()

    def deselectAll(self):
        for btn in self.gagBtns:
            btn.deselect()

    def isOnLastGag(self):
        return self.currentGag == len(self.gagBtns) - 1 or not self.gagBtns

    def isOnFirstGag(self):
        return self.currentGag == 0 or not self.gagBtns

    def selectNextGag(self):
        newIdx = self.currentGag + 1
        if newIdx > len(self.gagBtns) - 1:
            newIdx = 0
        self.selectGag(newIdx)

    def selectPrevGag(self):
        newIdx = self.currentGag - 1
        if newIdx < 0:
            newIdx = len(self.gagBtns) - 1
        self.selectGag(newIdx)

    def selectGag(self, idx):
        self.deselectAll()

        if self.gagBtns:
            self.currentGag = idx
            self.gagBtns[self.currentGag].select()

    def selectFirstGag(self):
        self.selectGag(0)

    def selectLastGag(self):
        self.selectGag(len(self.gagBtns) - 1)

    def stashContents(self):
        self.trackText.stash()
        for btn in self.gagBtns:
            btn.deselect()
            btn.stash()
        self.currentGag = 0

    def unstashContents(self):
        self.trackText.unstash()
        for btn in self.gagBtns:
            btn.unstash()

    def load(self):
        gags = GagGlobals.TrackGagNamesByTrackName[self.trackName]
        for i in xrange(len(gags)):
            gagName = gags[i]
            gagId = base.cr.attackMgr.getAttackIDByName(gagName)
            btn = GagWidget(self, gagId)
            btn.reparentTo(self)
            btn.setX(GAG_BTN_START + (GAG_BTN_OFFSET * i))
            if not base.localAvatar.hasAttackId(gagId) or gagName not in GagGlobals.tempAllowedGags:
                btn.setLocked(True)
            else:
                btn.setLocked(False)
            self.gagBtns.append(btn)
        self.stashContents()

class GagSelectionGui(DirectFrame, FSM):
    InactivityTime = 5.0

    AmmoZSelect = -0.15
    AmmoZIdle = 0.035

    def __init__(self):
        DirectFrame.__init__(self, parent = aspect2d, pos = (0, 0, 0.93), scale = 0.7)
        FSM.__init__(self, 'GagSelectionGui')
        self.setTransparency(TransparencyAttrib.MDual)
        self.tracks = []
        self.currentTrack = 0
        self.currentGag = None
        self.fwdShakeIval = None
        self.revShakeIval = None
        self.newTrackSound = None
        self.keyScrollSound = None
        self.selectSound = None
        self.selectDenySound = None
        self.lastActivityTime = 0.0
        self.activityTask = None
        self.midpoint = 0.0

        self.ammoFrame = DirectFrame(parent = self, pos = (0, 0, -0.2), image = 'phase_14/maps/status_bar.png',
                                     image_scale = (0.461 * 0.7, 0, 0.098), relief = None)
        self.ammoFrame.hide()
        self.ammoTitle = OnscreenText(parent = self.ammoFrame, text = 'SUPPLY', fg = (0, 0, 0, 0.65), align = TextNode.ALeft,
                                      pos = (-0.37 * 0.7, -0.015, 0))
        self.ammoText = OnscreenText(parent = self.ammoFrame, text = '', fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1),
                                     align = TextNode.ARight, pos = (0.37 * 0.7, -0.015, 0))

    def update(self):
        plyr = base.localAvatar
        
        if not base.localAvatar.hasAttacks():
            return
        
        gagId = -1
        if self.getCurrentOrNextState() == 'Idle':
            gagId = plyr.getEquippedAttack()
        elif self.getCurrentOrNextState() == 'Select' and self.currentGag:
            gagId = self.currentGag.gagId
        
        if gagId != -1:
            self.ammoFrame.showThrough()
            if plyr.hasAttackId(gagId):
                self.ammoText.setText('%i/%i' % (plyr.getAttackAmmo(gagId), plyr.getAttackMaxAmmo(gagId)))
            else:
                self.ammoText.setText('')
            col = GagGlobals.TrackColorByName[GagGlobals.getTrackOfGag(gagId)]
            self.ammoFrame['image_color'] = (col[0], col[1], col[2], 1.0)
        else:
            self.ammoFrame.hide()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def hide(self):
        showAmmo = False
        if not self.ammoFrame.isHidden():
            showAmmo = True
        DirectFrame.hide(self)
        if showAmmo:
            self.ammoFrame.showThrough()

    def enterSelect(self):
        base.localAvatar.disableGagKeys()
        self.ammoFrame.setZ(self.AmmoZSelect)
        self.show()
        self.update()
        self.acceptSelectionClick()
        self.resetTimeout()
        self.activityTask = taskMgr.add(self.__activityTask, "activityTask")

    def acceptSelectionClick(self):
        self.accept('mouse1-up', self.selectCurrentGag)

    def ignoreSelectionClick(self):
        self.ignore('mouse1-up')

    def resetTimeout(self):
        self.lastActivityTime = globalClock.getFrameTime()

    def __activityTask(self, task):
        time = globalClock.getFrameTime()
        if time - self.lastActivityTime >= self.InactivityTime:
            self.request('Idle')
            return task.done
        return task.cont

    def exitSelect(self):
        self.activityTask.remove()
        self.activityTask = None
        self.hide()
        self.ignoreSelectionClick()

    def enterIdle(self):
        self.ammoFrame.setZ(self.AmmoZIdle)
        self.hide()
        self.update()
        if base.localAvatar.avatarMovementEnabled:
            base.localAvatar.enableGagKeys()

    def exitIdle(self):
        pass

    def disable(self):
        self.disableControls()
        self.hide()

    def enable(self):
        self.enableControls()
        self.show()

    def cleanup(self):
        self.request('Off')

        self.disableControls()
        
        self.newTrackSound = None
        self.keyScrollSound = None
        self.selectSound = None
        self.selectDenySound = None

        if self.fwdShakeIval:
            self.fwdShakeIval.finish()
            self.fwdShakeIval = None
        if self.revShakeIval:
            self.revShakeIval.finish()
            self.revShakeIval = None
        self.currentTrack = None
        self.currentGag = None
        if self.tracks:
            for track in self.tracks:
                track.cleanup()
        self.tracks = None

        self.destroy()

    def __accumulateTracks(self):
        tracks = []
        for gagId in base.localAvatar.attacks.keys():
            trackId = GagGlobals.getTrackOfGag(gagId, getId = True)
            if trackId not in tracks:
                tracks.append(trackId)
        tracks.sort()
        return tracks

    def load(self):
        tracks = self.__accumulateTracks()
        for i in xrange(len(tracks)):
            track = GagTrack(self, tracks[i])
            track.load()
            track.reparentTo(self)
            track.setX(FRAME_OFFSET * i)
            self.tracks.append(track)

        self.midpoint = (len(self.tracks) / 2.0) * -FRAME_OFFSET
        # Center the gui horizontally
        self.setX(self.midpoint)
        self.ammoFrame.setX(-self.midpoint)

        if base.config.GetBool('gsg-want-hlsounds', False):
            self.newTrackSound = base.loadSfx("phase_14/audio/sfx/wpn_hudon.ogg")
            self.keyScrollSound = base.loadSfx('phase_14/audio/sfx/wpn_moveselect.ogg')
            self.selectSound = base.loadSfx('phase_14/audio/sfx/wpn_select.ogg')
            self.selectDenySound = base.loadSfx('phase_14/audio/sfx/wpn_denyselect.ogg')
        else:
            self.newTrackSound = base.loadSfx("phase_3/audio/sfx/GUI_create_toon_back.ogg")
            self.keyScrollSound = base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg')
            self.selectSound = base.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg')
            self.selectDenySound = base.loadSfx('phase_4/audio/sfx/ring_miss.ogg')

        self.fwdShakeIval = Effects.createXBounce(self, 1, Vec3(self.midpoint, 0, 0.93), 0.05, 0.05)
        self.revShakeIval = Effects.createXBounce(self, 1, Vec3(self.midpoint, 0, 0.93), 0.05, -0.05)
        
        if base.localAvatar.hasAttacks():
            self.updateCurrentTrack(0)

    def enableControls(self):
        self.accept('wheel_up', self.__handleScrollUp)
        self.accept('wheel_down', self.__handleScrollDown)

        for i in xrange(len(self.tracks)):
            self.accept(str(i + 1), self.__handleTrackChoose, [i])

        self.request('Idle')

    def selectCurrentGag(self):
        selected = False

        self.newTrackSound.stop()
        self.keyScrollSound.stop()
        
        if self.currentGag is not None:
            if base.localAvatar.getEquippedAttack() == self.currentGag.gagId:
                selected = True
            elif (not self.currentGag.locked and self.currentGag.hasAmmo()):
                gagId = self.currentGag.gagId
                base.localAvatar.needsToSwitchToGag = gagId
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.selectGag(gagId)
                    selected = True
                    
        if not selected:
            # Denied!
            self.selectDenySound.play()
            self.resetTimeout()
        else:
            self.selectSound.play()
            self.request('Idle')

    def disableControls(self):
        self.ignore('wheel_up')
        self.ignore('wheel_down')

        for i in xrange(len(self.tracks)):
            self.ignore(str(i + 1))

        self.request('Idle')

    def __maybeDoSelect(self):
        if self.getCurrentOrNextState() == 'Idle':
            self.request('Select')

    def __handleTrackChoose(self, idx):
        if not base.localAvatar.hasAttacks():
            return
            
        self.__maybeDoSelect()
        self.resetTimeout()

        if self.currentTrack == idx:
            # Scroll through the current track.
            self.tracks[self.currentTrack].selectNextGag()

            self.newTrackSound.stop()
            self.keyScrollSound.play()
        else:
            # Always start from the beginning when using the keys to choose a track.
            self.updateCurrentTrack(idx, 0)
            self.newTrackSound.play()

    def __handleScrollUp(self):
        if not base.localAvatar.hasAttacks():
            return
            
        self.__maybeDoSelect()
        self.resetTimeout()

        track = self.tracks[self.currentTrack]
        if track.isOnFirstGag():
            self.prevTrack()
        else:
            track.selectPrevGag()

        self.newTrackSound.stop()
        self.keyScrollSound.play()

    def __handleScrollDown(self):
        if not base.localAvatar.hasAttacks():
            return
            
        self.__maybeDoSelect()
        self.resetTimeout()

        track = self.tracks[self.currentTrack]
        if track.isOnLastGag():
            self.nextTrack()
        else:
            track.selectNextGag()

        self.newTrackSound.stop()
        self.keyScrollSound.play()

    def nextTrack(self):
        newIdx = self.currentTrack + 1
        if newIdx > len(self.tracks) - 1:
            newIdx = 0

        self.updateCurrentTrack(newIdx)

    def prevTrack(self):
        newIdx = self.currentTrack - 1
        if newIdx < 0:
            newIdx = len(self.tracks) - 1

        self.updateCurrentTrack(newIdx)

    def updateCurrentTrack(self, idx, startLoc = None):
        oldTrack = self.tracks[self.currentTrack]
        oldTrack.deselectAll()
        oldTrack.stashContents()

        if idx - self.currentTrack < 0:
            direction = 1
        else:
            direction = 0

        if startLoc is None:
            startLoc = direction

        if direction == 0:
            self.fwdShakeIval.start()
        else:
            self.revShakeIval.start()

        self.currentTrack = idx

        # Resort the tracks
        numTracks = len(self.tracks)
        maxTrack = numTracks - 1
        for i in xrange(len(self.tracks)):
            track = self.tracks[i]

            if i == idx:
                sort = FRAME_FRONT_SORT
            elif i > idx:
                sort = FRAME_SORT_BEGIN + (maxTrack - i) * FRAME_SORT_DISTANCE
            elif i < idx:
                sort = FRAME_SORT_BEGIN + (i * FRAME_SORT_DISTANCE)
            track.setBin('gsg-popup', sort)

            if i == idx:
                track.unstashContents()
                if startLoc == 0:
                    track.selectFirstGag()
                else:
                    track.selectLastGag()
            else:
                track.stashContents()
