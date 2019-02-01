"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIProgressScreen.py
@author Brian Lach
@date August 12, 2014

"""

from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import OnscreenImage, DirectWaitBar, DirectLabel, DirectFrame, OnscreenText
from panda3d.core import TextNode

from src.coginvasion.globals import CIGlobals
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.hood import ZoneUtil

import random

notify = DirectNotify().newCategory("CIProgressScreen")

class CIProgressScreen:

    Color = (118 / 255.0, 121 / 255.0, 127 / 255.0, 1.0)
    BarColor = (152 / 255.0, 129 / 255.0, 64 / 255.0, 1.0)

    def __init__(self):
        self.defaultLogoScale = 1
        self.defaultLogoZ = 0.65
        self.bgm = loader.loadModel("phase_3/models/gui/progress-background.bam")
        self.bgm.find('**/logo').stash()
        self.barShadow = OnscreenImage(image = self.bgm.find("**/bar_shadow"), parent = hidden)
        self.bgm.find("**/bar_shadow").removeNode()
        self.bg = self.bgm.find('**/bg')
        self.defaultBgTexture = self.bg.findTexture('*')
        
        self.logoNode, self.logoImg = CIGlobals.getLogoImage(hidden, self.defaultLogoScale, (0, 0, self.defaultLogoZ))
        
        self.bg_img = OnscreenImage(image=self.bg, parent=hidden)
        self.bg_img.setSx(1.35)
        self.bg_img.hide()
        self.progress_bar = DirectWaitBar(value=0, pos=(0, 0, -0.85), parent=hidden, text_pos = (0, 0, 0.2))
        self.progress_bar.setSx(1.064)
        self.progress_bar.setSz(0.38)
        toontipgui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        poster = toontipgui.find('**/questCard')
        self.toontipFrame = DirectFrame(image = poster, image_scale = (1.4, 1, 1), parent = hidden, relief = None, pos = (0, 0, -0.1), scale = 0.85)
        self.toontipLbl = OnscreenText(text = "", parent = self.toontipFrame, fg = (89.0 / 255, 95.0 / 255, 98.0 / 255, 1),
            font = CIGlobals.getToonFont(), wordwrap = 13, pos = (-0.59, 0.25), align = TextNode.ALeft, scale = 0.08)
        self.loading_lbl = DirectLabel(text="",
                                    relief=None,
                                    scale=0.08,
                                    pos=(-1.0725, 0, -0.79),
                                    text_align=TextNode.ALeft,
                                    sortOrder=100,
                                    text_fg=(1, 1, 1, 1), text_font = CIGlobals.getMinnieLogoFont(), parent=hidden,
                                    text_shadow=(0, 0, 0, 0))
        
        # This is useful when the user has chosen to hide aspect2d before the loading screen.
        # However, we want to show the loading screen all the time, so we need to restore the
        # previous state after the loading screen ends.
        self.mustRestoreHiddenAspect2d = False

    def begin(self, hood, range, wantGui):
        render.hide()
        NametagGlobals.setWant2dNametags(False)
        
        if base.aspect2d.isHidden():
            base.aspect2d.show()
            self.mustRestoreHiddenAspect2d = True
        
        self.renderFrames()
        base.setBackgroundColor(0, 0, 0)
        if hood == "localAvatarEnterGame":
            self.loading_lbl['text'] = "Entering..."
        elif hood == "init":
            self.loading_lbl['text'] = "Loading..."
        else:
            self.loading_lbl['text'] = "Heading to %s..." % hood
        self.progress_bar['barColor'] = self.BarColor
        self.progress_bar['range'] = range
        self.bgm.reparentTo(aspect2d)
        
        self.bg.ls()
        
        ZoneUtil.Hood2ZoneId.keys()
        
        # We only want to show special loading screens for actual in-game locations.
        if hood in ZoneUtil.Hood2ZoneId.keys():
            abbr = ZoneUtil.ZoneId2HoodAbbr.get(ZoneUtil.Hood2ZoneId.get(hood)).lower()
            bgTexture = loader.loadTexture('phase_14/maps/{0}_loading.png'.format(abbr), okMissing=True)
            
            if bgTexture:
                self.bg.setTexture(bgTexture, 1)

        self.barShadow.reparentTo(aspect2d)
        self.bg.reparentTo(render2d)
        self.bg_img.reparentTo(hidden)
        self.loading_lbl.reparentTo(aspect2d)
        self.logoNode.reparentTo(aspect2d)
        self.progress_bar.reparentTo(aspect2d)
        tip = random.choice(CIGlobals.ToonTips)
        self.toontipLbl.setText("TOON TIP:\n" + tip)
        self.toontipFrame.reparentTo(aspect2d)
        self.__count = 0
        self.__expectedCount = range
        self.progress_bar.update(self.__count)

    def renderFramesTask(self, task):
        self.renderFrames()
        return task.cont

    def end(self):
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        taskMgr.remove("renderFrames")
        render.show()
        
        if self.mustRestoreHiddenAspect2d:
            base.aspect2d.hide()
            self.mustRestoreHiddenAspect2d = False
        
        self.progress_bar.finish()
        self.bg_img.reparentTo(hidden)
        self.logoNode.reparentTo(hidden)
        self.barShadow.reparentTo(hidden)
        self.bg.reparentTo(hidden)
        
        # Let's get rid of the extra texture stage.
        self.bg.setTexture(self.defaultBgTexture, 1)
        
        self.bgm.reparentTo(hidden)
        self.loading_lbl.reparentTo(hidden)
        self.progress_bar.reparentTo(hidden)
        self.toontipFrame.reparentTo(hidden)
        base.transitions.fadeScreen(1.0)
        NametagGlobals.setWant2dNametags(True)
        self.renderFrames()

    def destroy(self):
        self.bg.removeNode()
        del self.bg
        self.bgm.removeNode()
        del self.bgm
        self.bg_img.destroy()
        self.barShadow.destroy()
        del self.barShadow
        self.loading_lbl.destroy()
        self.progress_bar.destroy()
        self.bgm.destroy()
        self.mustRestoreHiddenAspect2d = False
        del self.bg_img
        del self.loading_lbl
        del self.progress_bar
        del self.bgm
        del self.defaultBgTexture
        del self.mustRestoreHiddenAspect2d

    def renderFrames(self):
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

    def tick(self):
        self.__count += 1
        self.progress_bar.update(self.__count)
