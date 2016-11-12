import dengraph.distance

from dengraph_unittests.utility import unittest

from dengraph.quality.silhouette import silhouette_score
from dengraph.graphs.distance_graph import DistanceGraph
from dengraph.distances.delta_distance import DeltaDistance
from dengraph.dengraph import DenGraphIO


class ListDistance(dengraph.distance.Distance):
    def __call__(self, first, second, default=None):
        return abs(first[0] - second[0])

    def median(self, *args, **kwargs):
        pass

    def mean(self, *args, **kwargs):
        if len(args) == 1:
            args = [value_list[0] for value_list in args[0]]
        return sum(args) / float(len(args))


class TestSilhouette(unittest.TestCase):
    def test_zero_cluster(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=1,
            core_neighbours=5
        )
        with self.assertRaises(ValueError):
            silhouette_score(io_graph.clusters, io_graph.graph)

    def test_one_cluster(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=DeltaDistance(),
                symmetric=True),
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertEqual(-1, silhouette_score(io_graph.clusters, io_graph.graph))

    def test_one_cluster_inter_zero(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[(1,1), (1,2), (1,3), (1,4), (1,5), (1,6)],
                distance=ListDistance(),
                symmetric=True),
            cluster_distance=.1,
            core_neighbours=5
        )
        self.assertEqual(0, silhouette_score(io_graph.clusters, io_graph.graph))

    def test_two_cluster(self):
        io_graph = DenGraphIO(
            base_graph=DistanceGraph(
                nodes=[(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (2,1), (2,2), (2,3), (2,4), (2,5), (2,6)],
                distance=ListDistance(),
                symmetric=True),
            cluster_distance=.1,
            core_neighbours=5
        )
        self.assertEqual(1.0, silhouette_score(io_graph.clusters, io_graph.graph))

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
        self.assertEqual(10, len(io_graph.clusters))
        self.assertEqual(1.0, silhouette_score(io_graph.clusters, io_graph.graph))
