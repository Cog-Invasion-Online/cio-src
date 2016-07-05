# Filename: suitPathFinding.py
# Created by:  blach (20Aug15)
from panda3d.core import *
loadPrcFile('config/config_client.prc')
from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from lib.coginvasion.globals import CIGlobals

import time

class Node:

    def __init__(self, g_cost, h_cost, key, point):
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.key = key
        self.point = point
        self.parent = None

def get_distance(point1, point2):
    return (point1.getXy() - point2.getXy()).length()

def get_path(start_key, target_key):
    path = []

    for node in nodes:
        if node.key == start_key:
            start_node = node
        elif node.key == target_key:
            target_node = node

    current_node = target_node
    while (current_node.parent != start_node):
        print current_node.key
        path.append(current_node.key)
        current_node = current_node.parent
    path.append(start_key)
    return list(reversed(path))

def find_path(area, start_key, target_key):
    start_point = CIGlobals.SuitSpawnPoints[area][start_key]
    target_point = CIGlobals.SuitSpawnPoints[area][target_key]

    nodes = []
    open_nodes = []
    closed_nodes = []

    for key, point in CIGlobals.SuitSpawnPoints[area].items():
        g_cost = get_distance(point, start_point)
        h_cost = get_distance(point, target_point)
        node = Node(g_cost, h_cost, key, point)
        nodes.append(node)

    for node in nodes:
        if node.key == start_key:
            open_nodes.append(node)

    while len(open_nodes):
        f_cost_list = []
        for node in open_nodes:
            f_cost_list.append(node.f_cost)

        lowest_f_cost = min(f_cost_list)

        current = None
        for node in open_nodes:
            if lowest_f_cost == node.f_cost:
                current = node

        open_nodes.remove(current)
        closed_nodes.append(current)

        if current.key == target_key:
            return get_path(start_key, target_key)

        neighbor_keys = CIGlobals.SuitPathData[area][current.key]
        for neighbor_key in neighbor_keys:
            neighbor = None
            isClosed = False
            for node in closed_nodes:
                if node.key == neighbor_key:
                    isClosed = True
                    break
            if isClosed:
                continue
            for node in nodes:
                if node.key == neighbor_key:
                    neighbor = node
                    break
            nm_cost_2_neighbor = current.g_cost + get_distance(current.point, neighbor.point)
            if (not neighbor in open_nodes) or \
            (nm_cost_2_neighbor < neighbor.g_cost):
                neighbor.g_cost = nm_cost_2_neighbor
                neighbor.h_cost = get_distance(target_point, neighbor.point)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.parent = current
                if not neighbor in open_nodes:
                    open_nodes.append(neighbor)

import timeit
                    
print timeit.timeit("find_path(CIGlobals.ToontownCentral, '31', '31')", number = 1)

from lib.coginvasion.suit.Suit import Suit
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.distributed.ClientRepository import ClientRepository
from panda3d.core import *
"""
base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
base.cr.isShowingPlayerIds = False

suit = Suit()
suit.generateSuit("A", "mrhollywood", "s", 132, 0, False)
suit.loop("walk")
suit.reparentTo(render)

eyeLight = Spotlight('eyes')
eyeLens = PerspectiveLens()
eyeLens.setMinFov(70.0 / (4./3.))
eyeLight.setLens(eyeLens)
eyeNode = suit.headModel.attachNewNode(eyeLight)
eyeNode.setZ(-5)
eyeNode.setY(-4.5)

def checkInView(task):
    if eyeNode.node().isInView(camera.getPos(eyeNode)):
        print "In view!"
    return task.cont

taskMgr.add(checkInView, "checkInView")
"""
"""
current_path_index = 0

def walk():
    global current_path_index
    current_path_index += 1
    if len(the_path) <= current_path_index:
        print "Done walking"
        return
    key = the_path[current_path_index]
    endPoint = CIGlobals.SuitSpawnPoints[CIGlobals.ToontownCentral][key]
    oldKey = the_path[current_path_index - 1]
    startPoint = CIGlobals.SuitSpawnPoints[CIGlobals.ToontownCentral][oldKey]
    ival = NPCWalkInterval(suit, endPoint, 0.2, startPoint)
    ival.setDoneEvent('testIvalDone')
    base.acceptOnce('testIvalDone', walk)
    ival.start()

    print "walking!"

walk()
"""
base.run()
