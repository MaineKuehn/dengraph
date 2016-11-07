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
        super(DenGraphVIO, self).__init__(base_graph, cluster_distance, core_neighbours)

    def probe(self, virtual_node):
        for cluster in self.clusters:
            yield cluster, self._distance_to_cluster(virtual_node, cluster)

    def update_probe(self, virtual_node, old_distance, cluster):
        distance = self.graph.distance
        cluster_mean = distance.mean(cluster)
        return distance.update(cluster_mean, [virtual_node], old_distance)

    def _distance_to_cluster(self, node, cluster):
        distance = self.graph.distance
        cluster_mean = distance.mean(cluster)
        return distance(cluster_mean, node)
