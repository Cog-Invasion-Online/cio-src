from panda3d.core import NodePath, ModelNode

from Entity import Entity

class AmbientGeneric(Entity):
    
    def __init__(self):
        Entity.__init__(self)
        self.assign(NodePath(ModelNode('ambientGeneric')))
        self.node().setPreserveTransform(ModelNode.PTLocal)

        self.sndFile = None
        
    def load(self):
        Entity.load(self)
        
        loader = self.cEntity.getLoader()
        self.reparentTo(base.bspLoader.getResult())
        
        entnum = self.cEntity.getEntnum()
        self.sndFile = base.loadSfxOnNode(loader.getEntityValue(entnum, "message"), self)
        self.sndFile.setLoop(True)
        self.sndFile.setVolume(loader.getEntityValueFloat(entnum, "health"))
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        self.sndFile.play()

    def unload(self):
        Entity.unload(self)
        
        if self.sndFile:
            self.sndFile.stop()
            base.audio3d.detachSound(self.sndFile)
            self.sndFile = None
