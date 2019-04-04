"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PositionExaminer.py
@author Brian Lach
@date August 03, 2015

"""

from direct.showbase.DirectObject import DirectObject

from panda3d.core import NodePath

from panda3d.bullet import BulletGhostNode, BulletSphereShape

from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

class PositionExaminer(DirectObject, NodePath):

    def __init__(self):
        try:
            self.__initialized
            return
        except:
            self.__initialized = 1

        NodePath.__init__(self, hidden.attachNewNode('PositionExaminer'))
        
        bsph = BulletSphereShape(1.5)
        bgh = BulletGhostNode('positionExaminer_sphereGhost')
        bgh.addShape(bsph)
        bgh.setKinematic(True)
        self.cSphereNodePath = self.attachNewNode(bgh)

    def delete(self):
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def consider(self, node, pos, eyeHeight):
        self.reparentTo(node)
        self.setPos(pos)
        
        result = None
        
        floorLineStart = self.getPos(render) + (0, 0, 0.1)
        floorLineEnd = floorLineStart - (0, 0, 10000)
        floorResult = base.physicsWorld.rayTestClosest(floorLineStart, floorLineEnd, CIGlobals.FloorMask)
        if floorResult.hasHit():
            floorPoint = self.getRelativePoint(render, floorResult.getHitPos())
            if abs(floorPoint[2]) <= 4.0:
                pos += floorPoint
                
                self.setPos(pos)
                
                base.physicsWorld.attach(self.cSphereNodePath.node())
                self.cSphereNodePath.node().setTransformDirty()
                sphereContactResult = base.physicsWorld.contactTest(self.cSphereNodePath.node())
                base.physicsWorld.remove(self.cSphereNodePath.node())
                
                wallEntry = False
                
                for iContact in xrange(sphereContactResult.getNumContacts()):
                    contact = sphereContactResult.getContact(iContact)
                    node0 = NodePath(contact.getNode0())
                    node1 = NodePath(contact.getNode1())
                    
                    if (node0 == self.cSphereNodePath and
                    not base.localAvatar.isAncestorOf(node1) and
                    not node.isAncestorOf(node1)):
                        
                        if not (node1.getCollideMask() & CIGlobals.WallGroup).isZero():
                            wallEntry = True
                            break
                            
                    elif (node1 == self.cSphereNodePath and
                    not base.localAvatar.isAncestorOf(node0) and
                    not node.isAncestorOf(node0)):
                        
                        if not (node0.getCollideMask() & CIGlobals.WallGroup).isZero():
                            wallEntry = True
                            break
                            
                if not wallEntry:
                    lineStart = render.getRelativePoint(self, (0, 0, eyeHeight))
                    lineEnd = render.getRelativePoint(self, (-pos[0], -pos[1], eyeHeight))
                    lineResult = PhysicsUtils.rayTestClosestNotMe(node, lineStart, lineEnd, CIGlobals.WallGroup)
                    if not lineResult:
                        result = pos
                        
        self.reparentTo(hidden)
        return result
