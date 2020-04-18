from panda3d.core import NodePath

from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class TriggerTransitionAI(DistributedEntityAI):

    """
    Brush entity that marks all entities within its volume as preserved,
    which make the entity transition to the next level.
    """

    def preserveContainedEntities(self):
        for i in range(self.bspLoader.getNumEntities()):
            ent = self.bspLoader.getEntity(i)

            preserveIt = False

            if isinstance(ent, NodePath):
                if ent.isPreservable() and self.cEntity.isInside(ent.getPos(NodePath())):
                    # Entity is inside our volume, preserve it
                    preserveIt = True
                    
            self.bspLoader.markEntityPreserved(i, preserveIt)
