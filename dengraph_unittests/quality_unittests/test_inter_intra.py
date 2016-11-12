from dengraph_unittests.utility import unittest

from dengraph_unittests.quality_unittests.test_silhouette import ListDistance

from dengraph.quality.inter_intra import *
from dengraph.dengraph import DenGraphIO
from dengraph.distances.delta_distance import DeltaDistance
from dengraph.graphs.distance_graph import DistanceGraph


class TestInterIntra(unittest.TestCase):
    def setUp(self):
        self.io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=1,
            core_neighbours=5
        )
        self.one_cluster_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (2,1), (2,2), (2,3), (2,4), (2,5), (2,6)],
                distance=ListDistance(),
                symmetric=True),
            cluster_distance=.1,
            core_neighbours=5
        )

    def test_inter_cluster_mean_score(self):
        with self.assertRaises(ValueError):
            inter_cluster_mean_score(None, self.io_graph.graph)
        self.assertEqual(0, inter_cluster_mean_score(self.one_cluster_graph.clusters[0], self.one_cluster_graph.graph))

    def test_inter_cluster_mean_score_with_mean(self):
        cluster = self.one_cluster_graph.clusters[0]
        self.assertEqual(
            inter_cluster_mean_score(cluster, self.one_cluster_graph.graph),
            inter_cluster_mean_score(cluster, self.one_cluster_graph.graph, self.one_cluster_graph.graph.distance.mean(list(cluster)))
        )

    def test_inter_cluster_variance(self):
        self.assertEqual(0, inter_cluster_variance(self.one_cluster_graph.clusters, self.one_cluster_graph.graph))

    def test_inter_cluster_variance_zero_cluster(self):
        self.assertEqual(float("inf"), inter_cluster_variance(self.io_graph.clusters, self.io_graph.graph))

    def test_intra_cluster_variance(self):
        self.assertEqual(3, intra_cluster_variance(self.one_cluster_graph.clusters, self.one_cluster_graph.graph))
        self.assertEqual(0, intra_cluster_variance(
            [self.one_cluster_graph.clusters[0]], self.one_cluster_graph.graph
        ))
