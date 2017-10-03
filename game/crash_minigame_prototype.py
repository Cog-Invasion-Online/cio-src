"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file crash_minigame_prototype.py
@author Brian Lach
@date July 14, 2016

"""

from src.coginvasion.standalone.StandaloneToon import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.dna.DNALoader import *
from src.coginvasion.minigame.CrashWalker import CrashWalker
from src.coginvasion.toon import ParticleLoader
from src.coginvasion.hood import ZoneUtil

base.transitions.fadeScreen(1.0)

base.disableMouse()

base.localAvatar.disableAvatarControls()
base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.setAnimState('off')

base.localAvatar.controlManager.disable()
base.localAvatar.prepareToSwitchControlType()
base.localAvatar.controlManager.wantWASD = 0
base.localAvatar.controlManager.enable()

class Jellybean(NodePath, DirectObject):
    notify = directNotify.newCategory("Jellybean")
    
    def __init__(self, gui, collectable = True):
        NodePath.__init__(self, 'jellybean')
        
        self.gui = gui

        self.particle = ParticleLoader.loadParticleEffect('phase_4/etc/cmg_bean_sparkle.ptf')
        self.particle.reparentTo(self)

        self.mdl = loader.loadModel("phase_4/models/props/jellybean4.bam")
        self.mdl.setColor(VBase4(0.3, 0.3, 1.0, 1.0))
        self.mdl.flattenLight()
        self.mdl.reparentTo(self)
        self.mdl.setScale(3.0)
        self.mdl.setZ(1.0)

        self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
        self.shadow.setScale(.12)
        self.shadow.reparentTo(self)
        self.shadow.setBillboardAxis(2)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        
        self.jbCollNP = None
        
        self.spinIval = None
        
        self.pickupIval = None
        
        self.collectable = collectable
        if self.collectable:
            self.__initialiseCollisions()
            self.spinIval = LerpHprInterval(
                self,
                duration = 0.5,
                hpr = Vec3(360, 0, 0),
                startHpr = Vec3(0, 0, 0)
            )
            self.spinIval.loop()
            
    def getCollNodeName(self):
        return 'jbnode' + str(id(self))
            
    def __initialiseCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 1)
        sphere.setTangible(0)
        node = CollisionNode(self.getCollNodeName())
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.jbCollNP = self.attachNewNode(node)
        
    def allowPickup(self):
        self.acceptOnce('enter' + self.getCollNodeName(), self.__handleCollision)

    def rejectPickup(self):
        self.ignore('enter' + self.getCollNodeName())
        
    def __handleCollision(self, entry):
        self.pickup()

    def pickup(self):
        self.gui.collectedBean()
        self.wrtReparentTo(camera)
        self.setDepthWrite(1)
        self.setDepthTest(1)

        self.particle.wrtReparentTo(render)
        #self.particle.start()
        
        self.particle.setZ(0.5)

        taskMgr.doMethodLater(0.5, self.__stopParticle, 'stopParticle')

        self.shadow.hide()
        
        self.pickupIval = LerpPosInterval(
            self,
            duration = 0.3,
            pos = (-3, 8, 1),
            startPos = self.getPos(camera),
        )
        self.pickupIval.setDoneEvent(self.getCollNodeName())
        self.acceptOnce(self.pickupIval.getDoneEvent(), self.__handleMoveToGuiDone)
        self.pickupIval.start()

    def __stopParticle(self, task):
        self.particle.disable()
        return task.done
        
    def __handleMoveToGuiDone(self):
        self.gui.incrementJbs()
        self.cleanup()
        
    def cleanup(self):
        if self.pickupIval:
            self.ignore(self.pickupIval.getDoneEvent())
            self.pickupIval.finish()
            self.pickupIval = None
        if self.spinIval:
            self.spinIval.finish()
            self.spinIval = None
        if self.jbCollNP:
            self.jbCollNP.removeNode()
            self.jbCollNP = None
        if self.mdl:
            self.mdl.removeNode()
            self.mdl = None
        if self.shadow:
            self.shadow.removeNode()
            self.shadow = None
        self.collectable = None
        self.gui = None

class CrashGUIItem(DirectFrame):
    notify = directNotify.newCategory('CrashGUIItem')
    
    DownZ = -0.25
    UpZ = 0.5
    
    def __init__(self, visItem, visScale, frameX, visX, textX, textZ, textScale, spins = False, font = CIGlobals.getToonFont(),
                 align = TextNode.ACenter):
        DirectFrame.__init__(self, parent = base.a2dTopCenter, pos = (frameX, 0, self.UpZ))
        
        self.frameX = frameX
        
        self.item = visItem
        self.item.flattenLight()
        self.item.setDepthWrite(1)
        self.item.setDepthTest(1)
        self.item.setScale(visScale)
        self.item.setX(visX)
        self.item.reparentTo(self)
        
        self.spinIval = None
        if spins:
            self.spinIval = LerpHprInterval(
                self.item,
                duration = 0.5,
                hpr = Vec3(360, 0, 0),
                startHpr = Vec3(0, 0, 0)
            )
            self.spinIval.loop()
        
        self.text = OnscreenText(parent = self, pos = (textX, textZ, 0),
            scale = textScale, shadow = (0, 0, 0, 1), fg = (0.5, 0.5, 1.0, 1.0), font = font, align = align)
            
        self.fsm = ClassicFSM(
            "ItemFSM",
            [
                State('off', self.enterOff, self.exitOff),
                State('up', self.enterUp, self.exitUp),
                State('up2down', self.enterUp2Down, self.exitUp2Down),
                State('down', self.enterDown, self.exitDown),
                State('down2up', self.enterDown2Up, self.exitDown2Up)
            ],
            "up",
            "off"
        ); self.fsm.enterInitialState()
        
        self.initialiseoptions(CrashGUIItem)
        
    def taskName(self, name):
        return name + "-" + str(id(self))
        
    def enterOff(self):
        pass
        
    def exitOff(self):
        pass
        
    def enterUp(self):
        self.setZ(self.UpZ)
        
    def exitUp(self):
        pass
        
    def enterUp2Down(self):
        self.ival = LerpPosInterval(
            self,
            duration = 0.5,
            pos = (self.frameX, 0, self.DownZ),
            startPos = (self.frameX, 0, self.UpZ),
            name = self.taskName('up2downival'))
        self.ival.setDoneEvent(self.ival.getName())
        self.acceptOnce(self.ival.getDoneEvent(), self.__up2DownDone)
        self.ival.start()
    
    def __up2DownDone(self):
        self.fsm.request('down')
        
    def exitUp2Down(self):
        self.ignore(self.ival.getDoneEvent())
        self.ival.finish()
        del self.ival
        
    def enterDown(self):
        self.setZ(self.DownZ)
        downTime = 3.0
        taskMgr.doMethodLater(downTime, self.__downTask, self.taskName('downTask'))
        
    def __downTask(self, task):
        self.fsm.request('down2up')
        return task.done
        
    def exitDown(self):
        taskMgr.remove(self.taskName('downTask'))
        
    def enterDown2Up(self):
        self.ival = LerpPosInterval(
            self,
            duration = 0.5,
            pos = (self.frameX, 0, self.UpZ),
            startPos = (self.frameX, 0, self.DownZ),
            name = self.taskName('down2upival'))
        self.ival.setDoneEvent(self.ival.getName())
        self.acceptOnce(self.ival.getDoneEvent(), self.__down2UpDone)
        self.ival.start()
    
    def __down2UpDone(self):
        self.fsm.request('up')
        
    def exitDown2Up(self):
        self.ignore(self.ival.getDoneEvent())
        self.ival.finish()
        del self.ival
        
    def setTextText(self, text):
        self.text.setText(text)
        
    def show(self):
        if self.fsm.getCurrentState().getName() in ['up', 'down2up']:
            self.fsm.request('up2down')
        elif self.fsm.getCurrentState().getName() == 'down':
            taskMgr.remove(self.taskName('downTask'))
            self.enterDown()
            
crateAlloc = UniqueIdAllocator(0, 200)

from direct.actor.Actor import Actor
            
class Crate(NodePath, DirectObject):

    def __init__(self, numBeans, pos):
        self.numBeans = numBeans
        NodePath.__init__(self, 'crashCrate')
        self.setPos(pos)

        self.lastHitBotT = 0.0
        self.lastHitTopT = 0.0

        self.beans = []
        
        for i in xrange(numBeans):
            jb = Jellybean(game.gui)
            jb.reparentTo(render)
            jb.setPos(self.getPos(render) + (random.uniform(-1, 1), random.uniform(-1, 1), 0.2))
            game.gui.jbs.append(jb)
            self.beans.append(jb)
        
        self.mdl = Actor('phase_4/models/minigames/cc_opt/crash_crate.egg', {'bounce': 'phase_4/models/minigames/cc_opt/crash_crate-bounce.egg'})
        self.mdl.setScale(1.5)
        self.mdl.reparentTo(self)

        self.shadow = loader.loadModel('phase_3/models/props/square_drop_shadow.bam')
        self.shadow.setScale(0.65)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        self.shadow.reparentTo(self)
        self.shadow.setZ(0.01)
        #self.shadow.setBillboardAxis(2)
        
        self.sound = base.loadSfx("phase_4/audio/sfx/target_trampoline_2.ogg")
        
        self.crateId = crateAlloc.allocate()
        
        self.topName = "top_coll_" + str(self.crateId)
        self.find("**/top_coll").setName(self.topName)
        self.topColl = self.find("**/" + self.topName)
        self.topColl.setCollideMask(CIGlobals.FloorBitmask)
        self.topColl.hide()

        self.botName = "bot_coll_" + str(self.crateId)
        self.find("**/bot_coll").setName(self.botName)
        self.botColl = self.find("**/" + self.botName)
        self.botColl.setCollideMask(CIGlobals.EventBitmask | CIGlobals.WallBitmask)
        self.botColl.hide()
        
        self.sideColl = self.find("**/side_coll")
        self.sideColl.setCollideMask(CIGlobals.WallBitmask)
        self.sideColl.hide()
        
        self.accept("enter" + self.topName, self.__handleJumpedOnCrate)
        self.accept("exit" + self.topName, self.__handleJumpedOffCrate)

        self.accept("enter_overhead_" + self.botName, self.__handleCrateUnderAv)
        self.accept("exit_overhead_" + self.botName, self.__handleCrateNUnderAv)
        
        self.openSeq = Sequence(
        Parallel(
            LerpHprInterval(
                self.find("**/side_1"),
                duration = 1,
                hpr = (-90, 0, 0),
                startHpr = (0, 0, 0),
                blendType = "easeIn"
            ),
            LerpHprInterval(
                self.find("**/side_2"),
                duration = 1,
                hpr = (90, 0, -90),
                startHpr = (90, 0, 0),
                blendType = "easeIn"
            ),
            LerpHprInterval(
                self.find("**/side_3"),
                duration = 1,
                hpr = (0, 0, -90),
                startHpr = (0, 0, 0),
                blendType = "easeIn"
            ),
            LerpHprInterval(
                self.find("**/side_4"),
                duration = 1,
                hpr = (0, 0, 90),
                startHpr = (0, 0, 0),
                blendType = "easeIn"
            ),
            LerpPosInterval(
                self.find("**/top"),
                duration = 0.5,
                pos = (0, 0, 0),
                startPos = lambda self = self: self.find("**/top").getPos(),
                blendType = "easeIn"
            )
        ),
        Wait(2.5),
        Func(self.setTransparency, 1),
        LerpColorScaleInterval(self, duration = 1.0, colorScale = (1, 1, 1, 0), startColorScale = (1, 1, 1, 1)),
        Func(self.cleanup))

        self.ls()
        
        self.reparentTo(render)

    def getHitBottomEvent(self):
        return "hitBottom-" + str(self.crateId)

    def getHitTopEvent(self):
        return "hitTop-" + str(self.crateId)

    def _doCrateBounce(self, direction):
        base.localAvatar.walkControls.lifter.setVelocity(0)
        forceOffset = 0
        if direction:
            force = base.localAvatar.walkControls.avatarControlJumpForce - forceOffset
        else:
            force = -base.localAvatar.walkControls.avatarControlJumpForce + forceOffset
        print force
        base.localAvatar.walkControls.lifter.addVelocity(force)
        messenger.send("jumpStart")
        base.localAvatar.walkControls.isAirborne = 1

    def __handleCrateUnderAv(self, entry = None):

        taskMgr.add(self.__watchUnderneathCrate, "watchUnderCrate" + str(self.crateId))

    def __handleCrateNUnderAv(self, entry = None):
        self._stopWatchUnderneathCrate()

    def __watchUnderneathCrate(self, task):
        #print (base.localAvatar.getZ(self.botColl) + base.localAvatar.getHeight())
        z = base.localAvatar.getZ(self.botColl) + base.localAvatar.getHeight()
        if (z >= -0.1 and base.localAvatar.walkControls.isAirborne):
            # We've hit the bottom of this crate with our head.
            if (globalClock.getFrameTime() - self.lastHitBotT >= 0.05):
                self.lastHitBotT = globalClock.getFrameTime()
                messenger.send(self.getHitBottomEvent())
        
        return task.cont

    def _stopWatchUnderneathCrate(self):
        taskMgr.remove("watchUnderCrate" + str(self.crateId))
        
    def __handleJumpedOnCrate(self, entry = None):
        
        taskMgr.add(self.__watchOnCrate, "watchOnCrate" + str(self.crateId))

    def __watchOnCrate(self, task):
        if (base.localAvatar.getZ(self.topColl) <= 2.2 and base.localAvatar.getZ(self.topColl) >= 0 and base.localAvatar.walkControls.isAirborne):
            if (globalClock.getFrameTime() - self.lastHitTopT >= 0.05):
                self.lastHitTopT = globalClock.getFrameTime()
                messenger.send(self.getHitTopEvent())
            
        return task.cont

    def _stopWatchOnCrate(self):
        taskMgr.remove('watchOnCrate' + str(self.crateId))
        
    def __handleJumpedOffCrate(self, entry = None):
        self._stopWatchOnCrate()
    
    def _openCrate(self):
        self.mdl.stop()

        self.ignore("enter" + self.topName)
        self.ignore("exit" + self.topName)
        self.ignore("enter_overhead_" + self.botName)
        self.ignore("exit_overhead_" + self.botName)
    
        self.topColl.stash()
        self.sideColl.stash()
        self.botColl.stash()
                
        self.openSeq.start()
        
    def cleanup(self):
        self.mdl.removeNode()
        self.removeNode()
        
        self.openSeq.finish()
        del self.openSeq
        del self.sideColl
        del self.topColl
        del self.crateId
        del self.mdl
        del self.sound

class RegularCrate(Crate):

    def __init__(self, numBeans, pos):
        Crate.__init__(self, numBeans, pos)

        self.acceptOnce(self.getHitBottomEvent(), self.__handleHitCrateBot)
        self.acceptOnce(self.getHitTopEvent(), self.__handleHitCrateTop)

    def __handleHitCrate(self):
        base.playSfx(self.sound)
        self._stopWatchOnCrate()
        self._stopWatchUnderneathCrate()
        self._openCrate()

        for bean in self.beans:
            bean.allowPickup()

    def __handleHitCrateBot(self):
        self.__handleHitCrate()
        self._doCrateBounce(0)

    def __handleHitCrateTop(self):
        self.__handleHitCrate()
        self._doCrateBounce(1)

class BouncyCrate(Crate):

    def __init__(self, numBeans, pos):
        self.beansCollected = 0
        Crate.__init__(self, numBeans, pos)

        self.accept(self.getHitBottomEvent(), self.__handleHitCrateBot)
        self.accept(self.getHitTopEvent(), self.__handleHitCrateTop)

    def __handleHitCrateBot(self):
        base.playSfx(self.sound)
        self.beansCollected += 1

        self.mdl.play('bounce')

        if (len(self.beans)):
            bean = random.choice(self.beans)
            bean.pickup()
            self.beans.remove(bean)

        if (len(self.beans) == 0):
            self.ignore(self.getHitBottomEvent())
            self.ignore(self.getHitTopEvent())
            self._stopWatchOnCrate()
            self._stopWatchUnderneathCrate()
            self._openCrate()

        self._doCrateBounce(0)

    def __handleHitCrateTop(self):
        base.playSfx(self.sound)
        self.beansCollected += 1

        self.mdl.play('bounce')

        if (len(self.beans)):
            bean = random.choice(self.beans)
            bean.pickup()
            self.beans.remove(bean)

        if (len(self.beans) == 0):
            self.ignore(self.getHitBottomEvent())
            self.ignore(self.getHitTopEvent())
            self._stopWatchOnCrate()
            self._stopWatchUnderneathCrate()
            self._openCrate()

        self._doCrateBounce(1)

class CrashGUI:
    notify = directNotify.newCategory('CrashGUI')
    
    def __init__(self):
        self.pickupSound = base.loadSfx('phase_4/audio/sfx/MG_maze_pickup.ogg')
        
        jb = loader.loadModel('phase_4/models/props/jellybean4.bam')
        jb.setColor(VBase4(0.3, 0.3, 1.0, 1.0))
        jb.find("**/Jellybeanhilight").stash()
        self.jbItem = CrashGUIItem(jb, 1.0, -1.1, 0, 0.15, -0.07, 0.25, True, CIGlobals.getMickeyFont(), TextNode.ALeft)
        self.jbItem.setTextText("0")
        
        self.frames = [self.jbItem]
        self.jbs = []
        
        self.jbsCollected = 0

        self.incrementsInLine = 0
        
        jbTrans = ((-20, 5, 0), (-20, 7, 0), (-20, 9, 0), (-20, 11, 0), (-20, 13, 0), (-20, 15, 0),
                   (-30, 20, 0), (-30, 22, 0), (-30, 24, 0), (-30, 26, 0), (-30, 28, 0), (-30, 30, 0))
            
        for trans in jbTrans:
            jb = Jellybean(self)
            jb.reparentTo(render)
            jb.setPos(trans)
            jb.allowPickup()
            self.jbs.append(jb)

        self.incrementSeq = Sequence(
            Func(self.__updateJbs),
            SoundInterval(self.pickupSound, duration = self.pickupSound.length() / 2.0)
        )

        taskMgr.add(self.__processIncrements, "processJBIncrements")
            
        #self.jbs[len(self.jbs) - 1].place()

    def __updateJbs(self):
        self.jbsCollected += 1
        self.jbItem.setTextText(str(self.jbsCollected))

    def __processIncrements(self, task):
        if (self.incrementsInLine > 0):
            # Process the next increment.
            if (not self.incrementSeq.isPlaying()):
                self.incrementSeq.start()
                self.incrementsInLine -= 1

        return task.cont
            
    def collectedBean(self):
        self.jbItem.show()
        
    def incrementJbs(self):
        self.incrementsInLine += 1
        
    def showAll(self):
        for frame in self.frames:
            frame.show()

from direct.interval.IntervalGlobal import ActorInterval
import random

class LocalCrashToon:
    notify = directNotify.newCategory("LocalCrashToon")

    def __init__(self, toon):
        self.toon = toon
        self.jumpSound = base.loadSfx("resources/phase_3.5/audio/sfx/AV_jump.wav")

        self.didFlip = False

        self.jumpStSeq = Sequence(
            Func(self.jumpSound.play),
            ActorInterval(self.toon, 'zstart', startFrame = 12),
            Func(self.toon.loop, 'zhang')
        )

        self.flipPivot = self.toon.attachNewNode('pivot')
        self.flipPivot.setZ(self.toon.getHeight() / 2.0)
        self.flipSeq = Parallel(Sequence(Func(self.toon.shadow.hide), LerpHprInterval(
            self.flipPivot,
            duration = 0.45,
            hpr = (0, 0, 0),
            startHpr = (0, 360, 0),
            blendType = 'easeOut'
        ), Func(self.toon.shadow.show)),
        Sequence(
            ActorInterval(self.toon, 'zstart', startFrame = 20, endFrame = 5, playRate = 3.0),
            ActorInterval(self.toon, 'zstart', startFrame = 5, endFrame = 20, playRate = 2.0),
            Func(self.toon.loop, 'zhang')
        ))

        self.jumpEnSeq = None

    def enableAvatarControls(self):
        self.toon.enableAvatarControls()
        self.toon.ignore('jumpStart')
        self.toon.ignore('jumpLand')
        self.toon.ignore('jumpHardLand')

        self.toon.accept('jumpStart', self.__handleJumpStart)
        self.toon.accept('jumpLand', self.__handleJumpLand)
        self.toon.accept('jumpHardLand', self.__handleJumpLand)

    def __handleJumpStart(self):
        if (self.jumpEnSeq):
            self.jumpEnSeq.pause()
            self.jumpEnSeq = None

        self.toon.setAnimState('off')
        self.jumpStSeq.start()

        num = random.randint(0, 1)
        if (num == 0):
            taskMgr.doMethodLater(0.25, self.__doFlip, 'doFlip')

    def __doFlip(self, task):
        spd, rot, sli = self.toon.walkControls.getSpeeds()
        if (spd or rot or sli):
            self.jumpSound.play()
            self.toon.getGeomNode().wrtReparentTo(self.flipPivot)
            self.flipSeq.start()
            self.didFlip = True
        return task.done

    def __handleJumpLand(self):
       if (self.jumpEnSeq):
           self.jumpEnSeq.finish()
           self.jumpEnSeq = None

       if (self.jumpStSeq):
           self.jumpStSeq.finish()
        
       if (self.didFlip):
           taskMgr.remove('doFlip')
           self.flipSeq.finish()
           self.toon.getGeomNode().wrtReparentTo(self.toon)
           self.didFlip = False

       spd, rot, sli = self.toon.walkControls.getSpeeds()
       self.jumpEnSeq = Sequence(
                    ActorInterval(self.toon, 'zend', startFrame = 3, playRate = 1.0 if (not spd and not rot and not sli) else 3.0),
                    Func(self.toon.setAnimState, 'Happy')
       )
       self.jumpEnSeq.start()
            
from src.coginvasion.cogtropolis.NURBSMopath import NURBSMopath

SPPlatform = 56
            
class Game:
    
    def __init__(self):
        self.gui = None
        self.mopath = None
        self.platform = None
        self.platformNode = None

        self.lLineSeg = None
        self.rLineSeg = None
        
        self.crates = []
        
        self.music = base.loadMusic('phase_4/audio/bgm/MG_Crash_brrrgh.ogg')

        self.dnaStore = DNAStorage()
        loadDNAFile(self.dnaStore, 'phase_4/dna/storage.pdna')
        loadDNAFile(self.dnaStore, 'phase_5/dna/storage_town.pdna')
        loadDNAFile(self.dnaStore, 'phase_8/dna/storage_BR.pdna')
        loadDNAFile(self.dnaStore, 'phase_8/dna/storage_BR_town.pdna')

        node = loadDNAFile(self.dnaStore, 'phase_4/dna/test_brrrgh_ch_lvl.pdna')

        if node.getNumParents() == 1:
            geom = NodePath(node.getParent(0))
            geom.reparentTo(hidden)
        else:
            geom = hidden.attachNewNode(node)
        gsg = base.win.getGsg()
        if gsg:
            geom.prepareScene(gsg)
        geom.setName('test_level')
        geom.reparentTo(render)
        
        self.olc = ZoneUtil.getOutdoorLightingConfig(CIGlobals.TheBrrrgh)
        self.olc.setupAndApply()

        self.area = geom
        self.area.setH(90)

        self.lastCamPos = Point3(0, 0, 0)
        self.lastCamHpr = Vec3(0, 0, 0)
        self.lastCamNodeH = 0.0

        self.camNode = render.attachNewNode('crashCamNode')
        camera.reparentTo(self.camNode)


        base.minigame = self

        

        #self.camCurve = loader.loadModel('crash_test_cam_path.egg')
        #self.camMoPath = NURBSMopath(self.camCurve)
        #self.camMoPath.node = camera

        #self.camNodes = self.camMoPath.evaluator.getVertices()

                         #       X   Y   Z    H 
        self.camNodes = [VBase4(-20, 0, 7.5, 0), VBase4(-20, 130, 7.5, -90),
                         VBase4(60, 130, 7.5, -90)]

        self.localAv = LocalCrashToon(base.localAvatar)

        #base.transitions.noTransitions()
        #base.enableMouse()

        #base.localAvatar.stopSmartCamera()
        #base.localAvatar.detachCamera()

        #self.cra = Actor('phase_4/models/minigames/crash_crate.egg', {'bounce': 'phase_4/models/minigames/crash_crate-bounce.egg'})
        #self.cra.reparentTo(render)
        #self.cra.loop('bounce')
        #self.cra.setPos(100, 100, 0)
        #self.cra.ls()
        
        base.acceptOnce('s', self.start)
    
    def teleInDone(self):
        base.localAvatar.setAnimState('Happy')
        self.localAv.enableAvatarControls()
        base.localAvatar.startTrackAnimToSpeed()
        #Sequence(
        #    #ActorInterval(self.toon, 'zstart', startFrame = 20, endFrame = 5, playRate = 3.0),
        #    ActorInterval(base.localAvatar, 'zstart', startFrame = 20, endFrame = 5, playRate = 2.0),
        #    ActorInterval(base.localAvatar, 'zstart', startFrame = 5, endFrame = 20, playRate = 2.0),
        #    Func(base.localAvatar.loop, 'zhang')
        #).start()
        
    def __handleSteppedOnPlatform(self, entry):
        curve = self.area.find('**/platform_path')
        #base.localAvatar.disableAvatarControls()
        self.platformNode.ls()
        base.localAvatar.reparentTo(self.platformNode)
        base.localAvatar.setPos(0, 0, 0)
        mopath = NURBSMopath(curve)
        mopath.play(self.platformNode, duration = 10.0, rotate = False)

    def projectPositionOnRail(self, pos):
        closestNodeIndex = self.getClosestNode(pos)

        numVerts = len(self.camNodes)
        verts = []
        for i in xrange(numVerts):
            vert = self.camNodes[i]
            verts.append(Point3(vert.getX(), vert.getY(), vert.getZ()))

        if (closestNodeIndex == 0):
            trans = self.projectOnSegment(verts[0], verts[1], pos)
            return VBase4(trans.getX(), trans.getY(), trans.getZ(), self.camNodes[0].getW())
        elif (closestNodeIndex == numVerts - 1):
            trans = self.projectOnSegment(verts[numVerts - 1], verts[numVerts - 2], pos)
            return VBase4(trans.getX(), trans.getY(), trans.getZ(), self.camNodes[closestNodeIndex].getW())
        else:
            leftSeg = self.projectOnSegment(verts[closestNodeIndex - 1], verts[closestNodeIndex], pos)
            rightSeg = self.projectOnSegment(verts[closestNodeIndex + 1], verts[closestNodeIndex], pos)

            if (self.lLineSeg):
                self.lLineSeg.removeNode()
                self.lLineSeg = None
            if (self.rLineSeg):
                self.rLineSeg.removeNode()
                self.rLineSeg

            linesegs = LineSegs('visualL')
            linesegs.setColor(1, 0, 0, 1)
            linesegs.drawTo(pos)
            linesegs.drawTo(leftSeg)
            node = linesegs.create(False)
            #self.lLineSeg = render.attachNewNode(node)

            linesegs = LineSegs('visualR')
            linesegs.setColor(0, 0, 1, 1)
            linesegs.drawTo(pos)
            linesegs.drawTo(rightSeg)
            node = linesegs.create(False)
            #self.rLineSeg = render.attachNewNode(node)

            
            if ((pos - leftSeg).lengthSquared() <= (pos - rightSeg).lengthSquared()):
                return VBase4(leftSeg.getX(), leftSeg.getY(), leftSeg.getZ(), self.camNodes[closestNodeIndex - 1].getW())
            else:
                return VBase4(rightSeg.getX(), rightSeg.getY(), rightSeg.getZ(), self.camNodes[closestNodeIndex + 1].getW())

    def getClosestNode(self, pos):
        closestNodeIndex = 0
        shortestDistance = 0.0

        for i in xrange(len(self.camNodes)):
            vert = self.camNodes[i]
            vert = Point3(vert.getX(), vert.getY(), vert.getZ())
            sqrDistance = (vert - pos).lengthSquared()
            if (shortestDistance == 0.0 or sqrDistance < shortestDistance):
                shortestDistance = sqrDistance
                closestNodeIndex = i

        return closestNodeIndex

    def projectOnSegment(self, v1, v2, pos):
        v1ToPos = pos - v1
        segDir = v2 - v1
        segDir.normalize()

        distanceFromV1 = segDir.dot(v1ToPos)
        if (distanceFromV1 < 0.0):
            return v1
        elif (distanceFromV1 * distanceFromV1 > (v2 - v1).lengthSquared()):
            return v2
        else:
            fromV1 = segDir * distanceFromV1
            return v1 + fromV1

    def __camTask(self, task):
        lerpRatio = 0.15
        lerpRatio = 1 - pow(1 - lerpRatio, globalClock.getDt() * 30.0)
        trans = self.projectPositionOnRail(base.localAvatar.getPos())
        pos = Point3(trans.getX(), trans.getY(), trans.getZ())
        self.lastCamPos = pos * lerpRatio + self.lastCamPos * (1 - lerpRatio)
        self.camNode.setPos(self.lastCamPos)

        h = trans.getW()
        self.lastCamNodeH = h * lerpRatio + self.lastCamNodeH * (1 - lerpRatio)
        self.camNode.setH(self.lastCamNodeH)

        #camera.headsUp(base.localAvatar)
        #camera.setP(-5)

        currCamHpr = camera.getHpr()
        camera.lookAt(base.localAvatar, 0, 0, base.localAvatar.getHeight())
        goalHpr = camera.getHpr()
        camera.setHpr(currCamHpr)

        self.lastCamHpr = goalHpr * lerpRatio + self.lastCamHpr * (1 - lerpRatio)
        camera.setHpr(self.lastCamHpr)


        
        return task.again

    def start(self):
        self.gui = CrashGUI()
        self.gui.showAll()
        
        #self.platformNode = loader.loadModel('crash_platform.bam')
        #self.platformNode.reparentTo(render)
        #self.platformNode.setPosHpr(1.23, 66.51, 0, 90, 0, 0)
        
        #self.area.ls()
        #self.area.find('**/platform').removeNode()
        #self.area.find('**/platform_coll').removeNode()

        for i in xrange(len(self.camNodes)):
            vert = self.camNodes[i]
            smiley = loader.loadModel('models/smiley.egg.pz')
            #smiley.reparentTo(render)
            smiley.setPos(vert.getX(), vert.getY(), vert.getZ())

        taskMgr.add(self.__camTask, "camtask")
        
        regCrateTrans = ((-35, 30, 0), (-15, 10, 0),
        (-27, 45, 0), (-22, 45, 0), (-17, 45, 0),(-12, 45, 0))#, (25, 20, 0), (33, 10, 0), (33, 20, 0), (20, 16, 0))

        bouCrateTrans = ((-5, 20, 0), (-5, 20, 13), (-20, 100, 0), (-20, 100, 13))
        
        for trans in regCrateTrans:
            beans = random.randint(1, 4)
            c = RegularCrate(beans, trans)
            self.crates.append(c)

        for trans in bouCrateTrans:
            beans = random.randint(15, 15)
            c = BouncyCrate(beans, trans)
            self.crates.append(c)

        self.crates[len(self.crates) - 1].shadow.removeNode()

        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()


        base.localAvatar.destroyControls()

        wc = CrashWalker(legacyLifter = False)
        wc.setWallBitMask(CIGlobals.WallBitmask)
        wc.setFloorBitMask(CIGlobals.FloorBitmask)
        wc.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce
        )
        wc.initializeCollisions(base.cTrav, base.localAvatar, floorOffset=0.025, reach=4.0)
        wc.setAirborneHeightFunc(base.localAvatar.getAirborneHeight)

        base.localAvatar.walkControls = wc

        base.localAvatar.setPos(-20, 0, 0)
        
        base.localAvatar.setAnimState('teleportIn', callback = self.teleInDone)
        
        base.localAvatar.smartCamera.setCameraPositionByIndex(4)
        base.playMusic(self.music, looping = 1, volume = 0.7)
        
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        #base.enableMouse()

        base.camLens.setMinFov(70.0 / (4./3.))

        camera.reparentTo(self.camNode)
        camera.setPos(0, -20, 0)

        #base.oobe()

        base.transitions.fadeIn(0.2)
        
        #base.acceptOnce('enterplatform_coll', self.__handleSteppedOnPlatform)

game = Game()

#base.cTrav.showCollisions(render)

base.run()
