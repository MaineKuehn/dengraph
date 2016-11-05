import unittest
import random
import itertools


import dengraph.graphs.distance_graph
from dengraph.graph import NoSuchNode, NoSuchEdge
from dengraph.distances.delta_distance import DeltaDistance


class TestDistanceGraph(unittest.TestCase):
    #: the distance function/class with which to test
    distance_cls = DeltaDistance
    #: distance graph class to test
    graph_cls = dengraph.graphs.distance_graph.DistanceGraph

    @staticmethod
    def random_nodes(length_hint):
        return list({random.randint(-length_hint * 10, length_hint * 10) for _ in range(length_hint)})

    def make_node_samples(self, lengths=range(5, 101, 20)):
        yield [1, 2, 3, 10]
        for length in lengths:
            yield self.random_nodes(length)

    def test_symmetric(self):
        """Distance Graph: symmetric elements for symmetric distance"""
        if not self.distance_cls.is_symmetric:
            self.skipTest('Distance is not symmetric')
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = self.graph_cls(
                nodes,
                distance,
                symmetric=True
            )
            for node_a, node_b in itertools.product(nodes, nodes):
                self.assertEqual(distance(node_a, node_b), graph[node_a:node_b])
                self.assertEqual(graph[node_a:node_b], graph[node_b:node_a])

    def test_len(self):
        """Distance Graph: length is node count"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls(nodes, self.distance_cls())
            self.assertEqual(len(graph), len(nodes))

    def test_iter(self):
        """Distance Graph: iter produces all nodes"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls(nodes, self.distance_cls())
            self.assertSetEqual(set(iter(graph)), set(nodes))

    def test_contains_node(self):
        """Distance Graph: node in graph"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls(nodes, self.distance_cls())
            for node in nodes:
                self.assertIn(node, graph)
            self.assertNotIn(object(), graph)
            self.assertNotIn(None, graph)
            self.assertNotIn(max(nodes) + 1, graph)
            self.assertNotIn(min(nodes) - 1, graph)

    def test_contains_edge(self):
        """Distance Graph: edge in graph"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls(nodes, self.distance_cls())
            for node_a, node_b in itertools.product(nodes, nodes):
                self.assertIn(slice(node_a, node_b), graph)
            for node_a, node_b in itertools.product(nodes, (object(), None, max(nodes) + 1, min(nodes) - 1)):
                self.assertNotIn(slice(node_a, node_b), graph)
                self.assertNotIn(slice(node_b, node_a), graph)

    def test_getitem_edge(self):
        """Distance Graph: only edges for contained nodes"""
        for symmetric in (True, False):
            with self.subTest(symmetric=symmetric):
                for nodes in self.make_node_samples():
                    distance = self.distance_cls()
                    graph = self.graph_cls(nodes, distance)
                    for node_a, node_b in itertools.product(nodes, nodes):
                        self.assertEqual(distance(node_a, node_b), graph[node_a:node_b])
                        self.assertEqual(distance(node_a, node_b), graph[slice(node_a, node_b)])
                    for node_a, node_b in itertools.product(nodes, (object(), None, max(nodes) + 1, min(nodes) - 1)):
                        with self.assertRaises(NoSuchEdge):
                            graph[node_a:node_b]
                        with self.assertRaises(NoSuchEdge):
                            graph[node_b:node_a]

    def test_getitem_node(self):
        """Distance Graph: cannot get nodes"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls(nodes, self.distance_cls())
            for node in nodes:
                with self.assertRaises(TypeError):
                    graph[node]

    def test_setitem_edge(self):
        """Distance Graph: cannot set edges"""
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = self.graph_cls(nodes, distance)
            for node_a, node_b in itertools.product(nodes, nodes):
                with self.assertRaises(TypeError):
                    graph[node_a:node_b] = 0
            for node_a, node_b in itertools.product(nodes, (object(), None, max(nodes) + 1, min(nodes) - 1)):
                with self.assertRaises(TypeError):
                    graph[node_a:node_b] = 0
                with self.assertRaises(TypeError):
                    graph[node_b:node_a] = 0

    def test_setitem_node(self):
        """Distance Graph: set nodes"""
        for nodes in self.make_node_samples():
            graph = self.graph_cls([], self.distance_cls())
            last_len = 0
            for node in nodes:
                self.assertEqual(len(graph), last_len)
                last_len += 1
                graph[node] = {}
            self.assertEqual(len(graph), last_len)

    def test_delitem_edge(self):
        """Distance Graph: remove edges"""
        for symmetric in (True, False):
            with self.subTest(symmetric=symmetric):
                for nodes in self.make_node_samples():
                    distance = self.distance_cls()
                    graph = self.graph_cls(nodes, distance, symmetric=symmetric)
                    for node_a, node_b in itertools.product(nodes, nodes):
                        del graph[node_a:node_b]
                    for node_a, node_b in itertools.product(nodes, (object(), None, max(nodes) + 1, min(nodes) - 1)):
                        with self.assertRaises(NoSuchEdge):
                            del graph[node_a:node_b]
                        with self.assertRaises(NoSuchEdge):
                            del graph[node_b:node_a]

    def test_delitem_node(self):
        """Distance Graph: remove nodes"""
        for symmetric in (True, False):
            with self.subTest(symmetric=symmetric):
                for nodes in self.make_node_samples():
                    graph = self.graph_cls(nodes, self.distance_cls(), symmetric=symmetric)
                    for node in (object(), None, max(nodes) + 1, min(nodes) - 1):
                        with self.assertRaises(NoSuchNode):
                            del graph[node]
                    last_len = len(nodes)
                    for node in nodes:
                        self.assertEqual(len(graph), last_len)
                        last_len -= 1
                        del graph[node]
                        with self.assertRaises(NoSuchNode):
                            del graph[node]
                    for node in (object(), None, max(nodes) + 1, min(nodes) - 1):
                        with self.assertRaises(NoSuchNode):
                            del graph[node]

    def test_attributes(self):
        for nodes in self.make_node_samples():
            distance = self.distance_cls()
            graph = self.graph_cls(
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
        graph = self.graph_cls(
            nodes,
            distance,
            symmetric=True
        )
        for node in nodes:
            self.assertEqual(graph.get_neighbours(node, distance=threshold),
                             [elem for elem in range(node-threshold, node+threshold+1)
                              if elem != node and 0 <= elem < maximum])

    def test_exception(self):
        graph = self.graph_cls(
            nodes=[],
            distance=None,
            symmetric=True
        )
        self.assertIsNotNone(graph)
        with self.assertRaises(NoSuchNode):
            del graph[1]
