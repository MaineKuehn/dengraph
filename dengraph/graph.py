class NoSuchEdge(Exception):
    pass


class NoSuchNode(Exception):
    pass


class Graph(object):
    """
    Abstract Base Class for graphs represented via nodes

    Graphs are modelled as containers of *nodes* and *edges* between pairs of
    nodes. The graph interface used for :py:mod:`dengraph` primarily works on
    nodes: for example, `len(graph)`, and `iter(graph)` treat `graph` as a
    container for nodes. Edges are accessed via their node pair, e.g. as
    `graph[node_a:node_b]`.

    :warning: Nodes and edges may be of any type in general. However, nodes
              may *not* be of type :py:class:`slice` with two elements. Such
              nodes would be erroneously treated as edge identifiers.

    All implementations of this ABC guarantee the following operators:

    .. describe:: len(g)

      Return the number of nodes in the graph *g*.

    .. describe:: g[a:b]

      Return the edge between nodes `a` and `b`. Raises :py:exc:`NoSuchEdge` if
      no edge is defined for the nodes. Implementations of undirected graphs
      must guarantee `g[a, b] == `g[b, a]`.

    .. describe:: g[a:b] = value

      Set the edge between nodes `a` and `b` to `value` for graph `g`.

    .. describe:: del g[a:b]

      Remove the edge between nodes `a` and `b` from `g`.  Raises
      :exc:`NoSuchEdge` if the edge is not in the graph.

    .. describe:: del g[a]

      Remove the node `a` and all its edges from `g`.  Raises
      :exc:`NoSuchNode` if the node is not in the graph.

    .. describe:: a in g

      Return `True` if `g` has a node `a`, else `False`.

    .. describe:: iter(g)

      Return an iterator over the nodes in `g`.

    In addition, several methods are provided. While methods for retrieving
    data must be implemented by all subclasses, methods for *modifying* data
    may not be applicable to certain graphs.
    """
    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, a_b):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def get_neighbours(self, node, distance):
        """
        Get all nodes with edge weight to `node` smaller or equal to `distance`

        :param node: node from which edges originate.
        :param distance: maximum allowed distance to other nodes.
        :return: list of neighbouring nodes
        """
        raise NotImplementedError

    # TODO:
    # Interface for insert/remove node/edge, update edge

    # TODO:
    # -- intra distance
    # -- inter distance
