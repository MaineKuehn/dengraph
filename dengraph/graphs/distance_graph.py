from __future__ import absolute_import
from dengraph import graph
import dengraph.utilities.pretty


class DistanceGraph(graph.Graph):
    r"""
    Graph of nodes connected by a distance function

    :param nodes: all nodes contained in the graph
    :param distance: a function `dist(a, b)->object` that computes the distance between any two nodes
    :param symmetric: whether distance can be treated as symmetric, i.e. `dist(a, b) == dist(b, a)`

    :warning: For N nodes, all NxN edges are exposed. This may lead to
              O(N\ :sup:2\ ) runtime complexity.
    """
    def __init__(self, nodes, distance, symmetric=True):
        self._nodes = set(nodes)
        self.distance = distance
        self.symmetric = symmetric

    def __contains__(self, item):
        # a:b -> slice -> edge
        if item.__class__ == slice:
            node_from, node_to = item.start, item.stop
            return node_from in self._nodes and node_to in self._nodes
        # node
        return item in self._nodes

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            assert item.step is None, '%s does not support stride argument for edges' % self.__class__.__name__
            node_from, node_to = item.start, item.stop
            if node_from not in self._nodes:
                raise graph.NoSuchEdge  # first edge node
            elif node_to not in self._nodes:
                raise graph.NoSuchEdge  # second edge node
            # Since we don't know the type of nodes, we cannot test
            # node_to > node_from to detect swapped pairs. Since we
            # *do* store nodes in a `set`, they must support hash.
            if self.symmetric and hash(node_to) > hash(node_from):
                node_to, node_from = node_from, node_to
            return self.distance(node_from, node_to)
        else:
            if item not in self:
                raise dengraph.graph.NoSuchNode
            return {candidate: self[item:candidate] for candidate in self if candidate != item}

    def __setitem__(self, item, value):
        if value or isinstance(item, slice):
            raise TypeError('%s does not support edge assignment' % self.__class__.__name__)
        else:
            self._nodes.add(item)

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            raise TypeError('%s does not support edge deletion' % self.__class__.__name__)
        else:
            try:
                self._nodes.remove(item)
            except KeyError:
                raise graph.NoSuchNode

    def __iter__(self):
        return iter(self._nodes)

    def get_neighbours(self, node, distance=graph.ANY_DISTANCE):
        if node not in self._nodes:
            raise graph.NoSuchNode
        if distance is graph.ANY_DISTANCE:
            return (candidate for candidate in self if candidate != node)
        else:
            return (candidate for candidate in self if self[node:candidate] <= distance and candidate != node)

    def __add__(self, other):
        if isinstance(self, other.__class__) and self.distance == other.distance:
            return self.__class__(self._nodes.union(other), self.distance, self.symmetric and other.symmetric)
        return NotImplemented

    def __repr__(self):
        return '%s(distance=%r, symmetric=%r, nodes=%s)' % (
            self.__class__.__name__,
            self.distance,
            self.symmetric,
            dengraph.utilities.pretty.repr_container(self._nodes)
        )


class CachedDistanceGraph(DistanceGraph):
    r"""
    Graph of nodes connected by a cached distance function

    Compared to :py:class:`~DistanceGraph`, each edge is computed only once and
    stored for future lookup. Edges can be "deleted", which sets their value to
    an infinite value.

    :param nodes: all nodes contained in the graph
    :param distance: a function `dist(a, b)->object` that computes the distance between any two nodes
    :param symmetric: whether distance can be treated as symmetric, i.e. `dist(a, b) == dist(b, a)`

    :warning: For N nodes, all NxN edges are exposed and stored. This may lead
              to O(N\ :sup:2\ ) runtime and memory complexity.
    """
    def __init__(self, nodes, distance, symmetric=True):
        super(CachedDistanceGraph, self).__init__(nodes, distance, symmetric)
        self._distance_values = {}

    def __getitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            assert item.step is None, '%s does not support stride argument for edges' % self.__class__.__name__
            node_from, node_to = item.start, item.stop
            if node_from not in self._nodes:
                raise graph.NoSuchEdge  # first edge node
            elif node_to not in self._nodes:
                raise graph.NoSuchEdge  # second edge node
            # Since we don't know the type of nodes, we cannot test
            # node_to > node_from to detect swapped pairs. Since we
            # *do* store nodes in a `set`, they must support hash.
            if self.symmetric and hash(node_to) > hash(node_from):
                node_to, node_from = node_from, node_to
            try:
                return self._distance_values[node_from, node_to]
            except KeyError:
                self._distance_values[node_from, node_to] = self.distance(node_from, node_to)
                return self._distance_values[node_from, node_to]
        else:
            return super(CachedDistanceGraph, self).__getitem__(item)

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            node_from, node_to = item.start, item.stop
            if node_from not in self._nodes:
                raise graph.NoSuchEdge  # first edge node
            elif node_to not in self._nodes:
                raise graph.NoSuchEdge  # second edge node
            if self.symmetric and hash(node_to) > hash(node_from):
                node_to, node_from = node_from, node_to
            self._distance_values[node_from, node_to] = float("Inf")
        else:
            try:
                self._nodes.remove(item)
            except KeyError:
                raise graph.NoSuchNode
            else:
                # clean up all stored distances
                for node in self:
                    self._distance_values.pop((item, node), None)
                    if self.symmetric:
                        continue
                    self._distance_values.pop((node, item), None)
