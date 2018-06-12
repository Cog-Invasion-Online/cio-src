"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BirthdayCake.py
@author Maverick Liberty
@date July 07, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class BirthdayCake(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.BirthdayCake, "phase_5/models/props/birthday-cake-mod.bam", 75, GagGlobals.WHOLE_PIE_SPLAT_SFX, GagGlobals.CAKE_SPLAT_COLOR, anim = "phase_5/models/props/birthday-cake-chan.bam")
        self.setHealth(GagGlobals.BDCAKE_HEAL)
        self.setImage('phase_3.5/maps/cake.png')

    def equip(self):
        ThrowGag.equip(self)
        if self.isLocal():
            vmGag = base.localAvatar.getFPSCam().vmGag
            if vmGag:
                # The birthday cake on the viewmodel covers up way too much of the screen.
                # scale it down
                vmGag.setScale(vmGag.getScale() * 0.8)
