from __future__ import absolute_import

import itertools
import dengraph.graph
import dengraph.utilities.pretty
import dengraph.compat


class AdjacencyGraph(dengraph.graph.Graph):
    """
    Graph storing distances via adjacency lists

    :param source: adjacency mapping or graph
    :param max_distance: maximum allowed distance

    There are multiple formats to provide adjacency information via `source`:

    Adjacency :py:class:`Mapping`
        The most straightforward way for initialization is to provide adjacency
        in a mapping format with `distance = source[node_from][node_to]`.

    :py:class:`~dengraph.graph.Graph`
        Any subclass of :py:class:`~dengraph.graph.Graph`; complexity depends
        on the graph's implementation of `iter(graph)`, `graph.get_neighbours`
        and `graph[node_from:node_to]`.

    :py:const:`None`
        Initialize the graph as empty.

    :note: :py:class:`~AdjacencyGraph` does not store `max_distance`. It is not
           checked when adding edges or merging other graphs.
    """
    def __init__(self, source=None, max_distance=dengraph.graph.ANY_DISTANCE):
        self._adjacency = {}  # {node: {neighbour: distance, neighbour: distance, ...}, ...}
        if isinstance(source, dengraph.graph.Graph):
            self._adjacency.update(self._adjacency_from_graph(source, max_distance))
        elif isinstance(source, dengraph.compat.collections_abc.Mapping):
            self._adjacency.update(self._adjacency_from_dict(source, max_distance))
        elif source is None:
            # initialize empty graph
            pass
        else:
            raise TypeError("parameter 'source' must be an instance of Graph, a Mapping or None")

    @staticmethod
    def _adjacency_from_graph(graph, max_distance):
        adjacency = {}
        for node in graph:
            adjacency[node] = {other: graph[node:other] for other in graph.get_neighbours(node, max_distance)}
        return adjacency

    @staticmethod
    def _adjacency_from_dict(adjacency_dict, max_distance):
        adjacency = {}
        for node, neighbours in dengraph.compat.viewitems(adjacency_dict):
            if max_distance is dengraph.graph.ANY_DISTANCE:
                adjacency[node] = {other: neighbours[other] for other in neighbours}
            else:
                adjacency[node] = {
                    other: neighbours[other] for other in neighbours if neighbours[other] <= max_distance
                }
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
            try:
                return self._adjacency[item]
            except KeyError:
                raise dengraph.graph.NoSuchNode

    def __setitem__(self, item, value):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            node_from, node_to = item.start, item.stop
            if node_to not in self._adjacency:
                raise dengraph.graph.NoSuchNode  # second edge node
            try:
                self._adjacency[node_from][node_to] = value
                if self.symmetric:
                    self._adjacency[node_to][node_from] = value
            except KeyError:
                raise dengraph.graph.NoSuchNode  # first edge node
        else:
            # g[a] = g[a]
            if self._adjacency.get(item, object()) is value:
                return
            # g[a] = None, g[a] = a
            elif value is None or value is item:
                if item not in self._adjacency:
                    self._adjacency[item] = {}
            # g[a] = {b: 3, c: 4, d: 6}
            else:
                self._adjacency[item] = value.copy()

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            node_from, node_to = item.start, item.stop
            try:
                del self._adjacency[node_from][node_to]
            except KeyError:
                raise dengraph.graph.NoSuchEdge
        else:
            try:
                del self._adjacency[item]
            except KeyError:
                raise dengraph.graph.NoSuchNode
            else:
                # clean up all edges to this node
                for node in self:
                    self._adjacency[node].pop(item, None)

    def __iter__(self):
        return iter(self._adjacency)

    def get_neighbours(self, node, distance=dengraph.graph.ANY_DISTANCE):
        try:
            adjacency_list = self._adjacency[node]
        except KeyError:
            raise dengraph.graph.NoSuchNode
        else:
            if distance is dengraph.graph.ANY_DISTANCE:
                return iter(adjacency_list)
            return (neighbour for neighbour in adjacency_list if adjacency_list[neighbour] <= distance)

    def __add__(self, other):
        if isinstance(other, dengraph.graph.Graph):
            new_adjacency = {}
            for node in itertools.chain(self, other):
                if node in new_adjacency:
                    continue
                self_adjacency = self[node].copy() if node in self else {}
                other_adjacency = other[node].copy() if node in other else {}
                # make sure there is no ambiguity in edges from sequence of merging
                for common_node in dengraph.compat.viewkeys(self_adjacency) & dengraph.compat.viewkeys(other_adjacency):
                    if self_adjacency[common_node] != other_adjacency[common_node]:
                        raise ValueError('Edge [%r:%r] inconsistent between nodes' % (node, common_node))
                other_adjacency.update(self_adjacency)
                new_adjacency[node] = other_adjacency
            return self.__class__(new_adjacency)
        return NotImplemented

    def __repr__(self):
        return '%s(adjacency=%s)' % (
            self.__class__.__name__,
            dengraph.utilities.pretty.repr_container(self._adjacency)
        )


class BoundedAdjacencyGraph(AdjacencyGraph):
    """
    Graph storing distances via bounded adjacency lists

    :param source: adjacency mapping or graph
    :param max_distance: maximum allowed distance

    :see: :py:class:`~AdjacencyGraph` for formats of the `source` parameter.

    Instances of this class store their `max_distance` parameter. It is used
    to optimize memory and lookups. Any edges bigger than `max_distance` are
    silently ignored when trying to insert them. Querying for neighbours via
    :py:meth:`get_neighbours` is optimized if the search distance is higher
    than the graph's bound.
    """
    def __init__(self, source=None, max_distance=dengraph.graph.ANY_DISTANCE):
        self._max_distance = max_distance
        self._effective_bound = None
        super(BoundedAdjacencyGraph, self).__init__(source=source, max_distance=max_distance)

    def __setitem__(self, item, value):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            # do not add edges exceeding our maximum distance
            if self._max_distance is not dengraph.graph.ANY_DISTANCE and self._max_distance < value:
                return
        super(BoundedAdjacencyGraph, self).__setitem__(item, value)

    def get_neighbours(self, node, distance=dengraph.graph.ANY_DISTANCE):
        try:
            adjacency_list = self._adjacency[node]
        except KeyError:
            raise dengraph.graph.NoSuchNode
        else:
            if (
                distance is dengraph.graph.ANY_DISTANCE or (
                    self._max_distance is not dengraph.graph.ANY_DISTANCE and
                    self._max_distance <= distance
                )
            ):
                return iter(adjacency_list)
            return (neighbour for neighbour in adjacency_list if adjacency_list[neighbour] <= distance)
