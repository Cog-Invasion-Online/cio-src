########################################
# Filename: DistributedGunGameCapturePoint.py
# Created by: DecodedLogic (17Apr16)
########################################

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.interval.LerpInterval import LerpScaleInterval

from pandac.PandaModules import NodePath, CollisionSphere, CollisionNode
from pandac.PandaModules import TransparencyAttrib

from lib.coginvasion.minigame import GunGameGlobals as GGG

class DistributedGunGameCapturePoint(DistributedNode):
    notify = directNotify.newCategory('DistributedGunGameCapturePoint')
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'capture_point')
        self.capturePoint = None
        self.captureCircle = None
        self.aoogahSfx = None
        self.circleTrack = None
        self.circleTrackPlayRate = 1.0
        self.circleTrackDirection = 0

        self.team = None
        self.collNP = None
        self.pointCollNode = None
        
        self.neutralCapTexture = None
        self.redCapTexture = None
        self.blueCapTexture = None
        self.defCapTexture = None
        
    def delete(self):
        self.ignoreAll()
        if self.collNP:
            self.collNP.removeNode()
        if self.capturePoint:
            self.capturePoint.removeNode()
        if self.captureCircle:
            self.captureCircle.removeNode()
        if self.aoogahSfx:
            self.aoogahSfx.stop()
        if self.circleTrack:
            self.circleTrack.pause()
        del self.collNP
        del self.pointCollNode
        del self.capturePoint
        del self.captureCircle
        del self.aoogahSfx
        del self.circleTrack
        del self.circleTrackPlayRate
        del self.circleTrackDirection
        del self.team
        del self.neutralCapTexture
        del self.redCapTexture
        del self.blueCapTexture
        del self.defCapTexture
        self.removeNode()
        DistributedNode.delete(self)
        
    def getCircleScaleAnim(self, startScale, scale, duration = 1.5):
        return Sequence(
            LerpScaleInterval(self.captureCircle, startScale = startScale, scale = scale, duration = duration),
            Func(self.captureCircle.setColorScale, 0.976, 0, 0, 0.5), 
            Wait(0.25), 
        Func(self.captureCircle.setColorScale, 1, 1, 1, 0.5))
        
    def startCircleAnim(self, direction, timestamp):
        timestamp = 0
        # Begins the circle track in a certain direction.
        if self.circleTrack:
            self.circleTrack.pause()
            self.circleTrack = None

        self.circleTrackPlayRate = 1.0
        self.circleTrackDirection = direction
        
        if self.circleTrackDirection == 3:
            self.captureCircle.hide()
            return
        
        self.circleTrack = Sequence(Func(self.captureCircle.show))
            
        # Let's do the growing animation.
        if direction == 0:
            self.circleTrack = Sequence(Func(self.captureCircle.show),
                Func(self.captureCircle.setColorScale, 1, 1, 1, 0.5),
                LerpScaleInterval(self.captureCircle, startScale = 0.75, scale = 3.75, duration = 7.5),
                Func(self.captureCircle.setColorScale, 0.976, 0, 0, 0.5), 
                Wait(0.25), 
                Func(self.captureCircle.setColorScale, 1, 1, 1, 0.5),
                Wait(0.25), 
            Func(self.captureCircle.hide))
            self.circleTrack.start(timestamp)
            return
        elif direction == 1:
            # Let's do the shrinking animation.
            self.circleTrack = Sequence(
                Func(self.captureCircle.show),
                Func(self.captureCircle.setColorScale, 0.976, 0, 0, 0.5), 
                Wait(0.25), 
            Func(self.captureCircle.setColorScale, 1, 1, 1, 0.5))
            
            self.circleTrack.append(self.getCircleScaleAnim(3.75, 3.25))
            self.circleTrack.append(self.getCircleScaleAnim(3.25, 2.75))
            self.circleTrack.append(self.getCircleScaleAnim(2.75, 2.25))
            self.circleTrack.append(self.getCircleScaleAnim(2.25, 1.75))
            self.circleTrack.append(self.getCircleScaleAnim(1.75, 1.25))
            self.circleTrack.append(self.getCircleScaleAnim(1.25, 0.75))
        elif direction == 2:
            # Let's do the reset animation when a new toon fails to capture it.
            self.circleTrack = Sequence()
            self.circleTrack.append(self.getCircleScaleAnim(self.captureCircle.getScale(), 0.75, 1.0))
            self.circleTrack.append(Sequence(Wait(0.25), Func(self.captureCircle.hide)))
            self.circleTrack.start()
            return
        
        self.circleTrack.append(Sequence(Wait(0.25), Func(self.captureCircle.hide)))
        self.circleTrack.start()
        
    def handleContesters(self, contesters):
        if self.circleTrack:
            if self.circleTrackDirection == 1:
                self.circleTrack.pause()
                self.circleTrackPlayRate = self.circleTrackPlayRate + contesters
                self.circleTrack.setPlayRate(self.circleTrackPlayRate)
                self.circleTrack.resume()
            else:
                if contesters > 0 and not self.team:
                    self.circleTrack.pause()
                else:
                    self.circleTrack.resume()
                    
    def updateStatus(self, status, avId):
        if avId != 0:
            avatar = base.cr.doId2do.get(avId)

        if status == 0:
            base.minigame.showAlert('The hill is being contested!')
            self.aoogahSfx.play()
        elif status == 1:
            base.minigame.showAlert('%s has captured the hill!' % avatar.getName())
        elif status == 2:
            base.minigame.showAlert('The hill has been reset!')
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.capturePoint = loader.loadModel('phase_4/models/props/capture_point.bam')
        self.capturePoint.setScale(2.5)
        self.capturePoint.reparentTo(self)
        
        self.captureCircle = loader.loadModel('phase_4/models/minigames/ice_game_score_circle.bam')
        self.captureCircle.setAlphaScale(0.5)
        self.captureCircle.setTransparency(TransparencyAttrib.MAlpha)
        self.captureCircle.reparentTo(self)
        self.captureCircle.setPos(self.capturePoint.getPos(render))
        self.captureCircle.setX(self.captureCircle.getX() - 0.03)
        self.captureCircle.setY(self.captureCircle.getY() - 0.1)
        self.captureCircle.setZ(self.captureCircle.getZ() + 2.4)
        self.captureCircle.hide()
        self.captureCircle.setTextureOff(1)
        
        self.aoogahSfx = loader.loadSfx('phase_5/audio/sfx/AA_sound_aoogah.ogg')
        
        sphere = CollisionSphere(0, 0, 0, 4)
        sphere.setTangible(0)
        self.pointCollNode = CollisionNode(self.uniqueName('coll_node'))
        self.pointCollNode.addSolid(sphere)
        self.pointCollNode.setCollideMask(GGG.HILL_BITMASK)
        self.collNP = self.capturePoint.attachNewNode(self.pointCollNode)
        
        self.neutralCapTexture = loader.loadTexture('phase_4/maps/neutral_capture_point.jpg')
        self.redCapTexture = loader.loadTexture('phase_4/maps/red_capture_point.jpg')
        self.blueCapTexture = loader.loadTexture('phase_4/maps/blue_capture_point.jpg')
        self.defCapTexture = loader.loadTexture('phase_4/maps/captured_capture_point.jpg')
        
        self.reparentTo(render)
        
    def startListening(self):
        self.accept('enter' + self.uniqueName('coll_node'), self.requestEnter)
        self.accept('exit' + self.uniqueName('coll_node'), self.requestExit)
        
    def setCaptured(self, teamId):
        textureSection = self.capturePoint.find('**/capture_point')
        if (teamId - 2) in GGG.TeamNameById.values():
            self.team = (teamId - 2)
            
            if self.team == GGG.RED:
                textureSection.setTexture(self.redCapTexture, 1)
            elif self.team == GGG.BLUE:
                textureSection.setTexture(self.blueCapTexture, 1)
        elif (teamId - 2) == -2:
            self.team = None
            textureSection.setTexture(self.neutralCapTexture, 1)
        elif (teamId - 2) == -1:
            self.team = None
            textureSection.setTexture(self.defCapTexture, 1)
        self.captureCircle.setTextureOff(1)
            
    def getCaptured(self):
        return self.team
        
    def requestEnter(self, entry):
        if hasattr(self, 'capturePoint') and self.capturePoint:
            self.sendUpdate('requestEnter')
        
    def requestExit(self, entry):
        if hasattr(self, 'capturePoint') and self.capturePoint:
            self.sendUpdate('requestExit')
        