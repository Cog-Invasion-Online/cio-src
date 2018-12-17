from panda3d.core import NodePath, ModelNode

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

class Entity(NodePath):
    notify = directNotify.newCategory("Entity")
    
    def __init__(self):
        NodePath.__init__(self, ModelNode("entity"))
        #DirectObject.__init__(self)
        self.loaded = False
        self.cEntity = None
        self.outputs = []
        self.bspLoader = None
        
    def entityTaskName(self, taskName):
        return taskName + "-" + str(self.getEntnum())
        
    def getEntnum(self):
        assert self.cEntity
        return self.cEntity.getEntnum()
        
    def getEntityValue(self, key):
        assert self.bspLoader
        assert self.cEntity
        
        return self.bspLoader.getEntityValue(self.cEntity.getEntnum(), key)
        
    def getEntityValueInt(self, key):
        assert self.bspLoader
        assert self.cEntity
        
        return self.bspLoader.getEntityValueInt(self.cEntity.getEntnum(), key)
        
    def getEntityValueFloat(self, key):
        assert self.bspLoader
        assert self.cEntity
        
        return self.bspLoader.getEntityValueFloat(self.cEntity.getEntnum(), key)
        
    def getEntityValueVector(self, key):
        assert self.bspLoader
        assert self.cEntity
        
        return self.bspLoader.getEntityValueVector(self.cEntity.getEntnum(), key)
        
    def getEntityValueColor(self, key):
        assert self.bspLoader
        assert self.cEntity
        
        return self.bspLoader.getEntityValueColor(self.cEntity.getEntnum(), key)
        
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
        self.bspLoader.getEntityKeyvalues(keyvalues, self.cEntity.getEntnum())
        for k, v in keyvalues:
            if k[:2] != "On":
                continue
            data = v.split(',')
            if len(data) != 5:
                continue
            self.outputs.append({'output': k, 'target': data[0], 'input': data[1],
                                 'parameter': data[2], 'delay': float(data[3]),
                                 'once': bool(int(data[4])), 'active': True})
                                 
        self.dispatchOutput("OnSpawn")
                                     
    def unload(self):
        self.loaded = False
        self.outputs = None
        self.cEntity = None
        #self.ignoreAll()
