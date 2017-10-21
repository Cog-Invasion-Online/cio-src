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
    
    def __init__(self, avatar):
        self.avatar = avatar
        self.avatarName = None if not self.avatar else avatar.getName()
        self.notify = directNotify.newCategory('RPToonData[%s]' % self.avatarName if self.avatarName else 'Undefined')
        self.favoriteGag = CIGlobals.Cupcake

        # All the gag tracks
        self.tracks = OrderedDict()
        
        if not self.avatar:
            for track in GagGlobals.TrackNameById.values():
                self.tracks[track] = Track(track, 0, 0, 0)
        else:
            for track, exp in self.avatar.trackExperience.iteritems():
                self.tracks[track] = Track(track, exp, GagGlobals.getMaxExperienceValue(exp, track), 0)
    
    def toNetString(self, avDoId):
        dg = PyDatagram()
        dg.addUint32(avDoId)
        dg.addUint8(GagGlobals.gagIds.keys()[GagGlobals.gagIds.values().index(self.favoriteGag)])
        
        for trackName in self.tracks.keys():
            track = self.getTrackByName(trackName)
            dg.addUint8(GagGlobals.TrackNameById.keys()[GagGlobals.TrackNameById.values().index(trackName)])
            dg.addInt16(track.exp)
            dg.addInt16(track.maxExp)
            dg.addUint16(track.increment)
        dgi = PyDatagramIterator(dg)
        return dgi.getRemainingBytes()
    
    def fromNetString(self, netString):
        self.tracks.clear()
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)
        
        avDoId = dgi.getUint32()
        favGagId = dgi.getUint8()
        
        self.avatar = base.cr.doId2do.get(avDoId, None)
        self.avatarName = None if not self.avatar else self.avatar.getName()
        
        self.favoriteGag = GagGlobals.gagIds.get(favGagId)
        
        while dgi.getRemainingSize() > 0:
            track = GagGlobals.TrackNameById.get(dgi.getUint8())
            exp = dgi.getInt16()
            maxExp = dgi.getInt16()
            increment = dgi.getInt16()
            self.tracks[track] = Track(track, exp, maxExp, increment)
        return avDoId
            
    def getTrackByName(self, name):
        return self.tracks[name]
