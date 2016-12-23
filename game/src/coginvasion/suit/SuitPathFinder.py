# Filename: SuitPathFinder.py
# Created by:  blach (20Aug15)
#
# An implementation of the A* path finding algorithm for Cogs.

from src.coginvasion.globals import CIGlobals
import types

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

def get_path(start_key, target_key, nodes):
    path = []

    for node in nodes:
        if node.key == start_key:
            start_node = node
        elif node.key == target_key:
            target_node = node

    current_node = target_node
    while (current_node.parent != start_node):
        path.append(current_node.key)
        current_node = current_node.parent
    path.append(start_key)
    return list(reversed(path))

def find_path(pointDict, pathData, start_key, target_key):
    start_point = pointDict[start_key]
    target_point = pointDict[target_key]

    nodes = []
    open_nodes = []
    closed_nodes = []
    node_class_by_key = {}

    for key, point in pointDict.items():
        g_cost = get_distance(point, start_point)
        h_cost = get_distance(point, target_point)
        node = Node(g_cost, h_cost, key, point)
        node_class_by_key[key] = node
        nodes.append(node)

    open_nodes.append(node_class_by_key[start_key])

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
            return get_path(start_key, target_key, nodes)

        neighbor_keys = pathData[current.key]
        for neighbor_key in neighbor_keys:

            isClosed = False
            for node in closed_nodes:
                if node.key == neighbor_key:
                    isClosed = True
                    break
            if isClosed:
                continue

            neighbor = node_class_by_key[neighbor_key]

            nm_cost_2_neighbor = current.g_cost + get_distance(current.point, neighbor.point)
            if (not neighbor in open_nodes) or \
            (nm_cost_2_neighbor < neighbor.g_cost):
                neighbor.g_cost = nm_cost_2_neighbor
                neighbor.h_cost = get_distance(target_point, neighbor.point)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.parent = current

                if not neighbor in open_nodes:
                    open_nodes.append(neighbor)
