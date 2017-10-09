"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FriendRequest.py
@author Brian Lach
@date August 04, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectButton

from src.coginvasion.toon import ToonDNA

class FriendRequest(DirectFrame):
    notify = directNotify.newCategory('FriendRequest')

    def __init__(self, name, dnaStrand):
        DirectFrame.__init__(self)
        dna = ToonDNA.ToonDNA()
        dna.setDNAStrand(dnaStrand)
