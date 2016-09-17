# Filename: DistributedEagleGame.py
# Created by:  blach (04Jul15)

from panda3d.core import Fog, NodePath, Point3, Vec3, CollisionNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, Func, Wait, LerpQuatInterval
from direct.interval.IntervalGlobal import Parallel, ActorInterval, LerpHprInterval, ActorInterval
from direct.gui.DirectGui import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from direct.distributed.ClockDelta import globalClockDelta
from direct.actor.Actor import Actor

from lib.coginvasion.globals import CIGlobals
from FlightProjectileInterval import FlightProjectileInterval
from DistributedMinigame import DistributedMinigame
import EagleGameGlobals as EGG

def getGameText(fg = (1.0, 0.5, 0.0, 1.0)):
    return OnscreenText(text = "", scale = 0.15, fg = fg, font = CIGlobals.getMickeyFont())

def getIval(text, duration1, duration2, duration3):
    ival = Sequence(
        LerpPosInterval(
            text,
            duration = duration1,
            pos = (0, 0, 0.5),
            startPos = (0, 0, 1.7),
            blendType = 'easeIn'
        ),
        LerpPosInterval(
            text,
            duration = duration2,
            pos = (0.0, 0, 0),
            startPos = (0, 0, 0.5),
        ),
        LerpPosInterval(
            text,
            duration = duration3,
            pos = (0, 0, -1.3),
            startPos = (0, 0, 0),
            blendType = 'easeOut'
        )
    )
    return ival

def getRoundIval(text):
    return getIval(text, 0.4, 1.5, 0.15)

def getCountdownIval(text):
    return getIval(text, 0.2, 0.6, 0.2)

class DistributedEagleGame(DistributedMinigame):
    notify = directNotify.newCategory("DistributedEagleGame")

    Round2MusicSpeed = {
        1: 1.0,
        2: 1.15,
        3: 1.35,
    }

    def __init__(self, cr):
        DistributedMinigame.__init__(self, cr)
        self.platformPositions = {
            0: (-15, 0.5, -0.5),
            1: (-5, 0.5, -0.5),
            2: (5, 0.5, -0.5),
            3: (15, 0.5, -0.5)
        }
        self.fsm.addState(State('preGameMovie', self.enterPreGameMovie, self.exitPreGameMovie, ['start']))
        self.fsm.addState(State('roundCountdown', self.enterRoundCountdown, self.exitRoundCountdown, ['play']))
        self.fsm.addState(State('roundOver', self.enterRoundOver, self.exitRoundOver, ['finalScores', 'roundCountdown']))
        self.fsm.addState(State('finalScores', self.enterFinalScores, self.exitFinalScores, ['gameOver']))
        self.fsm.getStateNamed('waitForOthers').addTransition('preGameMovie')
        self.fsm.getStateNamed('waitForOthers').addTransition('roundCountdown')
        self.fsm.getStateNamed('play').addTransition('roundOver')
        self.fsm.getStateNamed('gameOver').addTransition('finalScores')

        self.cannonFSM = ClassicFSM('Cannon',
            [
                State('off', self.enterOff, self.exitOff),
                State('control', self.enterControlCannon, self.exitControlCannon),
                State('fly', self.enterFly, self.exitFly)
            ],
            'off', 'off'
        )
        self.cannonFSM.enterInitialState()
        self.cannon = None
        self.hitEagleSfx = None
        self.toonOof = None
        self.cannonMoveSfx = None
        self.fallSfx = None
        self.bgColor = (0.05, 0.05, 0.05)
        self.cannonId = None
        self.cannonBarrel = '**/cannon'
        self.fog = None
        self.platforms = []
        self.cannons = []
        self.round = 0
        self.world = None
        self.world2 = None
        self.worldModelPath = 'phase_5/models/cogdominium/tt_m_ara_cfg_quadrant2.bam'
        self.nodesToStash = ['lights', 'streamers', 'tt_m_ara_cfg_girders2b:Rwall_col',
            'tt_m_ara_cfg_girders2b:Lwall_col']
        self.triggers = ['tt_m_ara_cfg_clump2:col_clump2',
            'tt_m_ara_cfg_clump4:col_clump4', 'tt_m_ara_cfg_clump5:col_clump5',
            'tt_m_ara_cfg_clump6:col_clump6', 'tt_m_ara_cfg_clump7:col_clump7',
            'tt_m_ara_cfg_base:ceiling_collision']

    def allRoundsEnded(self):
        self.fsm.request('finalScores')

    def roundOver(self):
        if self.cannonId == None:
            self.__handleMissedEagle()
        self.fsm.request('roundOver')

    def enterControlCannon(self):
        self.__setupCamera(1)
        self.cannon = self.cr.doId2do.get(self.cannonId)
        array = []
        array.append(inputState.watchWithModifiers("cannonUp", "arrow_up", inputSource = inputState.ArrowKeys))
        array.append(inputState.watchWithModifiers("cannonDown", "arrow_down", inputSource = inputState.ArrowKeys))
        array.append(inputState.watchWithModifiers("cannonLeft", "arrow_left", inputSource = inputState.ArrowKeys))
        array.append(inputState.watchWithModifiers("cannonRight", "arrow_right", inputSource = inputState.ArrowKeys))
        self.cist = array # cannonInputStateArray
        taskMgr.add(self.__handleCannonControls, "DEagleGame-handleCannonControls")
        taskMgr.add(self.__broadcastCannonAndLTTask, "DEagleGame-broadcastCannonAndLT")
        self.acceptOnce("control", self.controlKeyPressed)

    def broadcastLTPos(self):
        lt = base.localAvatar
        lt.d_setPosHpr(lt.getX(render), lt.getY(render), lt.getZ(render), lt.getH(render), lt.getP(render), lt.getR(render))

    def __broadcastCannonAndLTTask(self, task):
        self.cannon.d_setBarrelOrientation(self.cannon.find(self.cannonBarrel).getH(), self.cannon.find(self.cannonBarrel).getP())
        self.broadcastLTPos()
        task.delayTime = 0.5
        return task.again

    def __handleCannonControls(self, task):
        up = inputState.isSet("cannonUp")
        down = inputState.isSet("cannonDown")
        left = inputState.isSet("cannonLeft")
        right = inputState.isSet("cannonRight")

        dt = globalClock.getDt()

        upAmount = 30 * dt
        downAmount = 45 * dt
        leftAmount = 45 * dt
        rightAmount = 45 * dt

        if up:
            self.cannon.find(self.cannonBarrel).setP(self.cannon.find(self.cannonBarrel).getP() + upAmount)
        elif down:
            self.cannon.find(self.cannonBarrel).setP(self.cannon.find(self.cannonBarrel).getP() - downAmount)
        if left:
            self.cannon.find(self.cannonBarrel).setH(self.cannon.find(self.cannonBarrel).getH() + leftAmount)
        elif right:
            self.cannon.find(self.cannonBarrel).setH(self.cannon.find(self.cannonBarrel).getH() - rightAmount)

        if (up or down or left or right):
            if self.cannonMoveSfx.status() == self.cannonMoveSfx.READY:
                base.playSfx(self.cannonMoveSfx)
        else:
            if self.cannonMoveSfx.status() == self.cannonMoveSfx.PLAYING:
                self.cannonMoveSfx.stop()

        return task.cont

    def exitControlCannon(self):
        self.ignore("control")
        taskMgr.remove("DEagleGame-handleCannonControls")
        taskMgr.remove("DEagleGame-broadcastCannonAndLT")
        for token in self.cist:
            token.release()
        del self.cist
        del self.cannon

    def controlKeyPressed(self):
        self.cannon.d_shoot()
        self.cannon.shoot()
        self.cannonFSM.request('fly')

    def __handleEagleHit(self, eagleId):
        self.b_poof()
        self.toonOof.play()
        self.hitEagleSfx.play()
        self.sendUpdate('hitEagle', [eagleId])

    def enterFly(self):
        self.acceptOnce(EGG.EAGLE_HIT_EVENT, self.__handleEagleHit)
        self.__setupCamera()
        cannon = self.cr.doId2do.get(self.cannonId)
        base.localAvatar.b_lookAtObject(0, 0, 0, blink = 0)
        base.localAvatar.b_setAnimState('swim')
        dummyNode = NodePath('dummyNode')
        dummyNode.reparentTo(base.localAvatar)
        dummyNode.setPos(0, 160, -90)
        base.localAvatar.setPos(base.localAvatar.getPos(render))
        base.localAvatar.setHpr(cannon.find(self.cannonBarrel).getHpr(render))
        base.localAvatar.reparentTo(render)
        self.flyProjectile = FlightProjectileInterval(
            base.localAvatar,
            startPos = cannon.find(self.cannonBarrel).getPos(render) + (0, 5.0, 0),
            endPos = dummyNode.getPos(render),
            duration = 5.0,
            name = 'DEagleGame-localAvatarFly',
            gravityMult = .25
        )
        self.flyProjectile.setDoneEvent(self.flyProjectile.getName())
        self.acceptOnce(self.flyProjectile.getDoneEvent(), self.__handleMissedEagle)
        self.flyProjectile.start()
        dummyNode.removeNode()
        del dummyNode
        self.cannonId = None
        del cannon
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()

    def __handleMissedEagle(self):
        base.playSfx(self.fallSfx)
        self.sendUpdate('missedEagle', [])

    def exitFly(self):
        self.ignore(EGG.EAGLE_HIT_EVENT)
        self.ignore(self.flyProjectile.getDoneEvent())
        self.flyProjectile.pause()
        del self.flyProjectile

    def __setupCamera(self, inCannon = 0):
        if inCannon:
            cannon = self.cr.doId2do.get(self.cannonId)
            camera.reparentTo(cannon)
        else:
            camera.reparentTo(base.localAvatar)
        camera.setPos(0.0, -14.75, 6.33)
        camera.setHpr(0, 0, 0)
        camera.setP(356.82)

    def enterPlay(self):
        DistributedMinigame.enterPlay(self)
        self.music.setPlayRate(self.Round2MusicSpeed[self.getRound()])
        self.createTimer()
        if self.cannonId != None:
            self.cannonFSM.request('control')

    def exitPlay(self):
        self.cannonFSM.request('off')
        self.deleteTimer()
        DistributedMinigame.exitPlay(self)
        
    def poof(self, x, y, z):
        cloud = Actor('phase_5/models/props/dust-mod.bam', {'chan': 'phase_5/models/props/dust-chan.bam'})
        cloud.reparentTo(render)
        cloud.setScale(2)
        cloud.setPos(x, y, z)
        cloud.setBillboardAxis(2)
        Sequence(ActorInterval(cloud, 'chan'), Func(cloud.cleanup)).start()
        
    def b_poof(self):
        x, y, z = base.localAvatar.getPos(render)
        self.sendUpdate('poof', [x, y, z])
        self.poof(x, y, z)

    def enterCannon(self, cannonId):
        self.cannonId = cannonId
        self.cannon = self.cr.doId2do.get(cannonId)
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.d_clearSmoothing()
        self.broadcastLTPos()
        base.localAvatar.reparentTo(self.cannon.find(self.cannonBarrel))
        base.localAvatar.setPosHpr(0, 3.5, 0, 90, -90, 90)
        base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.b_lookAtObject(0, 90, 0, blink = 0)
        base.localAvatar.animFSM.request('off')
        self.broadcastLTPos()
        if self.fsm.getCurrentState().getName() == 'play':
            self.cannonFSM.request('control')
        else:
            self.__setupCamera(1)

    def startRound(self, roundNum):
        self.round = roundNum
        self.fsm.request('roundCountdown', [roundNum])

    def getRound(self):
        return self.round

    def enterRoundCountdown(self, roundNum):
        self.text = getGameText()
        self.track = Sequence(
            Func(self.text.setText, "Round {0}".format(roundNum)),
            getRoundIval(self.text),
            Func(self.text.setText, "3"),
            getCountdownIval(self.text),
            Func(self.text.setText, "2"),
            getCountdownIval(self.text),
            Func(self.text.setText, "1"),
            getCountdownIval(self.text),
            Func(self.fsm.request, "play")
        )
        self.track.start()

    def exitRoundCountdown(self):
        self.track.pause()
        del self.track
        self.text.destroy()
        del self.text

    def enterRoundOver(self):
        self.text = getGameText()
        self.track = Sequence(
            Func(self.text.setText, "Time's Up!"),
            getRoundIval(self.text),
            Func(base.transitions.fadeOut, 1.0),
            Wait(2.0),
            Func(base.transitions.fadeIn, 1.0)
        )
        self.track.start()

    def exitRoundOver(self):
        self.track.pause()
        del self.track
        self.text.destroy()
        del self.text

    def allPlayersReady(self):
        self.waitLbl.hide()

    def load(self):
        self.hitEagleSfx = base.loadSfx('phase_4/audio/sfx/AA_drop_anvil_miss.ogg')
        
        self.hitObstacleSfx = base.loadSfx('phase_4/audio/sfx/MG_cannon_hit_tower.ogg')
        
        self.toonOof = base.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonHit.ogg')
        
        self.cannonMoveSfx = base.loadSfx("phase_4/audio/sfx/MG_cannon_adjust.ogg")
        self.cannonMoveSfx.setLoop(True)
        
        self.fallSfx = base.loadSfx("phase_4/audio/sfx/MG_sfx_vine_game_fall.ogg")
        
        self.setMinigameMusic("phase_9/audio/bgm/CHQ_FACT_bg.mid")
        
        self.setDescription("Shoot as many flying Legal Eagles as you can using your cannon. "
            "Use the arrow keys to aim your cannon and press the control key to fire.")
            
        self.setWinnerPrize(175)
        self.setLoserPrize(20)
        
        base.setBackgroundColor(*self.bgColor)
        
        self.world = loader.loadModel(self.worldModelPath)
        
        for nodeName in self.nodesToStash:
            node = self.world.find('**/' + nodeName)
            node.removeNode()
            
        self.world.find('**/tt_m_ara_cfg_clump7:clump7').setY(30.0)
        self.world.find('**/tt_m_ara_cfg_eagleNest:eagleNest_mesh').setY(30.0)
        self.world.setColorScale(0.75, 0.75, 0.75, 1.0)
        self.world.reparentTo(base.render)
        self.world.setZ(-5.0)
        
        self.world2 = self.world.copyTo(base.render)
        self.world2.setH(180)
        self.world2.setY(-10)
        # Remove all collision nodepaths from the other world.
        for np in self.world2.findAllMatches('**'):
            if np.node().isOfType(CollisionNode):
                print "Removing " + np.getName()
                np.removeNode()
                
        for i in range(len(self.platformPositions.keys())):
            platform = loader.loadModel("phase_9/models/cogHQ/platform1.bam")
            platform.find('**/platformcollision').removeNode()
            platform.reparentTo(render)
            platform.setPos(*self.platformPositions[i])
            self.platforms.append(platform)
            
        for triggerName in self.triggers:
            trigger = self.world.find('**/' + triggerName)
            trigger.setCollideMask(CIGlobals.WallBitmask)
            self.accept('enter' + triggerName, self.__handleHitWall)
            
        self.fog = Fog("DEagleGame-sceneFog")
        self.fog.setColor(*self.bgColor)
        self.fog.setExpDensity(0.01)
        
        render.setFog(self.fog)
        render.hide()
        
        self.fsm.request('waitForOthers')
        if not self.__handleCannonReady():
            self.accept('ToonCannon::ready', self.__handleCannonReady)
        
    def __handleCannonReady(self):
        if len(self.cannons) >= 4 and self.fsm.getCurrentState().getName() == 'waitForOthers':
            print "All cannons ready!"
            self.d_ready()
            return True
        return False
        
    def doPreGameMovie(self, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.fsm.request('preGameMovie', [ts])
        
    def enterPreGameMovie(self, ts):
        
        def parentToCannon():
            print self.cannonId
            camera.wrtReparentTo(self.cannon)
        
        def getToonsFlydownTrack():
            offset = 0.0
            track = Parallel()
            localAvCannon = None
            for toon in self.cr.doId2do.values():
                if not CIGlobals.isToon(toon):
                    continue
                tCannon = None
                for cannon in self.cannons:
                    print cannon.getOwner()
                    if cannon.getOwner() == toon.doId:
                        if toon.doId == base.localAvatar.doId:
                            print "Got local cannon id"
                            self.cannonId = cannon.doId
                            self.cannon = cannon
                        tCannon = cannon
                        break
                if tCannon:
                    propeller = loader.loadModel("phase_5/models/cogdominium/tt_m_ara_cfg_toonPropeller.bam")

                    torso = toon.getPart("torso")
                    bp = torso.attachNewNode('backpackInstance')
                    animal = toon.getAnimal()
                    bodyScale = CIGlobals.toonBodyScales[animal]
                    bpHeight = CIGlobals.torsoHeightDict[toon.getTorso()]* bodyScale - 0.5
                    bp.setPos(0, -0.325, bpHeight)

                    pInst = bp.attachNewNode("propellerInstance")
                    pInst.setPos(0, 0, 0)
                    pInst.setHpr(0, 20, 0)
                    pInst.setScale(1.0, 1.0, 1.25)

                    propeller.instanceTo(pInst)

                    ival = LerpHprInterval(
                        propeller,
                        duration = 0.35,
                        hpr = (360, 0, 0),
                        startHpr = (0, 0, 0)
                    ); ival.loop()
                    
                    toon.stopSmooth()
                    toon.loop('jump')
                    toon.wrtReparentTo(cannon)
                    toon.hide()
                    toon.setH(0)
                    track.append(
                        Sequence(
                            Wait(offset),
                            Func(toon.show),
                            Parallel(
                                Sequence(
                                    Wait(3.5),
                                    Func(ival.pause),
                                    ActorInterval(
                                        toon,
                                        "zend"
                                    ),
                                    Func(toon.loop, "neutral")
                                ),
                                LerpPosInterval(
                                    toon,
                                    duration = 4.0,
                                    pos = (5, 0, 0),
                                    startPos = (5, 0, 20),
                                    blendType = 'easeOut'
                                )
                            ),
                            Func(propeller.removeNode),
                            Func(pInst.removeNode),
                            Func(bp.removeNode),
                            Func(toon.wrtReparentTo, render)
                        )
                    )
                offset += 0.5
            
            return track
        camera.setPos(-17, -19.33, 7.15059)
        camera.setHpr(-18.5, -1.7759, 0)
        base.transitions.fadeScreen(1.0)
        render.show()
        #cannon = localAvCannon
        self.track = Sequence(
            Wait(0.2),
            Func(base.transitions.fadeIn, 2.0),
            Wait(2.5),
            Parallel(
                LerpPosInterval(
                    camera,
                    duration = 4.0,
                    pos = Point3(-18.6847, 38.7253, 11.5382),
                    startPos = camera.getPos(),
                    blendType = 'easeInOut'
                ),
                LerpHprInterval(
                    camera,
                    duration = 4.0,
                    hpr = Vec3(-156.855, -11.7019, 0),
                    startHpr = camera.getHpr(),
                    blendType = 'easeInOut'
                ),
                Sequence(
                    Wait(1.5),
                    getToonsFlydownTrack()
                )
            ),
            Func(parentToCannon),
            Parallel(
                LerpPosInterval(
                    camera,
                    duration = 4.0,
                    pos = Point3(0, -14.75, 6.33),
                    startPos = lambda camera = camera: camera.getPos(),
                    blendType = 'easeInOut'
                ),
                LerpHprInterval(
                    camera,
                    duration = 4.0,
                    hpr = (0, -3.18, 0),
                    startHpr = lambda camera = camera: camera.getHpr(),
                    blendType = 'easeInOut'
                )
            ),
        )
        self.track.setDoneEvent(self.uniqueName("preGameMovieDone"))
        self.acceptOnce(self.track.getDoneEvent(), self.__handlePreGameMovieDone)
        self.track.start(ts)
        
    def __handlePreGameMovieDone(self):
        self.fsm.request('start')
        
    def exitPreGameMovie(self):
        if hasattr(self, 'track'):
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            del self.track

    def __handleHitWall(self, entry):
        self.b_poof()
        self.toonOof.play()
        self.hitObstacleSfx.play()
        self.sendUpdate('missedEagle')

    def playMinigameMusic(self):
        DistributedMinigame.playMinigameMusic(self)
        self.music.setVolume(0.3)

    def announceGenerate(self):
        DistributedMinigame.announceGenerate(self)
        base.localAvatar.disableChatInput()
        self.load()

    def disable(self):
        for triggerName in self.triggers:
            self.ignore('enter' + triggerName)
        self.ignore('ToonCannon::ready')
        base.localAvatar.createChatInput()
        camera.reparentTo(render)
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        render.clearFog()
        self.triggers = None
        self.toonOof = None
        self.hitEagleSfx = None
        self.hitObstacleSfx = None
        self.cannonMoveSfx = None
        self.fallSfx = None
        self.cannons = None
        self.cannon = None
        if self.world:
            self.world.removeNode()
            self.world = None
        if self.world2:
            self.world2.removeNode()
            self.world2 = None
        self.worldModelPath = None
        self.nodesToStash = None
        self.fog = None
        self.round = None
        for platform in self.platforms:
            platform.removeNode()
        self.platforms = None
        self.cannonId = None
        self.cannonBarrel = None
        self.platformPositions = None
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        self.bgColor = None
        DistributedMinigame.disable(self)
