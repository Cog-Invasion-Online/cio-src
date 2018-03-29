"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TooltipManager.py
@author Brian Lach
@date March 10, 2018

"""

from panda3d.core import Datagram, DatagramIterator

class TooltipManager:

    Tips = []

    def __init__(self):
        self.seenTips = []

    def cleanup(self):
        self.seenTips = None

    def maybeShowTip(self, tipId):
        if not tipId in self.seenTips:
            # Show the tip
            tip = TooltipManager.Tips[tipId]()
            self.seenTips.append(tipId)

    def fromNetString(self, data):
        self.seenTips = []

        dg = Datagram(data)
        dgi = DatagramIterator(dg)
        # up to 255 tips
        numTips = dgi.getUint8()
        for i in xrange(numTips):
            tipId = dgi.getUint8()
            self.seenTips.append(tipId)

    def toNetString(self):
        dg = Datagram()
        dg.addUint8(len(self.seenTips))
        for tipId in self.seenTips:
            dg.addUint8(tipId)
        dgi = DatagramIterator(dg)
        return dgi.getRemainingBytes()