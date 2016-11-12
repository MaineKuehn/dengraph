from dengraph_unittests.utility import unittest

from dengraph_unittests.quality_unittests.test_silhouette import ListDistance

from dengraph.quality.davies_bouldin import davies_bouldin_score
from dengraph.distances.delta_distance import DeltaDistance
from dengraph.graphs.distance_graph import DistanceGraph
from dengraph.dengraph import DenGraphIO


class TestDaviesBouldin(unittest.TestCase):
    def test_zero_clusters(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=1,
            core_neighbours=5
        )
        with self.assertRaises(ValueError):
            davies_bouldin_score(io_graph.clusters, io_graph.graph)

    def test_one_cluster(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=5,
            core_neighbours=5
        )
        with self.assertRaises(ValueError):
            davies_bouldin_score(io_graph.clusters, io_graph.graph)

    def test_two_cluster(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertEqual(.25, davies_bouldin_score(io_graph.clusters, io_graph.graph))

    def test_two_cluster_zero_inter_distance(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (2,1), (2,2), (2,3), (2,4), (2,5), (2,6)],
                distance=ListDistance(),
                symmetric=True),
            cluster_distance=.1,
            core_neighbours=5
        )
        self.assertEqual(0.0, davies_bouldin_score(io_graph.clusters, io_graph.graph))

    def test_several_cluster(self):
        node_list = []
        for node in range(10):
            for position in range(10):
                node_list.append((node,position))
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=node_list,
                distance=ListDistance(),
                symmetric=True),
            cluster_distance=.1,
            core_neighbours=5
        )
        self.assertEqual(0.0, davies_bouldin_score(io_graph.clusters, io_graph.graph))
