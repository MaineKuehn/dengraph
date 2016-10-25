from __future__ import absolute_import
from dengraph import graph


class DistanceGraph(graph.Graph):
    """
    Graph of nodes connected by a distance function
    """
    def __init__(self, nodes, distance, symmetric=True):
        self._nodes = set(nodes)
        self.distance = distance
        self.symmetric = symmetric
        self._distance_values = {}

    def __contains__(self, node):
        return node in self._nodes

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            assert item.step is None, '%s does not support stride argument for edges' % self.__class__.__name__
            node_from, node_to = item.start, item.stop
            # Since we don't know the type of nodes, we cannot test
            # node_to > node_from to detect swapped pairs. Since we
            # *do* store nodes in a `set`, they must support hash.
            if self.symmetric and hash(node_to) > hash(node_from):
                node_to, node_from = node_from, node_to
            try:
                return self._distance_values[node_from, node_to]
            except KeyError:
                self._compute_distance(node_from, node_to)
                return self._distance_values[node_from, node_to]
        else:
            raise TypeError('Not an edge: %s' % item)

    def __setitem__(self, item, value):
        raise TypeError('%s does not support edge assignment' % self.__class__.__name__)

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            raise TypeError('%s does not support edge deletion' % self.__class__.__name__)
        else:
            try:
                self._nodes.remove(item)
            except KeyError:
                raise graph.NoSuchNode
            else:
                # clean up all stored distances
                for node in self:
                    self._distance_values.pop(item, node)
                    if self.symmetric:
                        continue
                    self._distance_values.pop(node, item)

    def _compute_distance(self, node_from, node_to, force=False):
        if not force and (node_from, node_to) in self._distance_values:
            return
        self._distance_values[node_from, node_to] = self.distance(node_from, node_to)

    def __iter__(self):
        return iter(self._nodes)

    def get_neighbours(self, node, distance):
        neighbours = [candidate for candidate in self if self[node:candidate] <= distance and candidate != node]
        neighbours.sort()
        return neighbours

    def insert_node(self, node):
        self._nodes.add(node)

    def insert_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'insert_edge'))

    def remove_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'remove_edge'))

    def modify_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'modify_edge'))
