"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedUnoTable.py
@author Maverick Liberty
@date March 25, 2018

"""

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import NodePath

from src.coginvasion.globals.CIGlobals import SPRender

class DistributedUnoTable(DistributedNode):
    notify = directNotify.newCategory('DistributedUnoTable')
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'd_unoTable')
        self.table = None
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.table = loader.loadModel('phase_6/models/golf/picnic_table.bam')
        self.table.reparentTo(self)
        
        self.setParent(SPRender)
        
    def delete(self):
        DistributedNode.delete(self)
        if self.table:
            self.table.removeNode()
    