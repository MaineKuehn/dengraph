from __future__ import absolute_import

import dengraph.graph
import dengraph.utilities.iterutils
import dengraph.compat


class AdjacencyGraph(dengraph.graph.Graph):
    """
    Graph storing distances via adjacency lists

    :param source: adjacency mapping or graph
    :param max_distance: maximum allowed distance

    There are multiple formats to provide adjacency information via `source`:

    Adjacency Mapping
        The most straightforward way for initialization is to provide adjacency
        in a mapping format with `distance = source[node_from][node_to]`.

    Graph
        Any subclass of :py:class:`~dengraph.graph.Graph`; complexity depends
        on the graph's implementation of `iter(graph)`, `graph.get_neighbours`
        and `graph[node_from:node_to]`.
    """
    def __init__(self, source, max_distance=dengraph.graph.ANY_DISTANCE):
        self._adjacency = {}  # {node: {neighbour: distance, neighbour: distance, ...}, ...}
        if isinstance(source, dengraph.graph.Graph):
            self._adjacency.update(self._adjacency_from_graph(source, max_distance))
        elif isinstance(source, dengraph.compat.collections_abc.Mapping):
            self._adjacency.update(self._adjacency_from_dict(source, max_distance))

    @staticmethod
    def _adjacency_from_graph(graph, max_distance):
        adjacency = {}
        for node in graph:
            adjacency[node] = {other: graph[node:other] for other in graph.get_neighbours(node, max_distance)}
        return adjacency

    @staticmethod
    def _adjacency_from_dict(adjacency_dict, max_distance):
        adjacency = {}
        for node, neighbours in dengraph.utilities.iterutils.iteritems(adjacency_dict):
            if max_distance is dengraph.graph.ANY_DISTANCE:
                adjacency[node] = {other: neighbours[other] for other in neighbours}
            else:
                adjacency[node] = {other: neighbours[other] for other in neighbours if neighbours[other] <= max_distance}
        return adjacency

    def __contains__(self, item):
        # a:b -> slice -> edge
        if item.__class__ == slice:
            node_from, node_to = item.start, item.stop
            return node_from in self._adjacency and node_to in self._adjacency[node_from]
        # node
        return item in self._adjacency

    def __len__(self):
        return len(self._adjacency)

    def __getitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            assert item.step is None, '%s does not support stride argument for edges' % self.__class__.__name__
            node_from, node_to = item.start, item.stop
            try:
                return self._adjacency[node_from][node_to]
            except KeyError:
                raise dengraph.graph.NoSuchEdge
        else:
            raise TypeError('Not an edge: %s' % item)

    def __setitem__(self, item, value):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            node_from, node_to = item.start, item.stop
            if node_to not in self._adjacency:
                raise dengraph.graph.NoSuchEdge  # second edge node
            try:
                self._adjacency[node_from][node_to] = value
            except KeyError:
                raise dengraph.graph.NoSuchEdge  # first edge node
        # g[a] = {b: 3, c: 4, d: 6}
        else:
            if item not in self._adjacency:
                self._adjacency[item] = value.copy()
            else:
                self._adjacency[item].update(value)

    def __iter__(self):
        return iter(self._adjacency)

    def get_neighbours(self, node, distance=dengraph.graph.ANY_DISTANCE):
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
