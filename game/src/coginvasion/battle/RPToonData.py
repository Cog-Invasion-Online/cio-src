"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RPToonData.py
@author Maverick Liberty
@date October 14, 2017

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals

from collections import OrderedDict

class Track:
    
    def __init__(self, name, exp, maxExp, increment):
        self.name = name
        self.exp = exp
        self.maxExp = maxExp
        self.increment = increment
        
    def toString(self):
        return '%d/%d' % (self.exp, self.maxExp)

class RPToonData:
    
    def __init__(self, avatarName):
        self.notify = directNotify.newCategory('RPToonData[%s]' % avatarName)
        self.avatarName = avatarName
        self.favoriteGag = CIGlobals.Cupcake

        # All the gag tracks
        self.tracks = OrderedDict()
        
        for track in GagGlobals.TrackNameById.values():
            self.tracks[track] = Track(track, 0, 0, 0)
            print track
    
    def toNetString(self, avDoId):
        dg = PyDatagram()
        dg.addUint32(avDoId)
        dg.addUint8(GagGlobals.gagIds.keys()[GagGlobals.gagIds.values().index(self.favoriteGag)])
        
        for i in range(len(self.tracks)):
            track = self.tracks.values()[i]
            dg.addUint8(i)
            dg.addUint16(track.exp)
            dg.addUint16(track.maxExp)
            dg.addUint16(track.increment)
        dgi = PyDatagramIterator(dg)
        return dgi.getRemainingBytes()
    
    def fromNetString(self, netString):
        self.tracks.clear()
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)
        
        avDoId = dgi.getUint32()
        favGagId = dgi.getUint8()
        
        av = base.cr.doId2do.get(avDoId, None)
        self.avatarName = None if not av else av.getName()
        
        self.favoriteGag = GagGlobals.gagIds.get(favGagId)
        
        while dgi.getRemainingSize() > 0:
            track = GagGlobals.TrackNameById.values()[dgi.getUint8()]
            exp = dgi.getUint16()
            maxExp = dgi.getUint16()
            increment = dgi.getUint16()
            self.tracks[track] = Track(track, increment, exp, maxExp)
        return avDoId
            
    def getTrackByName(self, name):
        return self.tracks[name]
