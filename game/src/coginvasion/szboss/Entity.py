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
        
    def task_dispatchOutput(self, target, op, task):
        param = op['parameter']
        params = param.split(';') if len(param) > 0 else []
        getattr(target, op['input']).__call__(*params)
        return task.done
        
    def dispatchOutput(self, outputName):
        for op in self.outputs:
            if op['output'] == outputName and op['active']:
                target = self.bspLoader.getPyEntityByTargetName(op['target'])
                if target:
                    if hasattr(target, op['input']) and callable(getattr(target, op['input'])):
                        taskMgr.doMethodLater(op['delay'], self.task_dispatchOutput, "dispatchOutput-" + str(id(op)),
                                              extraArgs = [target, op], appendTask = True)
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
        self.ignoreAll()
