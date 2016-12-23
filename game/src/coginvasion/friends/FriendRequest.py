# Filename: FriendRequest.py
# Created by:  blach (04Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectButton

from src.coginvasion.toon import ToonDNA

class FriendRequest(DirectFrame):
    notify = directNotify.newCategory('FriendRequest')

    def __init__(self, name, dnaStrand):
        DirectFrame.__init__(self)
        dna = ToonDNA.ToonDNA()
        dna.setDNAStrand(dnaStrand)
