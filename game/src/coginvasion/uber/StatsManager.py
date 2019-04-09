from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

class StatsManager(DistributedObjectGlobal):
    
    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
