# Filename: DistributedPieTurretAI.py
# Created by:  blach (14Jun15)
# Updated by:  DecodedLogic (10Aug15)

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.distributed.ClockDelta import globalClockDelta
from direct.task.Task import Task

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI

class DistributedPieTurretAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory('DistributedPieTurretAI')
    maximumRange = 40
    
    MAX_TARGETS = 8
    SCAN_TIME = 2
    ABANDON_PIES = 4

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.owner = 0
        self.mgr = None
        
        # This is to optimize the turrets.
        self.targets = []
        self.shooting = False
        
        # This is for abandoning targets.
        self.initialTargetHealth = 0
        self.piesShot = 0
        self.currentTarget = None
        self.deathEvent = None
        
    def announceGenerate(self):
        self.deathEvent = self.uniqueName('DistributedPieTurretAI-dead')
        
    def getDeathEvent(self):
        return self.deathEvent

    def setManager(self, mgr):
        self.mgr = mgr

    def getManager(self):
        return self.mgr
    
    def resetTurret(self):
        self.shooting = False
        self.currentTarget = None
        self.initialTargetHealth = 0
        self.piesShot = 0
    
    def selectTargets(self):
        if self.isDead() or self.shooting == True:
            return
        
        # Let's search for some targets.
        suitId2range = {}
        self.targets = []
        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if obj.zoneId == self.zoneId:
                if className == 'DistributedSuitAI':
                    if not obj.isDead():
                        suitId2range[obj.doId] = obj.getDistance(self)
                        
        # Let's organize the suits by distance.
        ranges = []
        for distance in suitId2range.values():
            ranges.append(distance)
        ranges.sort()
        
        # Let's see if there's some suits that match our criteria.
        for suitId in suitId2range.keys():
            distance = suitId2range[suitId]
            suit = self.air.doId2do.get(suitId)
            if len(self.targets) < self.MAX_TARGETS:
                if suit.getDistance(self) < self.maximumRange and not suit.isDead():
                    self.targets.append(self.air.doId2do.get(suitId))
            else: break
            
        # If we found some targets, let's shoot the closest one.
        if len(self.targets) > 0:
            self.__shootClosestTarget()

    def setHealth(self, hp):
        DistributedAvatarAI.setHealth(self, hp)
        if hp < 1:
            self.getManager().sendUpdateToAvatarId(self.getOwner(), 'yourTurretIsDead', [])
            self.sendUpdate('die', [])
            Sequence(Wait(2.0), Func(self.getManager().killTurret, self.doId)).start()

    def startScanning(self, afterShoot = 0):
        if not self.isDead():
            timestamp = globalClockDelta.getFrameNetworkTime()
            self.sendUpdate('scan', [timestamp, afterShoot])
            base.taskMgr.add(self.__scan, self.uniqueName('DistributedPieTurretAI-scan'))
            
    def shootTarget(self, target, task):
        self.shooting = True
        base.taskMgr.removeTasksMatching(self.uniqueName('DistributedPieTurretAI-scan'))
        
        def resumeScanning():
            self.track = Sequence(Wait(self.SCAN_TIME), Func(self.startScanning, 1))
            self.track.start()
        
        # Let's defeat our target!
        if self.currentTarget == target and self.isTargetReachable(target) and not self.shouldAbandon(target):
            self.sendUpdate('shoot', [target.doId])
            self.piesShot += 1
            task.delayTime = 0.5
            self.shooting = True
            return Task.again
        
        if self.currentTarget != target:
            return Task.done
        
        self.shooting = False
        
        # All done, let's remove this target.
        if target in self.targets:
            self.targets.remove(target)
        
        if len(self.targets) > 0:
            # Let's see if we have anymore good targets we can fire at.
            for nextTarget in self.targets:
                if self.isTargetReachable(nextTarget):
                    # Great! We don't have to search for another target.
                    self.currentTarget = nextTarget
                    self.initialTargetHealth = nextTarget.getHealth()
                    self.piesShot = 0
                    base.taskMgr.add(self.shootTarget, self.uniqueName('DistributedPieTurretAI-shootTarget'), extraArgs = [nextTarget], appendTask = True)
                    return Task.done
                self.targets.remove(nextTarget)
        resumeScanning()
        return Task.done
            
    def __shootClosestTarget(self):
        if not self.isDead() and self.shooting == False:
            for target in self.targets:
                if self.isTargetReachable(target):
                    # We found a target, let's shoot at him.
                    self.resetTurret()
                    self.initialTargetHealth = target.getHealth()
                    self.currentTarget = target
                    base.taskMgr.removeTasksMatching(self.uniqueName('DistributedPieTurretAI-scan'))
                    base.taskMgr.add(self.shootTarget, self.uniqueName('DistributedPieTurretAI-shootTarget'), extraArgs = [target], appendTask = True)
                    break
                else:
                    # This target is unreachable, let's remove him.
                    self.targets.remove(target)

    def __scan(self, task):
        if not self.isDead():
            self.selectTargets()
            task.delayTime = self.SCAN_TIME
            return Task.again
        return Task.done

    def setOwner(self, avId):
        self.owner = avId

    def d_setOwner(self, avId):
        self.sendUpdate('setOwner', [avId])

    def b_setOwner(self, avId):
        self.d_setOwner(avId)
        self.setOwner(avId)

    def getOwner(self):
        return self.owner
    
    def isTargetReachable(self, target):
        return not target.isDead() and not target.isEmpty() and target.getDistance(self) <= self.maximumRange
    
    def shouldAbandon(self, target):
        if self.piesShot == self.ABANDON_PIES and self.initialTargetHealth == target.getHealth():
            return True
        return False

    def disable(self):
        base.taskMgr.removeTasksMatching(self.uniqueName('DistributedPieTurretAI-scan'))
        base.taskMgr.removeTasksMatching(self.uniqueName('DistributedPieTurretAI-shootClosestTarget'))
        self.owner = None
        self.mgr = None
        self.targets = None
        self.shooting = None
        self.initialTargetHealth = None
        self.piesShot = None
        self.currentTarget = None
        self.deathEvent = None
        DistributedSmoothNodeAI.disable(self)
        DistributedAvatarAI.disable(self)