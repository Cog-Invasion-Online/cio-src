"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file StandaloneToon.py
@author Brian Lach
@date May 02, 2015

"""

import Standalone

from src.coginvasion.toon import LocalToon
from src.coginvasion.login.AvChoice import AvChoice

base.minigame = None
base.cr.localAvChoice = AvChoice("00/01/05/19/01/19/01/19/13/05/27/27/00", "Dog", 0, 0, 0)#"00/08/00/10/01/12/01/10/13/05/27/27/00", "Ducky", 0, 0)
base.musicManager.setVolume(0.65)

if False:
    dclass = base.cr.dclassesByName['DistributedPlayerToon']
    base.localAvatar = LocalToon.LocalToon(base.cr)
    base.localAvatar.dclass = dclass
    base.localAvatar.doId = base.cr.localAvChoice.getAvId()
    base.localAvatar.maxHealth = 50
    base.localAvatar.health = 50
    base.localAvatar.generate()
    base.localAvatar.setName(base.cr.localAvChoice.getName())
    base.localAvatar.setDNAStrand(base.cr.localAvChoice.getDNA())
    base.localAvatar.setBackpackAmmo("")
    base.localAvatar.announceGenerate()
    base.localAvatar.reparentTo(base.render)
    base.localAvatar.enableAvatarControls()

    if base.localAvatar.GTAControls:
        from src.coginvasion.toon.TPMouseMovement import TPMouseMovement
        mov = TPMouseMovement()
        mov.initialize()
