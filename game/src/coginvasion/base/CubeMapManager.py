"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CubeMapManager.py
@author Brian Lach
@date September 25, 2017

"""

from panda3d.core import TextureStage, Point3, NodePath, TexGenAttrib

from direct.directnotify.DirectNotifyGlobal import directNotify

class CubeMap:

    def __init__(self, baseFile, position):
        self.baseFile = baseFile
        self.position = position
        self.cubeTex = loader.loadCubeMap(baseFile)
        self.cubeStage = TextureStage('cube-' + baseFile + "-stage")
        self.cubeStage.setMode(TextureStage.MModulate)

    def cleanup(self):
        self.baseFile = None
        self.position = None
        self.cubeTex = None
        self.cubeStage = None

class Node:

    def __init__(self, np):
        self.nodePath = np
        self.currentCube = None

    def clearCurrentCube(self):
        if self.currentCube:
            if self.nodePath and not self.nodePath.isEmpty():
                self.nodePath.clearTexture(self.currentCube.cubeStage)
                self.nodePath.clearTexGen(self.currentCube.cubeStage)
            self.currentCube = None

    def setCurrentCube(self, cube):
        self.clearCurrentCube()

        self.currentCube = cube

        if self.nodePath and not self.nodePath.isEmpty():
            self.nodePath.setTexGen(self.currentCube.cubeStage, TexGenAttrib.MWorldCubeMap)
            self.nodePath.setTexture(self.currentCube.cubeStage, self.currentCube.cubeTex)

    def cleanup(self):
        self.clearCurrentCube()
        self.nodePath = None

class CubeMapManager:
    notify = directNotify.newCategory("CubeMapManager")

    def __init__(self):
        # Nodes that want cube maps applied and updated on them.
        self.nodes = []
        self.cubeMaps = []

        taskMgr.add(self.__tick, "cubeMapManager.__tick")

    def __tick(self, task):
        for node in self.nodes:
            if not node.nodePath or node.nodePath.isEmpty():
                self.nodes.remove(node)
                return task.cont

            # Find the closest cube map to this node.
            sortedCubes = list(self.cubeMaps)
            sortedCubes.sort(key = lambda cube: (node.nodePath.getPos(render) - cube.position).lengthSquared())

            # Closest cube is the first element.
            closestCube = sortedCubes[0]
            if closestCube != node.currentCube:
                node.setCurrentCube(closestCube)

        return task.cont

    def addCubeMap(self, baseFile, position = Point3(0, 0, 0)):
        cm = CubeMap(baseFile, position)
        self.cubeMaps.append(cm)

    def addNode(self, node):
        if not isinstance(node, NodePath):
            self.notify.warning("addNode: non-NodePath object cannot be added!")
            return

        if not node.isEmpty():
            self.nodes.append(Node(node))

    def clearAll(self):
        self.clearNodes()
        self.clearCubeMaps()

    def clearNodes(self):
        for node in self.nodes:
            node.cleanup()

        self.nodes = []

    def clearCubeMaps(self):
        for cm in self.cubeMaps:
            cm.cleanup()

        self.cubeMaps = []

