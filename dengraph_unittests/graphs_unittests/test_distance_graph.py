import unittest
import random
import itertools


import dengraph.graphs.distance_graph
from dengraph.graph import NoSuchNode


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

    def make_node_samples(self, lengths=range(5, 101, 20)):
        yield [1, 2, 3, 10]
        for length in lengths:
            yield self.random_nodes(length)

    def test_symmetric(self):
        if not self.distance_cls.is_symmetric:
            self.skipTest('Distance is not symmetric')
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = dengraph.graphs.distance_graph.DistanceGraph(
                nodes,
                distance,
                symmetric=True
            )
            for node_a, node_b in itertools.product(nodes, nodes):
                self.assertEqual(distance(node_a, node_b), graph[node_a:node_b])
                self.assertEqual(graph[node_a:node_b], graph[node_b:node_a])

    def test_diagonal(self):
        if not self.distance_cls.is_symmetric:
            self.skipTest('Distance is not symmetric')
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = dengraph.graphs.distance_graph.DistanceGraph(
                nodes,
                distance,
                symmetric=True
            )
            for node in nodes:
                self.assertEqual(0, distance(node, node))
                self.assertEqual(distance(node, node), graph[node:node])

    def test_attributes(self):
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = dengraph.graphs.distance_graph.DistanceGraph(
                nodes,
                distance,
                symmetric=True
            )
            for node in nodes:
                self.assertTrue(node in graph)  # checking for contains
            self.assertEqual(len(set(nodes)), len(graph))  # checking for length

            graph_nodes = set()
            for node in graph:
                graph_nodes.add(node)
            self.assertEqual(graph_nodes, set(nodes))

    def test_neighbors(self):
        maximum = 20
        threshold = 1
        nodes = list(range(maximum))
        distance = self.distance_cls()
        graph = dengraph.graphs.distance_graph.DistanceGraph(
            nodes,
            distance,
            symmetric=True
        )
        for node in nodes:
            self.assertEqual(graph.get_neighbours(node, distance=threshold),
                             [elem for elem in range(node-threshold, node+threshold+1)
                              if elem != node and 0 <= elem < maximum])

    def test_exception(self):
        graph = dengraph.graphs.distance_graph.DistanceGraph(
            nodes=[],
            distance=None,
            symmetric=True
        )
        self.assertIsNotNone(graph)
        with self.assertRaises(NoSuchNode):
            del graph[1]
