dengraph - Density based Graph Clustering
=========================================

DenGraph clusters data based on point-to-point distance.
It uses a density based approach:
large groups of items which are close to each other form clusters.
Isolated, distinct and uncommon items are left unclustered.

Quick Overview
--------------

To use ``dengraph`` for clustering your data, two steps are required:

- Your data must provided via the ``dengraph.graph.Graph`` interface.
  See the ``dengraph.graphs`` module for appropriate containers and examples.

- The graph must be fed to ``dengraph.dengraph.DenGraphIO``.

.. code:: python

    from dengraph.graphs.distance_graph import DistanceGraph
    from dengraph.dengraph import DenGraphIO

    # Graph with defined nodes, edges from distance function
    graph = DistanceGraph(
        nodes=(1, 2, 3, 4, 5, 10, 11, 13, 14, 15, 17, 22, 23, 24, 25, 28, 29, 30, 31),
        distance=lambda node_from, node_to: abs(node_from - node_to)
    )
    # Cluster the graph
    clustered_data = DenGraphIO(graph, cluster_distance=2, core_neighbours=3).clusters
    # And print clusters
    for cluster in sorted(clustered_data, key=lambda clstr: min(clstr)):
        print(sorted(cluster))

Further Information
-------------------

At the moment, you must refer to the module and class documentation.

- See ``dengraph.dengraph.DenGraphIO`` for an explanation of clustering settings.

- See ``dengraph.graph.Graph`` for documentation of the graph interface.

Useful Classes
..............

We provide several implementations and tools for the ``Graph`` interface:

- Create a graph from a list of nodes and a distance function via ``dengraph.graphs.distance_graph.DistanceGraph``

- Create a graph fro adjacency lists via ``dengraph.graphs.adjacency_graph.AdjacencyGraph``

- Read a distance matrix to a graph via ``dengraph.graphs.graph_io.csv_graph_reader``

Frequently Asked Questions
--------------------------

- Why is there no ``DenGraphHO`` class?

  We haven't implemented that one yet.
  It's on our Todo.

- Why is there no ``DenGraph`` class?

  We consider the original DenGraph algorithm to be broken.
  Since border nodes can belong to only one cluster, the first cluster wins - results depend on iteration order.
  The ``DenGraphIO`` algorithm does not have this issue and perform equally well.

- Why is ``DenGraphO`` the same class as ``DenGraphIO``?

  Algorithmically, ``DenGraphIO`` is basically ``DenGraphO`` *plus* the option to insert/remove/modify nodes/edges.
  In the static case (just initialization), both are equivalent.
  At the moment, we don't have any optimisations based on immutability of ``DenGraphO``.
  The alias exists so that applications can distinguish between the two, possibly benefiting from future optimizations.

Acknowledgement
---------------

This module is based on several publications:

.. admonition:: DenGraph-HO: a density-based hierarchical graph clustering algorithm

    by Nico Schlitter, Tanja Falkowski and Jörg Lässig
