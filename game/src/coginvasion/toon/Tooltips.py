"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Tooltips.py
@author Brian Lach
@date March 10, 2018

"""

from src.coginvasion.toon.ChatBalloon import ChatBalloon
from src.coginvasion.nametag import NametagGlobals

class Tooltip(ChatBalloon):

    def __init__(self):
        ChatBalloon.__init__(self, NametagGlobals.chatBalloon3dModel, NametagGlobals.chatBalloon3dWidth,
                             NametagGlobals.chatBalloon3dHeight, )
