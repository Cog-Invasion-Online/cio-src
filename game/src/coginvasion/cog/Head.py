"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Head.py
@author Maverick Liberty
@date July 31, 2015

"""

from src.coginvasion.cog.SuitType import SuitType
from direct.actor.Actor import Actor

from panda3d.core import Texture

class Head:

    # The 'suit' variable should only be set if we are working with a
    # normal COG. Setting 'suit' to None will make this load what
    # the 'head' variable is set to.

    def __init__(self, suit, head, headTex = None, headColor = None, headAnims = None):
        self.suit = suit
        self.head = head
        self.headTex = headTex
        self.headColor = headColor
        self.headMdl = None
        self.headAnims = headAnims

    def generate(self):
        if self.suit:
            phase = 4
            if self.suit == SuitType.C:
                phase = 3.5
            heads = loader.loadModel('phase_%s/models/char/suit%s-heads.bam' % (str(phase), self.suit))
            self.headMdl = heads.find('**/%s' % (self.head))
            
            if self.head == 'flunky' and self.headTex is None:
                glasses = heads.find('**/glasses')
                glasses.reparentTo(self.headMdl)
                glasses.setTwoSided(True)
            heads.removeNode()
        else:
            if not self.headAnims:
                self.headMdl = loader.loadModel(self.head)
            else:
                self.headMdl = Actor(self.head)
                self.headMdl.loadAnims(self.headAnims)
        if self.headTex:
            headTex = loader.loadTexture(self.headTex)
            headTex.setMinfilter(Texture.FTLinearMipmapLinear)
            headTex.setMagfilter(Texture.FTLinear)
            self.headMdl.setTexture(headTex, 1)
        if self.headColor:
            self.headMdl.setColor(self.headColor)
        return self.headMdl

    def get(self):
        return self.headMdl

    def cleanup(self):
        if self.headMdl:
            self.headMdl.removeNode()
            del self.headMdl
        del self.suit
        del self.headTex
        del self.headColor
        del self.head
