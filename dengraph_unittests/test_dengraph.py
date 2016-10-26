import unittest
import random

from dengraph.dengraph import DenGraphIO
from dengraph.graphs.distance_graph import DistanceGraph


class DeltaDistance(object):
    is_symmetric = True

    def __call__(self, a, b):
        return abs(a - b)


class TestDenGraphIO(unittest.TestCase):
    #: the distance function/class with which to test
    distance_cls = DeltaDistance

    @staticmethod
    def random_nodes(length, base):
        return [random.randint(base, 2*base) for _ in range(length)]

    def test_noise(self):
        graph = DistanceGraph(
            nodes=[1, 2, 3, 4, 5, 6, 20],
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertEqual(set([20]), io_graph.noise)

    def test_simple_graph(self):
        graph = DistanceGraph(
            nodes=self.random_nodes(100, 10) + self.random_nodes(100, 40),
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertEqual(2, len(io_graph.clusters))
        for index, cluster in enumerate(io_graph.clusters):
            print("%s (%s): %s" % (index, len(cluster), [element for element in cluster]))

    def test_simple_incremental_behaviour(self):
        nodes = [1, 2, 3, 4, 5, 6]
        validation_io_graph = self._validation_graph_for_nodes(
            nodes=nodes,
            distance=self.distance_cls,
            cluster_distance=5,
            core_neighbours=5)

        graph = DistanceGraph(
            nodes=[],
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertEqual(0, len(io_graph.clusters))
        for node in nodes:
            io_graph[node] = {}

        for cluster in io_graph.clusters:
            print("core %s, border %s" % (cluster.core_nodes, cluster.border_nodes))
        self.assertEqual(len(validation_io_graph.clusters), len(io_graph.clusters))
        self.assertEqual(validation_io_graph, io_graph)

    def test_add_incremental_behaviour(self):
        base_nodes = [1, 2, 3, 4, 5, 6, 7, 8]
        nodes_to_add = [10]
        validation_io_graph = self._validation_graph_for_nodes(
            nodes=base_nodes + nodes_to_add,
            distance=self.distance_cls,
            cluster_distance=5,
            core_neighbours=5
        )

        graph = DistanceGraph(
            nodes=base_nodes,
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        for node in nodes_to_add:
            io_graph[node] = {}
        self.assertEqual(validation_io_graph, io_graph)

    def test_noise_removal(self):
        base_nodes = [1, 2, 3, 4, 5, 6, 7, 8]
        remove_nodes = [30, 31]
        validation_io_graph = self._validation_graph_for_nodes(
            nodes=base_nodes,
            distance=self.distance_cls,
            cluster_distance=5,
            core_neighbours=5
        )
        graph = DistanceGraph(
            nodes=base_nodes+remove_nodes,
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertTrue(all([node in io_graph.noise for node in remove_nodes]))
        for node in remove_nodes:
            del io_graph[node]
        self.assertEqual(validation_io_graph, io_graph)
        self.assertTrue(all([node not in io_graph.noise for node in remove_nodes]))

    def test_remove_downgrade_behaviour(self):
        base_nodes = [1, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18]
        remove_nodes = [2]
        validation_io_graph = self._validation_graph_for_nodes(
            nodes=base_nodes,
            distance=self.distance_cls,
            cluster_distance=5,
            core_neighbours=5
        )
        graph = DistanceGraph(
            nodes=base_nodes + remove_nodes,
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        for node in remove_nodes:
            del io_graph[node]
        for cluster in io_graph.clusters:
            print("[downgrade]: core %s, border %s" % (cluster.core_nodes, cluster.border_nodes))
        for cluster in validation_io_graph.clusters:
            print("[downgrade_valid]: core %s, border %s" % (cluster.core_nodes, cluster.border_nodes))
        self.assertEqual(validation_io_graph, io_graph)

    def test_remove_incremental_behaviour(self):
        base_nodes = [1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16, 17]
        remove_nodes = [7]
        validation_io_graph = self._validation_graph_for_nodes(
            nodes=base_nodes,
            distance=self.distance_cls,
            cluster_distance=5,
            core_neighbours=5
        )
        graph = DistanceGraph(
            nodes=base_nodes + remove_nodes,
            distance=self.distance_cls(),
            symmetric=True
        )
        io_graph = DenGraphIO(
            base_graph=graph,
            cluster_distance=5,
            core_neighbours=5
        )
        for node in remove_nodes:
            del io_graph[node]
            self.assertEqual(validation_io_graph, io_graph)

    def _validation_graph_for_nodes(self, distance, nodes, cluster_distance, core_neighbours, graph_type=DistanceGraph):
        graph = graph_type(
            nodes=nodes,
            distance=distance(),
            symmetric=True
        )
        return DenGraphIO(
            base_graph=graph,
            cluster_distance=cluster_distance,
            core_neighbours=core_neighbours
        )
