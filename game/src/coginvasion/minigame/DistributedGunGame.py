"""

  Filename: DistributedGunGame.py
  Created by: blach (26Oct14)

"""

from pandac.PandaModules import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.gui.DirectGui import DirectButton, DirectFrame, OnscreenText, DirectLabel
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals, ChatGlobals
from src.coginvasion.gui.WhisperPopup import WhisperPopup
from src.coginvasion.minigame.GunGameToonFPS import GunGameToonFPS
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
from DistributedToonFPSGame import DistributedToonFPSGame
from TeamMinigame import *
import GunGameLevelLoader
import GunGameGlobals as GGG

import random
import math

class DistributedGunGame(DistributedToonFPSGame, TeamMinigame):
    notify = directNotify.newCategory("DistributedGunGame")
    GameMode2Description = {GGG.GameModes.CASUAL: "Battle and defeat the Toons on the other team with your gun to gain points. " + \
                        "Remember to reload your gun when you're out of ammo! " + \
                        "The Toon with the most points when the timer runs out gets a nice prize!",
                        GGG.GameModes.CTF: "Steal the other team's flag and take it to where your flag is to score a point. Follow the arrows at the bottom of the screen to find the flags! Use your gun to defend yourself and your flag!",
                        GGG.GameModes.KOTH : "Capture the central point and defend it from the other Toons. The Toon who holds the point the longest wins."}
    GameMode2Music = {GGG.GameModes.CASUAL: 'phase_4/audio/bgm/MG_TwoDGame.mid',
                      GGG.GameModes.CTF:    'phase_9/audio/bgm/CHQ_FACT_bg.mid',
                      GGG.GameModes.KOTH : 'phase_7/audio/bgm/encntr_suit_winning_indoor.mid'}

    def __init__(self, cr):
        try:
            self.DistributedGunGame_initialized
            return
        except:
            self.DistributedGunGame_initialized = 1
        DistributedToonFPSGame.__init__(self, cr)

        TeamMinigame.__init__(self, GGG.BLUE, ('phase_4/maps/blue_neutral.png',
                                               'phase_4/maps/blue_hover.png',
                                               'phase_4/maps/blue_hover.png'),
                                    GGG.RED, ('phase_4/maps/red_neutral.png',
        			                          'phase_4/maps/red_hover.png',
        			                          'phase_4/maps/red_hover.png'))

        self.fsm.addState(State('countdown', self.enterCountdown, self.exitCountdown, ['play']))
        self.fsm.addState(State('announceGameOver', self.enterAnnounceGameOver, self.exitAnnounceGameOver, ['finalScores']))
        self.fsm.addState(State('finalScores', self.enterFinalScores, self.exitFinalScores, ['gameOver']))
        self.fsm.addState(State('voteGM', self.enterVoteGameMode, self.exitVoteGameMode, ['start']))
        self.fsm.addState(State('chooseTeam', self.enterChooseTeam, self.exitChooseTeam, ['chooseGun']))
        self.fsm.addState(State('chooseGun', self.enterChooseGun, self.exitChooseGun, ['waitForOthers']))
        self.fsm.addState(State('announceTeamWon', self.enterAnnounceTeamWon, self.exitAnnounceTeamWon, ['finalScores']))
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.fsm.getStateNamed('waitForOthers').addTransition('voteGM')
        self.fsm.getStateNamed('play').addTransition('announceGameOver')
        self.fsm.getStateNamed('play').addTransition('announceTeamWon')
        self.fsm.getStateNamed('start').addTransition('chooseTeam')
        self.fsm.getStateNamed('start').addTransition('chooseGun')
        self.toonFps = GunGameToonFPS(self)
        self.loader = GunGameLevelLoader.GunGameLevelLoader(self)
        self.track = None
        self.isTimeUp = False
        self.cameraMovmentSeq = None
        self.gameMode = None
        self.flags = []
        self.localAvHasFlag = False
        self.blueScoreLbl = None
        self.redScoreLbl = None
        self.redArrow = None
        self.blueArrow = None
        self.infoLbl = None
        self.scoreByTeam = {GGG.Teams.RED: 0, GGG.Teams.BLUE: 0}
        self.balloonSound = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')
        self.decidedSound = base.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_win_vote.ogg')
        return

    def setKOTHPoints(self, points):
        self.toonFps.setKOTHPoints(points)
        DistributedToonFPSGame.setMyKOTHPoints(self, points)

    def getFlagOfOtherTeam(self, team):
        for flag in self.flags:
            if flag.team != team:
                return flag

    def startGameModeVote(self):
        self.fsm.request('voteGM')

    def enterVoteGameMode(self):
        render.hide()
        font = CIGlobals.getMickeyFont()
        imp = CIGlobals.getToonFont()
        box = DGG.getDefaultDialogGeom()
        geom = CIGlobals.getDefaultBtnGeom()
        self.container = DirectFrame()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (2.4, 1.4, 1.4),
            parent = self.container)
        self.title = OnscreenText(
            text = "Vote  on  Game  Mode", pos = (0, 0.5, 0), font = font,
            scale = (0.12), parent = self.container, fg = (1, 0.9, 0.3, 1))
        self.btnFrame = DirectFrame(parent = self.container, pos = (0.14, 0, 0))
        self.casualFrame = DirectFrame(parent = self.btnFrame, pos = (-0.80, 0, 0))
        self.ctfFrame = DirectFrame(parent = self.btnFrame, pos = (-0.125, 0, 0))
        self.kothFrame = DirectFrame(parent = self.btnFrame, pos = (0.55, 0, 0))
        self.casual = DirectButton(
            parent = self.casualFrame, relief = None, pressEffect = 0,
            image = ('phase_4/maps/casual_neutral.png',
                    'phase_4/maps/casual_hover.png',
                    'phase_4/maps/casual_hover.png'),
            image_scale = (0.9, 1, 1), scale = 0.4, command = self.__pickedGameMode, extraArgs = [GGG.GameModes.CASUAL])
        self.casual_votesLbl = OnscreenText(
            parent = self.casualFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.ctf = DirectButton(
            parent = self.ctfFrame, relief = None, pressEffect = 0,
            image = ('phase_4/maps/ctf_neutral.png',
                    'phase_4/maps/ctf_hover.png',
                    'phase_4/maps/ctf_hover.png'),
            image_scale = (0.9, 1, 1), scale = 0.4, command = self.__pickedGameMode, extraArgs = [GGG.GameModes.CTF])
        self.ctf_votesLbl = OnscreenText(
            parent = self.ctfFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.koth = DirectButton(
            parent = self.kothFrame, relief = None, pressEffect = 0,
            image = ('phase_4/maps/koth_neutral.png',
                    'phase_4/maps/koth_hover.png',
                    'phase_4/maps/koth_hover.png'),
            image_scale = (0.9, 1, 1), scale = 0.4, command = self.__pickedGameMode, extraArgs = [GGG.GameModes.KOTH])
        self.koth_votesLbl = OnscreenText(
            parent = self.kothFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.outcomeLbl = OnscreenText(
            parent = self.container, text = "", pos = (0, -0.6, 0), font = imp, scale = 0.1)

    def __pickedGameMode(self, mode):
        self.sendUpdate('myGameModeVote', [mode])
        self.ctf['state'] = DGG.DISABLED
        self.casual['state'] = DGG.DISABLED
        self.koth['state'] = DGG.DISABLED
        if mode == GGG.GameModes.CASUAL:
            self.ctf['image'] = 'phase_4/maps/ctf_neutral.png'
            self.koth['image'] = 'phase_4/maps/koth_neutral.png'
            self.casual['image'] = 'phase_4/maps/casual_hover.png'
        elif mode == GGG.GameModes.CTF:
            self.ctf['image'] = 'phase_4/maps/ctf_hover.png'
            self.casual['image'] = 'phase_4/maps/casual_neutral.png'
            self.koth['image'] = 'phase_4/maps/koth_neutral.png'
        elif mode == GGG.GameModes.KOTH:
            self.ctf['image'] = 'phase_4/maps/ctf_neutral.png'
            self.casual['image'] = 'phase_4/maps/casual_neutral.png'
            self.koth['image'] = 'phase_4/maps/koth_hover.png'

    def incrementGameModeVote(self, mode):
        base.playSfx(self.balloonSound)
        lbl = None
        if mode == GGG.GameModes.CTF:
            lbl = self.ctf_votesLbl
        elif mode == GGG.GameModes.CASUAL:
            lbl = self.casual_votesLbl
        elif mode == GGG.GameModes.KOTH:
            lbl = self.koth_votesLbl
        if lbl:
            lbl.setText(str(int(lbl.getText()) + 1))

    def gameModeDecided(self, mode, wasRandom):
        base.playSfx(self.decidedSound)
        if wasRandom:
            msg = GGG.MSG_CHOSE_MODE_TIE.format(GGG.GameModeNameById[mode])
        else:
            msg = GGG.MSG_CHOSE_MODE.format(GGG.GameModeNameById[mode])
        self.outcomeLbl.setText(msg)
        base.taskMgr.doMethodLater(3.0, self.__decided2chooseTeamTask, self.uniqueName('decided2chooseTeamTask'))

    def __decided2chooseTeamTask(self, task):
        self.fsm.request('start')
        return task.done

    def exitVoteGameMode(self):
        base.taskMgr.remove(self.uniqueName('decided2chooseTeamTask'))
        self.outcomeLbl.destroy()
        del self.outcomeLbl
        self.ctf_votesLbl.destroy()
        del self.ctf_votesLbl
        self.casual_votesLbl.destroy()
        del self.casual_votesLbl
        self.ctf.destroy()
        del self.ctf
        self.koth_votesLbl.destroy()
        del self.koth_votesLbl
        self.casual.destroy()
        del self.casual
        self.ctfFrame.destroy()
        del self.ctfFrame
        self.casualFrame.destroy()
        del self.casualFrame
        self.kothFrame.destroy()
        del self.kothFrame
        self.koth.destroy()
        del self.koth
        self.title.destroy()
        del self.title
        self.bg.destroy()
        del self.bg
        self.container.destroy()
        del self.container

    def enterChooseTeam(self):
        TeamMinigame.makeSelectionGUI(self)

    def acceptedIntoTeam(self):
        TeamMinigame.acceptedIntoTeam(self)

        self.fsm.request('chooseGun')
        pos, hpr = self.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)

    def exitChooseTeam(self):
        TeamMinigame.destroySelectionGUI(self)

    def setTeamOfPlayer(self, avId, team):
        remoteAvatar = self.getRemoteAvatar(avId)
        if remoteAvatar:
            remoteAvatar.setTeam(team)

    def enterChooseGun(self):
        font = CIGlobals.getToonFont()
        box = DGG.getDefaultDialogGeom()
        geom = CIGlobals.getDefaultBtnGeom()
        self.container = DirectFrame()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4),
            parent = self.container)
        self.title = OnscreenText(text = "Choose a Gun", pos = (0, 0.5, 0), font = font, scale = (0.12), parent = self.container)
        self.pistolBtn = DirectButton(geom = geom, text = "Pistol", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["pistol"], pos = (0, 0, 0.35), parent = self.container)
        self.shotgunBtn = DirectButton(geom = geom, text = "Shotgun", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["shotgun"], pos = (0, 0, 0.25), parent = self.container)
        self.sniperBtn = DirectButton(geom = geom, text = "Sniper", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["sniper"], pos = (0, 0, 0.15), parent = self.container)

    def __gunChoice(self, choice):
        self.toonFps.cleanup()
        self.toonFps = None
        self.toonFps = GunGameToonFPS(self, choice)
        self.toonFps.load()
        self.sendUpdate('readyToStart')
        self.fsm.request('waitForOthers')

    def exitChooseGun(self):
        self.sniperBtn.destroy()
        del self.sniperBtn
        self.shotgunBtn.destroy()
        del self.shotgunBtn
        self.pistolBtn.destroy()
        del self.pistolBtn
        self.title.destroy()
        del self.title
        self.bg.destroy()
        del self.bg
        self.container.destroy()
        del self.container

    def gunChoice(self, choice, avId):
        remoteAvatar = self.getRemoteAvatar(avId)
        if remoteAvatar:
            remoteAvatar.setGunName(choice)

    def setGameMode(self, mode):
        self.gameMode = mode
        self.setDescription(self.GameMode2Description[mode])
        self.setMinigameMusic(self.GameMode2Music[mode])

    def getGameMode(self):
        return self.gameMode

    def avatarHitByBullet(self, avId, damage):
        avatar = self.getRemoteAvatar(avId)
        if avatar:
            avatar.grunt()

    def headBackToMinigameArea(self):
        if self.loader:
            self.loader.unload()
            self.loader.cleanup()
            self.loader = None
        DistributedToonFPSGame.headBackToMinigameArea(self)

    def setupRemoteAvatar(self, avId):
        self.remoteAvatars.append(RemoteToonBattleAvatar(self, self.cr, avId))

    def setLevelName(self, levelName):
        self.loader.setLevel(levelName)
        self.loader.load()

    def pickSpawnPoint(self):
        return random.choice(self.loader.getSpawnPoints())

    def load(self):
        self.toonFps.load()
        self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
        self.setWinnerPrize(200)
        self.setLoserPrize(15)

        if not base.localAvatar.tokenIcon is None:
            base.localAvatar.tokenIcon.hide()

        #pos, hpr = self.loader.getCameraOfCurrentLevel()
        #camera.setPos(pos)
        #camera.setHpr(hpr)
        DistributedToonFPSGame.load(self, showDesc = False)
        DistributedToonFPSGame.handleDescAck(self)

    def handleDescAck(self):
        if self.gameMode in GGG.FFA_MODES:
            # This is a free for all game mode, don't choose teams.
            self.fsm.request('chooseGun')
            pos, hpr = self.pickSpawnPoint()
            base.localAvatar.setPos(pos)
            base.localAvatar.setHpr(hpr)
        else:
            self.fsm.request('chooseTeam')

    def incrementKills(self):
        self.toonFps.killedSomebody()

    def allPlayersReady(self):
        self.fsm.request('countdown')

    def timeUp(self):
        if not self.isTimeUp:
            self.fsm.request('announceGameOver')
            self.isTimeUp = True

    def teamWon(self, team):
        self.fsm.request('announceTeamWon', [team])

    def enterAnnounceTeamWon(self, team):
        whistleSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.ogg")
        whistleSfx.play()
        del whistleSfx

        if self.gameMode == GGG.GameModes.KOTH and DistributedToonFPSGame.getKOTHKing(self):
            text = DistributedToonFPSGame.getKOTHKing(self).getName()
        else:
            text = GGG.TeamNameById[team].split(' ')[0]
        self.gameOverLbl.setText("{0}\nWins!".format(text))
        self.gameOverLbl.show()
        self.track = Sequence(Wait(3.0), Func(self.fsm.request, 'finalScores'))
        self.track.start()

    def exitAnnounceTeamWon(self):
        if self.track:
            self.track.pause()
            self.track = None

    def enterAnnounceGameOver(self):
        whistleSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.ogg")
        whistleSfx.play()
        del whistleSfx
        self.gameOverLbl.setText("TIME's\nUP!")
        self.gameOverLbl.show()
        self.track = Sequence(Wait(3.0), Func(self.fsm.request, 'finalScores'))
        self.track.start()

    def exitAnnounceGameOver(self):
        if self.track:
            self.track.pause()
            self.track = None

    def enterFinalScores(self):
        DistributedToonFPSGame.enterFinalScores(self)
        self.sendUpdate('myFinalScore', [self.toonFps.points])

    def exitFinalScores(self):
        DistributedToonFPSGame.exitFinalScores(self)

    def incrementTeamScore(self, team):
        self.scoreByTeam[team] += 1
        if team == GGG.Teams.BLUE:
            self.blueScoreLbl.setText("Blue: {0}".format(self.scoreByTeam[team]))
        elif team == GGG.Teams.RED:
            self.redScoreLbl.setText('Red: {0}'.format(self.scoreByTeam[team]))

    def __updateArrows(self, task):
        blueFlag = None
        redFlag = None

        for flag in self.flags:
            if flag.team == GGG.Teams.BLUE:
                blueFlag = flag
            if flag.team == GGG.Teams.RED:
                redFlag = flag

        if not blueFlag or not redFlag:
            return task.done

        bLocation = blueFlag.flagMdl.getPos(base.cam)
        bRotation = base.cam.getQuat(base.cam)
        bCamSpacePos = bRotation.xform(bLocation)
        bArrowRadians = math.atan2(bCamSpacePos[0], bCamSpacePos[1])
        bArrowDegrees = (bArrowRadians/math.pi) * 180
        self.blueArrow.setR(bArrowDegrees - 90)

        rLocation = redFlag.flagMdl.getPos(base.cam)
        rRotation = base.cam.getQuat(base.cam)
        rCamSpacePos = rRotation.xform(rLocation)
        rArrowRadians = math.atan2(rCamSpacePos[0], rCamSpacePos[1])
        rArrowDegrees = (rArrowRadians/math.pi) * 180
        self.redArrow.setR(rArrowDegrees - 90)

        return task.cont

    def getTeamScoreLbl(self, team):
        if team == GGG.Teams.BLUE:
            return self.blueScoreLbl
        elif team == GGG.Teams.RED:
            return self.redScoreLbl

    def getTeamFlagArrow(self, team):
        if team == GGG.Teams.BLUE:
            return self.blueArrow
        elif team == GGG.Teams.RED:
            return self.redArrow

    def getTeamFrame(self, team):
        if team == GGG.Teams.BLUE:
            return self.blueFrame
        elif team == GGG.Teams.RED:
            return self.redFrame

    def enterCountdown(self):
        render.show()
        if self.gameMode == GGG.GameModes.CTF:
            self.blueFrame = DirectFrame(pos = (-0.1, 0, -0.85))
            self.blueScoreLbl = OnscreenText(text = "Blue: 0", scale = 0.1, parent = self.blueFrame,
                fg = GGG.TeamColorById[GGG.Teams.BLUE], shadow = (0,0,0,1), align = TextNode.ARight)
            self.blueArrow = loader.loadModel('phase_3/models/props/arrow.bam')
            self.blueArrow.setColor(GGG.TeamColorById[GGG.Teams.BLUE])
            self.blueArrow.reparentTo(self.blueFrame)
            self.blueArrow.setPos(-0.1, 0, 0.15)
            self.blueArrow.setScale(0.1)
            self.redFrame = DirectFrame(pos = (0.1, 0, -0.85))
            self.redScoreLbl = OnscreenText(text = "Red: 0", scale = 0.1, parent = self.redFrame,
                fg = GGG.TeamColorById[GGG.Teams.RED], shadow = (0,0,0,1), align = TextNode.ALeft)
            self.redArrow = loader.loadModel('phase_3/models/props/arrow.bam')
            self.redArrow.setColor(GGG.TeamColorById[GGG.Teams.RED])
            self.redArrow.reparentTo(self.redFrame)
            self.redArrow.setPos(0.1, 0, 0.15)
            self.redArrow.setScale(0.1)
            self.infoLbl = OnscreenText(text = "Playing to: 3", scale = 0.1, pos = (0, -0.95),
                fg = (1, 1, 1, 1), shadow = (0,0,0,1))
            base.taskMgr.add(self.__updateArrows, self.uniqueName('updateArrows'))
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)
        self.toonFps.fsm.request('alive')
        text = OnscreenText(text = "", scale = 0.1, pos = (0, 0.5), fg = (1, 1, 1, 1), shadow = (0,0,0,1))
        self.track = Sequence(
            Func(text.setText, "5"),
            Wait(1.0),
            Func(text.setText, "4"),
            Wait(1.0),
            Func(text.setText, "3"),
            Wait(1.0),
            Func(text.setText, "2"),
            Wait(1.0),
            Func(text.setText, "1"),
            Wait(1.0),
            Func(text.setText, "FIGHT!"),
            Func(self.fsm.request, 'play'),
            Wait(1.0),
            Func(text.destroy)
        )
        self.track.start()
        self.sendUpdate('gunChoice', [self.toonFps.weaponName, base.localAvatar.doId])

    def exitCountdown(self):
        if self.track:
            self.track.finish()
            self.track = None

    def enterPlay(self):
        DistributedToonFPSGame.enterPlay(self)
        self.toonFps.reallyStart()
        self.createTimer()

    def exitPlay(self):
        self.deleteTimer()
        if self.toonFps:
            self.toonFps.end()
        DistributedToonFPSGame.exitPlay(self)

    def announceGenerate(self):
        DistributedToonFPSGame.announceGenerate(self)
        base.localAvatar.walkControls.setWalkSpeed(GGG.ToonForwardSpeed, GGG.ToonJumpForce,
                                                   GGG.ToonReverseSpeed, GGG.ToonRotateSpeed)
        self.load()
        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))

    def disable(self):
        render.show()
        base.localAvatar.setWalkSpeedNormal()

        # Show the staff icon again.
        if not base.localAvatar.tokenIcon is None:
            base.localAvatar.tokenIcon.show()

        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.taskMgr.remove(self.uniqueName('updateArrows'))
        self.playersByTeam = None
        if self.blueArrow:
            self.blueArrow.removeNode()
            self.blueArrow = None
        if self.redArrow:
            self.redArrow.removeNode()
            self.redArrow = None
        if self.blueScoreLbl:
            self.blueScoreLbl.destroy()
            self.blueScoreLbl = None
        if self.redScoreLbl:
            self.redScoreLbl.destroy()
            self.redScoreLbl = None
        if self.infoLbl:
            self.infoLbl.destroy()
            self.infoLbl = None
        self.scoreByTeam = None
        self.flags = None
        self.gameMode = None
        self.team = None
        self.localAvHasFlag = None
        if self.loader:
            self.loader.unload()
            self.loader.cleanup()
            self.loader = None
        self.isTimeUp = None
        self.toonFps.reallyEnd()
        self.toonFps.cleanup()
        self.toonFps = None
        self.spawnPoints = None
        DistributedToonFPSGame.disable(self)
