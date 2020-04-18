from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class ScriptEnvironment:
    
    def __init__(self, targetEnt, scriptEnt, src):
        self.target = targetEnt
        self.script = scriptEnt
        self.src = src
        self.seq = None
        
    def addScriptTask(self, func, extraArgs = []):
        self.script.scriptTasks[func] = taskMgr.add(func, self.script.entityTaskName("script_task"), extraArgs = [self] + extraArgs, appendTask = True)
        
    def removeScriptTask(self, func):
        if func in self.script.scriptTasks:
            self.script.scriptTasks[func].remove()
            del self.script.scriptTasks[func]
        
    def finishScript(self, fromEntity = False):
        if self.seq:
            self.seq.pause()
        self.seq = None
        if not fromEntity:
            if self in self.script.scriptEnvirons:
                self.script.scriptEnvirons.remove(self)
        
    def run(self):
        seq = None
        exec(self.src)
        print seq
        self.seq = seq

class LogicScriptAI(DistributedEntityAI):
    
    SF_ExecuteImmediately = 1

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.scriptFilename = ""
        self.scriptSrc = ""
        self.target = None
        self.scriptTasks = {}
        self.scriptEnvirons = []
        self.clientSide = False
        
    def load(self):
        DistributedEntityAI.load(self)
        
        from panda3d.core import VirtualFileSystem
        vfs = VirtualFileSystem.getGlobalPtr()
        self.scriptSrc = vfs.readFile(self.scriptFilename, True)
        
        self.target = self.bspLoader.getPyEntityByTargetName(self.getEntityValue("scriptTarget"))
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        if self.hasSpawnFlags(self.SF_ExecuteImmediately):
            self.ExecuteScript()
        
    def loadEntityValues(self):
        self.scriptFilename = self.getEntityValue("scriptFilename")
        
    def ExecuteScript(self, target = None):
        if not target:
            target = self.target
        if self.scriptSrc is not None:
            environ = ScriptEnvironment(target, self, self.scriptSrc)
            environ.run()
            self.scriptEnvirons.append(environ)
            
        self.dispatchOutput("OnScriptExecute")
        
    def FinishScript(self, fromScript = False, sendOp = True):
        if not fromScript:
            for environ in self.scriptEnvirons:
                environ.finishScript()
            self.scriptEnvirons = []
        if sendOp:
            self.dispatchOutput("OnScriptFinish")
        
    def delete(self):
        for task in self.scriptTasks.values():
            task.remove()
        self.FinishScript(sendOp = False)
        self.scriptEnvirons = None
        self.scriptTasks = None
        self.target = None
        self.scriptFilename = None
        self.scriptSrc = None
        DistributedEntityAI.delete(self)
