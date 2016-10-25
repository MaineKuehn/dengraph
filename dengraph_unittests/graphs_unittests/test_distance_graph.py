import unittest
import random
import itertools


import dengraph.graphs.distance_graph


class DeltaDistance(object):
    is_symmetric = True

    def __call__(self, a, b):
        return abs(a - b)


class TestDistanceGraph(unittest.TestCase):
    #: the distance function/class with which to test
    distance_cls = DeltaDistance

    @staticmethod
    def random_nodes(length):
        return [random.randint(-length * 10, length * 10) for _ in range(length)]

    def test_symmetric(self):
        if not self.distance_cls.is_symmetric:
            self.skipTest('Distance is not symmetric')
        for nodes in (
                nodes_factory() for nodes_factory in (
                    lambda: [1, 2, 3], lambda: self.random_nodes(5), lambda: self.random_nodes(20)
        )):
            distance = self.distance_cls()
            graph = dengraph.graphs.distance_graph.DistanceGraph(
                nodes,
                distance,
                symmetric=True
            )
            for node_a, node_b in itertools.product(nodes, nodes):
                self.assertEqual(distance(node_a, node_b), graph[node_a:node_b])
                self.assertEqual(graph[node_a:node_b], graph[node_b:node_a])
