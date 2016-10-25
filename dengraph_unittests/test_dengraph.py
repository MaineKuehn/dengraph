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
