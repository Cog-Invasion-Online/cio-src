"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Credits.py
@author Maverick Liberty
@date 2017-03-27

"""

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import OnscreenImage, OnscreenText
from direct.interval.IntervalGlobal import Parallel, LerpColorScaleInterval, Func

from panda3d.core import PNMImage, Texture, TextureStage, NodePath
from panda3d.core import TexGenAttrib, Point3, Camera, ClockObject
from panda3d.core import AudioManager, TransparencyAttrib

from src.coginvasion.globals import CIGlobals

import math

class Credits(DirectObject):
    
    developers = {'Game Development' : ['DuckyDuck1553', 'DecodedLogic']}
    webDevelopers = {'Web Development' : ['totok', 'DuckyDuck1553', 'DecodedLogic']}
    artists = {'Artists' : ['John L. (supertricky)', 'DuckyDuck1553', 'DecodedLogic', 'Baru (fatigue)', 'Isabel (allyjean)', 'Colorblind', 'loonatic']}
    composers = {'Composers' : ['Dylan J.', 'Doc. Dynamite', 'CBiard']}
    communityManager = {'Community Manager' : ['Leo (Bradley)']}
    moderators = {'Moderation Team' : ['Mark (Black & White)', 'Jackson M.', 'Gabriel A.', 'Davon M.']}
    specialThanks = {'Special Thanks' : ['Jesse Schell', 'rdb', 'Baribal', 'ThomasEgi', 'tobspr', 
        'jjkoletar', 'mmavipc', 'CFSWorks', 'loblao', 'HarvTarv', 'Hawkheart',
        'TheRandomDog', 'Joey Z. (joey19982)', 'Disney Interactive', 'Microsoft', 'YorkeTheMouse', 'Disyer', '\n\n\nAnd of course, YOU!\n\n\n']}
    
    def __init__(self):
        DirectObject.__init__(self)

        base.setBackgroundColor(0, 0, 0)

        self.textParent = base.credits2d.attachNewNode('textParent')
        self.textParent.setBin("gui-popup", 61)
        self.textParent.setDepthWrite(False)
        self.textParent.setTransparency(True)

        self.logoImage = OnscreenImage('phase_3/maps/CogInvasion_Logo.png', parent = self.textParent,
            scale = (0.685, 1.0, 0.325))
        self.logoImage.setTransparency(1)
        
        text = self.buildCreditsText()
        self.creditsText = OnscreenText(parent = self.textParent, font = CIGlobals.getToonFont(),
            fg = (1, 1, 1, 1), scale = 0.065, pos = (0, -0.5, 0), text = text, shadow = (0, 0, 0, 1))

        self.posInterval = None

        self.backgroundImg = OnscreenImage('phase_3/maps/credits_fade.png', parent = render2d)
        self.backgroundImg.setTransparency(True)
        self.backgroundImg.setColor(0, 0, 0, 1.0)
        self.backgroundImg.setBin("gui-popup", 62)
        self.backgroundImg.setDepthWrite(False)

        self.exitText = OnscreenText(parent = base.credits2d, font = CIGlobals.getToonFont(),
            fg = (1.0, 0, 0, 1.0), shadow = (0, 0, 0, 1), scale = 0.085, pos = (0, -0.96, 0), text = 'Press any key to exit')
        self.exitText.hide()
        self.exitText.setBin("gui-popup", 63)
        self.exitText.setDepthWrite(False)
        self.exitText.setTransparency(True)
        
        self.creditsAudioMgr = AudioManager.createAudioManager()
        self.creditsAudioMgr.setVolume(0.65)
        self.bgm = self.creditsAudioMgr.getSound('phase_4/audio/bgm/new_years_fireworks_music.ogg')
        
    def buildCreditsText(self):
        def writeNames(message, namesList):
            for name in namesList:
                message = '%s%s\n' % (message, name)
            return message

        message = 'Cog Invasion Online\nVersion {0} (Build {1} : {2})\n'.format(game.version, game.build, game.buildtype)
        message += '\nCREDITS\n\n'
        
        # Write the game developers' names
        message += 'Programming\n\n'
        message += '%s\n' % self.developers.keys()[0]
        message = writeNames(message, self.developers.values()[0])
        message += '\n\n'
        
        # Write the web developers' names
        message += '%s\n' % self.webDevelopers.keys()[0]
        message = writeNames(message, self.webDevelopers.values()[0])
        
        # Let's begin the art section
        message += '\n\nArt\n\n'
        
        # Write the artists' names
        message += '%s\n' % self.artists.keys()[0]
        message = writeNames(message, self.artists.values()[0])
        
        message += '\n\n'
        
        # Write the composers' names
        message += '%s\n' % self.composers.keys()[0]
        message = writeNames(message, self.composers.values()[0])
        
        ##########################################
        # Let's begin the community section.
        message += '\n\nCommunity\n\n'
        
        # Write the community manager names
        message += '%s\n' % self.communityManager.keys()[0]
        message = writeNames(message, self.communityManager.values()[0])
        message += '\n\n'
        
        # Write the moderators' names
        message += '%s\n' % self.moderators.keys()[0]
        message = writeNames(message, self.moderators.values()[0])
        
        # Let's begin the Special Thanks section.
        message += '\n\n'
        
        # Write the special thanks' names
        message += '%s\n' % self.specialThanks.keys()[0]
        message = writeNames(message, self.specialThanks.values()[0])
        message += '\nWe thank the original Toontown Online team.\nNot only for the game, but for the memories.'
        message += "\n\n\n\n\"Don't cry because it's over.\nSmile because it happened.\"\n  - Dr. Seuss"
        
        return message
    
    def exit(self, key):
        self.__fadeOut()
        base.taskMgr.doMethodLater(1.1, self.__exitTask, "exitTask")

    def __exitTask(self, task):
        messenger.send('credits-Complete')
        self.ignoreAll()
        self.destroy()
        base.unMuteMusic()
        base.unMuteSfx()
        base.setBackgroundColor(0.05, 0.15, 0.4)
        base.transitions.fadeIn(1.0)
        return task.done
    
    def watchTextPosition(self, task):
        if self.textParent.getZ() >= 5.187:
            self.exitText.show()
            self.acceptOnce('button', self.exit)
            return task.done
        return task.cont

    def __fadeIn(self):
        Parallel(
            LerpColorScaleInterval(self.textParent, 1.0, (1, 1, 1, 1), (1, 1, 1, 0)),
            LerpColorScaleInterval(self.backgroundImg, 1.0, (1, 1, 1, 1), (1, 1, 1, 0)),
            LerpColorScaleInterval(self.exitText, 1.0, (1, 1, 1, 1), (1, 1, 1, 0))
        ).start()

    def __fadeOut(self):
        Parallel(
            LerpColorScaleInterval(self.textParent, 1.0, (1, 1, 1, 0), (1, 1, 1, 1)),
            LerpColorScaleInterval(self.backgroundImg, 1.0, (1, 1, 1, 0), (1, 1, 1, 1)),
            LerpColorScaleInterval(self.exitText, 1.0, (1, 1, 1, 0), (1, 1, 1, 1))
        ).start()
        
    def setup(self):
        self.__fadeIn()

        b3 = self.textParent.getTightBounds()
        dimensions = b3[1] - b3[0]
        self.posInterval = self.textParent.posInterval(50, Point3(0, 0, dimensions[2] + 2), Point3(0, 0, 0))
        self.posInterval.start()
        
        self.bgm.setLoop(1)
        self.bgm.play()
        
        base.buttonThrowers[0].node().setButtonDownEvent('button')
        taskMgr.add(self.watchTextPosition, 'Watch Text Position')
        
    def destroy(self):
        if self.posInterval:
            self.posInterval.pause()
            self.posInterval = None
        if self.bgm:
            self.bgm.stop()
            self.bgm = None
        if self.backgroundImg:
            self.backgroundImg.destroy()
            self.backgroundImg = None
        if self.creditsText:
            self.creditsText.destroy()
            self.creditsText = None
        if self.exitText:
            self.exitText.destroy()
            self.exitText = None
        if self.logoImage:
            self.logoImage.destroy()
            self.logoImage = None
        if self.textParent:
            self.textParent.removeNode()
            self.textParent = None
        if self.creditsAudioMgr:
            self.creditsAudioMgr.stopAllSounds()
            self.creditsAudioMgr = None
        self.developers = None
        self.webDevelopers = None
        self.artists = None
        self.specialThanks = None
        self.composers = None
        self.communityManager = None
        self.moderators = None
        self.prevMusic = None
