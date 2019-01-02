from DistributedEntity import DistributedEntity

class DistributedTriggerOnce(DistributedEntity):

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.watchTask = None
        self.wasInside = False

    def load(self):
        DistributedEntity.load(self)
        self.watchTask = taskMgr.add(self._triggerTask, self.uniqueName("triggerTask"))

    def _triggerTask(self, task):
        inside = self.cEntity.isInside(base.localAvatar.getPos(render))
        if inside and not self.wasInside:
            self.sendUpdate('onPlayerEnter')
            self.wasInside = True
        elif not inside and self.wasInside:
            self.sendUpdate('onPlayerExit')
            self.wasInside = False

        return task.cont

    def unload(self):
        DistributedEntity.unload(self)
        if self.watchTask:
            self.watchTask.remove()
            self.watchTask = None
        self.wasInside = None

class DistributedTriggerMultiple(DistributedTriggerOnce):
    pass
