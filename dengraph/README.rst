dengraph - Density-based Graph Clustering
=========================================

|travis| |codecov| |landscape|

DenGraph performs a density-based graph clustering.
The algorithm was proposed as an extension for DBSCAN to support overlapping clusters.
The approach is based around the neighbourhood of a node.
The neighbourhood is defined by the *number* of reachable nodes within a given *distance*.
Therefore, large groups of items which are close to each other form clusters.
As DenGraph is a non-partitioning approach, isolated, distinct and uncommon items are left unclustered.
Instead, they are treated as noise.

Quick Overview
--------------

To use ``dengraph`` for clustering your data, two steps are required:

- Your data must be provided via the ``dengraph.graph.Graph`` interface.
  See the ``dengraph.graphs`` module for appropriate containers and examples.

- The graph must be fed to ``dengraph.dengraph.DenGraphIO``.

.. code:: python

    >>> from dengraph.graphs.distance_graph import DistanceGraph
    >>> from dengraph.dengraph import DenGraphIO
    >>> # Graph with defined nodes, edges from distance function
    >>> graph = DistanceGraph(
    ...     nodes=(1, 2, 3, 4, 5, 10, 11, 13, 14, 15, 17, 22, 23, 24, 25, 28, 29, 30, 31),
    ...     distance=lambda node_from, node_to: abs(node_from - node_to)
    ... )
    >>> # Cluster the graph
    >>> clustered_data = DenGraphIO(graph, cluster_distance=2, core_neighbours=3).clusters
    >>> # And print clusters
    >>> for cluster in sorted(clustered_data, key=lambda clstr: min(clstr)):
    ...     print(sorted(cluster))
    [1, 2, 3, 4, 5]
    [11, 13, 14, 15, 17]
    [22, 23, 24, 25]
    [28, 29, 30, 31]

Further Information
-------------------

At the moment, you must refer to the module and class documentation.

- See ``dengraph.dengraph.DenGraphIO`` for an explanation of clustering settings.

- See ``dengraph.graph.Graph`` for documentation of the graph interface.

Useful Classes
..............

We provide several implementations and tools for the ``Graph`` interface:

- Create a graph from a list of nodes and a distance function via ``dengraph.graphs.distance_graph.DistanceGraph``

- Create a graph from adjacency lists via ``dengraph.graphs.adjacency_graph.AdjacencyGraph``

- Read a distance matrix to a graph via ``dengraph.graphs.graph_io.csv_graph_reader``

Frequently Asked Questions
--------------------------

- Why is there no ``DenGraphHO`` class?

  We haven't implemented that one yet.
  It's on our Todo.

- Why is there no ``DenGraph`` class?

  The original DenGraph algorithm is non-deterministic for unordered graphs.
  Since border nodes can belong to only one cluster, the first cluster wins - results depend on iteration order.
  The ``DenGraphIO`` algorithm does not have this issue and performs equally well.

- Why is ``DenGraphO`` the same class as ``DenGraphIO``?

  Algorithmically, ``DenGraphIO`` is basically ``DenGraphO`` *plus* the option to insert/remove/modify nodes/edges.
  In the static case (just initialisation), both are equivalent.
  At the moment, we don't have any optimisations based on immutability of ``DenGraphO``.
  The alias exists so that applications can distinguish between the two, possibly benefiting from future optimisations.

Acknowledgement
---------------

This module is based on several publications:

- [1] T. Falkowski, A. Barth, and M. Spiliopoulou, "DENGRAPH: A Density-based Community Detection Algorithm," presented at the IEEE/WIC/ACM International Conference on Web Intelligence (WI'07), 2007, pp. 112–115.
- [2] T. Falkowski, A. Barth, and M. Spiliopoulou, “Studying community dynamics with an incremental graph mining algorithm,” AMCIS 2008 Proceedings, 2008.
- [3] N. Schlitter, T. Falkowski, and J. Lässig, "DenGraph-HO - a density-based hierarchical graph clustering algorithm.," Expert Systems, vol. 31, no. 5, pp. 469–479, 2014.


.. |travis| image:: https://travis-ci.org/MaineKuehn/dengraph.svg?branch=master
    :target: https://travis-ci.org/MaineKuehn/dengraph
    :alt: Unit Tests

.. |codecov| image:: https://codecov.io/gh/MaineKuehn/dengraph/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MaineKuehn/dengraph
  :alt: Code Coverage

.. |landscape| image:: https://landscape.io/github/MaineKuehn/dengraph/master/landscape.svg?style=flat
   :target: https://landscape.io/github/MaineKuehn/dengraph/master
   :alt: Code Health
