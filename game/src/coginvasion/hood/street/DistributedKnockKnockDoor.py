"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedKnockKnockDoor.py
@author Maverick Liberty
@date October 22, 2017

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify

from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.hood.street import KnockKnockGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.ToonTalker import ToonTalker
from src.coginvasion.nametag.NametagGroup import NametagGroup
from src.coginvasion.nametag import NametagGlobals
import random

class DistributedKnockKnockDoor(DistributedObject, ToonTalker):
    notify = directNotify.newCategory('DistributedKnockKnockDoor')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        ToonTalker.__init__(self)
        self.zoneId = -1
        self.block = -1
        self.avatarType = CIGlobals.Toon
        self.realJokeNetworkTime = None
        self.collisionNode = None
        self.physDoor = None
        self.nametag = None
        self.nametagNodePath = None
        self.jokeSeq = None
        self.iKnocked = False
        
        # Let's load our knock sound.
        sfxs = ['GUI_knock_1.ogg', 'GUI_knock_3.ogg']
        sfx = sfxs[random.randint(0, len(sfxs) - 1)]
        self.knockSfx = base.loadSfx('phase_5/audio/sfx/%s' % sfx)
        self.jokeSfx = base.loadSfx('phase_5/audio/sfx/AA_heal_telljoke.ogg')
        
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        
        try:
            # Let's attempt to fetch our collision node.
            town = self.cr.playGame.hood.loader.geom
            searchStr = '**/KnockKnockDoorSphere*;+s'
            npc = town.findAllMatches('**/?b' + str(self.block) + ':*_DNARoot;+s')
            doorNodes = npc.findAllMatches(searchStr)
            
            for door in doorNodes:
                doorBlock = door.getName()[-1:]
                if doorBlock == str(self.block):
                    self.__setupDoor(door)
                    break
        except:
            self.notify.warning('Failure to fetch collision node for knock-knock door.')
            self.notify.warning('Knock-Knock Door with missing collision node: Exterior Zone: %d, Block: %d.' % (self.zoneId, self.block))
    
    def disable(self):
        DistributedObject.disable(self)
        if self.nametag:
            self.hideName()
        if self.jokeSeq:
            self.jokeSeq.pause()
            self.jokeSeq = None
        
    def delete(self):
        if self.nametag:
            self.nametag.destroy()
        self.collisionNode = None
        self.physDoor = None
        self.realJokeNetworkTime = None
        self.iKnocked = False
        DistributedObject.delete(self)
            
    def __setupDoor(self, node):
        self.collisionNode = node
        self.physDoor = node.getParent()
        self.collisionNode.node().setCollideMask(CIGlobals.EventBitmask)
        self.accept('enter' + self.collisionNode.getName(), self.__handleEnter)
        self.accept('exit' + self.collisionNode.getName(), self.__handleExit)
        
        # Let's setup our nametag
        self.nametag = NametagGroup()
        self.nametag.setAvatar(self.physDoor)
        self.setupNametag()
        
    def setChat(self, chatString = None):
        if self.nametag:
            self.nametag.setChatType(NametagGlobals.CHAT)
            shouldClear = self.autoClearChat
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)
            self.nametag.setChatText(chatString, timeout = shouldClear)
            
    def setupNametag(self):
        font = CIGlobals.getToonFont()
        
        self.nametag.setFont(font)
        self.nametag.setChatFont(font)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.setText('Door')
        self.nametag.updateAll()
        self.hideName()
        
    def hideName(self):
        self.setChat('')
        self.nametag.unmanage(base.marginManager)
        
    def showName(self):
        self.nametag.manage(base.marginManager)
        
    def __handleEnter(self, _):
        self.notify.warning('Welcome avatar!')
        self.requestJoke()
        
    def __handleExit(self, _):
        self.notify.warning('See ya, avatar!')
        self.iKnocked = False
        self.sendUpdate('avatarDitched', [])
        
    def avatarEntertained(self, avId):
        self.notify.warning('Haha, %d thought that was funny!' % avId)
        
    def requestJoke(self):
        if self.collisionNode:
            place = self.cr.playGame.getPlace()
            canRequestJoke = not self.collisionNode.isStashed()
            
            if canRequestJoke and place.fsm and place.fsm.getCurrentState().getName() == 'walk':
                self.iKnocked = True
                self.sendUpdate('requestJoke', [])
        else:
            self.notify.warning('Avatar attempted to request a joke from knock knock door, but collision node was not set.')
            self.notify.debug('Knock-Knock Door with missing collision node: Exterior Zone: %d, Block: %d.' % (self.zoneId, self.block))
            
    def playJoke(self, avId, timestamp):
        self.realJokeNetworkTime = globalClockDelta.localElapsedTime(timestamp)
        avatar = base.cr.doId2do.get(avId, None)
        
        if avatar:
            if self.jokeSeq:
                self.jokeSeq.pause()
                
            def playLaughTrack():
                base.playSfx(self.jokeSfx, time = 1.30)
            
            doorJoke = KnockKnockGlobals.Jokes.get(KnockKnockGlobals.Zone2Block2Joke.get(self.zoneId).get(self.block))
            knocker = doorJoke[0]
            punchline = doorJoke[1]
            holdTime = doorJoke[2] if len(doorJoke) == 3 else KnockKnockGlobals.DEF_PUNCHLINE_HOLD_TIME
            self.jokeSeq = Sequence()
            self.jokeSeq.append(Func(base.playSfx, self.knockSfx))
            self.jokeSeq.append(Wait(0.2))
            self.jokeSeq.append(Func(self.showName))
            self.jokeSeq.append(KnockKnockGlobals.generateBasicJoke(avatar, self, knocker, punchline, holdTime, playLaughTrack))
            self.jokeSeq.append(Func(self.hideName))
            self.jokeSeq.start(self.realJokeNetworkTime)
        
    def stopJoke(self):
        self.realJokeNetworkTime = None
        
        if self.jokeSeq:
            self.jokeSeq.pause()
            self.jokeSeq = None
        self.hideName()
        
    def setData(self, zoneId, blockNumber):
        self.zoneId = zoneId
        self.block = blockNumber
        
    def getData(self):
        return [self.zoneId, self.block]

