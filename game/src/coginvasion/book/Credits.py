"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Credits.py
@author Maverick Liberty
@date 2017-03-27

"""

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import OnscreenImage, OnscreenText

from panda3d.core import PNMImage, Texture, TextureStage, NodePath
from panda3d.core import TexGenAttrib, Point3, Camera, ClockObject
from panda3d.core import AudioManager

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
        self.backgroundImg = OnscreenImage('phase_3/maps/background.jpg', parent = render2d)
        self.backgroundImg.setColor(0.2, 0.2, 0.2, 1)
        self.fade = PNMImage(32, 32)
        self.fadeTexture = Texture()
        self.npParent = NodePath('dummyNode')
        self.textParent = self.npParent.attachNewNode('textParent')
        self.logoImage = OnscreenImage('phase_3/maps/CogInvasion_Logo.png', parent = self.textParent,
            scale = (0.75, 0, 0.5))
        self.logoImage.setTransparency(1)
        self.logoImage.setP(-90)
        
        text = self.buildCreditsText()
        self.creditsText = OnscreenText(parent = self.textParent, font = CIGlobals.getToonFont(),
            fg = (1, 1, 1, 1), scale = 0.065, pos = (0, -0.5, 0), text = text)
        self.creditsText.setP(-90)

        self.exitText = OnscreenText(parent = render2d, font = CIGlobals.getToonFont(),
            fg = (0.8, 0, 0, 0.5), scale = 0.085, pos = (0, -0.96, 0), text = 'Press any key to exit')
        self.exitText.hide()

        self.creditsCam = Camera('creditsCam')
        self.creditsCamNP = None
        self.posInterval = None
        
        self.creditsAudioMgr = AudioManager.createAudioManager()
        self.bgm = self.creditsAudioMgr.getSound('phase_3/audio/bgm/ci_theme2.ogg')
        
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
        messenger.send('credits-Complete')
        base.enableMusic(True)
        base.enableSoundEffects(True)
        self.ignoreAll()
        self.destroy()
    
    def watchTextPosition(self, task):
        if self.textParent.getY() >= 5.187:
            self.exitText.show()
            self.acceptOnce('button', self.exit)
            return task.done
        return task.cont
        
    def setup(self):
        globalClock.setMode(ClockObject.MSlave)

        self.fade.addAlpha()
        self.fade.fill(1)
        self.fade.alphaFill(1)
        
        for x in range(self.fade.getXSize()):
            for y in range(self.fade.getYSize()):
                self.fade.setAlpha(x, y, -0.2 + 2.5 * math.sin(math.pi * y / self.fade.getYSize()))
        
        self.fadeTexture.load(self.fade)
        self.fadeTexture.setWrapU(Texture.WMClamp)
        self.fadeTexture.setWrapV(Texture.WMClamp)
        
        self.textParent.setDepthTest(0)
        self.textParent.setDepthWrite(0)
        
        texStage = TextureStage('texStage')
        self.textParent.setTexGen(texStage, TexGenAttrib.MWorldPosition)
        self.textParent.setTexScale(texStage, 0.5, 0.5)
        self.textParent.setTexOffset(texStage, 0.25, 0.5)
        self.textParent.setTexture(texStage, self.fadeTexture)
        
        b3 = self.textParent.getTightBounds()
        dimensions = b3[1] - b3[0]
        self.posInterval = self.textParent.posInterval(50, Point3(0, dimensions[1] + 2, 0), Point3(0, 0, 0))
        self.posInterval.start()
        
        self.creditsCam.copyLens(base.cam2d.node().getLens())
        self.creditsCamNP = self.npParent.attachNewNode(self.creditsCam)
        self.creditsCamNP.setP(-90)
        
        displayRegion = base.win.makeDisplayRegion()
        displayRegion.setCamera(self.creditsCamNP)
        displayRegion.setSort(1000)
        
        base.enableMusic(False)
        base.enableSoundEffects(False)
        self.bgm.setLoop(1)
        self.bgm.play()
        
        base.buttonThrowers[0].node().setButtonDownEvent('button')
        taskMgr.add(self.watchTextPosition, 'Watch Text Position')
        
        globalClock.setMode(ClockObject.MNormal)
        
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
        if self.fade:
            self.fade.clear()
            self.fade = None
        if self.fadeTexture:
            self.fadeTexture.clear()
            self.fadeTexture = None
        if self.creditsText:
            self.creditsText.destroy()
            self.creditsText = None
        if self.exitText:
            self.exitText.destroy()
            self.exitText = None
        if self.logoImage:
            self.logoImage.destroy()
            self.logoImage = None
        if self.creditsCamNP:
            self.creditsCamNP.removeNode()
            self.creditsCamNP = None
        if self.creditsCam:
            self.creditsCam = None
        if self.textParent:
            self.textParent.removeNode()
            self.textParent = None
        if self.npParent:
            self.npParent.removeNode()
            self.npParent = None
        if self.creditsAudioMgr:
            self.creditsAudioMgr.shutdown()
            self.creditsAudioMgr = None
        self.developers = None
        self.webDevelopers = None
        self.artists = None
        self.specialThanks = None
        self.composers = None
        self.communityManager = None
        self.moderators = None
        self.prevMusic = None
