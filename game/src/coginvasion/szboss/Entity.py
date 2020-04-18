from panda3d.core import NodePath, ModelNode, Point3, Vec3, AudioSound

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.base.Precache import Precacheable
from src.coginvasion.phys import PhysicsUtils

class Entity(NodePath, Precacheable):
    notify = directNotify.newCategory("Entity")
    
    NeedNode = True
    
    def __init__(self, initNode = True):
        if initNode:
            NodePath.__init__(self, ModelNode("entity"))
        self.loaded = False
        self.cEntity = None
        self.outputs = []
        self.bspLoader = None
        self.spawnflags = 0
        self.entState = 0
        self.nextThink = 0.0
        self.lastThink = 0.0
        self.targetName = ""
        self.entnum = 0
        self.entStateTime = 0.0
        self.modelPath = ""
        self.modelIsAnimating = False
        self.modelOrigin = Point3(0)
        self.modelAngles = Vec3(0)
        self.modelScale = Point3(1)
        self.model = None
        self.sequence = None
        self.mapEnt = False
        self.sounds = {}
        
    def getIsMapEnt(self):
        return self.mapEnt
        
    def parentGenerated(self):
        print "Parent generated for", self, self.getParentEntity()
        self.tryEntityParent()
        
    def tryEntityParent(self):
        if not self.NeedNode:
            return
            
        try:
            parent = self.getParentEntity()
            if parent == render:
                self.reparentTo(render)
            else:
                self.wrtReparentTo(parent)
        except:
            self.reparentTo(render)
        
    def setupBrushEntityPhysics(self):
        pass
        #base.brushCollisionMaterialData.update(PhysicsUtils.makeBulletCollFromGeoms(self.cEntity.getModelNp()))
        
    def hasParentEntity(self):
        return len(self.getEntityValue("parent")) > 0
        
    def getParentEntity(self):
        if not self.hasParentEntity():
            return render
        return self.bspLoader.getPyEntityByTargetName(self.getEntityValue("parent"))
        
    def transitionXform(self, destLandmarkNP, mat):
        self.setMat(destLandmarkNP, mat)
        
    def isPreservable(self):
        return False

    def getModel(self):
        return [self.modelPath, self.modelIsAnimating]
        
    def getModelScale(self):
        return [self.modelScale[0], self.modelScale[1], self.modelScale[2]]
        
    def getModelOrigin(self):
        return [self.modelOrigin[0], self.modelOrigin[1], self.modelOrigin[2]]
        
    def getModelAngles(self):
        return [self.modelAngles[0], self.modelAngles[1], self.modelAngles[2]]

    def getFrameTime(self):
        return globalClock.getFrameTime()
        
    def getSound(self, name):
        return self.sounds[name]
        
    def isSoundPlaying(self, name):
        if name in self.sounds and self.sounds[name]:
            return self.sounds[name].status() == AudioSound.PLAYING
        return False
        
    def addSound(self, name, soundPath, spatialized = True, setLoop = False, node = None):
        if not node:
            node = self
        if spatialized:
            self.sounds[name] = base.loadSfxOnNode(soundPath, node)
        else:
            self.sounds[name] = loader.loadSfx(soundPath)
        self.sounds[name].setLoop(setLoop)
        
    def stopSound(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].stop()
            
    def stopAllSounds(self):
        if self.sounds:
            for sound in self.sounds.values():
                sound.stop()
        
    def playSound(self, name, volume = 1.0):
        if name in self.sounds:
            self.sounds[name].setVolume(volume)
            self.sounds[name].setLoop(False)
            self.sounds[name].play()
            
    def loopSound(self, name, volume = 1.0):
        if name in self.sounds:
            self.sounds[name].setVolume(volume)
            self.sounds[name].setLoop(True)
            self.sounds[name].play()
        
    def clearSequence(self):
        if self.sequence:
            self.sequence.finish()
        self.sequence = None
        
    def setSequence(self, seq, loop = False, startNow = True):
        self.clearSequence()
        self.sequence = seq
        if startNow:
            if loop:
                self.sequence.loop()
            else:
                self.sequence.start()
        
    def clearModel(self):
        if self.model:
            if isinstance(self.model, Actor):
                self.model.cleanup()
            else:
                self.model.removeNode()
        self.model = None
        
    def setModel(self, mdlPath, animating = False):
        self.clearModel()
        self.modelIsAnimating = animating
        if isinstance(mdlPath, str):
            self.modelPath = mdlPath
            if len(mdlPath) == 0:
                return
            if animating:
                self.model = Actor(mdlPath, flattenable = 0)
            else:
                self.model = loader.loadModel(mdlPath)
        else:
            # Assume it's an already loaded Actor/Model.
            self.model = mdlPath
        self.model.reparentTo(self)
        
    def enableModelCollisions(self):
        if self.model:
            base.createAndEnablePhysicsNodes(self.model)
            
    def disableModelCollisions(self):
        if self.model:
            base.disableAndRemovePhysicsNodes(self.model)
        
    def setModelOrigin(self, origin):
        self.modelOrigin = Point3(origin)
        if self.model:
            self.model.setPos(origin)
            
    def setModelAngles(self, angles):
        self.modelAngles = Vec3(angles)
        if self.model:
            self.model.setHpr(angles)
            
    def setModelScale(self, scale):
        self.modelScale = Point3(scale)
        if self.model:
            self.model.setScale(scale)
            
    def optimizeModel(self):
        if self.model:
            self.model.clearModelNodes()
            self.model.flattenStrong()
        
    def getModelNP(self):
        return self.model
        
    def getTargetName(self):
        return self.targetName
        
    def setNextThink(self, delay):
        self.nextThink = delay
        self.lastThink = globalClock.getFrameTime()
        
    def getNextThink(self):
        return self.nextThink
        
    def shouldThink(self):
        return self.nextThink >= 0 and globalClock.getFrameTime() - self.lastThink >= self.nextThink
        
    def setEntityState(self, state):
        self.entState = state
        self.entStateTime = globalClock.getFrameTime()
        
    def getEntityStateElapsed(self):
        return globalClock.getFrameTime() - self.entStateTime
        
    def getEntityState(self):
        return self.entState
        
    def __thinkTask(self, task):
        if self.shouldThink():
            self.lastThink = globalClock.getFrameTime()
            self.nextThink = 0.0
            self.think()
            
        return task.cont
            
    def think(self):
        pass

    def hasSpawnFlags(self, flags):
        return (self.spawnflags & flags) != 0

    def getCEntity(self):
        return self.cEntity

    def getLoader(self):
        return self.bspLoader
        
    def entityTaskName(self, taskName):
        if hasattr(self, 'doId'):
            entnum = self.doId
        elif self.mapEnt:
            entnum = self.getEntnum()
        else:
            entnum = id(self)
        return taskName + "-entity_" + str(entnum)
        
    def getEntnum(self):
        return self.entnum
        
    def getEntityValue(self, key):
        assert self.cEntity
        
        return self.cEntity.getEntityValue(key)
        
    def getEntityValueInt(self, key):
        assert self.cEntity
        
        try:
            return int(self.cEntity.getEntityValue(key))
        except:
            return 0

    def getEntityValueBool(self, key):
        assert self.cEntity
        
        try:
            return bool(int(self.cEntity.getEntityValue(key)))
        except:
            return False
        
    def getEntityValueFloat(self, key):
        assert self.cEntity
        
        try:
            return float(self.cEntity.getEntityValue(key))
        except:
            return 0.0
        
    def getEntityValueVector(self, key):
        assert self.cEntity
        
        return self.cEntity.getEntityValueVector(key)
        
    def getEntityValueColor(self, key):
        assert self.cEntity
        
        return self.cEntity.getEntityValueColor(key)
        
    def task_dispatchOutput(self, target, op, extraArgs, task):
        param = op['parameter']
        params = param.split(';') if len(param) > 0 else []
        params += extraArgs
        getattr(target, op['input']).__call__(*params)
        return task.done
        
    def dispatchOutput(self, outputName, extraArgs = []):
        for op in self.outputs:
            if op['output'] == outputName and op['active']:
                target = None
                if 'targetName' in op:
                    target = self.bspLoader.getPyEntityByTargetName(op['targetName'])
                elif 'target' in op:
                    target = op['target']
                if target:
                    if hasattr(target, op['input']) and callable(getattr(target, op['input'])):
                        taskMgr.doMethodLater(op['delay'], self.task_dispatchOutput, "dispatchOutput-" + str(id(op)),
                                              extraArgs = [target, op, extraArgs], appendTask = True)
                        if op['once']:
                            op['active'] = False
                            
    def connectOutput(self, outputName, inputEntity, inputName, parameter = "", onceOnly = False, delay = 0.0):
        self.outputs.append({'output': outputName, 'target': inputEntity,
                             'input': inputName, 'parameter': parameter,
                             'delay': delay, 'once': onceOnly, 'active': True})
        
    def load(self):
        self.loaded = True
        
        if hasattr(base, 'bspLoader') and not self.bspLoader:
            self.bspLoader = base.bspLoader

        if self.mapEnt:
            self.entnum = self.cEntity.getBspEntnum()
            
            keyvalues = []
            self.bspLoader.getEntityKeyvalues(keyvalues, self.cEntity.getBspEntnum())
            for k, v in keyvalues:
                if k[:2] != "On":
                    continue
                data = v.split(',')
                if len(data) != 5:
                    continue
                self.outputs.append({'output': k, 'targetName': data[0], 'input': data[1],
                                     'parameter': data[2], 'delay': float(data[3]),
                                     'once': bool(int(data[4])), 'active': True})

            self.spawnflags = self.getEntityValueInt("spawnflags")
                                     
            self.dispatchOutput("OnSpawn")

    def enableThink(self):
        taskMgr.add(self.__thinkTask, self.entityTaskName("think"))
                                     
    def unload(self):
        taskMgr.remove(self.entityTaskName("think"))
        self.stopAllSounds()
        self.sounds = None
        self.clearSequence()
        self.disableModelCollisions()
        self.clearModel()
        self.loaded = None
        self.cEntity = None
        self.outputs = None
        self.bspLoader = None
        self.spawnflags = None
        self.entState = None
        self.nextThink = None
        self.lastThink = None
        self.targetName = None
        self.entnum = None
        self.modelOrigin = None
        self.modelAngles = None
        self.modelScale = None
        self.modelPath = None
        self.modelIsAnimating = None
        #self.removeNode()
