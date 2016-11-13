@object.__new__
class Edge(object):
    """
    Factory for creating edges independent of graph access

    This is a verbose interface for creating :py:mod:`dengraph`'s lightweight
    edges via slice notation, without interacting with a graph.

    .. code:: python

        >>> atb = Edge[a:b]
        >>> a2b = Edge(a, b)
        >>> g[a:b] == g[atb] == g[a2b] == g[Edge[a:b]] == g[Edge(a, b)]

    This interface can also be used to make containment tests explicit.

    .. code:: python

        >>> Edge[a:b] in g

    :note: Edges created by this factory **cannot** be modified, assigned
           attributes, or used in :py:func:`hash`-based containers such as
           :py:class:`set` or :py:class:`dict` keys.
    """
    def __call__(self, node_from, node_to):
        return self[node_from:node_to]

    def __getitem__(self, item):
        if not isinstance(item, slice):
            raise TypeError('%s supports only slice notation' % self.__class__.__name__)
        return item

    def __repr__(self):
        return repr(self.__class__)
