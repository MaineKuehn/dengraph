# -*- coding: utf-8 -*-
from __future__ import absolute_import
from dengraph.dengraph import DenGraphIO
import dengraph.distance


class DenGraphVIO(DenGraphIO):
    """
    Density-based graph clustering that builds on DenGraphIO and therefore supports incremental
    clustering as well as overlapping clusters.
    The special about DenGraphVIO is the support for virtual nodes. Virtual nodes do not modify
    the underlying clustering but allow to get distances to the current instance of clusters.
    Virtual nodes can be updated anytime to get the current distances to available clusters.
    Virtual nodes are expected to by dynamic objects that will either converge to an existing
    cluster or diverge into noise. Whenever the dynamic object has finished, one can persist
    the virtual node to the current clustering.

    :param base_graph: the underlying graph
    :param cluster_distance: maximum distance for nodes to be considered as neighbours (ε)
    :param core_neighbours: number of neighbours required for core nodes (η)
    """

    def __init__(self, base_graph, cluster_distance, core_neighbours):
        try:
            if not isinstance(base_graph.distance, dengraph.distance.Distance):
                raise dengraph.distance.NoDistanceSupport
        except AttributeError:
            raise dengraph.distance.NoDistanceSupport
        self.virtual_nodes = {}
        super(DenGraphVIO, self).__init__(base_graph, cluster_distance, core_neighbours)

    def persist(self, virtual_node):
        del self.virtual_nodes[id(virtual_node)]
        self.graph[virtual_node] = None

    def probe(self, virtual_node):
        updated_node = self._update_distances(virtual_node)
        return (
            (cluster, distance)
            for cluster, distance in updated_node["distances"].items()
        )

    def update_probe(self, virtual_node, changes):
        updated_node = self._update_distances(virtual_node, changes)
        return (
            (cluster, distance)
            for cluster, distance in updated_node["distances"].items()
        )

    def _update_distances(self, virtual_node, changes=None):
        saved_node = self.virtual_nodes.setdefault(
            id(virtual_node), {"clusters": {}, "distances": {}}
        )
        distance = self.graph.distance
        for cluster in self.clusters:
            try:
                cluster_mean = saved_node["clusters"][cluster]
            except KeyError:
                cluster_mean = distance.mean(cluster)
                saved_node["clusters"][cluster] = cluster_mean
            if changes is not None:
                # update distance
                saved_node["distances"][cluster] = distance.update(
                    cluster_mean,
                    virtual_node,
                    changes,
                    saved_node["distances"][cluster],
                )
            else:
                saved_node["distances"][cluster] = distance(cluster_mean, virtual_node)
        return saved_node
