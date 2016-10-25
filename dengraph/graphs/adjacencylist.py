from __future__ import absolute_import
from dengraph import graph


class AdjacencyGraph(graph.Graph):
    def __init__(self, nodes, adjacency):
        self._nodes = set(nodes)
        self._adjacency = adjacency or {}  # {node: [(neighbour, distance), (neighbour, distance), ...], ...}
        assert all(node in self._nodes for node in self._adjacency), 'parameter adjacency must list node distances'

    def __contains__(self, node):
        return node in self._nodes

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, start_end):
        start, end = start_end
        try:
            adjacency = self._adjacency[start]
        except KeyError:
            raise graph.NoSuchEdge
        else:
            for node, distance in adjacency:
                if node == end:
                    return distance
            raise graph.NoSuchEdge

    def __iter__(self):
        return iter(self._nodes)

    def get_neighbours(self, node, distance):
        neighbours = []
        try:
            adjacency = self._adjacency[node]
        except KeyError:
            return neighbours
        else:
            for neighbour, dist in adjacency:
                if dist <= distance:
                    neighbours.append(neighbour)
                else:
                    break
            return neighbours
