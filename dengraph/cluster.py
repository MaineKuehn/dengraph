from __future__ import absolute_import
import dengraph.graph
import dengraph.utilities.pretty


class GraphError(Exception):
    pass


class DenGraphCluster(dengraph.graph.Graph):
    """
    Cluster in a DenGraph

    :param graph: underlying graph of which this cluster is a subgraph
    :type graph: :py:class:`~dengraph.graph.Graph`
    :param core_nodes: initial set of core nodes
    :type core_nodes: set or None
    :param border_nodes: initial set of border nodes
    :type border_nodes: set or None
    """
    CORE_NODE = 1
    BORDER_NODE = 2

    def __init__(self, graph, core_nodes=None, border_nodes=None):
        self.graph = graph
        self.core_nodes = set(core_nodes) if core_nodes is not None else set()
        self.border_nodes = set(border_nodes) if border_nodes is not None else set()

    def categorize_node(self, node, state):
        """
        Mark a node as core or border

        Categorizes the node in a safe way. The node is guaranteed to be marked
        *either* core or border, regardless of insertion history.

        :param node: node to categorize
        :param state: category of the node
        :type state: :py:attr:`DenGraphCluster.CORE_NODE` or :py:attr:`DenGraphCluster.BORDER_NODE`
        """
        if state == self.CORE_NODE:
            self.border_nodes.discard(node)
            self.core_nodes.add(node)
        elif state == self.BORDER_NODE:
            self.core_nodes.discard(node)
            self.border_nodes.add(node)
        else:
            raise ValueError(
                'invalid state %r, expected %r (%s.CORE_NODE) or %r (%s.BORDER_NODE)' % (
                    state, self.CORE_NODE, self.__class__.__name__, self.BORDER_NODE, self.__class__.__name__
                ))

    def __len__(self):
        return len(self.core_nodes) + len(self.border_nodes)

    def __iter__(self):
        for node in self.core_nodes:
            yield node
        for node in self.border_nodes:
            yield node

    def __getitem__(self, a_b):
        if isinstance(a_b, slice):
            node_a, node_b = a_b.start, a_b.stop
            if node_a not in self:
                raise dengraph.graph.NoSuchEdge
            if node_b not in self:
                raise dengraph.graph.NoSuchEdge
            return self.graph[a_b]
        return NotImplemented

    def __delitem__(self, key):
        if isinstance(key, slice):
            return NotImplemented
        self.core_nodes.discard(key)
        self.border_nodes.discard(key)

    def __setitem__(self, key, value):
        raise TypeError('Cannot add new nodes/edges to cluster')

    def __contains__(self, node):
        return node in self.border_nodes or node in self.core_nodes

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.core_nodes == other.core_nodes and self.border_nodes == other.border_nodes
        return NotImplemented

    def __ne__(self, other):
        if isinstance(self, other.__class__):
            return self.core_nodes != other.core_nodes or self.border_nodes != other.border_nodes
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(self, other.__class__):
            if self.graph != other.graph:
                raise GraphError
            if self == other:
                return self
            self.core_nodes.update(other.core_nodes)
            self.border_nodes.update(other.border_nodes)
            # ensure that none of the core nodes are in list of border nodes
            self.border_nodes = self.border_nodes - self.core_nodes
            return self
        return NotImplemented

    def __add__(self, other):
        if isinstance(self, other.__class__):
            if self.graph != other.graph:
                raise GraphError
            cluster = DenGraphCluster(self.graph)
            cluster.border_nodes = self.border_nodes.union(other.border_nodes)
            cluster.core_nodes = self.core_nodes.union(other.core_nodes)
            cluster.border_nodes = cluster.border_nodes - cluster.core_nodes
            return cluster
        return NotImplemented

    def __isub__(self, other):
        if isinstance(self, other.__class__):
            if self.graph != other.graph:
                raise GraphError
            if self == other:
                self.core_nodes.clear()
                self.border_nodes.clear()
                return self
            if not (other.core_nodes.issubset(self.core_nodes) and
                    other.border_nodes.issubset(self.border_nodes)):
                raise dengraph.graph.NoSuchNode
            self.core_nodes = self.core_nodes - other.core_nodes
            self.border_nodes = self.border_nodes - other.border_nodes
            return self
        return NotImplemented

    def __sub__(self, other):
        if isinstance(self, other.__class__):
            if self.graph != other.graph:
                raise GraphError
            if not (other.core_nodes.issubset(self.core_nodes) and
                    other.border_nodes.issubset(self.border_nodes)):
                raise dengraph.graph.NoSuchNode
            cluster = DenGraphCluster(self.graph)
            cluster.border_nodes = self.border_nodes - other.border_nodes
            cluster.core_nodes = self.core_nodes - other.core_nodes
            return cluster
        return NotImplemented

    def get_neighbours(self, node, distance=dengraph.graph.ANY_DISTANCE):
        return [
            neighbour for neighbour in self.graph.get_neighbours(node, distance)
            if neighbour in self
        ]

    def __repr__(self):
        return '%s(graph=%s, core_nodes=%s, border_nodes=%s)' % (
            self.__class__.__name__,
            self.graph,
            dengraph.utilities.pretty.repr_container(self.core_nodes),
            dengraph.utilities.pretty.repr_container(self.border_nodes),
        )

    def __hash__(self):
        return hash((self.__class__, id(self)))


class FrozenDenGraphCluster(DenGraphCluster):
    """
    Immutable, hashable cluster in a DenGraph

    Clusters of this type cannot be modified but behave properly in `dict` and other mappings.
    """
    def __init__(self, graph, core_nodes=None, border_nodes=None):
        if isinstance(graph, DenGraphCluster):
            assert core_nodes is None and border_nodes is None, "Cloning takes only one argument"
            core_nodes = graph.core_nodes
            border_nodes = graph.border_nodes
            graph = graph.graph
        super(FrozenDenGraphCluster, self).__init__(graph, core_nodes=core_nodes, border_nodes=border_nodes)
        self.core_nodes = frozenset(self.core_nodes)
        self.border_nodes = frozenset(self.border_nodes)

    def __hash__(self):
        return hash((self.__class__, self.core_nodes, self.border_nodes))

    def categorize_node(self, node, state):
        raise TypeError('%s object does not support content modification' % self.__class__.__name__)

    def __iadd__(self, other):
        raise TypeError('%s object does not support content modification' % self.__class__.__name__)

    def __isub__(self, other):
        raise TypeError('%s object does not support content modification' % self.__class__.__name__)
