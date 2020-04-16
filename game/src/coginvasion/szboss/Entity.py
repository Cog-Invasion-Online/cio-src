from panda3d.core import NodePath, ModelNode

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.base.Precache import Precacheable

class Entity(NodePath, Precacheable):
    notify = directNotify.newCategory("Entity")
    
    def __init__(self):
        NodePath.__init__(self, ModelNode("entity"))
        #DirectObject.__init__(self)
        self.loaded = False
        self.cEntity = None
        self.outputs = []
        self.bspLoader = None
        self.spawnflags = 0

    def hasSpawnFlags(self, flags):
        return (self.spawnflags & flags) != 0

    def getCEntity(self):
        return self.cEntity

    def getLoader(self):
        return self.bspLoader

    def entityTaskName(self, taskName):
        return taskName + "-entity_" + str(self.getBspEntnum())

    def getBspEntnum(self):
        assert self.cEntity
        return self.cEntity.getBspEntnum()

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
                target = self.bspLoader.getPyEntityByTargetName(op['target'])
                if target:
                    if hasattr(target, op['input']) and callable(getattr(target, op['input'])):
                        taskMgr.doMethodLater(op['delay'], self.task_dispatchOutput, "dispatchOutput-" + str(id(op)),
                                              extraArgs = [target, op, extraArgs], appendTask = True)
                        if op['once']:
                            op['active'] = False

    def load(self):
        self.loaded = True

        if hasattr(base, 'bspLoader') and not self.bspLoader:
            self.bspLoader = base.bspLoader

        keyvalues = []
        self.bspLoader.getEntityKeyvalues(keyvalues, self.cEntity.getBspEntnum())
        for k, v in keyvalues:
            if k[:2] != "On":
                continue
            data = v.split(',')
            if len(data) != 5:
                continue
            self.outputs.append({'output': k, 'target': data[0], 'input': data[1],
                                 'parameter': data[2], 'delay': float(data[3]),
                                 'once': bool(int(data[4])), 'active': True})

        self.spawnflags = self.getEntityValueInt("spawnflags")

        self.dispatchOutput("OnSpawn")

    def unload(self):
        self.loaded = False
        self.outputs = None
        self.cEntity = None
        #self.ignoreAll()
